"""Dependabot-owned workflow pins; repository-local metadata reconciliation.

The runtime writer deliberately cannot create/update workflow blobs. Native
Dependabot owns those changes; GITHUB_TOKEN writes only the JSON/Markdown bundle.
"""

from __future__ import annotations

import base64
import copy
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

import yaml
from packaging.version import Version

from . import reference
from .planning import recorded_release_override, recorded_standards_update

CENTRAL = "eigger/hass-repo-standards"
PREFIX = CENTRAL + "/"
DEPENDENCIES = [CENTRAL, PREFIX + "*"]
CALLER = ".github/workflows/update_standards.yml"
MANAGED = {".hass-standards.json", "STANDARDS.md"}
PROVIDER = reference.UPDATE_PROVIDER
LEGACY_NUMBER_INPUT = "${{ github.event.pull_request.number || inputs.pull-request-number || 0 }}"
NUMBER_INPUT = "${{ fromJSON(format('{0}', github.event.pull_request.number || inputs.pull-request-number || 0)) }}"


def caller_contract(document):
    """Recognize the one prior input expression without relaxing other caller fields."""
    result = copy.deepcopy(document)
    inputs = result.get("jobs", {}).get("update", {}).get("with", {})
    if inputs.get("pull-request-number") == LEGACY_NUMBER_INPUT:
        inputs["pull-request-number"] = NUMBER_INPUT
    return result


class Loader(yaml.SafeLoader):
    """GitHub YAML 1.2 event keys with true/false booleans."""


Loader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in items if tag != "tag:yaml.org,2002:bool"]
    for key, items in Loader.yaml_implicit_resolvers.items()
}
Loader.add_implicit_resolver(
    "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), list("tTfF")
)


def yaml_document(text):
    result = yaml.load(text, Loader=Loader)
    if not isinstance(result, dict):
        raise ValueError("Expected a YAML mapping")
    return result


def gh(endpoint, *, payload=None, method=None):
    command = ["gh", "api", endpoint]
    if method:
        command.extend(["--method", method])
    if payload is not None:
        command.extend(["--input", "-"])
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return json.loads(result) if result.strip() else None


def pages(endpoint):
    raw = subprocess.check_output(["gh", "api", "--paginate", "--slurp", endpoint], text=True)
    return [item for page in json.loads(raw) for item in page]


def blob(repository, sha, api=gh):
    result = api(f"repos/{repository}/git/blobs/{sha}")
    if result.get("encoding") != "base64":
        raise ValueError("Expected a base64 Git blob")
    return base64.b64decode(result["content"], validate=False).decode("utf-8")


def tree_files(repository, sha, api=gh):
    result = api(f"repos/{repository}/git/trees/{sha}?recursive=1")
    if result.get("truncated"):
        raise ValueError("Repository tree is truncated; refusing incomplete discovery")
    return {
        item["path"]: (item["sha"], item["mode"], item["type"])
        for item in result["tree"]
        if item["type"] != "tree"
    }


def central_uses(text):
    found = []

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            uses = value.get("uses")
            if isinstance(uses, str) and uses.startswith(PREFIX):
                if "@" not in uses:
                    raise ValueError("Central uses is missing a reference")
                found.append(uses.rsplit("@", 1))
            for item in value.values():
                walk(item)

    walk(yaml_document(text))
    return found


def normalized_workflow(text):
    document = copy.deepcopy(yaml_document(text))

    def walk(value):
        if isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            use = value.get("uses")
            if isinstance(use, str) and use.startswith(PREFIX):
                value["uses"] = use.rsplit("@", 1)[0] + "@<central-release>"
            for item in value.values():
                walk(item)

    walk(document)
    return document


def candidate_release(base_workflows, head_workflows, old, override=None):
    """Prove the PR changes central pins only, and all pins move as one bundle."""
    if set(base_workflows) != set(head_workflows):
        raise ValueError("Standards update may not add/delete/rename validation workflows")
    changed = set()
    for path, before in base_workflows.items():
        after = head_workflows[path]
        if normalized_workflow(before) != normalized_workflow(after):
            raise ValueError(f"Non-reference workflow change: {path}")
        previous = central_uses(before)
        current = central_uses(after)
        if len(previous) != len(current):
            raise ValueError("Central dependency set changed")
        for (before_path, before_ref), (after_path, after_ref) in zip(previous, current):
            if before_path != after_path:
                raise ValueError("Central dependency path changed")
            if before_ref != after_ref:
                if after_path.endswith("actions/release-zip") and before_ref == override:
                    raise ValueError("PR changes an explicitly scoped ZIP exception")
                if not reference.TAG.fullmatch(after_ref):
                    raise ValueError("Expected a stable exact release tag")
                changed.add(after_ref)
    if len(changed) != 1:
        raise ValueError("Expected exactly one new central release")
    tag = changed.pop()
    if Version(tag[1:]) <= Version(old["tag"][1:]):
        raise ValueError("Refusing a downgrade or same-version repair disguised as an update")
    for text in head_workflows.values():
        for path, ref in central_uses(text):
            if path.endswith("actions/release-zip") and ref == override:
                continue
            if ref != tag:
                raise ValueError("Partial central release update; wait for the complete group")
    return tag


def attest_release(tag, *, api=gh, runner=subprocess.check_output):
    if not reference.TAG.fullmatch(tag):
        raise ValueError("Expected an exact stable central release")
    release = api(f"repos/{CENTRAL}/releases/tags/{tag}")
    if (
        release.get("tag_name") != tag
        or release.get("draft") is not False
        or release.get("prerelease") is not False
        or release.get("immutable") is not True
    ):
        raise ValueError("Central release must be published, stable and immutable")
    lines = runner(
        ["git", "ls-remote", "--tags", f"https://github.com/{CENTRAL}.git", f"refs/tags/{tag}*"],
        text=True,
    ).splitlines()
    found = {}
    for line in lines:
        sha, name = line.split("\t")
        if not reference.SHA.fullmatch(sha) or name not in {
            f"refs/tags/{tag}",
            f"refs/tags/{tag}^{{}}",
        }:
            raise ValueError("Unexpected release ref response")
        found[name] = sha
    sha = found.get(f"refs/tags/{tag}^{{}}", found.get(f"refs/tags/{tag}"))
    return reference.descriptor(tag, sha)


def metadata_changes(config_text, document, new):
    config = json.loads(config_text)
    reference.validate(config["standards"])
    if config.get("standards_update") != PROVIDER:
        raise ValueError("Consumer has not adopted the metadata-backed updater")
    config["standards"] = reference.validate(new)
    return {
        ".hass-standards.json": json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        "STANDARDS.md": recorded_standards_update(document, new),
    }


def dispatchable_workflows(workflows):
    result = []
    for path, text in workflows.items():
        events = yaml_document(text).get("on", {})
        if isinstance(events, str):
            events = {events: None}
        elif isinstance(events, list):
            events = dict.fromkeys(events)
        if "pull_request" not in events:
            continue
        if "workflow_dispatch" not in events:
            raise ValueError(f"Validator does not support explicit dispatch: {path}")
        result.append(Path(path).name)
    if not result:
        raise ValueError("No dispatchable PR validation workflows")
    return sorted(result)


def sync_pr(repository, number, *, manual=False, api=gh, listing=pages, attest=attest_release):
    """Read PR files as data; write only metadata blobs on an existing PR branch."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid repository")
    meta = api(f"repos/{repository}")
    pr = api(f"repos/{repository}/pulls/{number}")
    if pr["state"] != "open":
        return None
    if (
        pr["base"]["ref"] != meta["default_branch"]
        or pr["head"]["repo"]["full_name"] != repository
        or pr["base"]["repo"]["full_name"] != repository
        or (not manual and pr["user"]["login"] != "dependabot[bot]")
    ):
        raise ValueError("PR is not an eligible same-repository default-branch update")
    base_sha = api(f"repos/{repository}/commits/{quote(meta['default_branch'], safe='')}")["sha"]
    head_sha = pr["head"]["sha"]
    base_tree = tree_files(repository, base_sha, api)
    head_tree = tree_files(repository, head_sha, api)
    changed = [p for p in set(base_tree) | set(head_tree) if base_tree.get(p) != head_tree.get(p)]
    for path in changed:
        workflow = path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
        if path not in MANAGED and not workflow:
            raise ValueError(f"PR changes unrelated content: {path}")
        if path not in base_tree or path not in head_tree:
            raise ValueError(f"PR adds/deletes/renames managed files: {path}")
        if base_tree[path][1:] != ("100644", "blob") or head_tree[path][1:] != ("100644", "blob"):
            raise ValueError(f"PR changes managed file modes: {path}")

    def read(tree, path):
        if tree[path][1:] != ("100644", "blob"):
            raise ValueError(f"Expected a regular managed file: {path}")
        return blob(repository, tree[path][0], api)

    base_config_text = read(base_tree, ".hass-standards.json")
    config = json.loads(base_config_text)
    if config.get("repository") != repository:
        raise ValueError("Consumer descriptor belongs to another repository")
    old = reference.validate(config["standards"])
    if old["kind"] != "release":
        raise ValueError("Legacy SHA consumer needs an explicit release adoption")
    document = read(base_tree, "STANDARDS.md")
    workflow_paths = {
        path
        for path in base_tree
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
    }
    head_paths = {
        path
        for path in head_tree
        if path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml"))
    }
    if workflow_paths != head_paths:
        raise ValueError("PR changes the workflow file set")
    before = {path: read(base_tree, path) for path in workflow_paths}
    after = {path: read(head_tree, path) for path in workflow_paths}
    if all(central_uses(before[p]) == central_uses(after[p]) for p in workflow_paths):
        return None
    tag = candidate_release(before, after, old, recorded_release_override(document))
    new = attest(tag)
    proposed = metadata_changes(base_config_text, document, new)
    updates = []
    for path, content in proposed.items():
        if read(head_tree, path) != content:
            updates.append({"path": path, "mode": "100644", "type": "blob", "content": content})
    # Only these two non-workflow paths are allowed through the runtime Git writer.
    if any(entry["path"] not in MANAGED for entry in updates):
        raise ValueError("Runtime writer must never modify workflow files")
    validators = dispatchable_workflows(after)
    if updates:
        parent = api(f"repos/{repository}/git/commits/{head_sha}")
        tree = api(
            f"repos/{repository}/git/trees",
            method="POST",
            payload={"base_tree": parent["tree"]["sha"], "tree": updates},
        )
        commit = api(
            f"repos/{repository}/git/commits",
            method="POST",
            payload={
                "message": f"ci: reconcile standards {tag} metadata [dependabot skip]",
                "tree": tree["sha"],
                "parents": [head_sha],
            },
        )
        latest = api(f"repos/{repository}/pulls/{number}")
        if latest["head"]["sha"] != head_sha or latest["state"] != "open":
            raise ValueError("PR changed during preparation; retry without overwriting it")
        api(
            f"repos/{repository}/git/refs/heads/{quote(pr['head']['ref'], safe='')}",
            method="PATCH",
            payload={"sha": commit["sha"], "force": False},
        )
        head_sha = commit["sha"]
    for workflow in validators:
        api(
            f"repos/{repository}/actions/workflows/{quote(workflow, safe='')}/dispatches",
            method="POST",
            payload={"ref": pr["head"]["ref"]},
        )
    same_major = Version(old["tag"][1:]).major == Version(tag[1:]).major
    return {
        "pr": number,
        "tag": tag,
        "sha": new["resolved_sha"],
        "head": head_sha,
        "validators": validators,
        "updated": bool(updates),
        "auto_eligible": same_major and pr["user"]["login"] == "dependabot[bot]",
    }


def validate_dependabot(data):
    actions = [u for u in data.get("updates", []) if u.get("package-ecosystem") == "github-actions"]
    if len(actions) != 1:
        raise ValueError("Exactly one github-actions updater is required")
    item = actions[0]
    if (
        item.get("directory") != "/"
        or item.get("target-branch")
        or item.get("open-pull-requests-limit", 5) < 1
        or item.get("rebase-strategy", "auto") != "auto"
    ):
        raise ValueError(
            "GitHub Actions updater must target the default branch at / with PRs enabled"
        )
    groups = item.get("groups", {})
    if "cooldown" in item and not all(
        name in item["cooldown"].get("exclude", []) for name in DEPENDENCIES
    ):
        raise ValueError("Central dependencies must be excluded from native release cooldown")
    if (
        item.get("schedule", {}).get("interval") != "daily"
        or next(iter(groups), None) != "central-standards"
        or groups["central-standards"] != {"patterns": DEPENDENCIES}
    ):
        raise ValueError(
            "Central group must be first, daily and include action and workflow dependency names"
        )
    names = [CENTRAL] + [
        PREFIX + ".github/workflows/" + name
        for name in (
            "python-tests.yml",
            "standards-update.yml",
            "dependency-update.yml",
            "validate-integration.yml",
        )
    ]
    for name in names:
        if "allow" in item and not any(
            fnmatch.fnmatchcase(name, x.get("dependency-name", "*")) for x in item["allow"]
        ):
            raise ValueError("Dependabot allow policy excludes a central dependency")
        if any(
            fnmatch.fnmatchcase(name, x.get("dependency-name", "")) for x in item.get("ignore", [])
        ):
            raise ValueError(
                "Dependabot ignore policy overlaps central dependencies; review explicitly"
            )


def configure_dependabot(text=None, *, override=None):
    data = yaml_document(text) if text else {"version": 2, "updates": []}
    if data.get("version") != 2 or not isinstance(data.get("updates"), list):
        raise ValueError("Unsupported Dependabot config")
    actions = [u for u in data["updates"] if u.get("package-ecosystem") == "github-actions"]
    if not actions:
        actions = [
            {
                "package-ecosystem": "github-actions",
                "directory": "/",
                "schedule": {"interval": "daily"},
                "allow": [{"dependency-name": name} for name in DEPENDENCIES],
            }
        ]
        data["updates"].extend(actions)
    for item in actions:
        cooldown = item.setdefault("cooldown", {})
        excluded = cooldown.setdefault("exclude", [])
        for name in DEPENDENCIES:
            if name not in excluded:
                excluded.append(name)
        item["schedule"] = {**item.get("schedule", {}), "interval": "daily"}
        item["schedule"].pop("day", None)
        if "allow" in item:
            for name in DEPENDENCIES:
                if not any(x.get("dependency-name") == name for x in item["allow"]):
                    item["allow"].append({"dependency-name": name})
        ignore = [x for x in item.get("ignore", []) if x.get("dependency-name") not in DEPENDENCIES]
        if override and not any(
            x.get("dependency-name") == PREFIX + "actions/release-zip" for x in ignore
        ):
            ignore.append({"dependency-name": PREFIX + "actions/release-zip"})
        if ignore:
            item["ignore"] = ignore
        else:
            item.pop("ignore", None)
        groups = item.get("groups", {})
        item["groups"] = {
            "central-standards": {"patterns": DEPENDENCIES},
            **{k: v for k, v in groups.items() if k != "central-standards"},
        }
    validate_dependabot(data)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def bootstrap_changes(root, new, template):
    """Explicit installer run by an operator with workflow write authority, not in CI."""
    root = Path(root).resolve()
    for relative in (*MANAGED, ".github", ".github/workflows", ".github/dependabot.yml", CALLER):
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Managed path escapes checkout: {relative}")
    config = json.loads((root / ".hass-standards.json").read_text())
    reference.validate(config["standards"])
    document = (root / "STANDARDS.md").read_text()
    override = recorded_release_override(document)
    config["standards"] = reference.validate(new)
    config["standards_update"] = PROVIDER
    result = {
        ".hass-standards.json": json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        "STANDARDS.md": recorded_standards_update(document, new),
    }
    pattern = re.compile(
        r"(?m)^(\s*(?:-\s*)?uses:\s*)(['\"]?)(eigger/hass-repo-standards/[^@\s'\"]+)@([^\s#'\"]+)\2"
    )
    for path in sorted((root / ".github/workflows").iterdir()):
        if path.suffix not in {".yml", ".yaml"}:
            continue
        if path.is_symlink():
            raise ValueError("Workflow symlinks are not supported")
        before = path.read_text()
        desired = copy.deepcopy(yaml_document(before))

        def walk(value):
            if isinstance(value, list):
                for v in value:
                    walk(v)
            elif isinstance(value, dict):
                use = value.get("uses", "")
                if isinstance(use, str) and use.startswith(PREFIX):
                    name, old_ref = use.rsplit("@", 1)
                    if not (name.endswith("actions/release-zip") and old_ref == override):
                        value["uses"] = name + "@" + new["tag"]
                    if isinstance(value.get("with"), dict):
                        value["with"].pop("standards-ref", None)
                for v in value.values():
                    walk(v)

        walk(desired)

        def replace(match):
            prefix, quoting, name, old_ref = match.groups()
            version = (
                old_ref
                if name.endswith("actions/release-zip") and old_ref == override
                else new["tag"]
            )
            return prefix + quoting + name + "@" + version + quoting

        after = pattern.sub(replace, before)
        after = re.sub(r"(?m)^\s+standards-ref:\s*[^\n]+\n", "", after)
        if yaml_document(after) != desired:
            raise ValueError(f"Unsupported caller formatting: {path}")
        result[path.relative_to(root).as_posix()] = after
    result[CALLER] = template.replace("@main", "@" + new["tag"])
    dep = root / ".github/dependabot.yml"
    result[".github/dependabot.yml"] = configure_dependabot(
        dep.read_text() if dep.exists() else None,
        override=override,
    )
    return {
        p: text
        for p, text in result.items()
        if not (root / p).exists() or (root / p).read_text() != text
    }

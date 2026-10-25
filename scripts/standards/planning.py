"""Produce deterministic, guarded integration changes; never apply target writes."""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
import re
import tempfile
from pathlib import Path

import yaml

from . import conditions, contract, inventory, readme, reference, scaffold

CENTRAL = contract.CENTRAL
ASSET_PATHS = (
    ".github",
    "actions",
    "scripts",
    "schemas",
    "templates",
    "skills",
    "docs",
    "AGENTS.md",
    "README.md",
    "README.ko.md",
)
SHA_RE = re.compile(r"[0-9a-f]{40}")


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def verify_standards(ref, central=None):
    central = Path(central or CENTRAL).resolve()
    # `str` is the deliberately retained pre-release compatibility API.
    item = reference.descriptor(ref) if isinstance(ref, str) else reference.validate(ref)
    sha = item["resolved_sha"]
    head = inventory.git(central, "rev-parse", "HEAD")
    if head is None or head.decode("utf-8").strip() != sha:
        raise ValueError("Executing standards checkout HEAD must equal resolved standards SHA")
    raw = inventory.git(
        central, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", *ASSET_PATHS
    )
    if raw is None or raw:
        raise ValueError(
            "Standards rules, scripts, schemas, templates and skills must be clean at standards-ref"
        )
    return central


def plan_reference(document):
    """Read either the retained full-SHA plan field or the release descriptor."""
    if "standards_reference" in document:
        return reference.validate(document["standards_reference"])
    return reference.descriptor(document["standards_ref"])


def observed(data, field):
    return [item for item in data["observations"] if item["field"] == field]


def requirement_lines(text):
    """Preserve every effective requirement verbatim except surrounding whitespace."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def environment_paths(data):
    environments = data["environments"]["value"]
    return {
        axis: {
            contract.validate_path(path)
            for field in ("requirements", "constraints")
            for path in environments[axis][field]
        }
        for axis in ("minimum", "current")
    }


def render_dependabot(source, data):
    """Retain central updates while protecting the actual minimum-only environment files."""
    paths = environment_paths(data)
    document = yaml.safe_load(source)
    for update in document["updates"]:
        if update.get("package-ecosystem") != "pip":
            continue
        exclusions = [
            path for path in update.get("exclude-paths", []) if path not in paths["current"]
        ]
        exclusions.extend(sorted(paths["minimum"] - paths["current"] - set(exclusions)))
        if exclusions:
            update["exclude-paths"] = exclusions
        else:
            update.pop("exclude-paths", None)
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def workflow_events(template, default_branch):
    """Render central trigger boundaries for both generation and read-only checks."""
    events = copy.deepcopy(template["on"])
    if isinstance(events, dict) and isinstance(events.get("push"), dict):
        events["push"]["branches"] = [default_branch]
    return events


def render_workflow(source, destination, data, ref):
    ref = reference.descriptor(ref) if isinstance(ref, str) else reference.validate(ref)
    parsed = yaml.safe_load(source)
    # PyYAML's YAML 1.1 resolver calls the unquoted 'on' key True; templates quote it.
    if not isinstance(parsed, dict) or "on" not in parsed:
        raise ValueError("Workflow template must have explicit on events")
    parsed["on"] = workflow_events(parsed, data["default_branch"]["value"])
    domain = data["domain"]["value"]
    environments = data["environments"]["value"]
    for job in parsed.get("jobs", {}).values():
        if not isinstance(job, dict):
            continue
        if isinstance(job.get("uses"), str):
            job["uses"] = job["uses"].removesuffix("@main") + "@" + reference.caller_ref(ref)
        for step in job.get("steps", []):
            if isinstance(step, dict) and str(step.get("uses", "")).startswith(
                "eigger/hass-repo-standards/"
            ):
                step["uses"] = step["uses"].removesuffix("@main") + "@" + reference.caller_ref(ref)
        params = job.get("with")
        if params is None:
            continue
        params["standards-ref"] = reference.resolved_sha(ref)
        if "domain" in params:
            params["domain"] = domain
        if "pytest-args" in params:
            params["pytest-args"] = f"tests/components/{domain}/ -v"
        if "validation-command" in params:
            params["validation-command"] = params["validation-command"].replace(
                "tests/components/example/", f"tests/components/{domain}/"
            )
        env = environments["current"]
        if "python-versions" in params:
            params["python-versions"] = json.dumps([env["python"]])
            params["expected-ha-version"] = env["ha"]
            params["requirements"] = " ".join(env["requirements"])
            if env["constraints"]:
                params["constraints"] = " ".join(env["constraints"])
        if "python-version" in params:
            params["python-version"] = env["python"]
        if "packages" in params:
            packages = sorted(
                {
                    requirement.name
                    for requirement in (
                        conditions.Requirement(text)
                        for text in data["manifest"]["value"].get("requirements", [])
                    )
                }
            )
            if not packages:
                raise ValueError("Dependency update workflow requires actual runtime packages")
            params["packages"] = json.dumps(packages)
    if (
        destination == ".github/workflows/tests.yml"
        and environments["minimum"] != environments["current"]
    ):
        current = parsed["jobs"]["current"]
        minimum = copy.deepcopy(current)
        env = environments["minimum"]
        minimum["with"].update(
            {
                "python-versions": json.dumps([env["python"]]),
                "expected-ha-version": env["ha"],
                "requirements": " ".join(env["requirements"]),
            }
        )
        minimum["with"].pop("constraints", None)
        if env["constraints"]:
            minimum["with"]["constraints"] = " ".join(env["constraints"])
        parsed["jobs"]["minimum"] = minimum
    return yaml.safe_dump(parsed, sort_keys=False, allow_unicode=True)


def reference_only_workflow_update(before, after):
    """Allow an adoption ref migration without touching caller-owned workflow data."""
    old, new = yaml.safe_load(before), yaml.safe_load(after)

    def normalize(value):
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {key: normalize(item) for key, item in value.items()}
        uses = result.get("uses")
        if isinstance(uses, str) and uses.startswith("eigger/hass-repo-standards/"):
            result["uses"] = uses.rsplit("@", 1)[0] + "@<central-reference>"
        if isinstance(result.get("with"), dict) and "standards-ref" in result["with"]:
            result["with"] = dict(result["with"], **{"standards-ref": "<resolved-sha>"})
        return result

    return normalize(old) == normalize(new)


def reference_only_workflow_content(before, after):
    """Keep caller formatting/comments while replacing only approved reference literals."""
    desired = yaml.safe_load(after)
    references = {}

    def collect(value):
        if isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, dict):
            uses = value.get("uses")
            if isinstance(uses, str) and uses.startswith("eigger/hass-repo-standards/"):
                references[uses.rsplit("@", 1)[0]] = uses.rsplit("@", 1)[1]
            for item in value.values():
                collect(item)

    collect(desired)

    def replace_use(match):
        prefix, quote, path, current = match.groups()
        return prefix + quote + path + "@" + references.get(path, current) + quote

    value = re.sub(
        r"(?m)^(\s*(?:-\s*)?uses:\s*)(['\"]?)(eigger/hass-repo-standards/[^@\s'\"]+)@([^\s#'\"]+)\2",
        replace_use,
        before,
    )
    sha = next(
        (
            item
            for item in re.findall(r"(?m)^\s*standards-ref:\s*['\"]?([^\s'\"]+)", after)
            if SHA_RE.fullmatch(item)
        ),
        None,
    )
    if sha:
        value = re.sub(
            r"(?m)^(\s*standards-ref:\s*)['\"]?[^\s#'\"]+['\"]?",
            r"\g<1>" + sha,
            value,
        )
    return value


def recorded_standards_update(text, standards_reference):
    """Change only central reference records; retain history, exceptions and prose."""
    item = reference.validate(standards_reference)
    head, separator, tail = text.partition("\n## ")

    def replace_one(value, pattern, replacement, *, required=False):
        matches = list(re.finditer(pattern, value, re.M))
        if not matches:
            if required:
                raise ValueError("STANDARDS.md has no single reviewed standards SHA record")
            return value
        if len(matches) != 1:
            raise ValueError("STANDARDS.md has ambiguous reviewed standards reference records")
        match = matches[0]
        start, end = match.span()
        replacement = replacement(match) if callable(replacement) else replacement
        return value[:start] + replacement + value[end:]

    value = replace_one(
        head,
        r"^\s*-\s*(?:참조 커밋 SHA|Reviewed standards SHA|Standards ref)\s*:.*$",
        f"- 참조 커밋 SHA: {item['resolved_sha']}",
        required=True,
    )
    if item["kind"] == "release":
        value = replace_one(
            value,
            r"^(\s*-\s*표준:\s*https://github\.com/eigger/hass-repo-standards/tree/)[^/\s]+(\s*)$",
            lambda match: match.group(1) + item["tag"] + match.group(2),
            required=True,
        )
    value = re.sub(r"^\s*-\s*Standards release\s*:.*\n?", "", value, flags=re.M)
    value = re.sub(r"^\s*-\s*Resolved standards SHA\s*:.*\n?", "", value, flags=re.M)
    if item["kind"] == "release":
        line = f"- 참조 커밋 SHA: {item['resolved_sha']}"
        addition = (
            line
            + f"\n- Standards release: {item['tag']}\n- Resolved standards SHA: {item['resolved_sha']}"
        )
        if value.count(line) != 1:
            raise ValueError("STANDARDS.md reference update became ambiguous")
        value = value.replace(line, addition, 1)
    return value + ("\n## " + tail if separator else "")


def recorded_release_override(text):
    """Return the one explicit ZIP-action SHA override, if the caller recorded one."""
    matches = re.findall(
        r"^\s*-\s*Reviewed release standards SHA\s*:\s*`?([0-9a-f]{40})`?\s*$",
        text,
        re.M,
    )
    if len(matches) > 1:
        raise ValueError("STANDARDS.md has ambiguous reviewed release SHA overrides")
    return matches[0] if matches else None


def metadata_conflicts(data, scanned):
    errors = list(scanned["conflicts"])
    repository = data["repository"]["value"]
    if "remote" not in data:
        errors.append("A sourced remote URL is required for planning")
    else:
        try:
            if (
                inventory.github_repository(data["remote"]["value"]).casefold()
                != repository.casefold()
            ):
                errors.append("Input remote and repository identity disagree")
        except ValueError as error:
            errors.append(str(error))
    if scanned["repository"] and scanned["repository"].casefold() != repository.casefold():
        errors.append("Input repository and observed origin disagree")
    if scanned["default_branch"] and scanned["default_branch"] != data["default_branch"]["value"]:
        errors.append("Input default branch and observed remote HEAD disagree")
    if any(
        inventory.normalized_ha(value["value"])
        != inventory.normalized_ha(data["environments"]["value"]["minimum"]["ha"])
        for value in observed(scanned, "minimum_ha")
    ):
        errors.append(
            "Input minimum HA differs from existing support declarations; preserve existing support"
        )
    manifests = observed(scanned, "manifest")
    if manifests:
        existing = manifests[0]["value"]
        requested = data["manifest"]["value"]
        for key in (
            "domain",
            "version",
            "requirements",
            "dependencies",
            "after_dependencies",
            "config_flow",
            "categories",
            "integration_type",
        ):
            if existing.get(
                key, [] if key in {"requirements", "dependencies", "after_dependencies"} else None
            ) != requested.get(
                key, [] if key in {"requirements", "dependencies", "after_dependencies"} else None
            ):
                errors.append(
                    f"Input manifest {key} differs from existing metadata; automatic changes are not permitted"
                )
    if data["domain"]["value"] != data["manifest"]["value"]["domain"]:
        errors.append("Input domain and manifest domain disagree")
    if data["manifest"]["value"].get("config_flow", False) != (
        data["configuration"]["value"] == "ui"
    ):
        errors.append("Configuration mode and manifest config_flow disagree")
    return errors


def fixture_block_update(original, template):
    """Replace complete Python comment-marker lines, preserving all fixture bytes outside."""

    def span(text):
        readme.block(text, "domain-fixtures")
        starts = list(
            re.finditer(r"^# <!-- hass-standards:domain-fixtures:start -->\r?$", text, re.M)
        )
        ends = list(re.finditer(r"^# <!-- hass-standards:domain-fixtures:end -->\r?$", text, re.M))
        if len(starts) != 1 or len(ends) != 1 or starts[0].start() >= ends[0].start():
            raise ValueError(
                "Domain fixtures require one ordered pair of complete Python comment markers"
            )
        return starts[0].start(), ends[0].end()

    start, end = span(original)
    first, last = span(template)
    return original[:start] + template[first:last] + original[end:]


def plan(
    target,
    mode,
    data,
    standards_ref,
    *,
    central=None,
    release_tag=None,
    release_verification=None,
    release_attestation=None,
    internal_replan=False,
    remote_runner=None,
):
    legacy_reference = release_tag is None and (
        isinstance(standards_ref, str)
        or (isinstance(standards_ref, dict) and standards_ref.get("kind") == "sha")
    )
    standards_reference = (
        reference.descriptor(release_tag, standards_ref)
        if release_tag
        else (
            reference.descriptor(standards_ref)
            if isinstance(standards_ref, str)
            else reference.validate(standards_ref)
        )
    )
    if standards_reference["kind"] == "release":
        if release_attestation is not None:
            if not internal_replan:
                raise ValueError("release attestation is reserved for apply/recover replan")
            if (
                not isinstance(release_attestation, str)
                or re.fullmatch(r"[0-9a-f]{64}", release_attestation) is None
            ):
                raise ValueError("release attestation digest is invalid")
        else:
            if release_verification is None:
                raise ValueError(
                    "exact release planning requires successful remote release verification evidence"
                )
            recorded = reference.read_verification(
                release_verification,
                "eigger/hass-repo-standards",
                standards_reference,
            )
            kwargs = {"runner": remote_runner} if remote_runner is not None else {}
            evidence = reference.verify_remote(
                "eigger/hass-repo-standards", standards_reference, **kwargs
            )
            if evidence != recorded:
                raise ValueError(
                    "release verification evidence differs from current remote attestation"
                )
            release_attestation = digest(canonical_json(evidence).encode("utf-8"))
    central = verify_standards(standards_reference, central)
    contract.validate_input(data)
    if "remote" in data:
        # Reject credentials/unsupported remotes before persisting an input snapshot.
        inventory.github_repository(data["remote"]["value"])
    validated_input = copy.deepcopy(data)
    # Serialize before doing any work so NaN/Infinity cannot leak through an open metadata object.
    input_digest = digest(canonical_json(validated_input).encode("utf-8"))
    target = Path(target).resolve()
    if mode not in {"create", "adopt"}:
        raise ValueError("Mode must be create or adopt")
    files = inventory.file_paths(target)
    initial_hashes = {name: digest((target / name).read_bytes()) for name in files}
    scanned = inventory.inspect(target)
    result = {
        "schema_version": 1,
        "target_identity": {
            "path": str(target),
            "root_exists": target.exists(),
            "repository": data["repository"]["value"],
            "domain": data["domain"]["value"],
        },
        "input_digest": input_digest,
        "validated_input": validated_input,
        "mode": mode,
        "guards": [],
        "operations": [],
        "unchanged": [],
        "pending": [
            message for message in scanned["pending"] if message.startswith("Ambiguous support")
        ],
        "conflicts": metadata_conflicts(data, scanned),
    }
    # Existing reviewed SHA plans remain byte-for-byte shaped as before. Exact
    # releases use the descriptor instead, so tag and resolved SHA have one
    # machine-readable source rather than parallel fields.
    if legacy_reference:
        result["standards_ref"] = standards_reference["resolved_sha"]
    else:
        result["standards_reference"] = standards_reference
        result["release_attestation"] = release_attestation
    if mode == "create" and target.exists() and any(target.iterdir()):
        result["conflicts"].append("Create requires an explicitly empty target directory")
    if mode == "adopt":
        if len(observed(scanned, "manifest")) != 1:
            result["conflicts"].append("Adopt requires exactly one actual integration manifest")
        if scanned["domains"] != [data["domain"]["value"]]:
            result["conflicts"].append("Actual manifest domain differs from input")
    if (
        data["default_branch"]["value"].strip() != data["default_branch"]["value"]
        or not data["default_branch"]["value"].strip()
    ):
        result["conflicts"].append("Default branch must be explicitly confirmed")
    if (
        inventory.git(central, "check-ref-format", "--branch", data["default_branch"]["value"])
        is None
    ):
        result["conflicts"].append("Default branch is not a valid Git branch name")
    guards = dict(initial_hashes)
    dirty = set(scanned["dirty_paths"])
    records = contract.load_contract(central / "templates/integration/contract.json")["records"]
    settings = contract.render_settings(data)
    settings["standards"] = standards_reference
    known_settings = observed(scanned, "standards_settings")
    if known_settings:
        old = known_settings[0]["value"]
        if not isinstance(old, dict):
            raise ValueError("Existing .hass-standards.json must be an object")
        merged = copy.deepcopy(old)
        merged.update({key: value for key, value in settings.items() if key != "readme"})
        if not isinstance(merged.get("readme", {}), dict):
            raise ValueError("Existing readme settings must be an object")
        merged.setdefault("readme", {}).update(settings["readme"])
        settings = merged
    destinations = set()
    existing_aliases = {}
    for path in files:
        alias = path.casefold()
        if alias in existing_aliases:
            result["conflicts"].append(f"Existing Windows path aliases collide: {path}")
        existing_aliases[alias] = path
    active = []
    for record in records:
        applies = conditions.matches(
            record["condition"],
            data,
            target if mode == "adopt" else None,
            target / f"custom_components/{data['domain']['value']}/manifest.json",
            readme.safe_path,
        )
        if not applies:
            # Losing a library never schedules deletion of its old documents.
            continue
        contract.validate_input(data, record["required_inputs"])
        platforms = data["platforms"]["value"] if record["condition"] == "platforms" else [None]
        for platform in platforms:
            destination = contract.destination_path(record, data["domain"]["value"], platform)
            inventory.safe_target_path(target, destination.rstrip("/"))
            alias = destination.rstrip("/").casefold()
            if alias in destinations:
                result["conflicts"].append(
                    f"Expanded contract destination collision: {destination}"
                )
                continue
            if alias in existing_aliases and existing_aliases[alias] != destination.rstrip("/"):
                result["conflicts"].append(
                    f"Destination aliases existing differently cased path: {destination}"
                )
                continue
            destinations.add(alias)
            guards.setdefault(destination.rstrip("/"), None)
            for parent in Path(destination.rstrip("/")).parents:
                if parent == Path("."):
                    continue
                name = parent.as_posix()
                path = inventory.safe_target_path(target, name)
                guards.setdefault(name, None)
                if path.exists() and not path.is_dir():
                    result["conflicts"].append(f"Destination parent is not a directory: {name}")
            active.append((record, destination))
    # Ancestor/descendant operations are also ambiguous, except directory-only pending records.
    concrete = [name for record, name in active if not name.endswith("/")]
    for name in concrete:
        if any(other != name and other.startswith(name + "/") for other in concrete):
            result["conflicts"].append(f"Contract file/directory collision: {name}")

    def propose(record, name, content):
        path = inventory.safe_target_path(target, name)
        if path.exists() and not path.is_file():
            result["conflicts"].append(f"Expected file, found directory: {name}")
            return
        before = path.read_bytes() if path.exists() else None
        after = content.encode("utf-8")
        if before == after:
            result["unchanged"].append(name)
            return
        if (
            name == "requirements_test.txt"
            and record["ownership"] == "merge"
            and before is not None
            and requirement_lines(before.decode("utf-8")) == requirement_lines(content)
        ):
            result["unchanged"].append(name)
            return
        if name in dirty:
            result["conflicts"].append(f"Preserve modified user file: {name}")
            return
        if before is not None and record["ownership"] == "create_only":
            result["pending"].append(
                f"Preserve integration-owned file and verify actual behavior: {name}"
            )
            return
        if before is not None and record["ownership"] == "exact_file":
            result["conflicts"].append(
                f"Exact central file differs; migrate custom content before replacement: {name}"
            )
            return
        if before is not None and record["ownership"] == "merge" and name != ".hass-standards.json":
            if name == "STANDARDS.md":
                pass
            elif name.startswith(".github/workflows/") or name == ".github/dependabot.yml":
                if yaml.safe_load(before.decode("utf-8")) == yaml.safe_load(content):
                    result["unchanged"].append(name)
                    return
                if name.startswith(".github/workflows/") and reference_only_workflow_update(
                    before.decode("utf-8"), content
                ):
                    desired_content = content
                    content = reference_only_workflow_content(
                        before.decode("utf-8"), desired_content
                    )
                    if yaml.safe_load(content) != yaml.safe_load(desired_content):
                        result["conflicts"].append(
                            f"Preserve existing extension; reviewed merge required: {name}"
                        )
                        return
                    after = content.encode("utf-8")
                else:
                    result["conflicts"].append(
                        f"Preserve existing extension; reviewed merge required: {name}"
                    )
                    return
            else:
                result["conflicts"].append(
                    f"Preserve existing extension; reviewed merge required: {name}"
                )
                return
        previous = before.decode("utf-8") if before is not None else ""
        diff = "".join(
            difflib.unified_diff(
                previous.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile="a/" + name if before is not None else "/dev/null",
                tofile="b/" + name,
            )
        )
        result["operations"].append(
            {
                "path": name,
                "action": "create" if before is None else "update",
                "ownership": record["ownership"],
                "source": record["source"],
                "rules": record["rules"],
                "before_sha256": digest(before) if before is not None else None,
                "after_sha256": digest(after),
                "content": content,
                "diff": diff,
            }
        )

    delayed = []
    for record, destination in active:
        if destination in {"README.md", "README.ko.md"}:
            delayed.append((record, destination))
            continue
        if (
            destination
            in {"hacs.json", f"custom_components/{data['domain']['value']}/manifest.json"}
            and (target / destination).is_file()
        ):
            result["unchanged"].append(destination)
            continue
        if scaffold.handles(record):
            content, incomplete = scaffold.render(
                record, destination, validated_input, central=central
            )
            existing = target / destination
            if (
                record["ownership"] == "create_only"
                and existing.is_file()
                and content is not None
                and existing.read_bytes() != content.encode("utf-8")
            ):
                result["pending"].append(
                    f"Preserve existing integration-owned implementation; verify with actual HA tests: {destination}"
                )
                result["unchanged"].append(destination)
            else:
                result["pending"].extend(incomplete)
                if content is not None:
                    propose(record, destination, content)
            continue
        if record["status"] == "pending" or destination.endswith("/"):
            result["pending"].append(
                f"Scaffold/manual implementation not available; preserve and complete: {destination}"
            )
            continue
        source = central / record["source"]
        content = (
            source.read_bytes().decode("utf-8")
            if record["ownership"] == "exact_file"
            else source.read_text(encoding="utf-8")
        )
        if destination == ".hass-standards.json":
            content = canonical_json(settings)
        elif destination.startswith(".github/workflows/"):
            try:
                content = render_workflow(content, destination, data, standards_reference)
                if destination == ".github/workflows/release.yml":
                    standards_path = target / "STANDARDS.md"
                    if standards_path.is_file() and (
                        override := recorded_release_override(
                            standards_path.read_text(encoding="utf-8")
                        )
                    ):
                        content = re.sub(
                            r"(eigger/hass-repo-standards/actions/release-zip@)(?:[0-9a-f]{40}|v[0-9]+\.[0-9]+\.[0-9]+)",
                            r"\g<1>" + override,
                            content,
                        )
            except ValueError as error:
                result["pending"].append(f"{destination}: {error}")
                continue
        elif destination == ".github/dependabot.yml":
            content = render_dependabot(content, validated_input)
            environments = validated_input["environments"]["value"]
            paths = environment_paths(validated_input)
            if any(
                environments["minimum"][key] != environments["current"][key]
                for key in ("ha", "python", "pytest_homeassistant_custom_component")
            ):
                for shared in sorted(paths["minimum"] & paths["current"]):
                    result["pending"].append(
                        f"Automatic minimum protection is unverified for shared environment path {shared}; review separate exact minimum constraints and update impact"
                    )
        elif destination == "requirements_test.txt":
            env = data["environments"]["value"]["current"]
            minimum = data["environments"]["value"]["minimum"]
            if destination not in env["requirements"]:
                result["pending"].append(
                    f"Environment-specific requirements require a separate registered asset: {destination}"
                )
                continue
            if destination in minimum["requirements"] and (
                minimum["ha"],
                minimum["python"],
                minimum["pytest_homeassistant_custom_component"],
            ) != (env["ha"], env["python"], env["pytest_homeassistant_custom_component"]):
                result["conflicts"].append(
                    "Minimum/current environments cannot share incompatible pinned requirements_test.txt"
                )
                continue
            content = (
                "# Confirmed current HA test environment; execution remains pending.\n"
                + f"homeassistant=={env['ha']}\npytest-homeassistant-custom-component=={env['pytest_homeassistant_custom_component']}\n"
            )
        elif destination == "tests/components/" + data["domain"]["value"] + "/conftest.py":
            existing = target / destination
            if existing.is_file():
                original = existing.read_bytes().decode("utf-8")
                try:
                    content = fixture_block_update(original, content)
                except ValueError as error:
                    result["conflicts"].append(f"{destination}: {error}")
                    continue
        elif destination.startswith("docs/") and (target / destination).exists():
            result["pending"].append(
                f"Preserve device documentation; review fixed structure and actual content: {destination}"
            )
            continue
        elif destination in {"STANDARDS.md", "ADOPTION_CHECKLIST.md"}:
            if (target / destination).exists():
                if destination == "STANDARDS.md":
                    try:
                        content = recorded_standards_update(
                            (target / destination).read_text(encoding="utf-8"), standards_reference
                        )
                    except ValueError as error:
                        result["conflicts"].append(f"{destination}: {error}")
                        continue
                else:
                    result["pending"].append(
                        f"Append new review and evidence without reusing past PASS: {destination}"
                    )
                    continue
            content = content.replace(
                "https://github.com/eigger/hass-repo-standards/tree/main",
                "https://github.com/eigger/hass-repo-standards/tree/"
                + reference.caller_ref(standards_reference),
            )
            content = content.replace(
                "채택 시 검토한 main의 전체 SHA 입력", standards_reference["resolved_sha"]
            )
            content = content.replace(
                "채택 시 검토한 exact release 입력", reference.caller_ref(standards_reference)
            )
            if destination == "STANDARDS.md" and legacy_reference:
                content = re.sub(r"^- Standards release:.*\n", "", content, flags=re.M)
                content = re.sub(r"^- Resolved standards SHA:.*\n", "", content, flags=re.M)
            result["pending"].append(
                f"Complete actual adoption evidence; template remains TODO: {destination}"
            )
        if record["condition"] in {"imagespec", "blesession"}:
            result["pending"].append(
                f"Replace placeholders with actual device/action details and verify: {destination}"
            )
        propose(record, destination, content)

    # Stage only metadata and planned workflow presence. Never invent a LICENSE to satisfy rendering.
    with tempfile.TemporaryDirectory(prefix="hass-standards-plan-") as staging:
        stage = Path(staging)
        for name in files:
            if (
                name in {"LICENSE", "hacs.json", "README.md", "README.ko.md"}
                or re.fullmatch(r"custom_components/[^/]+/manifest\.json", name)
                or name.startswith(".github/workflows/")
            ):
                output = stage / name
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes((target / name).read_bytes())
        for operation in result["operations"]:
            if (
                operation["path"].startswith(".github/workflows/")
                or operation["path"] == "hacs.json"
                or re.fullmatch(r"custom_components/[^/]+/manifest\.json", operation["path"])
            ):
                path = stage / operation["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(operation["content"].encode("utf-8"))
        for record, name in delayed:
            if not (stage / "LICENSE").is_file():
                result["pending"].append(
                    f"{name}: actual LICENSE required; no license file is invented"
                )
                continue
            try:
                if not (stage / name).exists():
                    (stage / name).write_bytes(
                        (central / record["source"]).read_text(encoding="utf-8").encode("utf-8")
                    )
                _, _, rendered = readme.readme_update(
                    stage, settings, "en" if name == "README.md" else "ko", name
                )
                propose(record, name, rendered)
            except (ValueError, KeyError, OSError) as error:
                result["conflicts"].append(f"{name}: {error}")
    for file in {
        item
        for axis in ("minimum", "current")
        for key in ("requirements", "constraints")
        for item in data["environments"]["value"][axis][key]
    }:
        inventory.safe_target_path(target, file)
        guards.setdefault(file, None)
        if file not in files and not any(
            operation["path"] == file for operation in result["operations"]
        ):
            result["pending"].append(
                f"Actual {file} environment file must be supplied; no unregistered path is generated"
            )
    result["guards"] = [
        {
            "path": name,
            "sha256": sha,
            "kind": "file"
            if sha is not None
            else "directory"
            if (target / name).is_dir()
            else "absent",
        }
        for name, sha in sorted(guards.items())
    ]
    for field in ("pending", "conflicts", "unchanged"):
        result[field] = sorted(set(result[field]))
    result["operations"].sort(key=lambda operation: operation["path"])
    verify_standards(standards_reference, central)
    final_hashes = {
        name: digest((target / name).read_bytes()) for name in inventory.file_paths(target)
    }
    if final_hashes != initial_hashes:
        raise ValueError(
            "Target changed while planning; inspect and plan again with the current files"
        )
    contract.validate_document(result, "plan")
    return result

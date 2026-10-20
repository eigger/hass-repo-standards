"""Read integration metadata without changing target files or Git state."""

from __future__ import annotations

import ast
import json
import math
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from . import categories, conditions, contract, readme


def load_json(path):
    def reject_constant(value):
        raise ValueError(f"Non-standard JSON constant: {value}")

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def parse_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("JSON number is not finite")
        return result

    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=reject_constant,
        parse_float=parse_float,
        object_pairs_hook=object_pairs,
    )


def git(root, *args, remote=False):
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            env=environment,
            timeout=15 if remote else 10,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("Git metadata query timed out; no target changes were made") from error
    return result.stdout if result.returncode == 0 else None


def github_repository(remote):
    if not isinstance(remote, str):
        raise ValueError("A confirmed GitHub remote is required")
    ssh = re.fullmatch(r"git@github\.com:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?", remote)
    if ssh:
        return ssh[1]
    parsed = urlsplit(remote)
    if (
        parsed.scheme not in {"https", "ssh"}
        or parsed.hostname != "github.com"
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use a confirmed HTTPS or SSH GitHub remote without credentials")
    if parsed.scheme == "https" and parsed.username:
        raise ValueError("Remote must not contain credentials")
    if parsed.scheme == "ssh" and parsed.username not in {None, "git"}:
        raise ValueError("Unsupported SSH remote user")
    path = parsed.path.removeprefix("/").removesuffix(".git")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", path):
        raise ValueError("Remote must identify owner/repository")
    return path


def safe_target_path(root, relative):
    contract.validate_path(relative)
    for part in relative.split("/"):
        if part != part.rstrip(" .") or re.search(r"[\x00-\x1f\x7f]", part):
            raise ValueError(f"Nonportable target path: {relative}")
        if re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part):
            raise ValueError(f"Reserved Windows path: {relative}")
    path = root / relative
    for candidate in (path, *path.parents):
        if candidate == root:
            break
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError(f"Symbolic links and junctions require manual review: {relative}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes target repository: {relative}")
    return path


def file_paths(root):
    """Tracked and nonignored preserved files; never enumerate ignored environments."""
    if not root.exists():
        return []
    top = git(root, "rev-parse", "--show-toplevel")
    if top is not None and Path(top.decode("utf-8").strip()).resolve() == root:
        raw = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
        if raw is None:
            raise ValueError("Unable to enumerate repository files")
        candidates = set(name for name in raw.decode("utf-8").split("\0") if name)
        # Critical metadata remains visible even when accidentally ignored.
        for pattern in ("custom_components/*/manifest.json", ".github/workflows/*"):
            candidates.update(path.relative_to(root).as_posix() for path in root.glob(pattern))
        candidates.update(
            name
            for name in (
                "LICENSE",
                "hacs.json",
                "README.md",
                "README.ko.md",
                ".hass-standards.json",
            )
            if (root / name).exists()
        )
    else:
        candidates = set()
        for directory, dirs, files in os.walk(root, followlinks=False):
            directory = Path(directory)
            dirs[:] = sorted(name for name in dirs if not (directory == root and name == ".git"))
            for name in dirs + sorted(files):
                if directory == root and name == ".git":
                    continue
                path = directory / name
                relative = path.relative_to(root).as_posix()
                safe_target_path(root, relative)
                if (
                    path.is_file()
                    or path.is_symlink()
                    or getattr(path, "is_junction", lambda: False)()
                ):
                    candidates.add(relative)
    result = []
    for relative in sorted(candidates):
        path = safe_target_path(root, relative)
        if path.is_file():
            result.append(relative)
    return result


def normalized_ha(value):
    if isinstance(value, str) and re.fullmatch(r"20\d{2}\.\d{1,2}(?:\.\d+)?", value):
        return value + ".0" if value.count(".") == 1 else value
    return value


def dirty_paths(root):
    raw = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if raw is None:
        return []
    records = raw.decode("utf-8").split("\0")
    paths, index = [], 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise ValueError("Unrecognized Git status record")
        status, name = record[:2], record[3:]
        contract.validate_path(name)
        paths.append(name)
        if "R" in status or "C" in status:
            if index >= len(records) or not records[index]:
                raise ValueError("Incomplete Git rename status")
            contract.validate_path(records[index])
            paths.append(records[index])
            index += 1
    return sorted(set(paths))


def inspect(root):
    root = Path(root).resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("Target must be a directory")
    paths = file_paths(root)
    result = {
        "schema_version": 1,
        "target": str(root),
        "repository": None,
        "default_branch": None,
        "current_branch": None,
        "dirty_paths": [],
        "domains": [],
        "observations": [],
        "conflicts": [],
        "pending": [],
    }

    def observe(field, value, source):
        result["observations"].append({"field": field, "value": value, "source": source})

    if git(root, "rev-parse", "--show-toplevel") is not None:
        top = git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        if Path(top).resolve() != root:
            result["conflicts"].append("Target must be the Git repository root")
        remote = git(root, "remote", "get-url", "origin")
        if remote:
            remote = remote.decode("utf-8").strip()
            redacted = re.sub(r"([A-Za-z][A-Za-z0-9+.-]*://)[^/@]+@", r"\1[redacted]@", remote)
            if remote.startswith("ssh://git@"):
                redacted = remote
            observe("remote", redacted, "git remote get-url origin")
            try:
                result["repository"] = github_repository(remote)
            except ValueError as error:
                result["pending"].append(str(error))
        branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
        result["current_branch"] = branch.decode("utf-8").strip() if branch else None
        default = git(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
        if default:
            result["default_branch"] = default.decode("utf-8").strip().removeprefix("origin/")
            observe(
                "default_branch",
                result["default_branch"],
                "git symbolic-ref refs/remotes/origin/HEAD",
            )
        # No network access or guessed branch: a missing observation needs explicit input.
        result["dirty_paths"] = dirty_paths(root)
    else:
        result["pending"].append(
            "Git metadata unavailable; provide confirmed remote and default branch"
        )
    if result["default_branch"] is None:
        result["pending"].append("Default branch unknown; no main/master fallback is used")
    if result["repository"] is None:
        result["pending"].append("Repository identity requires confirmed explicit input")

    manifests = [
        name for name in paths if re.fullmatch(r"custom_components/[^/]+/manifest\.json", name)
    ]
    if len(manifests) > 1:
        result["conflicts"].append(
            "Multiple integration manifests are outside automatic adoption scope"
        )
    for name in manifests:
        data = load_json(root / name)
        if not isinstance(data, dict):
            raise ValueError(f"Manifest must be an object: {name}")
        domain = data.get("domain")
        if (
            not isinstance(domain, str)
            or not re.fullmatch(r"[a-z][a-z0-9_]*", domain)
            or Path(name).parent.name != domain
        ):
            result["conflicts"].append(f"Manifest domain and directory disagree: {name}")
        else:
            result["domains"].append(domain)
        observe("manifest", data, name)
        try:
            categories.validate_manifest(data)
        except ValueError as error:
            result["pending"].append(
                f"HA-02 {name}: {error}; record product evidence, do not infer categories"
            )
        if "homeassistant" in data:
            observe("minimum_ha", data["homeassistant"], name)
        for package in ("imagespec", "blesession"):
            observe(
                "uses_" + package,
                conditions.uses_package(root, root / name, data, readme.safe_path, package),
                name + " and absolute Python imports",
            )
        modules = [
            path
            for path in paths
            if path.startswith(str(Path(name).parent.as_posix()) + "/") and path.endswith(".py")
        ]
        for module in modules:
            tree = ast.parse(
                (root / module).read_text(encoding="utf-8"), filename=str(root / module)
            )
            observe(
                "python_functions",
                sorted(
                    {
                        node.name
                        for node in ast.walk(tree)
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    }
                ),
                module,
            )
        observe("component_modules", modules, name)
    if "hacs.json" in paths:
        hacs = load_json(root / "hacs.json")
        if not isinstance(hacs, dict):
            raise ValueError("hacs.json must be an object")
        observe("hacs", hacs, "hacs.json")
        if "homeassistant" in hacs:
            observe("minimum_ha", hacs["homeassistant"], "hacs.json")
    for name in paths:
        if name in {"README.md", "README.ko.md"}:
            text = (root / name).read_text(encoding="utf-8")
            markers = re.findall(r"<!-- hass-standards:([a-z-]+):(start|end) -->", text)
            observe("readme_markers", [list(pair) for pair in markers], name)
            # Normalize explicit support minima only; ambiguous lines remain pending.
            support_lines = []
            for line in text.splitlines():
                if not re.search(r"Home Assistant|(?:\bHA\b)|지원|최소", line, re.I):
                    continue
                support_lines.append(line)
                versions = re.findall(r"(?<![\d.])(20\d{2}\.\d{1,2}(?:\.\d+)?)(?![\d.])", line)
                explicit = re.search(
                    r"minimum|min\s+HA|>=|≥|or later|or newer|이상|최소|\d\+", line, re.I
                )
                if explicit:
                    for value in versions:
                        observe("minimum_ha", normalized_ha(value), name + ": " + line.strip())
                elif versions and not re.search(r"tested|current|테스트|검증", line, re.I):
                    result["pending"].append(
                        f"Ambiguous support declaration requires review: {name}: {line.strip()}"
                    )
            observe("readme_support_lines", support_lines, name)
        if ("requirements" in Path(name).name or "constraints" in Path(name).name) and Path(
            name
        ).suffix in {".txt", ".in"}:
            observe("environment_requirements", (root / name).read_text(encoding="utf-8"), name)
        if name.startswith(".github/workflows/"):
            observe("workflow", (root / name).read_text(encoding="utf-8"), name)
        if name == ".hass-standards.json":
            observe("standards_settings", load_json(root / name), name)
    settings = next(
        (item["value"] for item in result["observations"] if item["field"] == "standards_settings"),
        {},
    )
    for item in result["observations"]:
        if item["field"] == "manifest":
            try:
                categories.validate_review(
                    item["value"],
                    settings.get("categories_review") if isinstance(settings, dict) else None,
                )
            except ValueError as error:
                result["pending"].append(
                    f"HA-02 {item['source']}: {error}; record product evidence, do not infer categories"
                )
    minimums = {
        str(normalized_ha(item["value"]))
        for item in result["observations"]
        if item["field"] == "minimum_ha"
    }
    if len(minimums) > 1:
        result["conflicts"].append(
            "Support minimum declarations disagree; preserve and reconcile actual declarations"
        )
    result["domains"] = sorted(set(result["domains"]))
    for field in ("conflicts", "pending"):
        result[field] = sorted(set(result[field]))
    contract.validate_document(result, "inventory")
    return result

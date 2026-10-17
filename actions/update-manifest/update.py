"""Propose stable PyPI manifest updates; no GitHub writes, dry-run by default."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import urllib.request
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version


def simple_spec(requirement: Requirement) -> tuple[str, Version]:
    specs = list(requirement.specifier)
    if requirement.url or len(specs) != 1 or specs[0].operator not in {"==", ">="}:
        raise ValueError(f"Manual review required for requirement: {requirement}")
    spec = specs[0]
    if "*" in spec.version:
        raise ValueError(f"Wildcard requirement is unsupported: {requirement}")
    return spec.operator, Version(spec.version)


def fetch_package(name: str) -> dict:
    url = f"https://pypi.org/pypi/{canonicalize_name(name)}/json"
    request = urllib.request.Request(url, headers={"User-Agent": "hass-repo-standards"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def latest_stable(data: dict, python_version: str) -> Version:
    candidates = []
    for raw, files in data["releases"].items():
        try:
            version = Version(raw)
        except InvalidVersion:
            continue
        if version.is_prerelease or version.is_devrelease:
            continue
        for file in files:
            if file.get("yanked"):
                continue
            requires_python = file.get("requires_python")
            if requires_python and not SpecifierSet(requires_python).contains(python_version):
                continue
            candidates.append(version)
            break
    if not candidates:
        raise ValueError("No stable non-yanked release supports the selected Python")
    return max(candidates)


def plan_updates(manifest: dict, packages: list[str], fetch=fetch_package, allow_major=False):
    if not packages or any(not isinstance(p, str) for p in packages):
        raise ValueError("packages must be a nonempty JSON array of package names")
    selected = {canonicalize_name(p) for p in packages}
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", p) for p in selected):
        raise ValueError("Invalid package name")
    requirements = manifest.get("requirements", [])
    seen = set()
    result = list(requirements)
    changes = []
    for index, text in enumerate(requirements):
        requirement = Requirement(text)
        name = canonicalize_name(requirement.name)
        if name not in selected:
            continue
        if name in seen:
            raise ValueError(f"Duplicate selected requirement: {name}")
        seen.add(name)
        if requirement.marker and not requirement.marker.evaluate():
            raise ValueError(
                f"Cannot validate inactive marker for {text}; "
                "run the updater in an environment where this marker is active"
            )
        operator, current = simple_spec(requirement)
        latest = latest_stable(fetch(name), platform.python_version())
        if latest <= current:
            continue
        if latest.major != current.major and not allow_major:
            raise ValueError(f"Major update needs review: {name} {current} -> {latest}")
        # Replace only the specifier token, preserving extras, marker and original spelling.
        pattern = (
            re.escape(operator) + r"\s*" + re.escape(str(next(iter(requirement.specifier)).version))
        )
        updated, count = re.subn(pattern, operator + str(latest), text, count=1)
        if count != 1:
            raise ValueError(f"Could not preserve requirement syntax: {text}")
        result[index] = updated
        changes.append(f"- `{text}` → `{updated}`")
    if selected - seen:
        raise ValueError(f"Selected packages absent from manifest: {sorted(selected - seen)}")
    return {**manifest, "requirements": result}, changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--packages", required=True, type=json.loads)
    parser.add_argument("--allow-major", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not isinstance(args.packages, list):
        parser.error("--packages must be a JSON array")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    updated, changes = plan_updates(manifest, args.packages, allow_major=args.allow_major)
    print("\n".join(changes) if changes else "Requirements are current; no change")
    if args.write and changes:
        args.manifest.write_text(
            json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"updated={'true' if changes else 'false'}\n")
    body = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "hass-dependency-update.md"
    body.write_text(
        "Manifest dependency update proposed by hass-repo-standards.\n\n"
        + "\n".join(changes)
        + "\n\nOperators, extras and markers are preserved. Changes to a >= floor raise the minimum.\n"
        + "The configured validation command runs before this PR is opened.\n"
        + "GITHUB_TOKEN does not automatically trigger subsequent push/PR workflows; "
        + "required checks must be completed before merge.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

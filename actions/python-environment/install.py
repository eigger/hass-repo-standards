"""Install caller test requirements and manifest requirements without shell interpolation."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version


def minimum_requirements(requirements: list[str], packages: list[str]):
    selected = {canonicalize_name(p) for p in packages}
    found = set()
    active = set()
    exact = []
    expected = {}
    for text in requirements:
        req = Requirement(text)
        name = canonicalize_name(req.name)
        if name not in selected:
            continue
        found.add(name)
        specs = list(req.specifier)
        if req.url or len(specs) != 1 or specs[0].operator not in {"==", ">="}:
            raise ValueError(f"Minimum must be an explicit == or >= version: {text}")
        spec = specs[0]
        version = Version(spec.version)
        if req.marker and not req.marker.evaluate():
            print(f"Skipping {req.name}: marker is inactive in this environment ({text})")
            continue
        active.add(name)
        extras = "[" + ",".join(sorted(req.extras)) + "]" if req.extras else ""
        exact.append(f"{req.name}{extras}=={version}")
        expected[name] = version
    if selected - found:
        raise ValueError(f"Minimum packages absent from manifest: {sorted(selected - found)}")
    if selected and not active:
        raise ValueError(
            "Every selected minimum package has an inactive marker in this environment"
        )
    return exact, expected


def component_requirements(root: Path, names: list[str]) -> list[str]:
    visited = set()
    requirements = set()

    def visit(name):
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise ValueError(f"Invalid Home Assistant component: {name}")
        if name in visited:
            return
        visited.add(name)
        manifest = root / "components" / name / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        requirements.update(data.get("requirements", []))
        for dependency in data.get("dependencies", []):
            visit(dependency)

    for name in names:
        visit(name)
    return sorted(requirements)


def pip(*arguments):
    subprocess.run([sys.executable, "-m", "pip", *arguments], check=True)


def main():
    domain = os.environ["INPUT_DOMAIN"]
    if not re.fullmatch(r"[a-z0-9_]+", domain):
        raise ValueError("Invalid domain")
    manifest = Path("custom_components") / domain / "manifest.json"
    requirements = json.loads(manifest.read_text(encoding="utf-8")).get("requirements", [])
    mode = os.environ.get("INPUT_DEPENDENCY_MODE", "current")
    if mode not in {"current", "minimum"}:
        raise ValueError("dependency-mode must be current or minimum")
    packages = json.loads(os.environ.get("INPUT_MINIMUM_PACKAGES", "[]"))
    if not isinstance(packages, list) or any(not isinstance(p, str) for p in packages):
        raise ValueError("minimum-packages must be a JSON string array")
    expected = {}
    if mode == "minimum":
        if not packages:
            raise ValueError("minimum mode requires minimum-packages")
        exact, expected = minimum_requirements(requirements, packages)
        requirements += exact
    temporary = Path(os.environ["RUNNER_TEMP"])
    generated = temporary / "hass-manifest-requirements.txt"
    generated.write_text("\n".join(requirements) + "\n", encoding="utf-8")
    test_file = os.environ["INPUT_REQUIREMENTS"]
    if not Path(test_file).is_file():
        raise FileNotFoundError(test_file)
    arguments = ["install", "-r", test_file, "-r", str(generated)]
    constraints = os.environ.get("INPUT_CONSTRAINTS", "")
    if constraints:
        arguments += ["-c", constraints]
    pip(*arguments)
    names = os.environ.get("INPUT_HA_COMPONENTS", "").split()
    if names:
        spec = importlib.util.find_spec("homeassistant")
        if spec is None or not spec.submodule_search_locations:
            raise ValueError("ha-components requires a real installed Home Assistant")
        root = Path(next(iter(spec.submodule_search_locations)))
        ha_file = temporary / "hass-component-requirements.txt"
        ha_file.write_text("\n".join(component_requirements(root, names)) + "\n", encoding="utf-8")
        # Resolve all requirements together again, preserving minimum and test constraints.
        pip(*arguments, "-r", str(ha_file))
    pip("check")
    for name, version in expected.items():
        actual = Version(importlib.metadata.version(name))
        if actual != version:
            raise ValueError(f"Minimum not installed: {name} {actual} != {version}")
    profile = os.environ.get("INPUT_TEST_PROFILE", "unit")
    if profile not in {"unit", "ha"}:
        raise ValueError("test-profile must be unit or ha")
    try:
        ha_version = importlib.metadata.version("homeassistant")
    except importlib.metadata.PackageNotFoundError:
        ha_version = "not installed"
    if profile == "ha" and ha_version == "not installed":
        raise ValueError("ha profile requires installed Home Assistant")
    expected_ha = os.environ.get("INPUT_EXPECTED_HA_VERSION", "")
    if expected_ha and (
        ha_version == "not installed" or Version(ha_version) != Version(expected_ha)
    ):
        raise ValueError(f"Wrong Home Assistant version: {ha_version} != {expected_ha}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    report = (
        f"Python {platform.python_version()} | profile {profile} | deps {mode} | HA {ha_version}\n"
    )
    print(report)
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(report)


if __name__ == "__main__":
    main()

"""Validate standards links and workflow/action contracts without network access."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class Loader(yaml.SafeLoader):
    pass


Loader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values if tag != "tag:yaml.org,2002:bool"]
    for key, values in Loader.yaml_implicit_resolvers.items()
}
for key in "tTfF":
    Loader.add_implicit_resolver(
        "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), [key]
    )


def is_destination_license_placeholder(file: Path, target: str):
    # README assets target the adopter's actual LICENSE; never distribute a
    # sample license that could overwrite or silently change its legal terms.
    return (
        file
        in {
            ROOT / "templates/integration/README.md",
            ROOT / "templates/integration/README.ko.md",
        }
        and target == "LICENSE"
    )


def check_template_integrity():
    from check_integration import readme_updates

    errors = []
    source = ROOT / "templates/integration"
    for relative in (
        "tests/__init__.py",
        "tests/components/__init__.py",
        "tests/components/example/__init__.py",
    ):
        path = source / relative
        if not path.is_file() or path.read_bytes():
            errors.append(f"templates/integration/{relative}: must exist and be empty")
    expected = (
        '"""Shared Home Assistant test configuration."""\n\nimport pytest\n\n\n'
        "@pytest.fixture(autouse=True)\ndef auto_enable_custom_integrations(enable_custom_integrations):\n"
        '    """Enable custom integrations for all tests."""\n'
    )
    if (source / "tests/conftest.py").read_text() != expected:
        errors.append("templates/integration/tests/conftest.py: central fixture contract changed")
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory)
        (fixture / "custom_components/example").mkdir(parents=True)
        (fixture / "custom_components/example/manifest.json").write_text('{"domain":"example"}')
        (fixture / "hacs.json").write_text("{}")
        (fixture / "LICENSE").write_text("Synthetic render fixture; not an adoption license")
        shutil.copytree(source / ".github", fixture / ".github")
        config = json.loads((source / ".hass-standards.json").read_text())
        for name in config["readmes"]:
            shutil.copyfile(source / name, fixture / name)
        try:
            for path, _ in readme_updates(fixture, config):
                errors.append(
                    f"templates/integration/{path.name}: managed areas differ from renderer"
                )
        except (ValueError, KeyError, FileNotFoundError) as err:
            errors.append(f"templates/integration: {err}")
    caller = yaml.load((source / ".github/workflows/validate.yml").read_text(), Loader=Loader)
    steps = caller.get("jobs", {}).get("standards", {}).get("steps", [])
    if not any(
        step.get("uses") == "eigger/hass-repo-standards/actions/check-standards@main"
        for step in steps
    ):
        errors.append("validate.yml: central standards action adoption placeholder required")
    action = yaml.load((ROOT / "actions/check-standards/action.yml").read_text(), Loader=Loader)
    if action["runs"]["using"] != "composite" or not any(
        "${{ github.action_path }}/../../scripts/check_integration.py" in step.get("run", "")
        and '"$GITHUB_WORKSPACE"' in step.get("run", "")
        for step in action["runs"]["steps"]
    ):
        errors.append("check-standards action: action_path script and caller checkout required")
    return errors


def check():
    errors = []
    documents = [
        *sorted(ROOT.glob("README*.md")),
        ROOT / "CONTRIBUTING.md",
        ROOT / "AGENTS.md",
        *sorted((ROOT / "templates/integration").glob("*.md")),
        *sorted((ROOT / "docs").glob("*.md")),
    ]
    for file in documents:
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            if (
                target
                and not (file.parent / target).exists()
                and not is_destination_license_placeholder(file, target)
            ):
                errors.append(f"{file.relative_to(ROOT)}: missing link {link}")
    workflows = [
        *sorted((ROOT / ".github/workflows").glob("*.yml")),
        *sorted((ROOT / "templates/integration/.github/workflows").glob("*.yml")),
    ]
    for file in workflows:
        data = yaml.load(file.read_text(encoding="utf-8"), Loader=Loader)
        if "on" not in data or "permissions" not in data:
            errors.append(f"{file.name}: explicit events and permissions required")
        for name, job in data.get("jobs", {}).items():
            if "uses" not in job and not job.get("timeout-minutes"):
                errors.append(f"{file.name}/{name}: timeout required")
            for step in job.get("steps", []):
                action = step.get("uses", "")
                if (
                    action.startswith("actions/checkout@")
                    and step.get("with", {}).get("persist-credentials") is not False
                ):
                    errors.append(f"{file.name}/{name}: checkout credentials must not persist")
        # Check caller examples against declared reusable workflow input types and names.
        for job in data.get("jobs", {}).values():
            reference = job.get("uses", "")
            marker = "eigger/hass-repo-standards/.github/workflows/"
            if not reference.startswith(marker):
                continue
            filename = reference.removeprefix(marker).split("@", 1)[0]
            called = yaml.load((ROOT / ".github/workflows" / filename).read_text(), Loader=Loader)
            declared = called["on"]["workflow_call"].get("inputs", {})
            supplied = job.get("with", {})
            for key in supplied:
                if key not in declared:
                    errors.append(f"{file.name}: unknown input {key}")
            for key, spec in declared.items():
                if spec.get("required") and key not in supplied:
                    errors.append(f"{file.name}: missing required input {key}")
    for file in ROOT.rglob("*.json"):
        if ".venv" not in file.parts:
            json.loads(file.read_text(encoding="utf-8"))
    errors.extend(check_template_integrity())
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(
        f"Checked {len(documents)} documents, {len(workflows)} workflows, JSON and caller input contracts"
    )


if __name__ == "__main__":
    check()

"""Validate standards links and workflow/action contracts without network access."""

from __future__ import annotations

import json
import re
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


def check():
    errors = []
    documents = [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        *sorted((ROOT / "docs").glob("*.md")),
    ]
    for file in documents:
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            if target and not (file.parent / target).exists():
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
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(
        f"Checked {len(documents)} documents, {len(workflows)} workflows, JSON and caller input contracts"
    )


if __name__ == "__main__":
    check()

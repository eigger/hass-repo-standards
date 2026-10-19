"""Validate standards links and workflow/action contracts without network access."""

from __future__ import annotations

import ast
import json
import math
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


def check_document_links(file):
    from bluetooth_documents import visible_markdown

    errors = []
    for link in re.findall(r"\]\(([^)]+)\)", visible_markdown(file.read_text(encoding="utf-8"))):
        if "://" in link or link.startswith("#"):
            continue
        target = link.split("#", 1)[0]
        if (
            target
            and not (file.parent / target).exists()
            and not is_destination_license_placeholder(file, target)
        ):
            errors.append(f"{file.relative_to(ROOT)}: missing link {link}")
    return errors


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


def contract_probe_input():
    """Synthetic schema/render probe only; never device or adoption evidence."""

    def sourced(value):
        return {"value": value, "source": "central offline integrity probe; not adoption evidence"}

    environment = {
        "ha": "2026.10.2",
        "python": "3.14",
        "pytest_homeassistant_custom_component": "0.13.373",
        "requirements": ["requirements_test.txt"],
        "constraints": [],
    }
    return {
        "schema_version": 1,
        "repository": sourced("fixture/example"),
        "default_branch": sourced("fixture-default"),
        "domain": sourced("example"),
        "manifest": sourced(
            {
                "domain": "example",
                "name": "Integrity probe",
                "version": "1.0.0",
                "documentation": "https://example.invalid",
                "issue_tracker": "https://example.invalid/issues",
                "codeowners": ["@fixture"],
                "requirements": [],
                "dependencies": [],
                "after_dependencies": [],
                "config_flow": True,
            }
        ),
        "readme": sourced(
            {
                "title": "Integrity probe",
                "descriptions": {"en": "Probe", "ko": "검사"},
                "issues": True,
                "discussions": False,
                "related_projects": [],
            }
        ),
        "license": sourced(
            {"name": "MIT License", "path": "LICENSE", "notices": {"en": [], "ko": []}}
        ),
        "configuration": sourced("ui"),
        "platforms": sourced(["sensor"]),
        "features": sourced(
            {
                name: True
                for name in (
                    "coordinator",
                    "shared_entity",
                    "diagnostics",
                    "actions",
                    "fixtures",
                    "snapshots",
                    "dependency_updates",
                )
            }
        ),
        "environments": sourced(
            {"minimum": environment.copy(), "current": environment.copy(), "libraries": {}}
        ),
    }


def check_contract_integrity():
    """Validate central schemas/assets; intentional draft TODOs remain allowed here."""
    from standards import contract, scaffold

    errors = []
    try:
        document = contract.load_contract(ROOT / "templates/integration/contract.json")
        schemas = {kind: contract.load_schema(kind) for kind in ("input", "inventory", "plan")}
        references = {f"integration-{kind}.schema.json": kind for kind in schemas}

        def walk(node, active=()):
            if not isinstance(node, dict):
                raise ValueError("Schema nodes must be objects")
            for keyword in ("$schema", "title", "description", "pattern"):
                if keyword in node and not isinstance(node[keyword], str):
                    raise ValueError(f"Schema {keyword} must be a string")
            if "type" in node:
                names = node["type"] if isinstance(node["type"], list) else [node["type"]]
                if (
                    not names
                    or any(not isinstance(name, str) for name in names)
                    or len(names) != len(set(names))
                ):
                    raise ValueError("Schema type must name unique types")
            if "enum" in node and (not isinstance(node["enum"], list) or not node["enum"]):
                raise ValueError("Schema enum must be a nonempty array")
            for keyword in ("minLength", "minItems", "maxItems"):
                if keyword in node and (type(node[keyword]) is not int or node[keyword] < 0):
                    raise ValueError(f"Schema {keyword} must be a nonnegative integer")
            if "minimum" in node and (
                isinstance(node["minimum"], bool)
                or not isinstance(node["minimum"], (int, float))
                or not math.isfinite(node["minimum"])
            ):
                raise ValueError("Schema minimum must be a finite number")
            if "uniqueItems" in node and type(node["uniqueItems"]) is not bool:
                raise ValueError("Schema uniqueItems must be boolean")
            if "$ref" in node:
                reference = node["$ref"]
                if not isinstance(reference, str) or reference not in references:
                    raise ValueError("Unsupported schema reference")
                kind = references[reference]
                if kind in active:
                    raise ValueError("Cyclic schema reference")
                walk(schemas[kind], (*active, kind))
            # Share supported vocabulary/type validation without following a ref twice.
            try:
                contract.validate_schema(None, {k: v for k, v in node.items() if k != "$ref"})
            except ValueError as error:
                if "unsupported schema" in str(error):
                    raise
            if "pattern" in node:
                re.compile(node["pattern"])
            if "required" in node and (
                not isinstance(node["required"], list)
                or any(not isinstance(name, str) for name in node["required"])
                or len(node["required"]) != len(set(node["required"]))
            ):
                raise ValueError("Schema required must contain unique property names")
            if "items" in node and not isinstance(node["items"], dict):
                raise ValueError("Schema items must be an object")
            if "additionalProperties" in node and not isinstance(
                node["additionalProperties"], (bool, dict)
            ):
                raise ValueError("Schema additionalProperties must be boolean or an object")
            if "properties" in node:
                if not isinstance(node["properties"], dict):
                    raise ValueError("Schema properties must be an object")
                for child in node["properties"].values():
                    walk(child, active)
            for keyword in ("items", "additionalProperties"):
                if isinstance(node.get(keyword), dict):
                    walk(node[keyword], active)
            for keyword in ("allOf", "anyOf"):
                if keyword in node:
                    if not isinstance(node[keyword], list) or not node[keyword]:
                        raise ValueError(f"Schema {keyword} must be a nonempty list")
                    for child in node[keyword]:
                        walk(child, active)

        for kind, schema in schemas.items():
            if (
                schema.get("properties", {}).get("schema_version", {}).get("const")
                != contract.SCHEMA_VERSION
            ):
                raise ValueError(f"{kind}: schema version differs from the contract")
            if "schema_version" not in schema.get("required", []):
                raise ValueError(f"{kind}: schema_version must remain required")
            walk(schema, (kind,))
        probe = contract_probe_input()
        contract.validate_input(probe)
        rendered = {}
        asset_ids = set()
        for record in document["records"]:
            if not scaffold.handles(record):
                continue
            asset_ids.add(record["id"])
            destination = contract.destination_path(record, "example", "sensor")
            content, pending = scaffold.render(record, destination, probe, central=ROOT)
            if content is None:
                raise ValueError(f"{destination}: central authoring asset cannot render")
            if destination.endswith(".py"):
                ast.parse(content, filename=destination, feature_version=(3, 9))
            elif destination.endswith(".json"):
                rendered[record["id"]] = json.loads(content)
            elif destination.endswith(".yaml"):
                yaml.safe_load(content)
            # pending/TODO is expected in central drafts; adopter checks reject it.
        if asset_ids != set(scaffold.ASSETS):
            raise ValueError("Scaffold renderer and declared assets differ")
        expected = {
            ROOT / "templates/integration/scaffold" / name for name in scaffold.ASSETS.values()
        }
        actual = set((ROOT / "templates/integration/scaffold").rglob("*.tmpl"))
        if actual != expected:
            raise ValueError("Unregistered or missing central scaffold template")
        if rendered["component-strings.json"] != rendered["component-translations-en.json"]:
            raise ValueError("English source and distributed translation differ")
        scaffold.validate_translations(
            rendered["component-translations-en.json"], rendered["component-translations-ko.json"]
        )
        for relative in (
            "scripts/manage_integration.py",
            "scripts/standards/apply.py",
            "docs/template-skill-plan.md",
            "docs/template-skill-tasks.md",
            "docs/template-skill-usage.md",
            "docs/template-skill-validation.md",
        ):
            if not (ROOT / relative).is_file():
                raise ValueError(f"Missing implemented-stage resource: {relative}")
        # No placeholder exception for future skills: once a skill folder exists,
        # its entry point and references must be real files.
        for directory in (ROOT / "skills").glob("*"):
            if directory.is_dir() and not (directory / "SKILL.md").is_file():
                raise ValueError(f"Missing skill entry point: {directory.name}")
        for file in (ROOT / "skills").rglob("*.md"):
            errors.extend(check_document_links(file))
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        SyntaxError,
        re.error,
        RecursionError,
    ) as error:
        errors.append(f"central integration contract: {error}")
    return errors


def check():
    errors = []
    documents = [
        *sorted(ROOT.glob("README*.md")),
        ROOT / "CONTRIBUTING.md",
        ROOT / "AGENTS.md",
        *sorted((ROOT / "templates/integration").rglob("*.md")),
        *sorted((ROOT / "docs").glob("*.md")),
    ]
    for file in documents:
        errors.extend(check_document_links(file))
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
    errors.extend(check_contract_integrity())
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(
        f"Checked {len(documents)} documents, {len(workflows)} workflows, JSON and caller input contracts"
    )


if __name__ == "__main__":
    check()

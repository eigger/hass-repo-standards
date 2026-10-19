"""Load versioned contracts and validate their JSON inputs without new dependencies.

The validator deliberately implements only the JSON Schema keywords shipped in
this repository. It rejects unsupported keywords instead of silently ignoring a
future schema feature. These contracts describe assets; they do not apply them.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path, PurePosixPath

CENTRAL = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 1
OWNERSHIP = {"exact_file", "managed_blocks", "create_only", "merge"}
CONDITIONS = {
    "always",
    "ui",
    "platforms",
    "coordinator",
    "shared_entity",
    "diagnostics",
    "actions",
    "fixtures",
    "snapshots",
    "dependency_updates",
    "imagespec",
    "blesession",
}


def _fail(path, message):
    raise ValueError(f"{path}: {message}")


def validate_schema(value, schema, path="input"):
    """Validate the explicitly supported schema vocabulary used by T1 artifacts."""
    allowed = {
        "$schema",
        "$ref",
        "title",
        "description",
        "type",
        "const",
        "enum",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minLength",
        "pattern",
        "minimum",
        "allOf",
        "anyOf",
    }
    unknown = set(schema) - allowed
    if unknown:
        _fail(path, f"unsupported schema keywords: {sorted(unknown)}")
    if "$ref" in schema:
        references = {
            f"integration-{kind}.schema.json": kind for kind in ("input", "inventory", "plan")
        }
        reference = schema["$ref"]
        if not isinstance(reference, str) or reference not in references:
            _fail(
                path,
                "unsupported schema reference; only named central integration schemas are allowed",
            )
        validate_schema(value, load_schema(references[reference]), path)
    types = {
        "object": lambda x: isinstance(x, dict),
        "array": lambda x: isinstance(x, list),
        "string": lambda x: isinstance(x, str),
        "boolean": lambda x: isinstance(x, bool),
        "integer": lambda x: (
            (isinstance(x, int) and not isinstance(x, bool))
            or (isinstance(x, float) and math.isfinite(x) and x.is_integer())
        ),
        "null": lambda x: x is None,
    }
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if any(name not in types for name in names):
            _fail(path, "unsupported schema type")
        if not any(types[name](value) for name in names):
            _fail(path, f"expected type {names}")

    def equal(left, right):
        # JSON Schema compares numbers mathematically, but booleans are distinct.
        if isinstance(left, bool) or isinstance(right, bool):
            return type(left) is type(right) and left == right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left == right
        return type(left) is type(right) and left == right

    if "const" in schema and not equal(value, schema["const"]):
        _fail(path, f"expected {schema['const']!r}")
    if "enum" in schema and not any(equal(value, x) for x in schema["enum"]):
        _fail(path, "unsupported value")
    for subschema in schema.get("allOf", []):
        validate_schema(value, subschema, path)
    if "anyOf" in schema:
        for subschema in schema["anyOf"]:
            try:
                validate_schema(value, subschema, path)
                break
            except ValueError:
                pass
        else:
            _fail(path, "no allowed schema variant matches")
    if isinstance(value, dict):
        missing = set(schema.get("required", [])) - value.keys()
        if missing:
            _fail(path, f"missing required inputs: {sorted(missing)}")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate_schema(item, properties[key], f"{path}.{key}")
            elif schema.get("additionalProperties", True) is False:
                _fail(path, f"unknown field {key}")
            elif isinstance(schema.get("additionalProperties"), dict):
                validate_schema(item, schema["additionalProperties"], f"{path}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get(
            "maxItems", float("inf")
        ):
            _fail(path, "invalid item count")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in value]
            if len(set(serialized)) != len(serialized):
                _fail(path, "duplicate items")
        for index, item in enumerate(value):
            validate_schema(item, schema.get("items", {}), f"{path}[{index}]")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            _fail(path, "string is too short")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            _fail(path, "invalid string format")
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value < schema.get("minimum", value)
    ):
        _fail(path, "value is below minimum")
    return value


def load_schema(kind):
    if kind not in {"input", "inventory", "plan"}:
        raise ValueError(f"Unknown integration schema: {kind}")
    return json.loads(
        (CENTRAL / f"schemas/integration-{kind}.schema.json").read_text(encoding="utf-8")
    )


def validate_input(data, required_inputs=()):
    validate_schema(data, load_schema("input"))
    for name in required_inputs:
        if name not in data:
            _fail("input", f"missing required input {name}")
    return data


def validate_document(data, kind):
    return validate_schema(data, load_schema(kind), kind)


def validate_path(value, *, tokens=False):
    """Allow portable relative paths only, with explicitly declared field tokens."""
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise ValueError(f"Invalid repository path: {value!r}")
    parts = value.rstrip("/").split("/")
    if any(part in {"", ".", ".."} for part in parts) or PurePosixPath(value).is_absolute():
        raise ValueError(f"Path escapes repository or is not canonical: {value}")
    remaining = value
    if tokens:
        remaining = remaining.replace("{domain}", "domain").replace("{platform}", "platform")
    if "{" in remaining or "}" in remaining or any(c in remaining for c in '<>"|?*'):
        raise ValueError(f"Unsupported path token or character: {value}")
    return value


def destination_path(record, domain, platform=None):
    """Expand declared tokens only; no generic formatting or template execution."""
    if not isinstance(domain, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", domain):
        raise ValueError("Invalid domain")
    destination = validate_path(record["destination"], tokens=True).replace("{domain}", domain)
    if "{platform}" in destination:
        if (
            record["condition"] != "platforms"
            or not isinstance(platform, str)
            or not re.fullmatch(r"[a-z][a-z0-9_]*", platform)
        ):
            raise ValueError("A validated selected platform is required")
        destination = destination.replace("{platform}", platform)
    return validate_path(destination)


def load_contract(path=None):
    data = json.loads(
        (Path(path) if path else CENTRAL / "templates/integration/contract.json").read_text(
            encoding="utf-8"
        )
    )
    if type(data.get("schema_version")) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported contract schema version")
    if set(data) != {
        "schema_version",
        "encoding",
        "newline",
        "tokens",
        "records",
        "preserved",
        "notes",
    }:
        raise ValueError("Unsupported or missing contract fields")
    if data["encoding"] != "utf-8" or set(data["tokens"]) != {"domain", "platform"}:
        raise ValueError("Unsupported encoding or path tokens")
    if not isinstance(data["newline"], str) or not data["newline"]:
        raise ValueError("Missing newline policy")
    for field in ("preserved", "notes"):
        values = data[field]
        if (
            not isinstance(values, list)
            or not values
            or any(not isinstance(x, str) or not x for x in values)
            or len(values) != len(set(values))
        ):
            raise ValueError(f"Invalid {field}")
    allowed_inputs = set(load_schema("input")["properties"]) - {"schema_version"}
    rules = set()
    for document in (CENTRAL / "docs").glob("*.md"):
        rules.update(
            re.findall(r"\*\*([A-Z]+-\d+) (?:필수|권장)\*\*", document.read_text(encoding="utf-8"))
        )
    seen_ids, seen_paths = set(), set()
    if not isinstance(data["records"], list) or not data["records"]:
        raise ValueError("Contract records must be a nonempty list")
    fields = {
        "id",
        "source",
        "destination",
        "ownership",
        "condition",
        "required_inputs",
        "markers",
        "extension",
        "rules",
        "status",
    }
    for record in data["records"]:
        if not isinstance(record, dict) or set(record) != fields:
            raise ValueError("Invalid contract record fields")
        if not isinstance(record["id"], str) or not record["id"] or record["id"] in seen_ids:
            raise ValueError("Duplicate or invalid contract id")
        seen_ids.add(record["id"])
        destination = validate_path(record["destination"], tokens=True)
        # Windows and case-insensitive filesystems must not alias two writes.
        normalized = destination.rstrip("/").casefold()
        if normalized in seen_paths:
            raise ValueError(f"Duplicate destination: {destination}")
        seen_paths.add(normalized)
        if not isinstance(record["ownership"], str) or record["ownership"] not in OWNERSHIP:
            raise ValueError(f"Unsupported ownership: {record['ownership']}")
        if not isinstance(record["condition"], str) or record["condition"] not in CONDITIONS:
            raise ValueError(f"Unsupported condition: {record['condition']}")
        if "{platform}" in destination and record["condition"] != "platforms":
            raise ValueError("Platform path requires the platforms condition")
        for field in ("required_inputs", "markers", "rules"):
            values = record[field]
            if (
                not isinstance(values, list)
                or any(not isinstance(x, str) or not x for x in values)
                or len(values) != len(set(values))
            ):
                raise ValueError(f"Invalid or duplicate {field}")
        if not set(record["required_inputs"]) <= allowed_inputs:
            raise ValueError("Unknown required input")
        if not record["rules"] or not set(record["rules"]) <= rules:
            raise ValueError("Unknown or missing rule ID")
        if record["extension"] is not None and not isinstance(record["extension"], str):
            raise ValueError("Invalid extension description")
        if not isinstance(record["status"], str) or record["status"] not in {
            "available",
            "pending",
        }:
            raise ValueError("Unsupported asset status")
        if record["ownership"] == "managed_blocks" and not record["markers"]:
            raise ValueError("Managed blocks require explicit markers")
        if any(not re.fullmatch(r"[a-z][a-z0-9-]*", marker) for marker in record["markers"]):
            raise ValueError("Invalid managed marker name")
        source = record["source"]
        if source is None:
            if record["status"] != "pending":
                raise ValueError("Missing source must remain pending")
        else:
            validate_path(source)
            target = CENTRAL / source
            if not target.resolve().is_relative_to(CENTRAL.resolve()) or not target.is_file():
                raise ValueError(f"Missing or escaping contract source: {source}")
            if record["markers"]:
                from .readme import block

                text = target.read_text(encoding="utf-8")
                for marker in record["markers"]:
                    block(text, marker)
            if record["status"] != "available":
                raise ValueError("Existing source must be explicitly available")
    return data


def render_settings(data):
    """Render confirmed settings for a new file; callers must merge existing ones."""
    validate_input(data)
    readme = dict(data["readme"]["value"])
    license_data = data["license"]["value"]
    readme.update(license_name=license_data["name"], license_notices=license_data["notices"])
    result = {
        "repository": data["repository"]["value"],
        "default_branch": data["default_branch"]["value"],
        "readmes": ["README.md", "README.ko.md"],
        "tests_workflow": "tests.yml",
        "validate_workflow": "validate.yml",
        "readme": readme,
    }
    if "payload" in data:
        result["payload"] = {"examples": data["payload"]["value"]["examples"]}
    return result

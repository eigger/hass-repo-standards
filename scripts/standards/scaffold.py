"""Render explicit, unfinished HA authoring assets without executing templates."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from . import contract

ASSETS = {
    "component-__init__.py": "init.py.tmpl",
    "component-manifest.json": "manifest.json.tmpl",
    "component-const.py": "const.py.tmpl",
    "component-strings.json": "translations.json.tmpl",
    "component-translations-en.json": "translations.json.tmpl",
    "component-translations-ko.json": "translations.json.tmpl",
    "component-config_flow.py": "config_flow.py.tmpl",
    "component-{platform}.py": "platform.py.tmpl",
    "component-coordinator.py": "coordinator.py.tmpl",
    "component-entity.py": "entity.py.tmpl",
    "component-diagnostics.py": "diagnostics.py.tmpl",
    "component-services.yaml": "services.yaml.tmpl",
    "test-test_init.py": "test_init.py.tmpl",
    "test-test_config_flow.py": "test_config_flow.py.tmpl",
    "test-test_{platform}.py": "test_platform.py.tmpl",
    "test-test_coordinator.py": "test_coordinator.py.tmpl",
    "test-test_diagnostics.py": "test_diagnostics.py.tmpl",
    "metadata-hacs.json": "hacs.json.tmpl",
}
TOKENS = {
    "domain_literal",
    "domain_import",
    "platforms_literal",
    "manifest_json",
    "hacs_json",
    "translations_json",
}


def handles(record):
    """Whether this renderer owns a declared authoring asset."""
    return record.get("id") in ASSETS


def translations(data, language):
    """Create the same explicit unfinished UI keys in both distributed languages."""
    if data["configuration"]["value"] != "ui":
        return {}
    text = (
        "TODO: Implement the actual configuration flow."
        if language == "en"
        else "TODO: 실제 설정 흐름을 구현하세요."
    )
    return {
        "config": {
            "step": {"user": {"title": data["manifest"]["value"]["name"], "description": text}}
        }
    }


def validate_translations(english, korean):
    """Reject missing keys/placeholders and unresolved Core translation references."""

    def flatten(value, prefix=()):
        if not isinstance(value, dict):
            raise ValueError("Translations must contain objects or string leaves")
        result = {prefix: ("object", None)}
        for key, item in value.items():
            path = (*prefix, key)
            if isinstance(item, dict):
                result.update(flatten(item, path))
            elif isinstance(item, str):
                if "[%key:" in item:
                    raise ValueError("Unresolved Core translation reference")
                result[path] = ("string", set(re.findall(r"\{([^{}]+)\}", item)))
            else:
                raise ValueError("Translation leaves must be strings")
        return result

    if flatten(english) != flatten(korean):
        raise ValueError("Translation keys or placeholders differ")


def render(record, destination, validated_input, *, central):
    """Return content and honest pending tasks; never write the target."""
    if not handles(record):
        raise ValueError("Unsupported scaffold record")
    contract.validate_input(validated_input)
    data = validated_input
    domain = data["domain"]["value"]
    expected = record["destination"].replace("{domain}", domain)
    if "{platform}" in expected:
        if destination not in [
            expected.replace("{platform}", p) for p in data["platforms"]["value"]
        ]:
            raise ValueError("Scaffold destination is not a selected platform")
    elif expected != destination:
        raise ValueError("Scaffold destination does not match its contract")
    relative = "templates/integration/scaffold/" + ASSETS[record["id"]]
    if record["source"] != relative:
        raise ValueError("Scaffold source does not match the central asset")
    root = Path(central).resolve()
    source = (root / relative).resolve()
    if not source.is_relative_to(root):
        raise ValueError("Escaping scaffold source")
    template = source.read_text(encoding="utf-8")
    english, korean = translations(data, "en"), translations(data, "ko")
    validate_translations(english, korean)
    manifest = data["manifest"]["value"]
    ordered_manifest = {
        key: manifest[key]
        for key in ("domain", "name", *sorted(set(manifest) - {"domain", "name"}))
    }
    encode = lambda value: json.dumps(value, ensure_ascii=False, indent=2)  # noqa: E731
    values = {
        "domain_literal": repr(domain),
        "domain_import": f"from custom_components.{domain}.const import DOMAIN",
        "platforms_literal": repr(data["platforms"]["value"]),
        "manifest_json": encode(ordered_manifest),
        "hacs_json": encode(
            {
                "name": manifest["name"],
                "homeassistant": data["environments"]["value"]["minimum"]["ha"],
            }
        ),
        "translations_json": encode(korean if destination.endswith("/ko.json") else english),
    }
    tokens = set(re.findall(r"@@([a-z_]+)@@", template))
    if tokens - TOKENS or "@@" in re.sub(r"@@[a-z_]+@@", "", template):
        raise ValueError("Unsupported scaffold token")
    # One regex substitution never reinterprets inserted user strings as tokens/code.
    content = re.sub(r"@@([a-z_]+)@@", lambda match: values[match[1]], template)
    if destination.endswith(".py"):
        ast.parse(content, filename=destination, feature_version=(3, 9))
    pending = []
    complete = {"component-manifest.json", "component-const.py", "metadata-hacs.json"}
    if record["id"] not in complete:
        pending.append(
            f"{destination}: TODO authoring scaffold; implement real device behavior and actual HA assertions; not validated"
        )
    if destination.endswith(".py") and record["id"] != "component-const.py":
        environments = data["environments"]["value"]
        pending.append(
            f"{destination}: Verify actual HA APIs in exact minimum "
            f"{environments['minimum']['ha']}/Python {environments['minimum']['python']} "
            f"and current {environments['current']['ha']}/Python {environments['current']['python']}; "
            "Python 3.9 grammar parsing is not runtime compatibility evidence"
        )
    return content, pending

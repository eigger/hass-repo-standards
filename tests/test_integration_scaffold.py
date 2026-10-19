"""Validate generated authoring assets without claiming device/HA validation."""

from __future__ import annotations

import ast
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from standards import conditions, contract, scaffold  # noqa: E402
from test_standards_contract import input_fixture  # noqa: E402


class IntegrationScaffold(unittest.TestCase):
    def setUp(self):
        self.data = input_fixture()
        self.records = contract.load_contract()["records"]

    def render(self, record, data=None):
        data = data or self.data
        destination = record["destination"].replace("{domain}", data["domain"]["value"])
        destination = destination.replace("{platform}", data["platforms"]["value"][0])
        return scaffold.render(record, destination, data, central=ROOT)

    def record(self, name):
        return next(r for r in self.records if r["id"] == name)

    def test_selected_assets_parse_and_unfinished_ones_remain_pending(self):
        self.data["features"]["value"].update(
            coordinator=True, shared_entity=True, diagnostics=True, actions=True
        )
        rendered = {}
        for record in self.records:
            if not scaffold.handles(record) or not conditions.matches(
                record["condition"], self.data
            ):
                continue
            content, pending = self.render(record)
            path = record["destination"].replace("{platform}", "sensor")
            self.assertIsNotNone(content)
            self.assertNotIn("@@", content)
            if path.endswith(".py"):
                ast.parse(content, feature_version=(3, 9))
            elif path.endswith(".json"):
                json.loads(content)
            elif path.endswith(".yaml"):
                self.assertEqual(yaml.safe_load(content), {})
            rendered[record["id"]] = content
            if record["id"] not in {
                "component-manifest.json",
                "component-const.py",
                "metadata-hacs.json",
            }:
                self.assertTrue(pending)
        self.assertEqual(
            rendered["component-strings.json"], rendered["component-translations-en.json"]
        )
        scaffold.validate_translations(
            json.loads(rendered["component-translations-en.json"]),
            json.loads(rendered["component-translations-ko.json"]),
        )
        self.assertIn("raise NotImplementedError", rendered["component-__init__.py"])
        self.assertIn("async_forward_entry_setups", rendered["component-__init__.py"])
        self.assertIn("async_unload_platforms", rendered["component-__init__.py"])
        self.assertNotIn("runtime_data", rendered["component-__init__.py"])
        self.assertIn("hass.config_entries.async_setup", rendered["test-test_init.py"])
        self.assertIn("ConfigEntryState.LOADED", rendered["test-test_init.py"])
        for key, content in rendered.items():
            if key.startswith("test-"):
                tree = ast.parse(content, feature_version=(3, 9))
                self.assertTrue(
                    any(
                        isinstance(node, ast.ImportFrom)
                        and node.module == "custom_components.example.const"
                        and any(alias.name == "DOMAIN" for alias in node.names)
                        for node in ast.walk(tree)
                    )
                )
                self.assertIn("raise NotImplementedError", content)
                self.assertNotIn("pytest.skip", content)
                self.assertNotIn("sys.modules", content)

    def test_disabled_features_do_not_select_assets(self):
        for name in (
            "component-coordinator.py",
            "component-entity.py",
            "component-diagnostics.py",
            "component-services.yaml",
        ):
            self.assertFalse(conditions.matches(self.record(name)["condition"], self.data))
        self.data["configuration"]["value"] = "yaml"
        self.data["manifest"]["value"]["config_flow"] = False
        self.data["platforms"]["value"] = []
        self.assertFalse(conditions.matches("ui", self.data))
        self.assertFalse(conditions.matches("platforms", self.data))
        self.assertEqual(scaffold.translations(self.data, "en"), {})

    def test_custom_components_package_marker_reuses_empty_source(self):
        record = self.record("custom-components-package-init")
        self.assertEqual(record["destination"], "custom_components/__init__.py")
        self.assertEqual(record["ownership"], "create_only")
        self.assertEqual(record["source"], "templates/integration/tests/__init__.py")
        self.assertEqual((ROOT / record["source"]).read_bytes(), b"")
        self.assertFalse(scaffold.handles(record))

    def test_confirmed_manifest_and_support_minimum_are_preserved(self):
        manifest = self.data["manifest"]["value"]
        manifest["requirements"] = ['imagespec[datamatrix]>=1.0.1; python_version >= "3.9"']
        manifest["iot_class"] = "local_push"
        self.data["environments"]["value"]["minimum"]["ha"] = "2025.3.0"
        output, pending = self.render(self.record("component-manifest.json"))
        self.assertEqual(json.loads(output), manifest)
        self.assertEqual(list(json.loads(output))[:2], ["domain", "name"])
        self.assertFalse(pending)
        hacs, pending = self.render(self.record("metadata-hacs.json"))
        self.assertEqual(json.loads(hacs)["homeassistant"], "2025.3.0")
        self.assertFalse(pending)

    def test_render_is_pure_and_deterministic(self):
        original = copy.deepcopy(self.data)
        record = self.record("component-config_flow.py")
        self.assertEqual(self.render(record), self.render(record))
        self.assertEqual(self.data, original)

    def test_translation_keys_placeholders_and_core_references_rejected(self):
        for english, korean in [
            ({"a": "Name"}, {"b": "이름"}),
            ({"a.b": "Name"}, {"a": {"b": "이름"}}),
            ({}, {"a": {}}),
            ({"a": "{name}"}, {"a": "이름"}),
            ({"a": "[%key:common::config_flow::abort::already_configured%]"}, {"a": "이름"}),
            ({"a": 1}, {"a": "이름"}),
        ]:
            with self.subTest(english=english), self.assertRaises(ValueError):
                scaffold.validate_translations(english, korean)
        scaffold.validate_translations({"a": "Hello {name}"}, {"a": "안녕 {name}"})

    def test_unknown_tokens_and_path_substitutions_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "templates/integration/scaffold"
            source.mkdir(parents=True)
            (source / "const.py.tmpl").write_text("@@unknown@@", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "token"):
                scaffold.render(
                    self.record("component-const.py"),
                    "custom_components/example/const.py",
                    self.data,
                    central=directory,
                )
        with self.assertRaisesRegex(ValueError, "destination"):
            scaffold.render(
                self.record("component-{platform}.py"),
                "custom_components/example/switch.py",
                self.data,
                central=ROOT,
            )
        record = copy.deepcopy(self.record("component-const.py"))
        record["source"] = "../outside"
        with self.assertRaisesRegex(ValueError, "source"):
            self.render(record)
        invalid = copy.deepcopy(self.data)
        invalid["domain"]["value"] = "example; import os"
        with self.assertRaises(ValueError):
            self.render(self.record("test-test_init.py"), invalid)

    def test_inserted_user_strings_are_json_data_not_executable_templates(self):
        self.data["manifest"]["value"]["name"] = 'Quotes " and @@domain_literal@@ and {name}'
        content, pending = self.render(self.record("component-manifest.json"))
        self.assertEqual(json.loads(content)["name"], self.data["manifest"]["value"]["name"])
        translated, pending = self.render(self.record("component-translations-en.json"))
        self.assertEqual(
            json.loads(translated)["config"]["step"]["user"]["title"],
            self.data["manifest"]["value"]["name"],
        )


if __name__ == "__main__":
    unittest.main()

"""Actual HA/plugin/imagespec runtime checks, in a separately installed environment."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AVAILABLE = all(
    importlib.util.find_spec(package) is not None
    for package in ("homeassistant", "pytest_homeassistant_custom_component", "imagespec")
)


@unittest.skipUnless(
    AVAILABLE, "Requires the real compatible HA/plugin/imagespec runtime environment"
)
class PayloadRuntime(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copytree(ROOT / "tests/fixtures/payload_integration", self.root, dirs_exist_ok=True)
        (self.root / "custom_components/payload_sample/manifest.json").write_text(
            json.dumps(
                {
                    "domain": "payload_sample",
                    "name": "Offline payload fixture",
                    "version": "0.0.0",
                    "requirements": ["imagespec==" + version("imagespec")],
                    "codeowners": [],
                    "integration_type": "device",
                    "iot_class": "local_push",
                }
            )
        )
        (self.root / "custom_components/__init__.py").touch()
        shutil.copyfile(
            ROOT / "templates/integration/tests/components/example/test_payload_examples.py",
            self.root / "tests/components/payload_sample/test_payload_examples.py",
        )
        (self.root / "examples/payload").mkdir(parents=True)
        (self.root / "examples/payload/minimal.yaml").write_text(
            'action: payload_sample.draw\ntarget:\n  entity_id: sensor.payload_sample\ndata:\n  width: "32"\n  height: 16\n  payload:\n    - type: text\n      x: 0\n      y: 0\n      value: "{{ states(\'sensor.payload_sample\') }}"\n      size: 8\n      color: black\n'
        )
        self.entry = {
            "path": "examples/payload/minimal.yaml",
            "payload_path": ["data", "payload"],
            "expected_size": [32, 16],
            "expected_palette": ["#000000", "#ffffff"],
        }
        (self.root / "pytest.ini").write_text(
            "[pytest]\nasyncio_mode = auto\nasyncio_default_fixture_loop_scope = function\n"
        )
        self.config = {"payload": {"examples": [self.entry]}}
        self.save()

    def save(self):
        (self.root / ".hass-standards.json").write_text(json.dumps(self.config))

    def run_contract(
        self,
        expected_success=True,
        arguments=(),
        plugin=True,
        target="tests/components/payload_sample/test_payload_examples.py",
    ):

        env = {
            **os.environ,
            "PYTHONPATH": str(self.root) + (os.pathsep + str(ROOT / "scripts") if plugin else ""),
            "PAYLOAD_REPOSITORY": str(self.root),
            "PAYLOAD_DOMAIN": "payload_sample",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        }
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "pytest_asyncio.plugin",
            "-p",
            "pytest_homeassistant_custom_component.plugins",
            *(["-p", "hass_standards_payload"] if plugin else []),
            target,
            "-q",
            *arguments,
        ]
        result = subprocess.run(
            command, cwd=self.root, env=env, text=True, capture_output=True, timeout=90
        )
        if expected_success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_real_schema_template_render_and_no_device_send(self):
        output = self.run_contract()
        self.assertIn("1 passed", output)
        self.assertNotIn("test_payload_contract_requires_plugin", output)

    def test_actual_yaml_string_schema_and_host_preparation(self):
        import yaml

        path = self.root / "examples/payload/minimal.yaml"
        action = yaml.safe_load(path.read_text())
        action["action"] = "payload_sample.draw_yaml"
        action["data"]["payload"] = yaml.safe_dump(action["data"]["payload"], default_style='"')
        path.write_text(yaml.safe_dump(action))
        self.entry["payload_format"] = "yaml"
        self.save()
        self.assertIn("1 passed", self.run_contract())

    def test_schema_dimensions_palette_and_deselection_fail(self):
        path = self.root / "examples/payload/minimal.yaml"
        original = path.read_text()
        path.write_text(original.replace('  width: "32"', "  width: invalid"))
        self.assertIn("width", self.run_contract(False))
        path.write_text(original)
        self.entry["expected_size"] = [33, 16]
        self.save()
        self.assertIn("Rendered dimensions differ", self.run_contract(False))
        self.entry["expected_size"] = [32, 16]
        self.entry["expected_palette"] = ["#ff0000"]
        self.save()
        self.assertIn("Output contains colors outside", self.run_contract(False))
        self.entry["expected_palette"] = ["#000000", "#ffffff"]
        self.save()
        self.assertIn(
            "required 1 executed examples, got 0", self.run_contract(False, ("-k", "never_matches"))
        )

    def test_plain_scaffold_fails_and_post_contract_regressions_run(self):
        self.assertIn("plain pytest run cannot validate", self.run_contract(False, plugin=False))
        self.run_contract()
        regression = self.root / "tests/components/payload_sample/test_existing.py"
        regression.write_text(
            'import pytest\n\n@pytest.mark.asyncio\nasync def test_actual_ha_regression(hass):\n    hass.states.async_set("sensor.existing", "ready")\n    assert hass.states.get("sensor.existing").state == "ready"\n'
        )
        output = self.run_contract(
            True,
            ("--ignore=tests/components/payload_sample/test_payload_examples.py",),
            plugin=False,
            target="tests/components/payload_sample/",
        )
        self.assertIn("1 passed", output)

    def test_marker_inactive_regression_needs_no_tool_or_imagespec_import(self):
        # Block the optional library import rather than providing any fake API.
        # HA and its plugin remain the actual installed runtime throughout.
        (self.root / "sitecustomize.py").write_text(
            'import sys\nclass BlockImagespec:\n    def find_spec(self, fullname, path=None, target=None):\n        if fullname == "imagespec" or fullname.startswith("imagespec."):\n            raise ModuleNotFoundError("imagespec is unavailable in this marker-inactive environment")\nsys.meta_path.insert(0, BlockImagespec())\n'
        )
        (self.root / "tests/components/payload_sample/test_existing.py").write_text(
            'def test_actual_ha_without_optional_library(hass):\n    import importlib.util\n    assert importlib.util.find_spec("hass_standards_payload") is None\n    hass.states.async_set("sensor.existing", "ready")\n    assert hass.states.get("sensor.existing").state == "ready"\n'
        )
        output = self.run_contract(
            True,
            ("--ignore=tests/components/payload_sample/test_payload_examples.py",),
            plugin=False,
            target="tests/components/payload_sample/",
        )
        self.assertIn("1 passed", output)

    def test_skipped_setup_is_not_completion(self):
        path = self.root / "tests/components/payload_sample/conftest.py"
        path.write_text(
            path.read_text().replace(
                "    hass.config.config_dir",
                '    pytest.skip("deliberate contract skip")\n    hass.config.config_dir',
            )
        )
        self.assertIn("required 1 executed examples, got 0", self.run_contract(False))


if __name__ == "__main__":
    unittest.main()

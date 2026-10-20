"""T4 structural validation fixtures; these are not actual HA adoption evidence."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import test_integration_contract as fixtures  # noqa: E402
from standards import contract as asset_contract  # noqa: E402
from standards import scaffold  # noqa: E402
from test_standards_contract import input_fixture  # noqa: E402

checker = fixtures.contract


class ScaffoldValidation(unittest.TestCase):
    setUp = fixtures.IntegrationContract.setUp
    save_config = fixtures.IntegrationContract.save_config

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def errors(self):
        return checker.check(self.root)

    def enable_ui(self):
        self.manifest["config_flow"] = True
        self.write("custom_components/example/manifest.json", json.dumps(self.manifest))
        self.write(
            "custom_components/example/const.py", 'DOMAIN = "example"\nPLATFORMS = ["sensor"]\n'
        )
        self.write(
            "custom_components/example/__init__.py",
            """from .const import DOMAIN, PLATFORMS
async def async_setup_entry(hass, entry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
""",
        )
        self.write(
            "custom_components/example/config_flow.py",
            """from homeassistant import config_entries
from .const import DOMAIN
class DeviceFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        return self.async_show_form(step_id="user")
""",
        )
        self.write(
            "custom_components/example/sensor.py",
            """from homeassistant.components.sensor import SensorEntity
class DeviceSensor(SensorEntity):
    _attr_translation_key = "power"
async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DeviceSensor()])
""",
        )
        self.write(
            "tests/components/example/test_config_flow.py",
            """async def test_flow(hass):
    result = await hass.config_entries.flow.async_init("example", context={"source": "user"})
    assert result["type"] is not None
""",
        )
        self.write(
            "tests/components/example/test_sensor.py",
            """async def test_sensor(hass):
    assert hass.states.get("sensor.fixture") is not None
""",
        )
        self.translations = {
            "config": {"step": {"user": {"title": "Device"}}},
            "entity": {"sensor": {"power": {"name": "Power {value}"}}},
        }
        self.save_translations()

    def save_translations(self, english=None, korean=None):
        source = english if english is not None else self.translations
        for name, data in (
            ("strings.json", source),
            ("translations/en.json", source),
            ("translations/ko.json", korean if korean is not None else source),
        ):
            self.write("custom_components/example/" + name, json.dumps(data))

    def test_normal_custom_implementation_is_accepted_without_template_byte_identity(self):
        self.enable_ui()
        self.assertEqual(self.errors(), [])
        path = self.root / "custom_components/example/sensor.py"
        original = path.read_bytes()
        path.write_bytes(
            original
            + b"\n# TODO: Add a future optional optimization.\nclass AbstractHelper:\n    def operation(self):\n        raise NotImplementedError('subclasses provide this capability')\n"
        )
        self.assertEqual(self.errors(), [])
        self.assertTrue(path.read_bytes().startswith(original))

    def test_required_files_and_corresponding_tests_fail_at_their_actual_paths(self):
        self.enable_ui()
        for name in (
            "custom_components/__init__.py",
            "custom_components/example/__init__.py",
            "custom_components/example/config_flow.py",
            "custom_components/example/sensor.py",
            "custom_components/example/strings.json",
            "custom_components/example/translations/en.json",
            "custom_components/example/translations/ko.json",
            "tests/components/example/test_config_flow.py",
            "tests/components/example/test_sensor.py",
            "tests/components/example/test_init.py",
        ):
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.unlink()
                try:
                    self.assertTrue(any(name in error for error in self.errors()))
                finally:
                    path.write_bytes(original)

    def test_selected_coordinator_and_diagnostics_require_their_own_tests(self):
        self.enable_ui()
        for module in ("coordinator", "diagnostics"):
            self.write(
                f"custom_components/example/{module}.py",
                f'"""Actual {module} implementation in a static checker fixture."""\n',
            )
            missing = f"tests/components/example/test_{module}.py"
            self.assertTrue(any(missing in error for error in self.errors()))
            self.write(missing, "def test_behavior():\n    assert 1 == 1\n")
        self.assertEqual(self.errors(), [])

    def test_domain_constant_and_config_flow_declaration_must_agree(self):
        self.enable_ui()
        self.write(
            "custom_components/example/const.py", 'DOMAIN = "different"\nPLATFORMS = ["sensor"]\n'
        )
        self.assertTrue(
            any("HA-01 custom_components/example/const.py" in error for error in self.errors())
        )
        self.manifest["config_flow"] = False
        self.write("custom_components/example/manifest.json", json.dumps(self.manifest))
        self.assertTrue(
            any("HA-04 custom_components/example/manifest.json" in error for error in self.errors())
        )

    def test_english_source_sync_korean_keys_placeholders_and_core_refs(self):
        self.enable_ui()
        for change in ("key", "placeholder", "core", "english"):
            with self.subTest(change=change):
                english = copy.deepcopy(self.translations)
                korean = copy.deepcopy(english)
                if change == "key":
                    del korean["entity"]["sensor"]["power"]
                elif change == "placeholder":
                    korean["entity"]["sensor"]["power"]["name"] = "Power {other}"
                elif change == "core":
                    korean["entity"]["sensor"]["power"]["name"] = "[%key:component::sensor::name%]"
                self.save_translations(english, korean)
                if change == "english":
                    self.write("custom_components/example/translations/en.json", "{}")
                self.assertTrue(any("HA-11" in error for error in self.errors()))
        self.save_translations()
        self.assertEqual(self.errors(), [])

    def test_missing_entry_platform_hooks_and_actual_action_metadata_fail(self):
        self.enable_ui()
        self.write("custom_components/example/__init__.py", "from .const import DOMAIN\n")
        self.assertTrue(
            any("HA-05" in error and "async_unload_entry" in error for error in self.errors())
        )
        self.enable_ui()
        self.write(
            "custom_components/example/sensor.py",
            "from homeassistant.components.sensor import SensorEntity\n",
        )
        self.assertTrue(any("Selected platform setup hook" in error for error in self.errors()))
        self.enable_ui()
        path = self.root / "custom_components/example/__init__.py"
        self.write(
            path.relative_to(self.root).as_posix(),
            path.read_bytes().decode()
            + '\ndef register(hass):\n    hass.services.async_register("example", "send", handler)\n',
        )
        self.assertTrue(
            any("HA-11 custom_components/example/services.yaml" in error for error in self.errors())
        )

    def test_registered_action_names_require_matching_metadata_and_translations(self):
        for registration in (
            'hass.services.async_register(DOMAIN, "send", handler)',
            'current.async_register_entity_service("send", {}, "send")',
        ):
            with self.subTest(registration=registration):
                self.enable_ui()
                path = self.root / "custom_components/example/__init__.py"
                original = path.read_text()
                self.write(
                    path.relative_to(self.root).as_posix(),
                    original
                    + "\nfrom homeassistant.helpers import entity_platform as ep\ndef register(hass):\n    current = ep.async_get_current_platform()\n    "
                    + registration
                    + "\n",
                )
                self.write("custom_components/example/services.yaml", "other: {}\n")
                self.translations["services"] = {"other": {"name": "Other"}}
                self.save_translations()
                errors = self.errors()
                self.assertTrue(
                    any("Registered action 'send' is missing metadata" in error for error in errors)
                )
                self.assertTrue(any("services.send" in error for error in errors))
                self.write("custom_components/example/services.yaml", "send: {}\n")
                self.translations["services"] = {"send": {"name": "Send"}}
                self.save_translations()
                self.assertEqual(self.errors(), [])
        self.enable_ui()
        path = self.root / "custom_components/example/__init__.py"
        self.write(
            path.relative_to(self.root).as_posix(),
            path.read_text()
            + '\ndef unrelated(hass, device):\n    hass.services.async_call(DOMAIN, "send", {})\n    device.async_register_entity_service("send", {}, "send")\n    device.services.async_register(DOMAIN, "send", handler)\n',
        )
        (self.root / "custom_components/example/services.yaml").unlink()
        self.assertEqual(self.errors(), [])

    def test_actual_config_entity_and_service_translation_keys_are_checked(self):
        self.enable_ui()
        del self.translations["config"]["step"]["user"]
        self.save_translations()
        self.assertTrue(any("config.step.user" in error for error in self.errors()))
        self.enable_ui()
        del self.translations["entity"]["sensor"]["power"]
        self.save_translations()
        self.assertTrue(any("entity.sensor.power" in error for error in self.errors()))
        self.enable_ui()
        self.write(
            "custom_components/example/services.yaml",
            "send:\n  description: Send a device command.\n",
        )
        self.assertTrue(any("services.send" in error for error in self.errors()))
        self.translations["services"] = {"send": {"name": "Send"}}
        self.save_translations()
        self.assertEqual(self.errors(), [])
        self.write("custom_components/example/services.yaml", "{}\n")
        self.assertTrue(any("unfinished or empty" in error for error in self.errors()))

    def test_options_flow_translation_namespace_is_distinct_from_config(self):
        self.enable_ui()
        path = self.root / "custom_components/example/config_flow.py"
        content = path.read_bytes().decode()
        self.write(
            path.relative_to(self.root).as_posix(),
            content
            + """\nclass DeviceOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_abort(reason="no_change")
        return self.async_show_form(step_id="init")
""",
        )
        self.translations["options"] = {
            "step": {"init": {"title": "Options"}},
            "abort": {"no_change": "No change"},
        }
        self.save_translations()
        self.assertEqual(self.errors(), [])
        del self.translations["options"]["abort"]["no_change"]
        self.save_translations()
        self.assertTrue(any("options.abort.no_change" in error for error in self.errors()))

    def enable_subentries(self, registration=None):
        self.enable_ui()
        self.write(
            "custom_components/example/const.py",
            'DOMAIN = "example"\nPLATFORMS = ["sensor"]\nSTATION = "station"\n',
        )
        path = self.root / "custom_components/example/config_flow.py"
        content = path.read_text().replace(
            "class DeviceFlow(config_entries.ConfigFlow, domain=DOMAIN):",
            "class DeviceFlow(config_entries.ConfigFlow, domain=DOMAIN):\n"
            "    @classmethod\n"
            "    def async_get_supported_subentry_types(cls, config_entry):\n"
            "        return "
            + (registration or '{STATION: StationFlow, "vehicle": VehicleFlow}')
            + "\n",
        )
        self.write(
            path.relative_to(self.root).as_posix(),
            content
            + """
from .const import STATION
from homeassistant.config_entries import ConfigSubentryFlow as SubentryHandler
class StationFlow(SubentryHandler):
    async def async_step_user(self, user_input=None):
        if user_input:
            return self.async_abort(reason="already_exists")
        return self.async_show_form(step_id="user")
class VehicleFlow(config_entries.ConfigSubentryFlow):
    async def async_step_select(self, user_input=None):
        return self.async_show_form(step_id="select")
""",
        )
        self.translations["config_subentries"] = {
            "station": {
                "step": {"user": {"title": "Station"}},
                "abort": {"already_exists": "Already exists"},
            },
            "vehicle": {"step": {"select": {"title": "Vehicle"}}},
        }
        self.save_translations()

    def test_subentry_types_use_their_registered_translation_namespaces(self):
        self.enable_subentries()
        self.assertEqual(self.errors(), [])
        for subentry_type, section, key in (
            ("station", "step", "user"),
            ("station", "abort", "already_exists"),
            ("vehicle", "step", "select"),
        ):
            with self.subTest(subentry_type=subentry_type, section=section):
                self.enable_subentries()
                del self.translations["config_subentries"][subentry_type][section][key]
                self.save_translations()
                self.assertTrue(
                    any(
                        f"config_subentries.{subentry_type}.{section}.{key}" in error
                        for error in self.errors()
                    )
                )

    def test_subentry_module_aliases_and_shared_handler_check_every_type(self):
        self.enable_subentries('{STATION: StationFlow, "vehicle": StationFlow}')
        path = self.root / "custom_components/example/config_flow.py"
        content = (
            path.read_text()
            .replace(
                "from homeassistant.config_entries import ConfigSubentryFlow as SubentryHandler",
                "import homeassistant.config_entries as entries",
            )
            .replace(
                "class StationFlow(SubentryHandler):",
                "class StationFlow(entries.ConfigSubentryFlow):",
            )
        )
        # The unused class is deliberately removed; an unregistered handler is unresolved.
        content = content.split("class VehicleFlow", 1)[0]
        self.write(path.relative_to(self.root).as_posix(), content)
        self.translations["config_subentries"]["vehicle"] = copy.deepcopy(
            self.translations["config_subentries"]["station"]
        )
        self.save_translations()
        self.assertEqual(self.errors(), [])
        del self.translations["config_subentries"]["vehicle"]["abort"]["already_exists"]
        self.save_translations()
        self.assertTrue(
            any(
                "config_subentries.vehicle.abort.already_exists" in error for error in self.errors()
            )
        )

    def test_unresolved_subentry_registration_fails_instead_of_using_config(self):
        for registration in (
            "dynamic_types()",
            "{UNKNOWN: StationFlow}",
            '{"station": UnknownFlow}',
        ):
            with self.subTest(registration=registration):
                self.enable_subentries(registration)
                errors = self.errors()
                self.assertTrue(any("Unresolved subentry" in error for error in errors))
                self.assertFalse(any("config.step.select" in error for error in errors))

    def test_only_central_scaffold_sentinels_fail_not_every_todo_or_abstract_method(self):
        self.enable_ui()
        data = input_fixture()
        record = next(
            record
            for record in asset_contract.load_contract()["records"]
            if record["id"] == "component-__init__.py"
        )
        text, pending = scaffold.render(
            record, "custom_components/example/__init__.py", data, central=ROOT
        )
        self.assertTrue(pending)
        self.write("custom_components/example/__init__.py", text)
        self.assertTrue(any("Central authoring scaffold" in error for error in self.errors()))
        self.enable_ui()
        record = next(
            record
            for record in asset_contract.load_contract()["records"]
            if record["id"] == "test-test_init.py"
        )
        text, _ = scaffold.render(
            record, "tests/components/example/test_init.py", data, central=ROOT
        )
        self.write("tests/components/example/test_init.py", text)
        self.assertTrue(
            any("TEST-07 tests/components/example/test_init.py" in error for error in self.errors())
        )
        self.enable_ui()
        self.translations["config"]["step"]["user"]["title"] = (
            "TODO: Implement the actual configuration flow."
        )
        self.save_translations()
        self.assertTrue(any("translation authoring scaffold" in error for error in self.errors()))

    def test_entirely_empty_return_skipped_or_xfailed_required_tests_cannot_pass(self):
        self.enable_ui()
        invalid = (
            "def test_loading():\n    pass\n",
            "def test_loading():\n    return True\n",
            'import pytest\ndef test_loading():\n    pytest.skip("not implemented")\n',
            'import pytest\ndef test_loading():\n    pytest.xfail("not implemented")\n',
            "import pytest\n@pytest.mark.xfail\ndef test_loading():\n    assert True\n",
            "import pytest\npytestmark = pytest.mark.skip\ndef test_loading():\n    assert True\n",
            'import pytest\n@pytest.mark.skip(reason="not implemented")\ndef test_loading():\n    assert True\n',
            "import pytest\n@pytest.mark.skip\nclass TestLoading:\n    def test_entry(self):\n        assert True\n",
        )
        invalid += (
            'import pytest\npytest.skip("unsupported", allow_module_level=True)\ndef test_loading():\n    assert True\n',
            'import unittest\n@unittest.skip("unsupported")\nclass Loading(unittest.TestCase):\n    def test_loading(self):\n        self.assertTrue(True)\n',
            'import unittest\n@unittest.skipIf(True, "unsupported")\nclass Loading(unittest.TestCase):\n    def test_loading(self):\n        self.assertTrue(True)\n',
            'import unittest\n@unittest.skipUnless(False, "unsupported")\nclass Loading(unittest.TestCase):\n    def test_loading(self):\n        self.assertTrue(True)\n',
        )
        for text in invalid:
            with self.subTest(text=text):
                self.write("tests/components/example/test_init.py", text)
                self.assertTrue(
                    any(
                        "TEST-07 tests/components/example/test_init.py" in error
                        for error in self.errors()
                    )
                )
        self.write(
            "tests/components/example/test_init.py",
            'import pytest\n@pytest.mark.skip(reason="unsupported subcase")\ndef test_optional():\n    assert True\nasync def test_actual_loading(hass):\n    assert hass is not None\n',
        )
        self.assertEqual(self.errors(), [])
        self.write(
            "tests/components/example/test_init.py",
            'import pytest\n@pytest.mark.xfail(False, reason="conditional case remains active")\ndef test_loading():\n    assert True\n',
        )
        self.assertEqual(self.errors(), [])

    def test_conditional_or_partial_unittest_skip_retains_active_cases(self):
        self.enable_ui()
        for marker in (
            'skipIf(False, "active")',
            'skipUnless(True, "active")',
            'skipIf(UNKNOWN, "runtime condition")',
        ):
            with self.subTest(marker=marker):
                self.write(
                    "tests/components/example/test_init.py",
                    "import unittest\n@unittest."
                    + marker
                    + "\nclass Loading(unittest.TestCase):\n    def test_loading(self):\n        self.assertTrue(True)\n",
                )
                self.assertEqual(self.errors(), [])
        self.write(
            "tests/components/example/test_init.py",
            'import unittest\n@unittest.skip("unsupported")\nclass Optional(unittest.TestCase):\n    def test_optional(self):\n        self.assertTrue(True)\nclass Loading(unittest.TestCase):\n    def test_loading(self):\n        self.assertTrue(True)\n',
        )
        self.assertEqual(self.errors(), [])

    def test_workflow_action_and_standards_ref_must_share_visible_reviewed_sha(self):
        self.enable_ui()
        tests = self.root / ".github/workflows/tests.yml"
        original = tests.read_bytes()
        self.write(
            tests.relative_to(self.root).as_posix(),
            original.decode().replace("standards-ref: " + "a" * 40, "standards-ref: " + "b" * 40),
        )
        self.assertTrue(
            any("GOV-02" in error and "standards-ref" in error for error in self.errors())
        )
        tests.write_bytes(original)
        self.write("STANDARDS.md", "<!--\n- 참조 커밋 SHA: " + "a" * 40 + "\n-->\n")
        self.assertTrue(any("GOV-02 STANDARDS.md" in error for error in self.errors()))
        self.write("STANDARDS.md", "```markdown\n- 참조 커밋 SHA: " + "a" * 40 + "\n```\n")
        self.assertTrue(any("GOV-02 STANDARDS.md" in error for error in self.errors()))
        self.write("STANDARDS.md", "- 참조 커밋 SHA: " + "a" * 40 + "\n")
        self.assertEqual(self.errors(), [])

    def test_exact_approved_exception_still_applies_without_hiding_other_paths(self):
        self.enable_ui()
        self.write(
            "custom_components/example/const.py", 'DOMAIN = "other"\nPLATFORMS = ["sensor"]\n'
        )
        self.config["exceptions"] = [
            {
                "id": "EX-DOMAIN",
                "rule": "HA-01",
                "paths": ["custom_components/example/const.py"],
                "reason": "Static checker unit evidence only",
                "approved_by": "unit fixture owner",
                "approved_at": "2026-10-19",
                "evidence": "STANDARDS.md#ex-domain",
            }
        ]
        self.save_config()
        self.write(
            "STANDARDS.md",
            "- 참조 커밋 SHA: " + "a" * 40 + "\n## EX-DOMAIN\nChecker fixture evidence.\n",
        )
        before = (self.root / "custom_components/example/const.py").read_bytes()
        self.assertEqual(self.errors(), [])
        self.assertEqual((self.root / "custom_components/example/const.py").read_bytes(), before)
        (self.root / "tests/components/example/test_sensor.py").unlink()
        self.assertTrue(
            any(
                "TEST-08 tests/components/example/test_sensor.py" in error
                for error in self.errors()
            )
        )

    def test_helper_import_is_not_guessed_as_a_platform_and_platform_enums_work(self):
        self.enable_ui()
        self.write(
            "custom_components/example/helper.py",
            "from homeassistant.components.helper import Helper\n",
        )
        self.write(
            "custom_components/example/const.py",
            'from homeassistant.const import Platform\nDOMAIN = "example"\nPLATFORMS = [Platform.SENSOR]\n',
        )
        self.assertEqual(self.errors(), [])
        self.write(
            "custom_components/example/const.py",
            'DOMAIN = "example"\nPLATFORMS = UNKNOWN_EXTERNAL_LIST\n',
        )
        self.assertTrue(
            any("Cannot statically verify PLATFORMS" in error for error in self.errors())
        )


if __name__ == "__main__":
    unittest.main()

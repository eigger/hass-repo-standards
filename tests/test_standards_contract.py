"""Contract validation, feature conditions and shared-renderer regression tests."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import bluetooth_documents  # noqa: E402
import check_integration  # noqa: E402
import payload_documents  # noqa: E402
import sync_badges  # noqa: E402
from standards import badges, conditions, contract, readme  # noqa: E402


def input_fixture():
    def sourced(value):
        return {"value": value, "source": "explicit unit-test input (not device evidence)"}

    environment = {
        "ha": "2026.10.2",
        "python": "3.14",
        "pytest_homeassistant_custom_component": "0.13.373",
        "requirements": ["requirements_test.txt"],
        "constraints": [],
    }
    return {
        "schema_version": 1,
        "repository": sourced("owner/example"),
        "default_branch": sourced("trunk"),
        "domain": sourced("example"),
        "manifest": sourced(
            {
                "domain": "example",
                "name": "Example",
                "version": "1.0.0",
                "documentation": "https://github.com/owner/example",
                "issue_tracker": "https://github.com/owner/example/issues",
                "codeowners": ["@owner"],
                "requirements": [],
                "dependencies": [],
                "after_dependencies": [],
                "config_flow": True,
            }
        ),
        "readme": sourced(
            {
                "title": "Example",
                "descriptions": {"en": "An integration.", "ko": "통합입니다."},
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
                "coordinator": False,
                "shared_entity": False,
                "diagnostics": False,
                "actions": False,
                "fixtures": False,
                "snapshots": False,
                "dependency_updates": False,
            }
        ),
        "environments": sourced(
            {
                "minimum": copy.deepcopy(environment),
                "current": copy.deepcopy(environment),
                "libraries": {},
            }
        ),
    }


class StandardsContract(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.data = input_fixture()
        self.contract = contract.load_contract()

    def load_modified(self, mutate):
        data = copy.deepcopy(self.contract)
        mutate(data)
        path = self.root / "contract.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return contract.load_contract(path)

    def test_assets_include_component_test_and_conditional_paths(self):
        records = {record["destination"]: record for record in self.contract["records"]}
        for destination in (
            "custom_components/{domain}/__init__.py",
            "custom_components/{domain}/manifest.json",
            "custom_components/{domain}/translations/en.json",
            "custom_components/{domain}/translations/ko.json",
            "custom_components/{domain}/{platform}.py",
            "tests/components/{domain}/test_{platform}.py",
            "tests/components/{domain}/test_init.py",
            "tests/components/{domain}/fixtures/",
            "tests/components/{domain}/snapshots/",
            "docs/troubleshooting.ko.md",
            "docs/payload.md",
        ):
            self.assertIn(destination, records)
        self.assertEqual(records["custom_components/{domain}/__init__.py"]["status"], "pending")
        self.assertIsNone(records["custom_components/{domain}/__init__.py"]["source"])
        self.assertNotIn("AGENTS.md", records)
        self.assertNotIn("LICENSE", records)

    def test_managed_contract_markers_and_metadata_are_validated(self):
        record = next(r for r in self.contract["records"] if r["id"] == "domain-conftest")
        self.assertEqual(record["markers"], ["domain-fixtures"])
        index = self.contract["records"].index(record)
        for markers in ([], ["missing-marker"], ["../invalid"]):
            with self.subTest(markers=markers), self.assertRaises(ValueError):
                self.load_modified(lambda data: data["records"][index].update(markers=markers))
        for field, value in (("newline", None), ("preserved", "LICENSE"), ("notes", [])):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.load_modified(lambda data: data.update({field: value}))

    def test_numeric_validation_follows_json_schema_equality(self):
        data = copy.deepcopy(self.data)
        data["schema_version"] = 1.0
        self.assertEqual(contract.validate_input(data), data)
        for schema in ({"type": "integer"}, {"const": 1}, {"enum": [1]}):
            self.assertEqual(contract.validate_schema(1.0, schema), 1.0)
            with self.assertRaises(ValueError):
                contract.validate_schema(True, schema)
        with self.assertRaises(ValueError):
            contract.validate_schema(1.5, {"type": "integer"})
        with self.assertRaisesRegex(ValueError, "below minimum"):
            contract.validate_schema(0.0, {"type": "integer", "minimum": 1})
        payload_schema = contract.load_schema("input")["properties"]["payload"]["properties"][
            "value"
        ]["properties"]["examples"]["items"]["properties"]["expected_size"]
        with self.assertRaisesRegex(ValueError, "below minimum"):
            contract.validate_schema([0.0, 16], payload_schema)

    def test_unknown_contract_versions_fail(self):
        for version in (0, 2, "1", True, None):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "version"):
                self.load_modified(lambda data: data.update(schema_version=version))

    def test_duplicate_ids_and_destinations_fail(self):
        for field in ("id", "destination"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "[Dd]uplicate"):
                self.load_modified(
                    lambda data: data["records"][1].update({field: data["records"][0][field]})
                )
        with self.assertRaisesRegex(ValueError, "Duplicate destination"):
            self.load_modified(
                lambda data: data["records"][1].update(destination="TESTS/__INIT__.PY")
            )

    def test_unknown_condition_ownership_rule_and_input_fail(self):
        for field, value in (
            ("condition", "invented"),
            ("ownership", "overwrite"),
            ("rules", ["HA-999"]),
            ("required_inputs", ["guess"]),
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.load_modified(lambda data: data["records"][0].update({field: value}))

    def test_contract_destination_and_source_escape_fail(self):
        for value in (
            "../outside",
            "/absolute",
            "C:/absolute",
            "tests/../outside",
            "a\\b",
            "a/{untrusted}.py",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.load_modified(lambda data: data["records"][0].update(destination=value))
        with self.assertRaises(ValueError):
            self.load_modified(lambda data: data["records"][0].update(source="../outside"))
        with self.assertRaises(ValueError):
            self.load_modified(
                lambda data: data["records"][0].update(source="templates/integration/missing.py")
            )

    def test_missing_source_cannot_claim_available(self):
        with self.assertRaisesRegex(ValueError, "pending"):
            self.load_modified(lambda data: data["records"][0].update(source=None))

    def test_valid_input_keeps_exact_environments_and_requirement_text(self):
        self.data["environments"]["value"]["minimum"]["ha"] = "2025.1.0"
        self.data["manifest"]["value"]["requirements"] = [
            'imagespec[extra]>=1.2; python_version < "2"'
        ]
        before = copy.deepcopy(self.data)
        self.assertIs(contract.validate_input(self.data), self.data)
        self.assertEqual(self.data, before)

    def test_schema_and_input_validation_agree_for_valid_and_invalid_cases(self):
        schema = contract.load_schema("input")
        invalid = []
        for key in ("domain", "environments", "manifest", "license"):
            data = copy.deepcopy(self.data)
            del data[key]
            invalid.append(data)
        for version in (True, 2, "1"):
            data = copy.deepcopy(self.data)
            data["schema_version"] = version
            invalid.append(data)
        for key, value in (
            ("platforms", ["sensor", "sensor"]),
            ("domain", "../escape"),
            ("configuration", "guessed"),
        ):
            data = copy.deepcopy(self.data)
            data[key]["value"] = value
            invalid.append(data)
        data = copy.deepcopy(self.data)
        data["repository"]["source"] = ""
        invalid.append(data)
        data = copy.deepcopy(self.data)
        data["environments"]["value"]["minimum"]["requirements"] = ["../escape"]
        invalid.append(data)
        data = copy.deepcopy(self.data)
        data["invented"] = 1
        invalid.append(data)
        self.assertEqual(contract.validate_schema(self.data, schema), self.data)
        for index, data in enumerate(invalid):
            with self.subTest(case=index):
                for validate in (
                    contract.validate_input,
                    lambda data: contract.validate_schema(data, schema),
                ):
                    with self.assertRaises(ValueError):
                        validate(data)

    def test_optional_remote_preserves_https_and_ssh_with_provenance(self):
        for remote in ("https://github.com/owner/example.git", "git@github.com:owner/example.git"):
            with self.subTest(remote=remote):
                data = copy.deepcopy(self.data)
                data["remote"] = {"value": remote, "source": "git remote get-url origin"}
                self.assertEqual(contract.validate_input(data)["remote"]["value"], remote)
        for field in ("value", "source"):
            for value in ("", "   ", None):
                with self.subTest(field=field, value=value):
                    data = copy.deepcopy(self.data)
                    data["remote"] = {
                        "value": "git@github.com:owner/example.git",
                        "source": "explicit input",
                    }
                    data["remote"][field] = value
                    for validate in (
                        contract.validate_input,
                        lambda data: contract.validate_schema(data, contract.load_schema("input")),
                    ):
                        with self.assertRaises(ValueError):
                            validate(data)

    def test_record_required_input_failure(self):
        with self.assertRaisesRegex(ValueError, "payload"):
            contract.validate_input(self.data, ["payload"])

    def test_inventory_and_plan_schemas_are_versioned_and_reject_unknown_keys(self):
        for kind in ("inventory", "plan"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                contract.validate_document({"schema_version": 2}, kind)
        with self.assertRaises(ValueError):
            contract.load_schema("invented")
        with self.assertRaisesRegex(ValueError, "unsupported schema keywords"):
            contract.validate_schema(1, {"unsupported": True})

    def test_conditions_for_four_library_combinations_and_markers(self):
        for packages in ([], ["imagespec"], ["blesession"], ["imagespec", "blesession"]):
            with self.subTest(packages=packages):
                self.data["manifest"]["value"]["requirements"] = [
                    f'{name}[extra]>=1.2; python_version < "2"' for name in packages
                ]
                for name in ("imagespec", "blesession"):
                    self.assertEqual(conditions.matches(name, self.data), name in packages)
        self.assertTrue(conditions.matches("ui", self.data))
        self.assertTrue(conditions.matches("platforms", self.data))
        self.assertFalse(conditions.matches("diagnostics", self.data))
        with self.assertRaisesRegex(ValueError, "Unsupported condition"):
            conditions.matches("guess", self.data)

    def test_absolute_import_detection_is_shared_with_both_checkers(self):
        component = self.root / "custom_components/example"
        component.mkdir(parents=True)
        manifest_path = component / "manifest.json"
        manifest_path.write_text("{}")
        code = component / "__init__.py"
        manifest = self.data["manifest"]["value"]
        for text, expected in (
            ("# import imagespec\nfrom .imagespec import local\n", False),
            ("from imagespec.render import render\n", True),
        ):
            code.write_text(text)
            for detector in (
                conditions.uses_package,
                bluetooth_documents.uses_package,
                payload_documents.uses_package,
            ):
                self.assertEqual(
                    detector(self.root, manifest_path, manifest, readme.safe_path, "imagespec"),
                    expected,
                )
            self.assertEqual(
                conditions.matches(
                    "imagespec", self.data, self.root, manifest_path, readme.safe_path
                ),
                expected,
            )
        code.write_text("def bad(:\n")
        with self.assertRaises(SyntaxError):
            conditions.uses_package(
                self.root, manifest_path, manifest, readme.safe_path, "imagespec"
            )
        manifest["requirements"] = ["not a requirement ??"]
        with self.assertRaises(ValueError):
            conditions.matches("imagespec", self.data)

    def test_destination_expands_only_domain_and_selected_platform(self):
        record = {
            "destination": "custom_components/{domain}/{platform}.py",
            "condition": "platforms",
        }
        self.assertEqual(
            contract.destination_path(record, "example", "sensor"),
            "custom_components/example/sensor.py",
        )
        for domain, platform in (
            ("../other", "sensor"),
            ("example", "../sensor"),
            ("example", None),
        ):
            with self.subTest(domain=domain, platform=platform), self.assertRaises(ValueError):
                contract.destination_path(record, domain, platform)
        record["condition"] = "always"
        with self.assertRaises(ValueError):
            contract.destination_path(record, "example", "sensor")

    def prepare_rendering(self):
        component = self.root / "custom_components/example"
        component.mkdir(parents=True)
        (component / "manifest.json").write_text(json.dumps(self.data["manifest"]["value"]))
        (self.root / "hacs.json").write_text('{"homeassistant":"2026.10.2"}')
        (self.root / "LICENSE").write_text("MIT")
        return contract.render_settings(self.data)

    def test_checker_and_generation_share_identical_managed_area_bytes(self):
        settings = self.prepare_rendering()
        for language, name in (("en", "README.md"), ("ko", "README.ko.md")):
            original = ""
            for area in readme.AREAS:
                content = f"{badges.START}\n{badges.END}\n" if area == "header" else ""
                start, end = readme.markers(area)
                original += f"{start}\n{content}{end}\n\n"
                if area == "header":
                    original += "## Body\r\n\r\nPreserve  bytes.\r\n"
            generated = readme.render_readme(self.root, settings, language, original)
            checked = check_integration.render_readme(self.root, settings, language, original)
            self.assertEqual(generated.encode(), checked.encode())
            self.assertIn("Preserve  bytes.\r\n", generated)
            self.assertIn("query=%24.example.total", generated)
            self.assertEqual(
                badges.render(self.root, settings, self.root / name),
                sync_badges.render(self.root, settings, self.root / name),
            )
            self.assertEqual(
                readme.render_readme(self.root, settings, language, generated), generated
            )

    def test_managed_boundaries_and_prose_protection_remain_strict(self):
        with self.assertRaisesRegex(ValueError, "marker"):
            readme.block("unmarked prose", "header")
        with self.assertRaisesRegex(ValueError, "Preserve existing"):
            readme.guard_content("Copyright original author", "## License", "license")
        with self.assertRaisesRegex(ValueError, "non-badge"):
            badges.preserve_extra_badges(badges.START + "\nkeep prose\n" + badges.END, "")

    def test_settings_are_new_confirmed_values_without_fake_payload_or_evidence(self):
        settings = contract.render_settings(self.data)
        self.assertEqual(settings["default_branch"], "trunk")
        self.assertNotIn("payload", settings)
        self.assertNotIn("exceptions", settings)
        self.assertNotIn("environments", settings)
        self.assertEqual(settings["readme"]["license_name"], "MIT License")


if __name__ == "__main__":
    unittest.main()

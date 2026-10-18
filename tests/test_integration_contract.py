"""Regression checks for central integration contract enforcement."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location(
    "integration_contract", ROOT / "scripts/check_integration.py"
)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class IntegrationContract(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        component = self.root / "custom_components/example"
        component.mkdir(parents=True)
        (component / "manifest.json").write_text('{"domain":"example","requirements":[]}')
        (self.root / "hacs.json").write_text('{"homeassistant":"2026.1.0"}')
        (self.root / "LICENSE").write_text("MIT")
        shutil.copytree(ROOT / "templates/integration/tests", self.root / "tests")
        (self.root / "tests/components/example/test_init.py").write_text(
            '"""Fixture lifecycle test placeholder in checker unit fixture only."""\n'
        )
        shutil.copytree(ROOT / "templates/integration/.github", self.root / ".github")
        for file in (self.root / ".github/workflows").glob("*.yml"):
            file.write_text(file.read_text().replace("@main", "@" + "a" * 40))
        self.config = {
            "repository": "owner/example",
            "default_branch": "main",
            "readmes": ["README.md", "README.ko.md"],
            "release": True,
            "readme": {
                "title": "Example",
                "descriptions": {"en": "An integration.", "ko": "통합입니다."},
                "issues": True,
                "discussions": True,
                "license_name": "MIT License",
                "related_projects": [],
            },
        }
        self.save_config()
        for language, name in zip(("en", "ko"), self.config["readmes"]):
            header = "\n".join(
                [
                    contract.BADGES_START,
                    "[![Special](https://example.com/badge)](https://example.com)",
                    contract.BADGES_END,
                ]
            )
            original = ""
            for area in contract.AREAS:
                start, end = contract.markers(area)
                original += f"{start}\n{header if area == 'header' else ''}\n{end}\n\n"
                if area == "header":
                    original += "## Existing section\n\nKeep  exact spaces.\r\n\n"
            (self.root / name).write_bytes(
                contract.render_readme(self.root, self.config, language, original).encode()
            )

    def save_config(self):
        (self.root / ".hass-standards.json").write_text(json.dumps(self.config))

    def test_valid_fixture_and_badge_order(self):
        self.assertEqual(contract.check(self.root), [])
        text = (self.root / "README.md").read_text()
        self.assertLess(text.index("[![Release]"), text.index("[![HACS Custom]"))
        self.assertLess(text.index("label=Usage"), text.index("[![Special]"))
        self.assertNotIn("flat-square", text)

    def test_write_preserves_outside_bytes_and_unique_badges(self):
        path = self.root / "README.md"
        original = path.read_bytes()
        self.config["readme"]["title"] = "Updated"
        self.save_config()
        self.assertTrue(contract.check(self.root))
        self.assertEqual(contract.check(self.root, write_readmes=True), [])
        updated = path.read_bytes()
        self.assertEqual(updated, original.replace(b"# Example", b"# Updated"))
        self.assertIn(b"Keep  exact spaces.\r\n", updated)

    def test_both_languages_preflight_before_writing(self):
        path = self.root / "README.md"
        original = path.read_bytes()
        self.config["readme"]["title"] = "Updated"
        self.save_config()
        (self.root / "README.ko.md").write_text("Missing markers")
        self.assertTrue(contract.check(self.root, write_readmes=True))
        self.assertEqual(path.read_bytes(), original)

    def test_reordered_overlapping_duplicate_or_orphan_markers_fail(self):
        path = self.root / "README.md"
        original = path.read_text()
        start, end = contract.markers("support")
        for broken in [
            original + start,
            original.replace(start, end),
            original.replace(end, start),
            original.replace(start, ""),
        ]:
            with self.subTest(broken=broken[-100:]):
                path.write_text(broken)
                self.assertTrue(contract.check(self.root))

    def test_root_conftest_and_init_cannot_drift(self):
        (self.root / "tests/conftest.py").write_text("# customized\n")
        (self.root / "tests/__init__.py").write_text("# not empty\n")
        errors = contract.check(self.root)
        self.assertTrue(any("exactly" in error for error in errors))
        self.assertTrue(any("empty" in error for error in errors))

    def test_pr_narrowing_and_schedule_removal_fail(self):
        path = self.root / ".github/workflows/validate.yml"
        original = path.read_text()
        for replacement in [
            original.replace("pull_request: null", "pull_request: {branches: [main]}"),
            original.replace("  schedule:\n  - cron: 23 3 * * 1\n", ""),
        ]:
            path.write_text(replacement)
            self.assertTrue(any("CI-02" in e for e in contract.check(self.root)))

    def test_unpinned_central_workflows_and_action_fail(self):
        path = self.root / ".github/workflows/validate.yml"
        path.write_text(path.read_text().replace("@" + "a" * 40, "@main"))
        self.assertTrue(any("pinned" in e for e in contract.check(self.root)))

    def test_symlink_write_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as external:
            destination = Path(external) / "README.md"
            destination.write_text("Outside content")
            path = self.root / "README.md"
            path.unlink()
            path.symlink_to(destination)
            self.assertTrue(contract.check(self.root, write_readmes=True))
            self.assertEqual(destination.read_text(), "Outside content")

    def test_unknown_managed_prose_is_not_erased(self):
        path = self.root / "README.md"
        original = path.read_text().replace("## Support", "## Support\n\nImportant support notice.")
        path.write_text(original)
        self.assertTrue(contract.check(self.root, write_readmes=True))
        self.assertEqual(path.read_text(), original)

    def test_license_notices_must_be_preserved(self):
        path = self.root / "README.md"
        original = path.read_text().replace(
            "## License", "## License\n\nCopyright original contributor."
        )
        path.write_text(original)
        self.assertTrue(contract.check(self.root, write_readmes=True))
        self.assertEqual(path.read_text(), original)
        self.config["readme"]["license_notices"] = {"en": ["Copyright original contributor."]}
        self.save_config()
        self.assertEqual(contract.check(self.root, write_readmes=True), [])

    def test_status_badges_cannot_be_disabled_and_license_required(self):
        self.config["tests_workflow"] = ""
        self.save_config()
        self.assertTrue(contract.check(self.root))
        self.config.pop("tests_workflow")
        self.save_config()
        (self.root / "LICENSE").unlink()
        self.assertTrue(contract.check(self.root))

    def test_common_checks_cannot_be_skipped_or_suppressed(self):
        path = self.root / ".github/workflows/validate.yml"
        original = path.read_text()
        for field in ("if: false", "continue-on-error: true", "needs: skipped"):
            with self.subTest(field=field):
                path.write_text(original.replace("  standards:\n", f"  standards:\n    {field}\n"))
                self.assertTrue(any("CI-04" in e for e in contract.check(self.root)))
        path.write_text(
            original.replace(
                "    - uses: actions/checkout@", "    - if: false\n      uses: actions/checkout@"
            )
        )
        self.assertTrue(any("CI-03" in e for e in contract.check(self.root)))

    def test_template_license_exemption_is_narrow(self):
        from check_repository import is_destination_license_placeholder

        self.assertTrue(
            is_destination_license_placeholder(ROOT / "templates/integration/README.md", "LICENSE")
        )
        self.assertFalse(is_destination_license_placeholder(ROOT / "README.md", "LICENSE"))
        self.assertFalse(
            is_destination_license_placeholder(
                ROOT / "templates/integration/README.md", "MISSING.md"
            )
        )

    def test_english_exception_cannot_hide_korean_failure(self):
        (self.root / "README.ko.md").write_text("Missing Korean markers")
        item = {
            "id": "EX-EN",
            "rule": "DOC-01",
            "paths": ["README.md"],
            "reason": "English layout exception",
            "approved_by": "repository owner",
            "approved_at": "2026-10-18",
            "evidence": "STANDARDS.md#ex-en",
        }
        self.config["exceptions"] = [item]
        self.save_config()
        (self.root / "STANDARDS.md").write_text("## EX-EN\nUser approval recorded here.")
        errors = contract.check(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("README.ko.md", errors[0])
        # Both broken languages must be collected; an English exception cannot
        # stop preflight before the Korean failure is examined.
        (self.root / "README.md").write_text("Missing English markers")
        errors = contract.check(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("README.ko.md", errors[0])

    def test_exceptions_require_evidence_and_apply_only_exact_scope(self):
        errors = [
            ("TEST-08", "tests/__init__.py", "not empty"),
            ("TEST-08", "tests/components/__init__.py", "not empty"),
        ]
        item = {
            "id": "EX-001",
            "rule": "TEST-08",
            "paths": ["tests/__init__.py"],
            "reason": "Documented requirement",
            "approved_by": "repository owner",
            "approved_at": "2026-10-18",
            "evidence": "STANDARDS.md#ex-001",
        }
        self.config["exceptions"] = [item]
        with self.assertRaises(ValueError):
            contract.apply_exceptions(self.root, self.config, errors)
        (self.root / "STANDARDS.md").write_text("## EX-001\nUser approval recorded here.")
        remaining = contract.apply_exceptions(self.root, self.config, errors)
        self.assertEqual(len(remaining), 1)
        self.assertIn("components", remaining[0])
        item["paths"] = ["tests/*"]
        with self.assertRaises(ValueError):
            contract.apply_exceptions(self.root, self.config, errors)


if __name__ == "__main__":
    unittest.main()

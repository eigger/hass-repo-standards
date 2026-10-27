"""Regression checks for central integration contract enforcement."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

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
        self.manifest = {
            "domain": "example",
            "name": "Example",
            "version": "1.0.0",
            "documentation": "https://github.com/owner/example",
            "issue_tracker": "https://github.com/owner/example/issues",
            "categories": ["diy_makers"],
            "codeowners": ["@owner"],
            "requirements": [],
        }
        (component / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (component.parent / "__init__.py").write_bytes(b"")
        (component / "__init__.py").write_text('DOMAIN = "example"\n', encoding="utf-8")
        (component / "translations").mkdir()
        for name in ("strings.json", "translations/en.json", "translations/ko.json"):
            (component / name).write_text("{}", encoding="utf-8")
        (self.root / "STANDARDS.md").write_text(
            "- 참조 커밋 SHA: " + "a" * 40 + "\n", encoding="utf-8"
        )
        (self.root / "ADOPTION_CHECKLIST.md").write_text(
            "Checker unit fixture; actual HA execution is not established here.\n", encoding="utf-8"
        )
        (self.root / "hacs.json").write_text('{"homeassistant":"2026.1.0"}')
        (self.root / "LICENSE").write_text("MIT")
        shutil.copytree(ROOT / "templates/integration/tests", self.root / "tests")
        (self.root / "tests/components/example/test_init.py").write_text(
            '"""Static checker fixture; not actual HA validation evidence."""\n'
            "async def test_lifecycle(hass, mock_config_entry):\n"
            "    mock_config_entry.add_to_hass(hass)\n"
            "    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)\n"
            "    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)\n"
        )
        shutil.copytree(ROOT / "templates/integration/.github", self.root / ".github")
        for file in (self.root / ".github/workflows").glob("*.yml"):
            file.write_text(
                file.read_text()
                .replace("@main", "@" + "a" * 40)
                .replace("standards-ref: main", "standards-ref: " + "a" * 40)
            )
        self.config = {
            "repository": "owner/example",
            "default_branch": "main",
            "readmes": ["README.md", "README.ko.md"],
            "release": True,
            "categories_review": {
                "value": ["diy_makers"],
                "integration_type": None,
                "source": "Synthetic tool fixture decision, not device evidence.",
            },
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

    def test_categories_and_recorded_review_are_required_without_automatic_defaults(self):
        path = self.root / "custom_components/example/manifest.json"
        original_manifest = path.read_bytes()
        for review in (
            None,
            {**self.config["categories_review"], "source": "TODO"},
            {**self.config["categories_review"], "value": ["pets"]},
            {**self.config["categories_review"], "integration_type": "device"},
        ):
            config = {**self.config, "categories_review": review}
            (self.root / ".hass-standards.json").write_text(json.dumps(config))
            errors = contract.check(self.root)
            self.assertTrue(
                any("HA-02" in error and "categories_review" in error for error in errors)
            )
            self.assertEqual(path.read_bytes(), original_manifest)
        self.save_config()
        manifest = dict(self.manifest)
        del manifest["categories"]
        path.write_text(json.dumps(manifest))
        self.assertTrue(
            any("HA-02" in error and "categories" in error for error in contract.check(self.root))
        )

    def test_installation_links_use_real_repository_for_both_hacs_modes(self):
        (self.root / "hacs.json").write_text(
            '{"zip_release":true,"filename":"example.zip"}', encoding="utf-8"
        )
        for status in ("custom", "default"):
            self.config["hacs"] = status
            self.config["hacs_default_evidence"] = "https://github.com/hacs/default — 2026-10-20"
            self.save_config()
            self.assertEqual(contract.check(self.root, write_readmes=True), [])
            for name in self.config["readmes"]:
                text = (self.root / name).read_text()
                install = contract.block(text, "installation")
                params = parse_qs(
                    urlsplit(install.split("]](", 1)[-1].split(")](", 1)[-1][:-1]).query
                )
                self.assertEqual(params["owner"], ["owner"])
                self.assertEqual(params["repository"], ["example"])
                self.assertEqual(
                    params.get("category"), ["integration"] if status == "custom" else None
                )
                self.assertEqual(text.count("<!-- hass-standards:installation:start -->"), 1)

    def test_installation_insertion_preserves_existing_heading_and_prose(self):
        for language, name, heading in (
            ("en", "README.md", "## Installation"),
            ("ko", "README.ko.md", "## 설치"),
        ):
            path = self.root / name
            text = path.read_bytes().decode()
            start, end = contract.markers("installation")
            before, rest = text.split(start)
            _, after = rest.split(end)
            text = before + after
            body = "\nKeep original steps.\r\n\n```yaml\nexample: original\n```\n"
            text = text.replace(heading, heading + body)
            path.write_bytes(text.encode())
            self.assertEqual(contract.check(self.root, write_readmes=True), [])
            updated = path.read_bytes().decode()
            self.assertEqual(updated.count(heading), 1)
            self.assertIn(body, updated)
            self.assertIn("Keep  exact spaces.\r\n", updated)
            self.assertEqual(contract.check(self.root), [])

    def test_configured_installation_anchors_preserve_existing_custom_headings(self):
        self.config["installation_links"] = {
            "README.md": "#installation-with-hacs",
            "README.ko.md": "#설치-hacs",
        }
        self.save_config()
        for name, old, new in (
            ("README.md", "## Installation", "## Installation with HACS"),
            ("README.ko.md", "## 설치", "## 설치 HACS"),
        ):
            path = self.root / name
            text = path.read_text().replace(old, new)
            start, end = contract.markers("installation")
            before, rest = text.split(start)
            _, after = rest.split(end)
            path.write_text(before + "Existing installation instructions.\n" + after)
        self.assertEqual(contract.check(self.root, write_readmes=True), [])
        for name in self.config["readmes"]:
            text = (self.root / name).read_text()
            self.assertEqual(text.count("hass-standards:installation:start"), 1)
            self.assertIn("Existing installation instructions.", text)
        self.assertEqual(contract.check(self.root), [])

    def test_fenced_installation_examples_are_preserved_outside_badge_section(self):
        for fence in ("```", "~~~~"):
            path = self.root / "README.md"
            original = path.read_text()
            start, end = contract.markers("installation")
            before, rest = original.split(start)
            _, after = rest.split(end)
            original = (before + after).replace("## Installation\n", "")
            sample = f"## Documentation\n{fence}markdown\n## Installation\nexample text\n{fence}\n"
            path.write_text(
                original.replace("## Existing section", sample + "\n## Existing section")
            )
            self.assertEqual(contract.check(self.root, write_readmes=True), [])
            updated = path.read_text()
            self.assertIn(sample, updated)
            self.assertGreater(updated.index(start), updated.index(sample) + len(sample))
            self.assertEqual(contract.check(self.root), [])

    def test_missing_configured_installation_heading_fails_without_writing(self):
        self.config["installation_links"] = {"README.md": "#does-not-exist"}
        self.save_config()
        original = (self.root / "README.md").read_bytes()
        self.assertTrue(contract.check(self.root, write_readmes=True))
        self.assertEqual((self.root / "README.md").read_bytes(), original)

    def test_installation_block_refuses_to_erase_prose_and_rejects_duplicates(self):
        path = self.root / "README.md"
        text = path.read_text()
        for broken in (
            text.replace(
                "<!-- hass-standards:installation:end -->",
                "Keep this step.\n<!-- hass-standards:installation:end -->",
            ),
            text + "<!-- hass-standards:installation:start -->",
        ):
            path.write_text(broken)
            before = path.read_bytes()
            self.assertTrue(contract.check(self.root, write_readmes=True))
            self.assertEqual(path.read_bytes(), before)

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

    def test_current_job_follows_plugin_pin_when_minimum_job_exists(self):
        path = self.root / ".github/workflows/tests.yml"
        original = path.read_text()
        key = "      test-profile: ha\n"
        explicit = original.replace(key, "      expected-ha-version: '2026.10.2'\n" + key, 1)
        body = original.split("  current:\n", 1)[1]
        minimum = "  minimum-ha:\n" + body.replace(
            key, "      expected-ha-version: '2025.1.0'\n" + key, 1
        )

        def errors():
            return [e for e in contract.check(self.root) if "expected-ha-version" in e]

        path.write_text(explicit)  # a single shared job keeps its explicit minimum
        self.assertFalse(errors())
        path.write_text(original.rstrip("\n") + "\n" + minimum)
        self.assertFalse(errors())
        path.write_text(explicit.rstrip("\n") + "\n" + minimum)
        self.assertTrue(any("CI-07" in e for e in errors()))
        # Library-mode split with the same HA is not a separate minimum HA job.
        same = "  minimum:\n" + body.replace(
            key, "      expected-ha-version: '2026.10.2'\n" + key, 1
        )
        path.write_text(explicit.rstrip("\n") + "\n" + same)
        self.assertFalse(errors())

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
        path = self.root / ".github/workflows/standards.yml"
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

    def test_standards_layouts_enforce_the_same_existing_job_criteria(self):
        """A file/name move cannot bypass the existing action and job safeguards."""
        import copy

        import yaml

        workflows = self.root / ".github/workflows"
        validate_path = workflows / "validate.yml"
        standards_path = workflows / "standards.yml"
        validate = yaml.load(validate_path.read_text(), Loader=contract.Loader)
        standards = yaml.load(standards_path.read_text(), Loader=contract.Loader)
        original_job = standards["jobs"]["standards"]
        mutations = (
            ("missing job", "CI-01", lambda jobs: jobs.pop("standards")),
            (
                "unpinned action",
                "CI-01",
                lambda jobs: jobs["standards"]["steps"][-1].update(
                    uses="eigger/hass-repo-standards/actions/check-standards@main"
                ),
            ),
            ("job conditional", "CI-04", lambda jobs: jobs["standards"].update({"if": False})),
            ("job dependency", "CI-04", lambda jobs: jobs["standards"].update(needs="skipped")),
            (
                "job failure suppression",
                "CI-04",
                lambda jobs: jobs["standards"].update({"continue-on-error": True}),
            ),
            (
                "action conditional",
                "CI-04",
                lambda jobs: jobs["standards"]["steps"][-1].update({"if": False}),
            ),
            (
                "action failure suppression",
                "CI-04",
                lambda jobs: jobs["standards"]["steps"][-1].update({"continue-on-error": True}),
            ),
            (
                "checkout conditional",
                "CI-03",
                lambda jobs: jobs["standards"]["steps"][0].update({"if": False}),
            ),
            (
                "checkout failure suppression",
                "CI-03",
                lambda jobs: jobs["standards"]["steps"][0].update({"continue-on-error": True}),
            ),
            (
                "persisted credentials",
                "CI-03",
                lambda jobs: jobs["standards"]["steps"][0]["with"].update(
                    {"persist-credentials": True}
                ),
            ),
            ("missing timeout", "CI-03", lambda jobs: jobs["standards"].pop("timeout-minutes")),
        )
        for layout in ("split", "legacy inline"):
            with self.subTest(layout=layout):
                caller = copy.deepcopy(standards if layout == "split" else validate)
                caller["jobs"]["standards"] = copy.deepcopy(original_job)
                if layout == "legacy inline":
                    caller["jobs"]["standards"]["name"] = "Central template compliance"
                    standards_path.unlink(missing_ok=True)
                    path = validate_path
                else:
                    validate_path.write_text(yaml.safe_dump(validate, sort_keys=False))
                    path = standards_path
                original = copy.deepcopy(caller)
                path.write_text(yaml.safe_dump(original, sort_keys=False))
                self.assertEqual(contract.check(self.root), [])
                for label, expected_rule, mutate in mutations:
                    with self.subTest(layout=layout, change=label):
                        changed = copy.deepcopy(original)
                        mutate(changed["jobs"])
                        path.write_text(yaml.safe_dump(changed, sort_keys=False))
                        errors = contract.workflow_errors(self.root, self.config, "example")
                        self.assertTrue(any(rule == expected_rule for rule, _, _ in errors), errors)

    def test_inline_safeguards_still_apply_when_standards_is_split(self):
        import yaml

        workflows = self.root / ".github/workflows"
        standards = yaml.load((workflows / "standards.yml").read_text(), Loader=contract.Loader)
        validate_path = workflows / "validate.yml"
        validate = yaml.load(validate_path.read_text(), Loader=contract.Loader)
        validate["jobs"]["standards"] = standards["jobs"]["standards"]
        validate["jobs"]["standards"]["continue-on-error"] = True
        validate_path.write_text(yaml.safe_dump(validate, sort_keys=False))
        errors = contract.workflow_errors(self.root, self.config, "example")
        self.assertTrue(any(rule == "CI-04" for rule, _, _ in errors))

    def test_separate_standards_keeps_validate_event_contract(self):
        path = self.root / ".github/workflows/standards.yml"
        original = path.read_text()
        for changed in (
            original.replace("name: Standards", "name: Other", 1),
            original.replace("pull_request: null", "pull_request: {branches: [main]}"),
            original.replace("  schedule:\n  - cron: 23 3 * * 1\n", ""),
        ):
            with self.subTest(changed=changed):
                path.write_text(changed)
                errors = contract.workflow_errors(self.root, self.config, "example")
                self.assertTrue(any(rule == "CI-02" for rule, _, _ in errors))

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

    def make_payload_documents(self, requirement="imagespec>=1.0.1"):
        import re

        (self.root / "custom_components/example/manifest.json").write_text(
            json.dumps({**self.manifest, "requirements": [requirement]})
        )
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / "examples/payload").mkdir(parents=True, exist_ok=True)
        example = self.root / "examples/payload/minimal.yaml"
        example.write_text(
            """action: example.draw\ndata:\n  payload:\n    - type: text\n      x: 0\n      y: 0\n      value: "{{ states('sensor.actual') }}"\n      size: 8\n"""
        )
        self.config["payload"] = {
            "examples": [
                {
                    "path": "examples/payload/minimal.yaml",
                    "payload_path": ["data", "payload"],
                    "expected_size": [32, 16],
                    "expected_palette": ["#000000", "#ffffff"],
                }
            ]
        }
        self.save_config()
        for name, readme in (("payload.md", "README.md"), ("payload.ko.md", "README.ko.md")):
            text = (
                (ROOT / "templates/integration/docs" / name)
                .read_text()
                .replace("REPLACE_REPOSITORY", self.config["repository"])
            )
            text = re.sub(r"REPLACE_[A-Z_]+", "Actual device condition", text)
            (self.root / "docs" / name).write_text(text)
            path = self.root / readme
            path.write_text(
                path.read_text().replace(
                    contract.markers("support")[0],
                    f"[Payload](docs/{name})\n\n" + contract.markers("support")[0],
                )
            )
        for file in (self.root / ".github/workflows").glob("*.yml"):
            text = file.read_text().replace("standards-ref: main", "standards-ref: " + "a" * 40)
            if file.name == "tests.yml":
                text = text.replace(
                    "      domain: example",
                    """      dependency-modes: '["current", "minimum"]'\n      minimum-packages: '["imagespec"]'\n      domain: example""",
                )
            file.write_text(text)

    def test_payload_contract_structure_and_real_jinja_are_accepted(self):
        self.make_payload_documents()
        self.assertEqual(contract.check(self.root), [])

    def test_payload_missing_locale_placeholder_heading_link_and_unregistered_yaml(self):
        self.make_payload_documents()
        path = self.root / "docs/payload.ko.md"
        original = path.read_text()
        for broken in (
            "Missing Korean document structure",
            original + "\nREPLACE_DEVICE_DETAILS\n",
            original.replace("## 최소 동작 예제", "## 다른 절"),
            original.replace("../README.ko.md", "../README.md"),
            original.replace(
                "imagespec/blob/main/docs/payload.ko.md", "imagespec/blob/main/docs/payload.md"
            ),
            original + "\n[Other example](../examples/payload/untested.yaml)\n",
            original + "\n[Encoded example](../examples/payload/untested%2Eyaml)\n",
            "<pre>\n" + original + "\n</pre>",
        ):
            path.write_text(broken)
            self.assertTrue(
                any("DOC-08 docs/payload.ko.md" in error for error in contract.check(self.root))
            )
        path.unlink()
        self.assertTrue(
            any("DOC-08 docs/payload.ko.md" in error for error in contract.check(self.root))
        )

    def test_payload_sha_and_collective_minimum_coverage(self):
        self.make_payload_documents()
        path = self.root / ".github/workflows/tests.yml"
        original = path.read_text()
        path.write_text(
            original.replace("standards-ref: " + "a" * 40, "standards-ref: " + "b" * 40)
        )
        self.assertTrue(any("standards-ref" in error for error in contract.check(self.root)))
        path.write_text(original.replace('["current", "minimum"]', '["current"]'))
        self.assertTrue(any("exact minimum" in error for error in contract.check(self.root)))
        # Separate required jobs may collectively cover package modes.
        data = contract.yaml.load(original, Loader=contract.Loader)
        job = data["jobs"]["current"]
        job["with"]["dependency-modes"] = '["current"]'
        import copy

        minimum = copy.deepcopy(job)
        minimum["with"]["dependency-modes"] = '["minimum"]'
        data["jobs"]["minimum"] = minimum
        path.write_text(contract.yaml.safe_dump(data, sort_keys=False))
        self.assertEqual(contract.check(self.root), [])
        # An actual exact pin can reuse one current job.
        del data["jobs"]["minimum"]
        path.write_text(contract.yaml.safe_dump(data, sort_keys=False))
        (self.root / "custom_components/example/manifest.json").write_text(
            json.dumps({**self.manifest, "requirements": ["imagespec==1.0.1"]})
        )
        self.assertEqual(contract.check(self.root), [])

    def test_inactive_jobs_do_not_count_as_payload_version_coverage(self):
        self.make_payload_documents('imagespec>=1.0.1; python_version >= "3.14"')
        path = self.root / ".github/workflows/tests.yml"
        original = path.read_text()
        path.write_text(original.replace('["3.14"]', '["3.13"]'))
        self.assertTrue(any("exact minimum" in error for error in contract.check(self.root)))
        path.write_text(original)
        self.assertEqual(contract.check(self.root), [])

    def test_payload_scaffold_examples_and_paths_cannot_be_faked(self):
        self.make_payload_documents()
        path = self.root / "tests/components/example/test_payload_examples.py"
        path.write_text("def test_payload(): pass\n")
        self.assertTrue(
            any("central payload contract scaffold" in error for error in contract.check(self.root))
        )
        shutil.copyfile(
            ROOT / "templates/integration/tests/components/example/test_payload_examples.py", path
        )
        self.config["payload"]["examples"][0]["payload_path"] = ["data", "missing"]
        self.save_config()
        self.assertTrue(
            any("DOC-08 .hass-standards.json" in error for error in contract.check(self.root))
        )
        self.config["payload"]["examples"][0]["payload_path"] = ["data", "payload"]
        self.save_config()
        outside = self.root / "docs/payload.md"
        outside.unlink()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "payload.md"
            target.write_text("Outside")
            outside.symlink_to(target)
            self.assertTrue(
                any(
                    "DOC-08 docs/payload.md" in error and "escapes" in error
                    for error in contract.check(self.root)
                )
            )

    def make_bluetooth_documents(self, requirement="blesession[extra]>=0.9; python_version < '2'"):
        manifest = self.root / "custom_components/example/manifest.json"
        manifest.write_text(
            json.dumps({**self.manifest, "requirements": [requirement] if requirement else []})
        )
        (self.root / "docs").mkdir(exist_ok=True)
        for name, readme, other, suffix in (
            ("troubleshooting.md", "README.md", "troubleshooting.ko.md", ""),
            ("troubleshooting.ko.md", "README.ko.md", "troubleshooting.md", ".ko"),
        ):
            text = (ROOT / "templates/integration/docs" / name).read_text()
            text = text.replace("{{repository}}", self.config["repository"])
            import re

            text = re.sub(
                r"\{\{.*?\}\}",
                "N/A: this device has no pairing control; use the existing Home Assistant log.",
                text,
            )
            (self.root / "docs" / name).write_text(text)
            path = self.root / readme
            content = path.read_text()
            marker = contract.markers("support")[0]
            content = content.replace(
                marker,
                f"[Device troubleshooting](docs/{name}) and [Proxy guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth{suffix}.md).\n\n"
                + marker,
            )
            path.write_text(content)

    def test_blesession_requirement_identity_and_import_detection(self):
        import bluetooth_documents

        path = self.root / "custom_components/example/manifest.json"
        for requirement in (
            "BLESession==0.9.0",
            "blesession[extra]>=0.9; python_version < '2'",
            "blesession @ https://example.org/blesession.whl",
        ):
            self.assertTrue(
                bluetooth_documents.uses_blesession(
                    self.root, path, {"requirements": [requirement]}, contract.safe_path
                )
            )
        for requirement in ("not-blesession==1", "blesession-helper==1"):
            self.assertFalse(
                bluetooth_documents.uses_blesession(
                    self.root, path, {"requirements": [requirement]}, contract.safe_path
                )
            )
        code = path.parent / "client.py"
        code.write_text('# import blesession\ntext = "from blesession import Client"\n')
        self.assertFalse(
            bluetooth_documents.uses_blesession(self.root, path, {}, contract.safe_path)
        )
        for source in ("import blesession as library", "from blesession.client import Client"):
            code.write_text(source)
            self.assertTrue(
                bluetooth_documents.uses_blesession(self.root, path, {}, contract.safe_path)
            )
        code.write_text("from .blesession import Client")
        self.assertFalse(
            bluetooth_documents.uses_blesession(self.root, path, {}, contract.safe_path)
        )

    @unittest.skipUnless(sys.version_info >= (3, 14), "t-string parsing requires Python 3.14+")
    def test_checker_accepts_actual_python314_syntax_and_detects_imports(self):
        source = self.root / "custom_components/example/client.py"
        source.write_text('name = "device"\nmessage = t"Status: {name}"\n')
        self.assertEqual(contract.check(self.root), [])
        # Exercise both test-source and integration-source AST parsers under
        # the interpreter selected for the standalone standards job.
        (self.root / "tests/components/example/test_template.py").write_text(
            'message = t"Status: {name}"\n'
        )
        self.assertEqual(contract.check(self.root), [])
        source.write_text(source.read_text() + "import blesession\n")
        errors = contract.check(self.root)
        self.assertTrue(any("DOC-07 docs/troubleshooting.md" in error for error in errors))
        self.assertFalse(any("cannot parse" in error for error in errors))
        self.make_bluetooth_documents(requirement=None)
        self.assertEqual(contract.check(self.root), [])

    def test_parser_failure_names_actual_source_and_checker_interpreter(self):
        source = self.root / "custom_components/example/client.py"
        source.write_text("def broken(:\n")
        errors = contract.check(self.root)
        self.assertTrue(
            any(
                "DOC-07 custom_components/example/client.py" in error
                and "Run the checker with Python matching" in error
                for error in errors
            )
        )
        self.assertFalse(
            any("DOC-07 custom_components/example/manifest.json" in error for error in errors)
        )
        source.unlink()
        (self.root / "tests/components/example/test_broken.py").write_text("def broken(:\n")
        self.assertTrue(
            any(
                "TEST-08 tests/components/example/test_broken.py" in error
                and "Run the checker with Python matching" in error
                for error in contract.check(self.root)
            )
        )

    def test_complete_blesession_documents_pass(self):
        self.make_bluetooth_documents()
        self.assertEqual(contract.check(self.root), [])

    def test_blesession_missing_language_and_exact_exception_scope(self):
        self.make_bluetooth_documents()
        (self.root / "docs/troubleshooting.ko.md").unlink()
        self.assertTrue(
            any("DOC-07 docs/troubleshooting.ko.md" in error for error in contract.check(self.root))
        )
        self.config["exceptions"] = [
            {
                "id": "BLE-EN",
                "rule": "DOC-07",
                "paths": ["docs/troubleshooting.md"],
                "reason": "English document exception",
                "approved_by": "repository owner",
                "approved_at": "2026-10-18",
                "evidence": "STANDARDS.md#ble-en",
            }
        ]
        self.save_config()
        (self.root / "STANDARDS.md").write_text(
            "- 참조 커밋 SHA: " + "a" * 40 + "\n## BLE-EN\nUser approval reference.",
            encoding="utf-8",
        )
        self.assertTrue(
            any("DOC-07 docs/troubleshooting.ko.md" in error for error in contract.check(self.root))
        )

    def test_blesession_headings_links_table_and_placeholders_enforced(self):
        self.make_bluetooth_documents()
        path = self.root / "docs/troubleshooting.md"
        original = path.read_text()
        for broken in (
            original.replace("## Device-specific checks", "## Changed heading"),
            original.replace("## Device-specific checks", "## Diagnostics and logs", 1),
            original.replace(
                "https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md",
                "https://github.com/eigger/blesession/blob/main/docs/troubleshooting.ko.md",
            ),
            original.replace("../README.md", "../README.ko.md"),
            original.replace("troubleshooting.ko.md", "not_a_language.md"),
            original.replace(
                "https://github.com/owner/example/issues", "https://github.com/another/repo/issues"
            ),
            original.replace("| Symptom |", "| Missing |"),
            original.replace("|---|---|---|---|", "|bad|bad|bad|bad|"),
            original + "\nTODO: fill this in\n",
            original + "\n{{device_conditions}}\n",
            "```markdown\n" + original + "\n```",
            "<!--\n" + original + "\n-->",
            "<pre>\n" + original + "\n</pre>",
            "<CODE class='sample'>\n" + original + "\n</CODE>",
            "<pre>\n" + original,
        ):
            with self.subTest(broken=broken[-100:]):
                path.write_text(broken)
                self.assertTrue(
                    any(
                        "DOC-07 docs/troubleshooting.md" in error
                        for error in contract.check(self.root)
                    )
                )
        path.write_text(original)
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text().replace("(docs/troubleshooting.md)", "(docs/troubleshooting.ko.md)")
        )
        self.assertTrue(any("DOC-07 README.md" in error for error in contract.check(self.root)))

    def test_blesession_scaffold_copy_is_not_pass(self):
        self.make_bluetooth_documents()
        shutil.copyfile(
            ROOT / "templates/integration/docs/troubleshooting.md",
            self.root / "docs/troubleshooting.md",
        )
        self.assertTrue(any("placeholder" in error for error in contract.check(self.root)))

    def test_blesession_document_symlink_cannot_escape(self):
        self.make_bluetooth_documents()
        path = self.root / "docs/troubleshooting.md"
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "troubleshooting.md"
            outside.write_bytes(path.read_bytes())
            path.unlink()
            path.symlink_to(outside)
            self.assertTrue(
                any(
                    "DOC-07 docs/troubleshooting.md" in error and "escapes" in error
                    for error in contract.check(self.root)
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
        (self.root / "STANDARDS.md").write_text(
            "- 참조 커밋 SHA: " + "a" * 40 + "\n## EX-EN\nUser approval recorded here.",
            encoding="utf-8",
        )
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
        (self.root / "STANDARDS.md").write_text(
            "- 참조 커밋 SHA: " + "a" * 40 + "\n## EX-001\nUser approval recorded here.",
            encoding="utf-8",
        )
        remaining = contract.apply_exceptions(self.root, self.config, errors)
        self.assertEqual(len(remaining), 1)
        self.assertIn("components", remaining[0])
        item["paths"] = ["tests/*"]
        with self.assertRaises(ValueError):
            contract.apply_exceptions(self.root, self.config, errors)


if __name__ == "__main__":
    unittest.main()

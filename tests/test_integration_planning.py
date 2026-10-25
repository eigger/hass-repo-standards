"""Read-only inventory and deterministic integration planning in temporary repositories."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from standards import apply as application  # noqa: E402
from standards import contract, inventory, planning, readme, validation  # noqa: E402
from standards import reference as standards_reference  # noqa: E402
from test_standards_contract import input_fixture  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "manage_integration", ROOT / "scripts/manage_integration.py"
)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


def git(root, *args):
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),
    )
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout.decode("utf-8").strip()


def initialize(root):
    root.mkdir(exist_ok=True)
    git(root, "init", "--initial-branch=fixture-working")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Local test fixture")
    git(root, "config", "core.autocrlf", "false")


def commit(root):
    git(root, "add", ".")
    git(root, "commit", "--allow-empty", "-m", "Temporary checker test fixture")
    return git(root, "rev-parse", "HEAD")


class IntegrationPlanning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets_directory = tempfile.TemporaryDirectory(prefix="standards-T2-assets-")
        cls.central = Path(cls.assets_directory.name)
        for name in ("scripts", "templates", "docs", "schemas", "skills"):
            shutil.copytree(
                ROOT / name,
                cls.central / name,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        for name in ("README.md", "README.ko.md", "AGENTS.md", ".gitignore"):
            shutil.copyfile(ROOT / name, cls.central / name)
        initialize(cls.central)
        cls.ref = commit(cls.central)

    @classmethod
    def tearDownClass(cls):
        cls.assets_directory.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="standards-T2-target-")
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.target = self.base / "target"
        self.data = input_fixture()
        self.data["remote"] = {
            "value": "https://github.com/owner/example.git",
            "source": "explicit fixture origin",
        }

    def adopt_fixture(self):
        initialize(self.target)
        component = self.target / "custom_components/example"
        component.mkdir(parents=True)
        (component / "manifest.json").write_text(
            json.dumps(self.data["manifest"]["value"]), encoding="utf-8"
        )
        (component / "__init__.py").write_text(
            "# Actual unit fixture, not a device integration.\n", encoding="utf-8"
        )
        (self.target / "hacs.json").write_text('{"homeassistant":"2026.10.2"}', encoding="utf-8")
        (self.target / "LICENSE").write_text("Actual fixture MIT notice", encoding="utf-8")
        for language, name in (("en", "README.md"), ("ko", "README.ko.md")):
            original = (ROOT / "templates/integration" / name).read_text(encoding="utf-8")
            settings = contract.render_settings(self.data)
            (self.target / name).write_bytes(
                readme.render_readme(self.target, settings, language, original).encode("utf-8")
            )
        (self.target / ".gitignore").write_text(".venv/\n__pycache__/\n", encoding="utf-8")
        commit(self.target)
        git(self.target, "remote", "add", "origin", self.data["remote"]["value"])
        git(self.target, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        git(self.target, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")

    def plan(self, mode="create", data=None):
        return planning.plan(self.target, mode, data or self.data, self.ref, central=self.central)

    def snapshot(self):
        return {
            name: (self.target / name).read_bytes() for name in inventory.file_paths(self.target)
        }

    def test_adopt_category_decision_differences_are_conflicts_without_manifest_writes(self):
        self.adopt_fixture()
        path = self.target / "custom_components/example/manifest.json"
        original = path.read_bytes()
        self.data["manifest"]["value"]["categories"] = ["pets"]
        self.data["categories"]["value"] = ["pets"]
        result = self.plan("adopt")
        self.assertTrue(
            any("manifest categories differs" in value for value in result["conflicts"])
        )
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(
            any(item["path"].endswith("manifest.json") for item in result["operations"])
        )

    def test_inspect_missing_categories_records_required_manual_review(self):
        self.adopt_fixture()
        path = self.target / "custom_components/example/manifest.json"
        manifest = json.loads(path.read_text())
        del manifest["categories"]
        path.write_text(json.dumps(manifest))
        result = inventory.inspect(self.target)
        self.assertTrue(
            any("HA-02" in value and "categories" in value for value in result["pending"])
        )

    def test_create_missing_and_empty_targets_generate_reproducible_drafts_without_writes(self):
        first = self.plan()
        second = self.plan()
        self.assertEqual(planning.canonical_json(first), planning.canonical_json(second))
        self.assertFalse(self.target.exists())
        self.assertEqual(first["conflicts"], [])
        self.assertTrue(first["operations"])
        self.assertTrue(
            all(operation["before_sha256"] is None for operation in first["operations"])
        )
        self.assertTrue(any("actual LICENSE" in item for item in first["pending"]))
        self.assertTrue(any("test_init.py" in item for item in first["pending"]))
        created = {operation["path"] for operation in first["operations"]}
        self.assertIn("custom_components/example/manifest.json", created)
        self.assertIn("custom_components/example/__init__.py", created)
        self.target.mkdir()
        self.assertEqual(self.plan()["conflicts"], [])
        self.assertEqual(list(self.target.iterdir()), [])

    def test_validated_input_is_an_immutable_schema_validated_snapshot(self):
        data = copy.deepcopy(self.data)
        result = self.plan(data=data)
        expected_digest = planning.digest(
            planning.canonical_json(result["validated_input"]).encode("utf-8")
        )
        self.assertEqual(result["input_digest"], expected_digest)
        data["manifest"]["value"]["version"] = "9.9.9"
        self.assertEqual(result["validated_input"]["manifest"]["value"]["version"], "1.0.0")
        broken = copy.deepcopy(result)
        del broken["validated_input"]["domain"]
        with self.assertRaisesRegex(ValueError, "domain"):
            contract.validate_document(broken, "plan")
        for reference in (
            "https://example.invalid/schema",
            "../integration-input.schema.json",
            "/integration-input.schema.json",
            "integration-input.schema.json#fragment",
        ):
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, "reference"):
                contract.validate_schema(data, {"$ref": reference})
        with self.assertRaisesRegex(ValueError, "expected"):
            contract.validate_schema(data, {"$ref": "integration-input.schema.json", "const": 1})

    def test_equivalent_two_and_three_component_minima_are_not_conflicts(self):
        self.adopt_fixture()
        (self.target / "hacs.json").write_text('{"homeassistant":"2026.10"}', encoding="utf-8")
        (self.target / "README.md").write_text("Home Assistant >= 2026.10.0", encoding="utf-8")
        result = inventory.inspect(self.target)
        self.assertFalse(any("minimum declarations" in item for item in result["conflicts"]))
        declarations = inventory.inspect(self.target)["observations"]
        self.assertTrue(
            any(
                item["field"] == "minimum_ha"
                and item["value"] == "2026.10"
                and item["source"] == "hacs.json"
                for item in declarations
            )
        )

    def test_create_nonempty_and_adopt_missing_manifest_return_conflicts(self):
        self.target.mkdir()
        (self.target / "keep.txt").write_text("User content")
        self.assertTrue(any("empty" in message for message in self.plan()["conflicts"]))
        self.assertTrue(
            any("exactly one" in message for message in self.plan("adopt")["conflicts"])
        )

    def test_inspection_reads_real_identity_default_branch_and_provenance(self):
        self.adopt_fixture()
        result = inventory.inspect(self.target)
        self.assertEqual(result["repository"], "owner/example")
        self.assertEqual(result["default_branch"], "trunk")
        self.assertEqual(result["current_branch"], "fixture-working")
        self.assertEqual(result["domains"], ["example"])
        self.assertTrue(
            any(
                item["field"] == "manifest" and item["source"].endswith("manifest.json")
                for item in result["observations"]
            )
        )
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(self.plan("adopt")["conflicts"], [])

    def test_adopt_is_read_only_and_guards_preserved_untracked_files(self):
        self.adopt_fixture()
        (self.target / "한글 사용자 파일.txt").write_text("Keep me", encoding="utf-8")
        (self.target / "AGENTS.md").write_text("Existing project instructions", encoding="utf-8")
        before = self.snapshot()
        index = (self.target / ".git/index").read_bytes()
        result = self.plan("adopt")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((self.target / ".git/index").read_bytes(), index)
        guarded = {guard["path"]: guard for guard in result["guards"]}
        self.assertEqual(
            guarded["한글 사용자 파일.txt"]["sha256"], planning.digest("Keep me".encode())
        )
        self.assertIn("AGENTS.md", guarded)
        self.assertFalse(any(op["path"] == "AGENTS.md" for op in result["operations"]))
        self.assertFalse(
            any("modified user file" in message.lower() for message in result["conflicts"])
        )

    def test_dirty_managed_file_is_preserved_without_rejecting_unrelated_dirty_paths(self):
        self.adopt_fixture()
        path = self.target / "README.md"
        path.write_bytes(path.read_bytes().replace(b"# Example", b"# User edited title"))
        before = path.read_bytes()
        result = self.plan("adopt")
        self.assertTrue(
            any("modified user file: README.md" in item for item in result["conflicts"])
        )
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(any(op["path"] == "README.md" for op in result["operations"]))

    def test_renamed_utf8_and_space_names_are_observed_without_quoting(self):
        self.adopt_fixture()
        (self.target / "이전 이름.txt").write_text("Unchanged rename fixture", encoding="utf-8")
        commit(self.target)
        git(self.target, "mv", "이전 이름.txt", "새 이름.txt")
        result = inventory.inspect(self.target)
        self.assertIn("이전 이름.txt", result["dirty_paths"])
        self.assertIn("새 이름.txt", result["dirty_paths"])

    def test_no_default_branch_is_guessed(self):
        self.adopt_fixture()
        git(self.target, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        result = inventory.inspect(self.target)
        self.assertIsNone(result["default_branch"])
        self.assertTrue(any("no main/master" in message for message in result["pending"]))
        self.assertEqual(self.plan("adopt")["conflicts"], [])

    def test_explicit_remote_is_required_and_must_match_observed_identity(self):
        no_remote = copy.deepcopy(self.data)
        del no_remote["remote"]
        self.assertTrue(
            any("sourced remote" in value for value in self.plan(data=no_remote)["conflicts"])
        )
        self.adopt_fixture()
        changed = copy.deepcopy(self.data)
        changed["remote"]["value"] = "git@github.com:owner/different.git"
        self.assertTrue(
            any("remote" in value.lower() for value in self.plan("adopt", changed)["conflicts"])
        )
        changed = copy.deepcopy(self.data)
        changed["default_branch"]["value"] = "different"
        self.assertTrue(
            any("default branch" in value for value in self.plan("adopt", changed)["conflicts"])
        )

    def test_credentials_are_redacted_from_inventory(self):
        self.adopt_fixture()
        git(
            self.target,
            "remote",
            "set-url",
            "origin",
            "https://secret-token@github.com/owner/example.git",
        )
        result = planning.canonical_json(inventory.inspect(self.target))
        self.assertNotIn("secret-token", result)
        self.assertIn("redacted", result)

    def test_domain_and_multiple_manifest_disagreements_block(self):
        self.adopt_fixture()
        data = copy.deepcopy(self.data)
        data["domain"]["value"] = "other"
        self.assertTrue(any("domain" in value for value in self.plan("adopt", data)["conflicts"]))
        other = self.target / "custom_components/other"
        other.mkdir()
        (other / "manifest.json").write_text('{"domain":"other"}')
        self.assertTrue(any("Multiple" in value for value in self.plan("adopt")["conflicts"]))

    def test_minimum_support_disagreements_and_common_readme_forms_block(self):
        self.adopt_fixture()
        for declaration in (
            "Home Assistant 2025.1 or later",
            "Home Assistant >= 2025.1.0",
            "Home Assistant 2025.1.0+",
            "최소 HA 2025.1.0 이상",
        ):
            with self.subTest(declaration=declaration):
                path = self.target / "README.md"
                path.write_text(
                    path.read_text(encoding="utf-8") + "\n" + declaration + "\n", encoding="utf-8"
                )
                result = self.plan("adopt")
                self.assertTrue(any("support" in item.lower() for item in result["conflicts"]))
        changed = copy.deepcopy(self.data)
        changed["environments"]["value"]["minimum"]["ha"] = "2026.11.0"
        self.assertTrue(
            any("minimum HA" in value for value in self.plan("adopt", changed)["conflicts"])
        )

    def test_ambiguous_support_is_pending_and_minimum_current_files_stay_separate(self):
        self.adopt_fixture()
        (self.target / "README.md").write_text("Home Assistant 2025.1 supported", encoding="utf-8")
        self.assertTrue(any("Ambiguous support" in item for item in self.plan("adopt")["pending"]))
        data = copy.deepcopy(self.data)
        data["environments"]["value"]["minimum"].update(ha="2025.1.0", python="3.13")
        result = self.plan("adopt", data)
        self.assertTrue(any("share incompatible" in item for item in result["conflicts"]))

    def test_wrong_or_modified_standards_sha_is_rejected(self):
        for ref in ("main", "0" * 40, self.ref[:7]):
            with self.subTest(ref=ref), self.assertRaisesRegex(ValueError, "SHA|HEAD"):
                planning.plan(self.target, "create", self.data, ref, central=self.central)
        for relative in ("docs/temporary-untracked-rule.md", "skills/temporary-untracked-skill.md"):
            path = self.central / relative
            path.write_text("Modified execution assets")
            try:
                with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, "clean"):
                    self.plan()
            finally:
                path.unlink()

    def test_identical_effective_test_requirements_preserve_existing_bytes(self):
        self.adopt_fixture()
        generated = next(
            operation["content"]
            for operation in self.plan("adopt")["operations"]
            if operation["path"] == "requirements_test.txt"
        )
        requirements = [
            line for line in generated.splitlines() if line and not line.startswith("#")
        ]
        original = (
            "# Existing compatible environment; retain this explanation.\r\n\r\n  "
            + requirements[0]
            + "  \r\n\t# Existing plugin rationale\r\n\t"
            + requirements[1]
            + "\t\r\n"
        ).encode("utf-8")
        path = self.target / "requirements_test.txt"
        path.write_bytes(original)
        commit(self.target)
        for dirty in (False, True):
            with self.subTest(dirty=dirty):
                if dirty:
                    path.write_bytes(original + b"# User's uncommitted explanation\r\n")
                before = self.snapshot()
                result = self.plan("adopt")
                self.assertIn("requirements_test.txt", result["unchanged"])
                self.assertFalse(
                    any(
                        operation["path"] == "requirements_test.txt"
                        for operation in result["operations"]
                    )
                )
                self.assertFalse(
                    any("requirements_test.txt" in conflict for conflict in result["conflicts"])
                )
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(
                    next(
                        guard["sha256"]
                        for guard in result["guards"]
                        if guard["path"] == "requirements_test.txt"
                    ),
                    planning.digest(path.read_bytes()),
                )

    def test_changed_effective_test_requirements_still_require_reviewed_merge(self):
        self.adopt_fixture()
        generated = next(
            operation["content"]
            for operation in self.plan("adopt")["operations"]
            if operation["path"] == "requirements_test.txt"
        )
        lines = [line for line in generated.splitlines() if line and not line.startswith("#")]
        path = self.target / "requirements_test.txt"
        variants = (
            [lines[0].replace("==", ">="), lines[1]],
            [lines[0] + '; python_version >= "3.14"', lines[1]],
            [lines[0].replace("homeassistant", "homeassistant[extra]"), lines[1]],
            [*lines, "pytest-timeout==2.4.0"],
            [*lines, "-r other.txt"],
            [*lines, "-c constraints.txt"],
            [lines[0] + " # inline comment retained for review", lines[1]],
            [lines[0], lines[0], lines[1]],
        )
        for variant in variants:
            with self.subTest(variant=variant):
                original = ("\n".join(variant) + "\n").encode("utf-8")
                path.write_bytes(original)
                commit(self.target)
                result = self.plan("adopt")
                self.assertTrue(
                    any(
                        "reviewed merge required: requirements_test.txt" in conflict
                        for conflict in result["conflicts"]
                    )
                )
                self.assertFalse(
                    any(
                        operation["path"] == "requirements_test.txt"
                        for operation in result["operations"]
                    )
                )
                self.assertEqual(path.read_bytes(), original)

    def test_dependabot_protects_actual_minimum_environment_paths_and_preserves_updates(self):
        data = copy.deepcopy(self.data)
        environments = data["environments"]["value"]
        environments["minimum"]["requirements"] = ["requirements_minimum.txt"]
        environments["minimum"]["constraints"] = ["constraints/confirmed-minimum.txt"]
        environments["minimum"]["pytest_homeassistant_custom_component"] = "0.12.0"
        source = (self.central / "templates/integration/.github/dependabot.yml").read_text()
        baseline = yaml.safe_load(source)
        result = self.plan(data=data)
        operation = next(
            item for item in result["operations"] if item["path"] == ".github/dependabot.yml"
        )
        rendered = yaml.safe_load(operation["content"])
        pip = next(update for update in rendered["updates"] if update["package-ecosystem"] == "pip")
        self.assertIn("requirements_minimum.txt", pip["exclude-paths"])
        self.assertIn("constraints/confirmed-minimum.txt", pip["exclude-paths"])
        self.assertNotIn("requirements_test.txt", pip["exclude-paths"])
        original_pip = next(
            update for update in baseline["updates"] if update["package-ecosystem"] == "pip"
        )
        for path in original_pip["exclude-paths"]:
            self.assertIn(path, pip["exclude-paths"])
        pip.pop("exclude-paths")
        original_pip.pop("exclude-paths")
        self.assertEqual(rendered, baseline)
        self.assertEqual(result["validated_input"]["environments"]["value"], environments)

    def test_dependabot_shared_current_paths_are_not_excluded_and_existing_yaml_is_noop(self):
        source = (self.central / "templates/integration/.github/dependabot.yml").read_text()
        data = copy.deepcopy(self.data)
        for axis in ("minimum", "current"):
            data["environments"]["value"][axis]["constraints"] = [
                "constraints/homeassistant-min.txt"
            ]
        document = yaml.safe_load(planning.render_dependabot(source, data))
        pip = next(update for update in document["updates"] if update["package-ecosystem"] == "pip")
        self.assertNotIn("requirements_test.txt", pip["exclude-paths"])
        self.assertNotIn("constraints/homeassistant-min.txt", pip["exclude-paths"])
        self.adopt_fixture()
        path = self.target / ".github/dependabot.yml"
        path.parent.mkdir(parents=True)
        generated = next(
            operation["content"]
            for operation in self.plan("adopt")["operations"]
            if operation["path"] == ".github/dependabot.yml"
        )
        original = (
            "# Retain existing formatting and rationale.\r\n" + generated.replace("\n", "\r\n")
        ).encode("utf-8")
        path.write_bytes(original)
        commit(self.target)
        result = self.plan("adopt")
        self.assertIn(".github/dependabot.yml", result["unchanged"])
        self.assertFalse(
            any(operation["path"] == ".github/dependabot.yml" for operation in result["operations"])
        )
        self.assertEqual(path.read_bytes(), original)
        document = yaml.safe_load(original)
        document["updates"][0]["schedule"]["interval"] = "monthly"
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
        commit(self.target)
        result = self.plan("adopt")
        self.assertTrue(
            any(
                "reviewed merge required: .github/dependabot.yml" in conflict
                for conflict in result["conflicts"]
            )
        )
        self.assertEqual(yaml.safe_load(path.read_bytes()), document)

    def test_dependabot_shared_paths_in_distinct_environments_remain_explicitly_unverified(self):
        data = copy.deepcopy(self.data)
        for axis in ("minimum", "current"):
            data["environments"]["value"][axis]["constraints"] = ["constraints/shared.txt"]
        data["environments"]["value"]["minimum"]["python"] = "3.13"
        result = self.plan(data=data)
        content = next(
            operation["content"]
            for operation in result["operations"]
            if operation["path"] == ".github/dependabot.yml"
        )
        pip = next(
            update
            for update in yaml.safe_load(content)["updates"]
            if update["package-ecosystem"] == "pip"
        )
        for shared in ("requirements_test.txt", "constraints/shared.txt"):
            self.assertNotIn(shared, pip["exclude-paths"])
            self.assertTrue(
                any(
                    "Automatic minimum protection is unverified" in pending and shared in pending
                    for pending in result["pending"]
                )
            )
        same = self.plan()
        self.assertFalse(
            any(
                "Automatic minimum protection is unverified" in pending
                for pending in same["pending"]
            )
        )

    def test_dependabot_environment_paths_are_validated_before_rendering(self):
        source = (self.central / "templates/integration/.github/dependabot.yml").read_text()
        for invalid in ("../escape.txt", "/absolute.txt", "constraints/*.txt", "C:/escape.txt"):
            with self.subTest(invalid=invalid):
                data = copy.deepcopy(self.data)
                data["environments"]["value"]["minimum"]["constraints"] = [invalid]
                with self.assertRaises(ValueError):
                    planning.render_dependabot(source, data)

    def test_library_combinations_share_detection_and_never_delete_removed_documents(self):
        for packages in ([], ["imagespec"], ["blesession"], ["imagespec", "blesession"]):
            data = copy.deepcopy(self.data)
            data["manifest"]["value"]["requirements"] = [
                f'{name}[extra]>=1.2; python_version < "2"' for name in packages
            ]
            if "imagespec" in packages:
                data["payload"] = {
                    "value": {
                        "examples": [
                            {
                                "path": "examples/payload/real.yaml",
                                "payload_path": ["data", "payload"],
                                "expected_size": [16, 16],
                                "expected_palette": ["#000000"],
                            }
                        ],
                        "adapter": "actual integration preparation callable, still pending",
                    },
                    "source": "unit fixture input only",
                }
            result = self.plan(data=data)
            paths = {operation["path"] for operation in result["operations"]}
            self.assertEqual("docs/payload.md" in paths, "imagespec" in packages)
            self.assertEqual("docs/troubleshooting.md" in paths, "blesession" in packages)
        self.adopt_fixture()
        docs = self.target / "docs"
        docs.mkdir()
        (docs / "payload.md").write_text("Existing examples remain", encoding="utf-8")
        result = self.plan("adopt")
        self.assertFalse(any(op["path"] == "docs/payload.md" for op in result["operations"]))
        self.assertIn("docs/payload.md", {guard["path"] for guard in result["guards"]})

    def test_platform_path_collision_is_a_conflict(self):
        data = copy.deepcopy(self.data)
        data["platforms"]["value"] = ["const"]
        self.assertTrue(
            any("collision" in message for message in self.plan(data=data)["conflicts"])
        )

    def test_metadata_changed_during_inspection_cannot_be_guarded_as_old_input(self):
        self.adopt_fixture()
        original_inspect = inventory.inspect

        def inspect_then_edit(target):
            result = original_inspect(target)
            (self.target / "hacs.json").write_text('{"homeassistant":"2025.1.0"}', encoding="utf-8")
            return result

        with patch.object(inventory, "inspect", side_effect=inspect_then_edit):
            with self.assertRaisesRegex(ValueError, "changed while planning"):
                self.plan("adopt")
        self.assertEqual(
            inventory.load_json(self.target / "hacs.json")["homeassistant"], "2025.1.0"
        )

    def test_exact_source_crlf_bytes_and_digest_are_preserved(self):
        source = self.central / "templates/integration/tests/conftest.py"
        original = source.read_bytes()
        previous_ref = self.ref
        try:
            crlf = original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            source.write_bytes(crlf)
            self.ref = commit(self.central)
            operation = next(
                operation
                for operation in self.plan()["operations"]
                if operation["path"] == "tests/conftest.py"
            )
            self.assertEqual(operation["content"].encode("utf-8"), crlf)
            self.assertEqual(operation["after_sha256"], planning.digest(crlf))
        finally:
            source.write_bytes(original)
            # Restore only this private fixture's tracked state and head.
            git(self.central, "reset", "--soft", previous_ref)
            git(self.central, "add", "templates/integration/tests/conftest.py")
            self.ref = previous_ref

    def test_git_timeout_is_an_actionable_input_error(self):
        with patch.object(
            inventory.subprocess, "run", side_effect=subprocess.TimeoutExpired(["git"], 10)
        ):
            with self.assertRaisesRegex(ValueError, "timed out"):
                inventory.git(self.target, "status")
            self.assertEqual(
                cli.main(
                    ["inspect", str(self.target), "--output", str(self.base / "inventory.json")]
                ),
                2,
            )

    def test_nonstandard_json_constants_and_duplicate_keys_are_rejected(self):
        path = self.base / "input.json"
        for content in (
            '{"value":NaN}',
            '{"value":Infinity}',
            '{"value":1e999}',
            '{"key":1,"key":2}',
        ):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    inventory.load_json(path)
        data = copy.deepcopy(self.data)
        data["manifest"]["value"]["extra"] = float("nan")
        with self.assertRaises(ValueError):
            self.plan(data=data)

    def test_nonportable_paths_are_rejected_before_target_access(self):
        for name in (
            "../outside",
            "C:/outside",
            "folder\\outside",
            "aux.txt",
            "path. ",
            "newline\nname",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                inventory.safe_target_path(self.target, name)

    def test_ignored_virtual_environment_is_not_inspected_or_guarded(self):
        self.adopt_fixture()
        virtual = self.target / ".venv"
        virtual.mkdir()
        (virtual / "ignored.txt").write_text("Environment churn")
        result = self.plan("adopt")
        self.assertFalse(any(guard["path"].startswith(".venv/") for guard in result["guards"]))
        self.assertEqual(inventory.inspect(self.target)["conflicts"], [])

    def test_output_must_be_outside_target_and_not_overwrite_input(self):
        self.target.mkdir()
        with self.assertRaisesRegex(ValueError, "outside"):
            cli.output_path(self.target / "plan.json", self.target)
        path = self.base / "input.json"
        path.write_text(planning.canonical_json(self.data), encoding="utf-8")
        self.assertEqual(
            cli.main(
                [
                    "plan",
                    str(self.target),
                    "--mode",
                    "create",
                    "--input",
                    str(path),
                    "--output",
                    str(path),
                    "--standards-ref",
                    self.ref,
                ]
            ),
            2,
        )
        self.assertEqual(inventory.load_json(path), self.data)

    def test_cli_inspect_output_and_exit_codes_do_not_mutate_target(self):
        self.adopt_fixture()
        output = self.base / "inventory.json"
        before = self.snapshot()
        self.assertEqual(cli.main(["inspect", str(self.target), "--output", str(output)]), 0)
        self.assertEqual(inventory.load_json(output)["default_branch"], "trunk")
        self.assertEqual(self.snapshot(), before)
        input_path = self.base / "input.json"
        input_path.write_text(planning.canonical_json(self.data), encoding="utf-8")
        output = self.base / "plan.json"
        with patch.object(planning, "CENTRAL", self.central):
            args = [
                "plan",
                str(self.target),
                "--mode",
                "adopt",
                "--input",
                str(input_path),
                "--output",
                str(output),
                "--standards-ref",
                self.ref,
            ]
            self.assertEqual(cli.main(args), 0)
            first = output.read_bytes()
            self.assertEqual(cli.main(args), 0)
            self.assertEqual(output.read_bytes(), first)
            data = copy.deepcopy(self.data)
            del data["remote"]
            input_path.write_text(planning.canonical_json(data), encoding="utf-8")
            self.assertEqual(cli.main(args), 2)
            self.assertTrue(inventory.load_json(output)["conflicts"])
        self.assertEqual(self.snapshot(), before)

    def test_symlink_escape_and_output_aliases_fail_without_writes(self):
        self.adopt_fixture()
        outside = self.base / "outside"
        outside.mkdir()
        link = self.target / "linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if os.name == "nt" and error.winerror == 1314:
                self.skipTest(
                    "Windows symlink creation permission unavailable; Linux independent test required"
                )
            raise
        with self.assertRaises(ValueError):
            inventory.inspect(self.target)
        output_link = self.base / "output-link"
        output_link.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            cli.output_path(output_link / "plan.json", self.target)
        self.assertEqual(list(outside.iterdir()), [])

    def test_exact_release_plan_requires_attestation_and_renders_tag_with_resolved_sha(self):
        proof = self.base / "release-verification.json"
        proof.write_text(
            planning.canonical_json(
                {
                    "repository": "eigger/hass-repo-standards",
                    "kind": "release",
                    "tag": "v1.0.0",
                    "resolved_sha": self.ref,
                    "verified": "remote",
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "verification evidence"):
            planning.plan(
                self.target,
                "create",
                self.data,
                self.ref,
                central=self.central,
                release_tag="v1.0.0",
            )
        evidence = {
            "repository": "eigger/hass-repo-standards",
            "kind": "release",
            "tag": "v1.0.0",
            "resolved_sha": self.ref,
            "verified": "remote",
        }
        with patch.object(planning.reference, "verify_remote", return_value=evidence):
            result = planning.plan(
                self.target,
                "create",
                self.data,
                self.ref,
                central=self.central,
                release_tag="v1.0.0",
                release_verification=proof,
            )
        self.assertEqual(
            result["standards_reference"],
            {"kind": "release", "tag": "v1.0.0", "resolved_sha": self.ref},
        )
        self.assertRegex(result["release_attestation"], r"^[0-9a-f]{64}$")
        workflows = {item["path"]: item["content"] for item in result["operations"]}
        self.assertIn("@v1.0.0", workflows[".github/workflows/tests.yml"])
        self.assertIn("standards-ref: " + self.ref, workflows[".github/workflows/tests.yml"])
        self.assertRegex(workflows["STANDARDS.md"], r"(?m)^- Standards release: v1\.0\.0$")
        with self.assertRaisesRegex(ValueError, "reserved for apply/recover"):
            planning.plan(
                self.target,
                "create",
                self.data,
                {"kind": "release", "tag": "v1.0.0", "resolved_sha": self.ref},
                central=self.central,
                release_attestation=result["release_attestation"],
            )
        with patch.object(
            standards_reference, "verify_remote", side_effect=ValueError("unpublished")
        ):
            with self.assertRaisesRegex(ValueError, "unpublished"):
                planning.plan(
                    self.target,
                    "create",
                    self.data,
                    self.ref,
                    central=self.central,
                    release_tag="v1.0.0",
                    release_verification=proof,
                )

    def test_adopt_migrates_only_central_refs_and_standards_record_to_a_release(self):
        self.adopt_fixture()
        legacy = self.plan("adopt")
        plan_path = self.base / "legacy-plan.json"
        plan_path.write_text(planning.canonical_json(legacy), encoding="utf-8")
        self.assertEqual(
            application.apply_plan(self.target, plan_path, central=self.central)["status"],
            "completed",
        )
        commit(self.target)
        proof = self.base / "release-verification.json"
        evidence = {
            "repository": "eigger/hass-repo-standards",
            "kind": "release",
            "tag": "v1.0.0",
            "resolved_sha": self.ref,
            "verified": "remote",
        }
        proof.write_text(planning.canonical_json(evidence), encoding="utf-8")
        with patch.object(planning.reference, "verify_remote", return_value=evidence):
            migrated = planning.plan(
                self.target,
                "adopt",
                self.data,
                self.ref,
                central=self.central,
                release_tag="v1.0.0",
                release_verification=proof,
            )
        self.assertEqual(migrated["conflicts"], [])
        changed = {operation["path"] for operation in migrated["operations"]}
        self.assertTrue({".hass-standards.json", "STANDARDS.md"} <= changed)
        self.assertIn(".github/workflows/tests.yml", changed)
        self.assertNotIn("ADOPTION_CHECKLIST.md", changed)
        release_plan = self.base / "release-plan.json"
        release_plan.write_text(planning.canonical_json(migrated), encoding="utf-8")
        self.assertEqual(
            application.apply_plan(self.target, release_plan, central=self.central)["status"],
            "completed",
        )
        config = json.loads((self.target / ".hass-standards.json").read_text(encoding="utf-8"))
        self.assertEqual(validation.reference_errors(self.target, readme.safe_path, config), [])


if __name__ == "__main__":
    unittest.main()

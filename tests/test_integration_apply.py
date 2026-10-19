"""Guarded apply/recovery with actual temporary files and injected I/O failures."""

from __future__ import annotations

import base64
import copy
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import test_integration_planning as fixtures  # noqa: E402
from standards import apply as application  # noqa: E402
from standards import inventory, planning  # noqa: E402

cli = fixtures.cli


class IntegrationApply(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.IntegrationPlanning.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.IntegrationPlanning.tearDownClass.__func__(cls)

    setUp = fixtures.IntegrationPlanning.setUp
    adopt_fixture = fixtures.IntegrationPlanning.adopt_fixture
    snapshot = fixtures.IntegrationPlanning.snapshot

    def prepare(self, mode="create", data=None):
        self.plan_path = self.base / "plan.json"
        self.journal_path = self.base / "plan.apply.json"
        self.document = planning.plan(
            self.target, mode, data or self.data, self.ref, central=self.central
        )
        self.assertEqual(self.document["conflicts"], [])
        self.plan_path.write_text(planning.canonical_json(self.document), encoding="utf-8")
        return self.document

    def apply(self):
        return application.apply_plan(self.target, self.plan_path, central=self.central)

    def recover(self):
        return application.recover(self.target, self.journal_path, central=self.central)

    def mutate_plan(self, mutate):
        doc = copy.deepcopy(self.document)
        mutate(doc)
        self.plan_path.write_text(planning.canonical_json(doc), encoding="utf-8")

    def test_create_applies_draft_and_adopt_replan_is_idempotent(self):
        self.prepare()
        result = self.apply()
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["pending"])
        self.assertTrue((self.target / "custom_components/example/manifest.json").is_file())
        self.assertTrue((self.target / "custom_components/__init__.py").is_file())
        self.assertEqual((self.target / "custom_components/__init__.py").read_bytes(), b"")
        self.assertEqual(set(result["applied"]), {op["path"] for op in self.document["operations"]})
        repeated = planning.plan(self.target, "adopt", self.data, self.ref, central=self.central)
        self.assertEqual(repeated["operations"], [])
        self.assertTrue(repeated["pending"])
        journal = inventory.load_json(self.journal_path)
        self.assertTrue(journal["root_created"])
        self.assertTrue(journal["created_directories"])
        self.assertFalse(any(path.name.endswith(".lock") for path in self.base.iterdir()))

    def test_recovery_restores_absent_target_and_is_repeatable(self):
        self.prepare()
        self.apply()
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())
        self.assertEqual(self.recover()["status"], "recovered")

    def test_recovery_preserves_original_empty_target_and_user_files_in_new_directories(self):
        self.target.mkdir()
        self.prepare()
        self.apply()
        user = self.target / "tests/user-owned.txt"
        user.write_text("New user content", encoding="utf-8")
        result = self.recover()
        self.assertEqual(result["status"], "recovered")
        self.assertEqual(user.read_text(encoding="utf-8"), "New user content")
        self.assertIn("tests", result["preserved_directories"])
        self.assertTrue(self.target.is_dir())

    def test_adopt_preserves_original_bytes_and_recovers_managed_changes(self):
        self.adopt_fixture()
        before = self.snapshot()
        self.prepare("adopt")
        self.apply()
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertEqual(self.snapshot(), before)

    def test_existing_custom_implementation_is_preserved_without_scaffold_todo_claim(self):
        self.adopt_fixture()
        path = self.target / "custom_components/example/__init__.py"
        original = path.read_bytes()
        self.assertNotIn(b"TODO", original)
        document = self.prepare("adopt")
        related = [
            message
            for message in document["pending"]
            if "custom_components/example/__init__.py" in message
        ]
        self.assertTrue(any("actual HA tests" in message for message in related))
        self.assertFalse(
            any(
                "TODO authoring scaffold" in message or "implement real device behavior" in message
                for message in related
            )
        )
        self.assertFalse(
            any(
                op["path"] == "custom_components/example/__init__.py"
                for op in document["operations"]
            )
        )
        self.apply()
        self.assertEqual(path.read_bytes(), original)

    def test_existing_custom_components_root_init_bytes_are_preserved_through_recovery(self):
        self.adopt_fixture()
        root_init = self.target / "custom_components/__init__.py"
        original = b"# Existing project package notice\r\nPROJECT_CONSTANT = 'preserve  bytes'\r\n"
        root_init.write_bytes(original)
        fixtures.commit(self.target)
        before = self.snapshot()
        document = self.prepare("adopt")
        self.assertFalse(
            any(op["path"] == "custom_components/__init__.py" for op in document["operations"])
        )
        self.apply()
        self.assertEqual(root_init.read_bytes(), original)
        self.assertEqual(
            planning.plan(self.target, "adopt", self.data, self.ref, central=self.central)[
                "operations"
            ],
            [],
        )
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(root_init.read_bytes(), original)

    def test_stale_file_presence_absence_and_content_fail_before_any_write(self):
        for mode in ("presence", "content", "absence"):
            with self.subTest(mode=mode):
                if self.target.exists():
                    # Only temporary fixture files; keep each case isolated.
                    import shutil

                    shutil.rmtree(self.target)
                self.prepare()
                name = self.document["operations"][0]["path"]
                path = self.target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Concurrent user content", encoding="utf-8")
                if mode == "absence":
                    path.unlink()
                    (self.target / "unrelated.txt").write_text("new user file")
                before = self.snapshot()
                with self.assertRaises(ValueError):
                    self.apply()
                self.assertEqual(self.snapshot(), before)
                self.assertFalse(self.journal_path.exists())

    def test_modified_plan_content_paths_ownership_hash_or_input_are_rejected(self):
        self.prepare()
        changes = (
            lambda doc: doc["operations"][0].update(content="Injected content"),
            lambda doc: doc["operations"][0].update(path="AGENTS.md"),
            lambda doc: doc["operations"][0].update(path="../outside.txt"),
            lambda doc: doc["operations"][0].update(ownership="create_only"),
            lambda doc: doc.update(input_digest="0" * 64),
            lambda doc: doc["validated_input"]["domain"].update(value="other"),
            lambda doc: doc["target_identity"].update(path=str(self.base / "other")),
        )
        for mutate in changes:
            with self.subTest(mutate=mutate):
                self.mutate_plan(mutate)
                with self.assertRaises(ValueError):
                    self.apply()
                self.assertFalse(self.target.exists())
                self.assertFalse(self.journal_path.exists())

    def test_self_consistent_plan_content_and_hash_tamper_still_cannot_apply(self):
        self.prepare()

        def mutate(doc):
            op = doc["operations"][0]
            op["content"] = "Fake but self-consistent content"
            op["after_sha256"] = planning.digest(op["content"].encode())

        self.mutate_plan(mutate)
        with self.assertRaisesRegex(ValueError, "replan"):
            self.apply()
        self.assertFalse(self.target.exists())

    def test_standards_wrong_sha_or_dirty_assets_are_rejected_before_write(self):
        self.prepare()
        self.mutate_plan(lambda doc: doc.update(standards_ref="0" * 40))
        with self.assertRaises(ValueError):
            self.apply()
        self.plan_path.write_text(planning.canonical_json(self.document), encoding="utf-8")
        file = self.central / "scripts/dirty-apply-fixture.py"
        file.write_text("# uncommitted execution asset")
        try:
            with self.assertRaisesRegex(ValueError, "clean"):
                self.apply()
        finally:
            file.unlink()
        self.assertFalse(self.target.exists())

    def test_exclusive_lock_prevents_second_transaction_and_preserves_owner(self):
        self.prepare()
        with application.target_lock(self.target):
            locks = list(self.base.glob("*.lock"))
            self.assertEqual(len(locks), 1)
            with self.assertRaisesRegex(ValueError, "lock"):
                self.apply()
            self.assertTrue(locks[0].is_file())
            self.assertFalse(self.target.exists())
        self.assertFalse(list(self.base.glob("*.lock")))

    def test_case_aliases_share_one_lock_under_windows_path_normalization(self):
        # Exercise the platform normalization boundary on every test host.
        with patch.object(application.os.path, "normcase", side_effect=lambda value: value.lower()):
            with application.target_lock(self.target):
                with self.assertRaisesRegex(ValueError, "lock"):
                    with application.target_lock(self.base / "TARGET"):
                        self.fail("Case aliases must not acquire independent locks")
        self.assertFalse(list(self.base.glob("*.lock")))

    def test_lock_then_revalidation_detects_concurrent_change(self):
        self.prepare()
        original = application.validate_plan
        calls = 0

        def validate(root, doc, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                root.mkdir()
                (root / "concurrent.txt").write_text("preserve")
            return original(root, doc, **kwargs)

        with patch.object(application, "validate_plan", side_effect=validate):
            with self.assertRaises(ValueError):
                self.apply()
        self.assertEqual((self.target / "concurrent.txt").read_text(), "preserve")
        self.assertFalse(self.journal_path.exists())

    def test_partial_replace_failure_reports_and_recovers_only_applied_files(self):
        self.prepare()
        actual = application.replace_file
        calls = 0

        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("Injected replacement failure")
            return actual(*args, **kwargs)

        with patch.object(application, "replace_file", side_effect=fail_second):
            result = self.apply()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(result["applied"]), 1)
        self.assertIn("recover", result["recovery_command"])
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())

    def test_replace_succeeded_before_journal_update_failure_remains_recoverable(self):
        self.prepare()
        actual = application.atomic_json
        failed = False

        def fail_after_write(path, journal):
            nonlocal failed
            if not failed and any(entry["state"] == "applied" for entry in journal["entries"]):
                failed = True
                raise OSError("Injected post-replacement journal failure")
            return actual(path, journal)

        with patch.object(application, "atomic_json", side_effect=fail_after_write):
            result = self.apply()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(result["applied"]), 1)
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())

    def test_durable_writing_state_recovers_when_all_later_journal_updates_fail(self):
        self.prepare()
        actual = application.atomic_json

        def persistent_failure(path, journal):
            if any(entry["state"] == "applied" for entry in journal["entries"]):
                raise OSError("Journal unavailable after replacement")
            return actual(path, journal)

        with patch.object(application, "atomic_json", side_effect=persistent_failure):
            result = self.apply()
        self.assertEqual(result["status"], "failed")
        self.assertIn(
            "writing",
            [entry["state"] for entry in inventory.load_json(self.journal_path)["entries"]],
        )
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())

    def test_journal_initial_write_failure_cannot_modify_target(self):
        self.prepare()
        with patch.object(
            application, "reserve_journal", side_effect=OSError("Backup device unavailable")
        ):
            with self.assertRaises(OSError):
                self.apply()
        self.assertFalse(self.target.exists())

    def test_initial_journal_publish_failure_cleans_temporary_artifacts(self):
        self.prepare()
        with patch.object(
            application.os, "link", side_effect=OSError("Cannot publish backup journal")
        ):
            with self.assertRaises(OSError):
                self.apply()
        self.assertFalse(self.target.exists())
        self.assertFalse(self.journal_path.exists())
        self.assertFalse(list(self.base.glob(".hass-journal-*")))
        self.assertFalse(list(self.base.glob("*.lock")))

    def test_subsequent_user_edit_blocks_all_recovery_writes(self):
        self.prepare()
        self.apply()
        path = self.target / self.document["operations"][0]["path"]
        path.write_text("User changes after apply", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "user changes"):
            self.recover()
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_backup_encoding_hash_and_journal_plan_are_rejected(self):
        self.adopt_fixture()
        self.prepare("adopt")
        self.apply()
        journal = inventory.load_json(self.journal_path)
        entry_index = next(
            index
            for index, entry in enumerate(journal["entries"])
            if entry["before_sha256"] is not None
        )
        for mutate in (
            lambda doc: doc["entries"][entry_index].update(before_base64="not base64"),
            lambda doc: doc["entries"][entry_index].update(
                before_base64=base64.b64encode(b"Injected original").decode()
            ),
            lambda doc: doc.update(plan_sha256="0" * 64),
            lambda doc: doc["plan"]["operations"][0].update(path="AGENTS.md"),
        ):
            corrupted = copy.deepcopy(journal)
            mutate(corrupted)
            self.journal_path.write_text(planning.canonical_json(corrupted), encoding="utf-8")
            before = self.snapshot()
            with self.assertRaises(ValueError):
                self.recover()
            self.assertEqual(self.snapshot(), before)

    def test_self_consistent_backup_plan_guard_and_digests_tamper_is_rejected(self):
        self.adopt_fixture()
        self.prepare("adopt")
        self.apply()
        journal = inventory.load_json(self.journal_path)
        index = next(
            index for index, entry in enumerate(journal["entries"]) if entry["path"] == "README.md"
        )
        entry = journal["entries"][index]
        forged = base64.b64decode(entry["before_base64"]).replace(
            b"<!-- hass-standards:support:start -->",
            b"Injected arbitrary original body\n\n<!-- hass-standards:support:start -->",
        )
        forged_hash = planning.digest(forged)
        entry.update(before_base64=base64.b64encode(forged).decode(), before_sha256=forged_hash)
        journal["plan"]["operations"][index]["before_sha256"] = forged_hash
        next(guard for guard in journal["plan"]["guards"] if guard["path"] == entry["path"])[
            "sha256"
        ] = forged_hash
        journal["plan_sha256"] = planning.digest(planning.canonical_json(journal["plan"]).encode())
        self.journal_path.write_text(planning.canonical_json(journal), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "anchor"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        # Even changing both local artifacts cannot make an arbitrary backup
        # body reproduce the renderer's original output.
        application.anchor_path(self.journal_path, self.target).write_text(
            planning.canonical_json(journal["plan"]), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "preimage"):
            self.recover()
        self.assertEqual(self.snapshot(), before)

    def test_journal_cannot_claim_an_original_empty_root_was_created(self):
        self.target.mkdir()
        self.prepare()
        self.assertTrue(self.document["target_identity"]["root_exists"])
        self.apply()
        journal = inventory.load_json(self.journal_path)
        journal["root_created"] = True
        self.journal_path.write_text(planning.canonical_json(journal), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "originally existed"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.target.is_dir())

    def test_conftest_comment_markers_and_outside_fixture_bytes_stay_intact(self):
        self.adopt_fixture()
        destination = self.target / "tests/components/example/conftest.py"
        destination.parent.mkdir(parents=True)
        template = (
            self.central / "templates/integration/tests/components/example/conftest.py"
        ).read_text(encoding="utf-8")
        prefix, suffix = (
            b"# Existing fixture notice\r\n",
            b"\r\nCUSTOM_DATA = {'keep': 'exact  bytes'}\r\n",
        )
        destination.write_bytes(prefix + template.encode() + suffix)
        fixtures.commit(self.target)
        self.prepare("adopt")
        self.apply()
        content = destination.read_bytes()
        self.assertTrue(content.startswith(prefix))
        self.assertTrue(content.endswith(suffix))
        import ast

        ast.parse(content.decode("utf-8"))
        self.assertEqual(
            planning.plan(self.target, "adopt", self.data, self.ref, central=self.central)[
                "operations"
            ],
            [],
        )

    def test_self_consistent_root_existence_forgery_cannot_change_original_anchor(self):
        self.target.mkdir()
        self.prepare()
        self.apply()
        journal = inventory.load_json(self.journal_path)
        journal["root_created"] = True
        journal["plan"]["target_identity"]["root_exists"] = False
        journal["plan_sha256"] = planning.digest(planning.canonical_json(journal["plan"]).encode())
        self.journal_path.write_text(planning.canonical_json(journal), encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "anchor"):
            self.recover()
        self.assertEqual(self.snapshot(), before)

    def test_missing_changed_or_orphaned_anchor_is_never_overwritten_or_trusted(self):
        self.prepare()
        anchor = application.anchor_path(self.journal_path, self.target)
        anchor.write_bytes(planning.canonical_json(self.document).encode("utf-8"))
        with self.assertRaisesRegex(ValueError, "anchor"):
            self.apply()
        self.assertFalse(self.target.exists())
        original = anchor.read_bytes()
        self.assertEqual(original, planning.canonical_json(self.document).encode())
        anchor.unlink()
        self.apply()
        before = self.snapshot()
        anchor.unlink()
        with self.assertRaises(ValueError):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        changed = copy.deepcopy(self.document)
        changed["input_digest"] = "0" * 64
        anchor.write_text(planning.canonical_json(changed), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "anchor"):
            self.recover()
        self.assertEqual(self.snapshot(), before)
        anchor.write_bytes(original)
        self.plan_path.unlink()  # The independently preserved anchor is sufficient.
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())

    def test_anchor_publish_failure_never_starts_target_writes(self):
        self.prepare()
        with patch.object(
            application,
            "publish_exclusive",
            side_effect=OSError("Cannot publish original plan anchor"),
        ):
            with self.assertRaises(OSError):
                self.apply()
        self.assertFalse(self.target.exists())
        self.assertFalse(self.journal_path.exists())
        self.assertFalse(application.anchor_path(self.journal_path, self.target).exists())

    def test_recovery_failure_is_retryable_without_overwriting_new_user_edits(self):
        self.prepare()
        self.apply()
        actual = application.restore_file
        calls = 0

        def fail_second(root, entry):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("Injected recovery I/O failure")
            return actual(root, entry)

        with patch.object(application, "restore_file", side_effect=fail_second):
            result = self.recover()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(self.recover()["status"], "recovered")
        self.assertFalse(self.target.exists())

    def test_existing_journal_cannot_be_overwritten(self):
        self.prepare()
        self.journal_path.write_text("Previous recovery evidence", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "new file"):
            self.apply()
        self.assertEqual(
            self.journal_path.read_text(encoding="utf-8"), "Previous recovery evidence"
        )
        self.assertFalse(self.target.exists())

    def test_cli_apply_and_recover_report_pending_and_real_outcomes(self):
        self.prepare()
        with patch.object(planning, "CENTRAL", self.central):
            self.assertEqual(
                cli.main(["apply", str(self.target), "--plan", str(self.plan_path)]), 0
            )
            self.assertTrue(self.target.exists())
            self.assertEqual(
                cli.main(["recover", str(self.target), "--journal", str(self.journal_path)]), 0
            )
        self.assertFalse(self.target.exists())

    def test_user_file_appearing_immediately_before_replace_is_preserved(self):
        self.prepare()
        actual_hash = application.current_hash
        injected = False
        name = self.document["operations"][0]["path"]

        def insert_before_replace(root, relative):
            nonlocal injected
            path = root / relative
            if not injected and relative == name and list(path.parent.glob(".hass-write-*")):
                injected = True
                path.write_text("Concurrent user content", encoding="utf-8")
            return actual_hash(root, relative)

        with patch.object(application, "current_hash", side_effect=insert_before_replace):
            result = self.apply()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(
            (self.target / name).read_text(encoding="utf-8"), "Concurrent user content"
        )
        self.assertFalse(list(self.target.rglob(".hass-write-*")))

    def test_read_error_during_preflight_leaves_no_target_or_recovery_artifacts(self):
        self.adopt_fixture()
        before = self.snapshot()
        self.prepare("adopt")
        with patch.object(
            application, "current_hash", side_effect=OSError("Injected unreadable source")
        ):
            with self.assertRaises(OSError):
                self.apply()
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.journal_path.exists())
        self.assertFalse(application.anchor_path(self.journal_path, self.target).exists())

    def test_parent_symlink_introduced_after_preflight_cannot_receive_writes(self):
        self.prepare()
        outside = self.base / "outside"
        outside.mkdir()
        probe = self.base / "probe-link"
        try:
            probe.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if os.name == "nt" and error.winerror == 1314:
                self.skipTest(
                    "Windows symlink permission unavailable; independent Linux verification required"
                )
            raise
        probe.unlink()
        actual = application.replace_file

        def redirect_parent(root, operation, journal, journal_path):
            root.mkdir()
            (root / ".github").symlink_to(outside, target_is_directory=True)
            return actual(root, operation, journal, journal_path)

        with patch.object(application, "replace_file", side_effect=redirect_parent):
            result = self.apply()
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["applied"], [])
        self.assertEqual(list(outside.iterdir()), [])
        self.assertTrue((self.target / ".github").is_symlink())

    def test_symlink_target_or_journal_alias_is_rejected_before_writes(self):
        self.prepare()
        outside = self.base / "outside"
        outside.mkdir()
        link = self.base / "linked-journals"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            if os.name == "nt" and error.winerror == 1314:
                self.skipTest(
                    "Windows symlink permission unavailable; independent Linux verification required"
                )
            raise
        with self.assertRaisesRegex(ValueError, "symlink"):
            application.apply_plan(
                self.target,
                self.plan_path,
                journal_path=link / "journal.json",
                central=self.central,
            )
        self.assertFalse(self.target.exists())
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

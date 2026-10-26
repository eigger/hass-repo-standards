"""Central release grouping, metadata transaction and privileged writer boundaries."""

import base64
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from standards import reference, update  # noqa: E402

OLD = reference.descriptor("v1.0.1", "a" * 40)
NEW = reference.descriptor("v1.1.0", "b" * 40)
WORKFLOW = """name: Test
'on':
  pull_request: null
  workflow_dispatch: null
jobs:
  test:
    uses: eigger/hass-repo-standards/.github/workflows/python-tests.yml@v1.0.1
"""
DOC = """# Standards

- 표준: https://github.com/eigger/hass-repo-standards/tree/v1.0.1
- Standards release: `v1.0.1`
- Resolved standards SHA: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- Reviewed standards SHA: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`

## Adoption history
Keep this historical SHA aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.
"""


class Repository:
    def __init__(self):
        self.writes = []
        self.config = json.dumps(
            {"repository": "eigger/sample", "standards": OLD, "standards_update": update.PROVIDER}
        )
        self.contents = {
            "config": self.config,
            "doc": DOC,
            "before": WORKFLOW,
            "after": WORKFLOW.replace("v1.0.1", "v1.1.0"),
        }
        self.base = {
            ".hass-standards.json": "config",
            "STANDARDS.md": "doc",
            ".github/workflows/tests.yml": "before",
        }
        self.head = {**self.base, ".github/workflows/tests.yml": "after"}
        self.pr = {
            "state": "open",
            "user": {"login": "dependabot[bot]"},
            "head": {
                "sha": "head",
                "ref": "dependabot/central-standards",
                "repo": {"full_name": "eigger/sample"},
            },
            "base": {"ref": "main", "repo": {"full_name": "eigger/sample"}},
        }
        self.race = False

    def api(self, endpoint, *, payload=None, method=None):
        path = endpoint.removeprefix("repos/eigger/sample/")
        if method:
            self.writes.append((path, payload))
            if path == "git/trees":
                return {"sha": "newtree"}
            if path == "git/commits":
                return {"sha": "newhead"}
            return None
        if path == "repos/eigger/sample":
            return {"default_branch": "main"}
        if path == "pulls/1":
            if self.race and self.writes:
                return {**self.pr, "head": {**self.pr["head"], "sha": "otherhead"}}
            return self.pr
        if path == "commits/main":
            return {"sha": "base"}
        if path == "git/commits/head":
            return {"tree": {"sha": "parent-tree"}}
        if path.startswith("git/trees/"):
            data = self.base if "/base?" in path else self.head
            return {
                "truncated": False,
                "tree": [
                    {"path": p, "sha": sha, "mode": "100644", "type": "blob"}
                    for p, sha in data.items()
                ],
            }
        if path.startswith("git/blobs/"):
            return {
                "encoding": "base64",
                "content": base64.b64encode(
                    self.contents[path.rsplit("/", 1)[1]].encode()
                ).decode(),
            }
        raise AssertionError(endpoint)

    def sync(self, **kwargs):
        return update.sync_pr("eigger/sample", 1, api=self.api, attest=lambda tag: NEW, **kwargs)


class StandardsUpdate(unittest.TestCase):
    def test_atomic_bundle_preserves_history_and_only_writes_metadata(self):
        repo = Repository()
        result = repo.sync()
        self.assertTrue(result["auto_eligible"])
        tree = repo.writes[0][1]
        self.assertEqual(tree["base_tree"], "parent-tree")
        self.assertEqual({e["path"] for e in tree["tree"]}, update.MANAGED)
        doc = next(e["content"] for e in tree["tree"] if e["path"] == "STANDARDS.md")
        self.assertIn("Standards release: v1.1.0", doc)
        self.assertTrue(doc.endswith(DOC.split("## Adoption history")[1]))
        self.assertEqual(
            repo.writes[-1],
            ("actions/workflows/tests.yml/dispatches", {"ref": "dependabot/central-standards"}),
        )
        self.assertIn(
            ("git/refs/heads/dependabot%2Fcentral-standards", {"sha": "newhead", "force": False}),
            repo.writes,
        )

    def test_partial_group_and_unrelated_changes_fail_before_writes(self):
        repo = Repository()
        repo.contents["after"] += (
            "  another:\n    uses: eigger/hass-repo-standards/.github/workflows/dependency-update.yml@v1.0.1\n"
        )
        repo.contents["before"] += (
            "  another:\n    uses: eigger/hass-repo-standards/.github/workflows/dependency-update.yml@v1.0.1\n"
        )
        with self.assertRaisesRegex(ValueError, "Partial"):
            repo.sync()
        self.assertEqual(repo.writes, [])
        repo = Repository()
        repo.contents["after"] += "    with:\n      command: unsafe\n"
        with self.assertRaisesRegex(ValueError, "Non-reference"):
            repo.sync()
        self.assertEqual(repo.writes, [])
        repo = Repository()
        repo.head["script.py"] = "after"
        with self.assertRaisesRegex(ValueError, "unrelated"):
            repo.sync()
        self.assertEqual(repo.writes, [])

    def test_fork_and_human_are_rejected_except_explicit_operator(self):
        repo = Repository()
        repo.pr["head"]["repo"]["full_name"] = "attacker/sample"
        with self.assertRaisesRegex(ValueError, "same-repository"):
            repo.sync(manual=True)
        self.assertEqual(repo.writes, [])
        repo = Repository()
        repo.pr["user"]["login"] = "eigger"
        with self.assertRaises(ValueError):
            repo.sync()
        result = repo.sync(manual=True)
        self.assertTrue(result["updated"])
        self.assertFalse(result["auto_eligible"])

    def test_concurrent_head_never_overwritten(self):
        repo = Repository()
        repo.race = True
        with self.assertRaisesRegex(ValueError, "changed during"):
            repo.sync()
        self.assertFalse(any(path.startswith("git/refs/") for path, _ in repo.writes))

    def test_executable_and_symlink_entries_are_not_hidden(self):
        result = update.tree_files(
            "eigger/sample",
            "head",
            lambda _: {
                "tree": [
                    {"path": "new-link", "sha": "x", "mode": "120000", "type": "blob"},
                    {"path": "executable", "sha": "y", "mode": "100755", "type": "blob"},
                ],
                "truncated": False,
            },
        )
        self.assertEqual(set(result), {"new-link", "executable"})
        with self.assertRaisesRegex(ValueError, "truncated"):
            update.tree_files("eigger/sample", "head", lambda _: {"truncated": True})

    def test_native_group_first_daily_preserves_other_ecosystems(self):
        source = """version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule: {interval: weekly}
  - package-ecosystem: github-actions
    directory: /
    schedule: {interval: weekly, day: monday}
    groups: {all: {patterns: ['*']}}
"""
        result = update.yaml_document(update.configure_dependabot(source))
        self.assertEqual(result["updates"][0]["schedule"], {"interval": "weekly"})
        actions = result["updates"][1]
        self.assertEqual(actions["schedule"], {"interval": "daily"})
        self.assertEqual(list(actions["groups"]), ["central-standards", "all"])
        self.assertEqual(
            update.yaml_document(update.configure_dependabot())["updates"][0]["allow"],
            [{"dependency-name": name} for name in update.DEPENDENCIES],
        )

    def test_release_attestation_requires_immutable_and_peeled_sha(self):
        def api(_):
            return {"tag_name": "v1.1.0", "draft": False, "prerelease": False, "immutable": True}

        lines = "c" * 40 + "\trefs/tags/v1.1.0\n" + "b" * 40 + "\trefs/tags/v1.1.0^{}\n"
        self.assertEqual(
            update.attest_release("v1.1.0", api=api, runner=lambda *a, **kw: lines), NEW
        )
        with self.assertRaisesRegex(ValueError, "immutable"):
            update.attest_release("v1.1.0", api=lambda _: {**api(None), "immutable": False})

    def test_disabled_updates_and_specific_workflow_ignore_are_rejected(self):
        data = update.yaml_document(update.configure_dependabot())
        item = data["updates"][0]
        for field, value in (
            ("open-pull-requests-limit", 0),
            ("target-branch", "other"),
            ("rebase-strategy", "disabled"),
        ):
            with self.subTest(field=field):
                item[field] = value
                with self.assertRaises(ValueError):
                    update.validate_dependabot(data)
                del item[field]
        item["ignore"] = [
            {"dependency-name": update.PREFIX + ".github/workflows/dependency-update.yml"}
        ]
        with self.assertRaisesRegex(ValueError, "ignore policy"):
            update.validate_dependabot(data)

    def test_metadata_fallback_requires_opt_in_release_and_no_explicit_mismatch(self):
        config = {"standards": NEW, "standards_update": update.PROVIDER}
        self.assertEqual(reference.metadata_input(config), "b" * 40)
        self.assertEqual(reference.metadata_input(config, "wrong"), "wrong")
        self.assertIsNone(reference.metadata_input({"standards": NEW}))
        self.assertIsNone(
            reference.metadata_input({**config, "standards": reference.descriptor("b" * 40)})
        )

    def test_major_is_never_auto_eligible(self):
        repo = Repository()
        repo.contents["after"] = repo.contents["after"].replace("v1.1.0", "v2.0.0")
        with patch.object(update, "metadata_changes", return_value={}):
            result = repo.sync()
        self.assertFalse(result["auto_eligible"])


if __name__ == "__main__":
    unittest.main()

"""Behavioral gates for privileged manifest automation; GitHub is the only mocked boundary."""

import base64
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import install_dependency_automation as installer  # noqa: E402
from standards import manifest_merge as merge  # noqa: E402
from standards import update

ROOT = Path(__file__).resolve().parents[1]
REPO = "eigger/sample"
OLD = {
    "domain": "sample",
    "version": "1.0.0",
    "requirements": ["blesession>=0.9.1", "imagespec[datamatrix]>=1.1.1"],
}
NEW = {**OLD, "requirements": ["blesession>=0.10.0", "imagespec[datamatrix]>=1.2.0"]}
WORKFLOW = "name: Test\n'on':\n  pull_request: null\n  workflow_dispatch: null\njobs: {}\n"


class GitHub:
    def __init__(self):
        self.writes = []
        self.deleted = []
        self.pr = {
            "number": 1,
            "state": "open",
            "draft": False,
            "user": {"login": merge.BOT},
            "head": {"sha": "head", "ref": merge.BRANCH, "repo": {"full_name": REPO}},
            "base": {"ref": "main", "repo": {"full_name": REPO}},
        }
        self.files = [{"filename": "custom_components/sample/manifest.json", "status": "modified"}]
        self.base, self.head = "base", "head"
        self.ahead = 1
        self.new = copy.deepcopy(NEW)
        self.manifest_mode = "100644"
        self.truncated = False
        self.run_conclusion = "success"
        self.run_status = "completed"
        self.fresh = True
        self.dispatched = set()
        self.merged = False
        self.branch_tip = "head"
        self.workflow_text = WORKFLOW
        self.merge_result = True
        self.merge_states = ["CLEAN"]
        self.merge_error = None
        self.sleeps = []
        self.pr_runs = {}

    def pr_run(self, **overrides):
        return {
            "id": 1,
            "head_sha": self.head,
            "head_branch": merge.BRANCH,
            "head_repository": {"full_name": REPO},
            "event": "pull_request",
            "pull_requests": [],
            "status": "completed",
            "conclusion": "action_required",
            "html_url": "https://github.com/pr-check",
            **overrides,
        }

    def api(self, endpoint, *, method=None, payload=None):
        p = endpoint.removeprefix("repos/" + REPO + "/")
        if endpoint == "graphql":
            gate = self.merge_states[0]
            if len(self.merge_states) > 1:
                self.merge_states.pop(0)
            return {
                "data": {
                    "repository": {
                        "pullRequest": {
                            "state": self.pr["state"].upper(),
                            "headRefOid": self.pr["head"]["sha"],
                            "baseRefOid": self.base,
                            "mergeStateStatus": gate,
                        }
                    }
                }
            }
        if method:
            self.writes.append((method, p, payload))
            if p.endswith("/dispatches"):
                self.dispatched.add(p.split("/")[2])
            if p == "pulls/1/merge":
                if self.merge_error is not None:
                    message, self.merge_error = self.merge_error, None
                    raise subprocess.CalledProcessError(1, ["gh", "api"], stderr=message)
                if self.merge_result:
                    self.merged = True
                    self.pr.update(state="closed", merged_at="today")
                return {"merged": self.merge_result, "sha": "squash"}
            return None
        if endpoint == "repos/" + REPO:
            return {"default_branch": "main"}
        if p == "pulls/1":
            return self.pr
        if p == "git/ref/heads/main":
            return {"object": {"sha": self.base}}
        if p.startswith("git/ref/heads/bot"):
            return {"object": {"sha": self.branch_tip}}
        if p.startswith("compare/"):
            return {"merge_base_commit": {"sha": self.base}, "ahead_by": self.ahead}
        if p.startswith("git/trees/"):
            head = p.split("/")[2].split("?")[0] != self.base
            return {
                "truncated": self.truncated,
                "tree": [
                    {
                        "path": "custom_components/sample/manifest.json",
                        "sha": "new" if head else "old",
                        "mode": self.manifest_mode,
                        "type": "blob",
                    },
                    *[
                        {
                            "path": ".github/workflows/" + n,
                            "sha": "workflow",
                            "mode": "100644",
                            "type": "blob",
                        }
                        for n in ["tests.yml", "standards.yml", "validate.yml"]
                    ],
                ],
            }
        if p.startswith("git/blobs/"):
            content = {
                "new": json.dumps(self.new),
                "old": json.dumps(OLD),
                "workflow": self.workflow_text,
            }[p.split("/")[-1]]
            return {"encoding": "base64", "content": base64.b64encode(content.encode()).decode()}
        if "/runs?event=pull_request" in p:
            assert "&branch=bot%2Fmanifest-dependencies&head_sha=head&" in p, p
            return {"workflow_runs": self.pr_runs.get(p.split("/")[2], [])}
        if "/runs?" in p:
            dispatched = p.split("/")[2] in self.dispatched and self.fresh
            return {
                "workflow_runs": [
                    {
                        "id": 2 if dispatched else 1,
                        "head_sha": "head",
                        "head_branch": "hass-dependency-validation/test",
                        "event": "workflow_dispatch",
                        "status": self.run_status,
                        "conclusion": self.run_conclusion,
                        "html_url": "https://github.com/run",
                    }
                ]
            }
        raise AssertionError(endpoint)

    def pages(self, endpoint):
        if "/files?" in endpoint:
            return self.files
        if "/matching-refs/" in endpoint:
            return [{"ref": "refs/heads/" + merge.BRANCH, "object": {"sha": "head"}}]
        if "/pulls?" in endpoint:
            return [self.pr]
        raise AssertionError(endpoint)

    def run(self, **kwargs):
        return merge.merge(
            REPO,
            1,
            "sample",
            ["blesession", "imagespec"],
            api=self.api,
            listing=self.pages,
            delete=lambda repo, ref, head: self.deleted.append((ref, head)),
            validation_ref="hass-dependency-validation/test",
            sleep=self.sleeps.append,
            **kwargs,
        )


class ManifestPolicy(unittest.TestCase):
    def test_same_major_updates_preserve_all_other_data(self):
        self.assertEqual(
            merge.validate_manifest(OLD, NEW, ["blesession", "imagespec"]),
            ["blesession", "imagespec"],
        )
        old = {"requirements": ['ImageSpec[datamatrix] >= 1.1; python_version >= "3.9"']}
        new = {"requirements": ['ImageSpec[datamatrix] >=1.2; python_version >= "3.9"']}
        self.assertEqual(merge.validate_manifest(old, new, ["imagespec"]), ["imagespec"])

    def test_rejects_unrelated_changes_and_noneligible_versions(self):
        examples = [
            {**NEW, "version": "2"},
            {**NEW, "requirements": NEW["requirements"] + ["evil>=1"]},
            {**OLD},
            {**NEW, "requirements": ["blesession>=1.0.0", NEW["requirements"][1]]},
            {**NEW, "requirements": ["blesession>=0.9.0", NEW["requirements"][1]]},
            {**NEW, "requirements": ["blesession>=0.10.0rc1", NEW["requirements"][1]]},
            {**NEW, "requirements": ["blesession>=0.10.0+local", NEW["requirements"][1]]},
            {**NEW, "requirements": ["blesession==0.10.0", NEW["requirements"][1]]},
            {**NEW, "requirements": [NEW["requirements"][0], "imagespec>=1.2.0"]},
        ]
        for after in examples:
            with self.subTest(after=after), self.assertRaises(ValueError):
                merge.validate_manifest(OLD, after, ["blesession", "imagespec"])
        with self.assertRaises(ValueError):
            merge.validate_manifest(OLD, NEW, ["arbitrary"])


class Controller(unittest.TestCase):
    def test_dispatches_fresh_checks_squashes_exact_head_then_deletes_branch(self):
        gh = GitHub()
        result = gh.run()
        self.assertEqual(result["merge"], "squash")
        self.assertEqual(len(gh.dispatched), 3)
        writes = gh.writes
        self.assertEqual(
            writes[-1], ("PUT", "pulls/1/merge", {"merge_method": "squash", "sha": "head"})
        )
        self.assertEqual(
            gh.deleted, [(merge.BRANCH, "head"), ("hass-dependency-validation/test", "head")]
        )

    def test_approval_required_defers_before_dispatch_or_merge(self):
        gh = GitHub()
        gh.merge_states = ["BLOCKED"]
        gh.pr_runs["tests.yml"] = [gh.pr_run()]
        self.assertEqual(
            gh.run(),
            {
                "pr": 1,
                "head": "head",
                "status": "approval_pending",
                "runs": [{"workflow": "tests.yml", "url": "https://github.com/pr-check"}],
            },
        )
        self.assertEqual(gh.pr["state"], "open")
        self.assertFalse(gh.writes or gh.deleted or gh.sleeps)

    def test_optional_approval_does_not_defer_a_clean_pr(self):
        gh = GitHub()
        gh.pr_runs["tests.yml"] = [gh.pr_run()]
        self.assertEqual(gh.run()["merge"], "squash")

    def test_approval_appearing_during_merge_poll_cleans_only_validation_ref(self):
        gh = GitHub()
        gh.merge_states = ["BLOCKED"]
        original = gh.api

        def api(endpoint, **kwargs):
            if endpoint == "graphql":
                gh.pr_runs["tests.yml"] = [gh.pr_run()]
            return original(endpoint, **kwargs)

        gh.api = api
        self.assertEqual(gh.run()["status"], "approval_pending")
        self.assertEqual(len(gh.dispatched), 3)
        self.assertEqual(gh.deleted, [("hass-dependency-validation/test", "head")])
        self.assertFalse(gh.merged or gh.sleeps)

    def test_unrelated_or_superseded_approval_does_not_defer(self):
        gh = GitHub()
        gh.pr_runs["tests.yml"] = [
            gh.pr_run(),
            gh.pr_run(id=2, status="in_progress", conclusion=None),
            gh.pr_run(id=3, head_sha="old"),
            gh.pr_run(id=4, head_branch="other"),
            gh.pr_run(id=5, head_repository={"full_name": "fork/sample"}),
            gh.pr_run(id=6, pull_requests=[{"number": 2}]),
            gh.pr_run(id=7, event="workflow_dispatch"),
        ]
        self.assertEqual(gh.run()["merge"], "squash")

    def test_pr_validator_failure_is_not_hidden_by_other_approval_wait(self):
        gh = GitHub()
        gh.pr_runs["standards.yml"] = [gh.pr_run()]
        gh.pr_runs["tests.yml"] = [gh.pr_run(conclusion="failure")]
        gh.merge_states = ["BLOCKED"]
        times = iter([0, 2])
        with self.assertRaisesRegex(TimeoutError, "Required PR merge"):
            gh.run(clock=lambda: next(times), timeout=1)
        self.assertFalse(gh.merged)

    def test_identity_guards_never_dispatch_or_merge(self):
        for field, value in [("user", {"login": "human"}), ("draft", True), ("state", "closed")]:
            gh = GitHub()
            gh.pr[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gh.run()
            self.assertFalse(gh.writes)
        for side, key, value in [
            ("head", "ref", "other"),
            ("head", "repo", {"full_name": "attacker/fork"}),
            ("base", "ref", "other"),
        ]:
            gh = GitHub()
            gh.pr[side][key] = value
            with self.subTest(side=side, key=key), self.assertRaises(ValueError):
                gh.run()
            self.assertFalse(gh.writes)

    def test_rejects_extra_file_rename_modes_truncation_and_non_dispatchable_checks(self):
        for mutation in ["extra", "rename", "mode", "truncated", "behind", "workflow"]:
            gh = GitHub()
            if mutation == "extra":
                gh.files.append({"filename": "danger.py", "status": "added"})
            if mutation == "rename":
                gh.files[0]["status"] = "renamed"
            if mutation == "mode":
                gh.manifest_mode = "120000"
            if mutation == "truncated":
                gh.truncated = True
            if mutation == "behind":
                gh.ahead = 2
            if mutation == "workflow":
                gh.workflow_text = WORKFLOW.replace("  workflow_dispatch: null\n", "")
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                gh.run()
            self.assertFalse(gh.writes)

    def test_failed_cancelled_skipped_checks_never_merge(self):
        for outcome in ["failure", "cancelled", "skipped", "neutral", "timed_out"]:
            gh = GitHub()
            gh.run_conclusion = outcome
            with self.subTest(outcome=outcome), self.assertRaises(ValueError):
                gh.run()
            self.assertFalse(gh.merged)
            self.assertFalse(any(w[0] == "DELETE" for w in gh.writes))

    def test_old_success_or_pending_run_cannot_satisfy_gate(self):
        for stale in [True, False]:
            gh = GitHub()
            if stale:
                gh.fresh = False
            else:
                gh.run_status = "in_progress"
            times = iter([0, 2])
            with self.subTest(stale=stale), self.assertRaises(TimeoutError):
                gh.run(clock=lambda: next(times), timeout=1)
            self.assertFalse(gh.merged)

    def test_changed_head_or_base_after_validation_prevents_merge(self):
        for change in ["head", "base"]:
            gh = GitHub()
            original = gh.api
            count = 0

            def racing(endpoint, **kwargs):
                nonlocal count
                if endpoint.endswith("/pulls/1"):
                    count += 1
                    if count == 2:
                        if change == "head":
                            gh.pr["head"]["sha"] = "other"
                        else:
                            gh.base = "other"
                return original(endpoint, **kwargs)

            with self.subTest(change=change), self.assertRaises((ValueError, AssertionError)):
                merge.merge(
                    REPO,
                    1,
                    "sample",
                    ["blesession", "imagespec"],
                    api=racing,
                    listing=gh.pages,
                    delete=lambda *args: gh.deleted.append(args),
                    validation_ref="hass-dependency-validation/test",
                )
            self.assertFalse(gh.merged)

    def test_merge_refusal_preserves_branch(self):
        gh = GitHub()
        gh.merge_result = False
        with self.assertRaises(ValueError):
            gh.run()
        self.assertFalse(any(w[0] == "DELETE" for w in gh.writes))

    def test_cleanup_preserves_open_unmerged_human_or_recreated_branches(self):
        for mode in ["open", "unmerged", "human", "recreated"]:
            gh = GitHub()
            gh.pr.update(state="closed", merged_at="today")
            if mode == "open":
                gh.pr["state"] = "open"
            if mode == "unmerged":
                gh.pr["merged_at"] = None
            if mode == "human":
                gh.pr["user"]["login"] = "human"
            if mode == "recreated":
                gh.branch_tip = "new-head"
            with self.subTest(mode=mode):
                self.assertFalse(
                    merge.cleanup(
                        REPO,
                        api=gh.api,
                        listing=gh.pages,
                        delete=lambda *args: gh.deleted.append(args),
                    )
                )
            self.assertFalse(gh.writes)

    def test_successful_head_checks_wait_for_required_pr_merge_checks(self):
        gh = GitHub()
        gh.merge_states = ["BLOCKED", "UNKNOWN", "CLEAN"]
        gh.run()
        self.assertEqual(gh.sleeps, [15, 15])
        self.assertEqual(len([w for w in gh.writes if w[0] == "PUT"]), 1)

    def test_blocked_pr_conditions_timeout_without_merge(self):
        gh = GitHub()
        gh.merge_states = ["BLOCKED"]
        times = iter([0, 2])
        with self.assertRaisesRegex(TimeoutError, "Required PR merge"):
            gh.run(clock=lambda: next(times), timeout=1)
        self.assertFalse(gh.merged)

    def test_merge_readiness_race_is_rechecked_without_bypassing_requirements(self):
        gh = GitHub()
        gh.merge_error = "gh: required status check still pending (HTTP 405)"
        gh.run()
        self.assertEqual(gh.sleeps, [15])
        writes = [w for w in gh.writes if w[0] == "PUT"]
        self.assertEqual(len(writes), 2)
        self.assertTrue(all(w[2]["sha"] == "head" for w in writes))

    def test_pr_head_or_base_drift_while_blocked_aborts_without_merge(self):
        for field in ["head", "base"]:
            gh = GitHub()
            gh.merge_states = ["BLOCKED", "CLEAN"]
            original = gh.api
            polls = 0

            def api(endpoint, **kwargs):
                nonlocal polls
                if endpoint == "graphql":
                    polls += 1
                    if polls == 2:
                        if field == "head":
                            gh.pr["head"]["sha"] = "advanced"
                        else:
                            gh.base = "advanced"
                return original(endpoint, **kwargs)

            gh.api = api
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(ValueError, "identity or base changed"),
            ):
                gh.run()
            self.assertFalse(gh.merged)

    def test_conflict_then_new_head_is_never_retried_with_new_sha(self):
        gh = GitHub()
        gh.merge_error = "gh: Head branch was modified (HTTP 409)"
        original = gh.api

        def api(endpoint, **kwargs):
            try:
                return original(endpoint, **kwargs)
            except subprocess.CalledProcessError:
                gh.pr["head"]["sha"] = "advanced"
                raise

        gh.api = api
        with self.assertRaisesRegex(ValueError, "identity or base changed"):
            gh.run()
        self.assertFalse(gh.merged)
        self.assertEqual(len([w for w in gh.writes if w[0] == "PUT"]), 1)

    def test_merge_permission_error_is_reported_without_retry(self):
        gh = GitHub()
        gh.merge_error = "gh: Resource not accessible by integration (HTTP 403)"
        with self.assertRaisesRegex(RuntimeError, "HTTP 403"):
            gh.run()
        self.assertFalse(gh.merged)
        self.assertEqual(gh.sleeps, [])

    def test_delete_ref_uses_atomic_lease_and_propagates_rejection(self):
        calls = []
        merge.delete_ref(REPO, merge.BRANCH, "head", runner=lambda args, **kw: calls.append(args))
        self.assertIn("--force-with-lease=refs/heads/bot/manifest-dependencies:head", calls[0])
        self.assertEqual(calls[0][-1], ":refs/heads/bot/manifest-dependencies")

        def rejected(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0])

        with self.assertRaises(subprocess.CalledProcessError):
            merge.delete_ref(REPO, merge.BRANCH, "head", runner=rejected)

    def test_immutable_tree_diff_rejects_hidden_workflow_changes(self):
        gh = GitHub()
        original = gh.api

        def api(endpoint, **kwargs):
            result = original(endpoint, **kwargs)
            if "/git/trees/head?" in endpoint:
                result["tree"].append(
                    {"path": "evil.py", "sha": "new", "mode": "100644", "type": "blob"}
                )
            return result

        with self.assertRaisesRegex(ValueError, "outside the manifest"):
            merge.proposal(
                REPO, 1, "sample", ["blesession", "imagespec"], api=api, listing=gh.pages
            )
        self.assertFalse(gh.writes)

    def test_installer_plans_caller_and_rejects_invalid_input_before_writing(self):
        templates = ROOT / "templates/integration"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github/workflows").mkdir(parents=True)
            source = root / ".github/workflows/update_dependencies.yml"
            template = (templates / ".github/workflows/update_dependencies.yml").read_text()
            source.write_text(template)
            with patch.object(update, "bootstrap_changes", return_value={}):
                result = installer.changes(root, {"tag": "v1.3.0"}, templates)
                self.assertIn("@v1.3.0", result[installer.CALLER])
                self.assertFalse((root / installer.CALLER).exists())
                for bad in ["{}", '["evil"]', '["imagespec", "imagespec"]']:
                    source.write_text(template.replace('["imagespec", "blesession"]', bad))
                    with self.subTest(bad=bad), self.assertRaises(ValueError):
                        installer.changes(root, {"tag": "v1.3.0"}, templates)
                source.write_text(template.replace("domain: example", "domain: Unicode한글"))
                with self.assertRaises(ValueError):
                    installer.changes(root, {"tag": "v1.3.0"}, templates)

    def test_workflow_uses_default_branch_and_pinned_tools_not_pr_checkout(self):
        workflow = update.yaml_document(
            (ROOT / ".github/workflows/manifest-dependency-merge.yml").read_text()
        )
        job = workflow["jobs"]["merge"]
        self.assertEqual(
            job["permissions"], {"contents": "write", "pull-requests": "write", "actions": "write"}
        )
        steps = job["steps"]
        checkout = [s["with"] for s in steps if "actions/checkout@" in s.get("uses", "")]
        self.assertEqual(checkout[0]["ref"], "${{ steps.repository.outputs.branch }}")
        self.assertEqual(checkout[1]["ref"], "${{ steps.reference.outputs.sha }}")
        self.assertTrue(all(c["persist-credentials"] is False for c in checkout))
        caller = update.yaml_document(
            (ROOT / "templates/integration/.github/workflows/merge_dependencies.yml").read_text()
        )
        self.assertEqual(set(caller["on"]), {"workflow_run", "schedule", "workflow_dispatch"})
        self.assertEqual(caller["on"]["workflow_run"]["workflows"], ["Update dependencies"])


if __name__ == "__main__":
    unittest.main()

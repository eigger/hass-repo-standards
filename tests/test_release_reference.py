"""Regression coverage for immutable release attestation boundaries."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from standards import reference  # noqa: E402

SHA = "a" * 40


class Result:
    def __init__(self, text):
        self.stdout = text


class ReleaseReference(unittest.TestCase):
    def test_legacy_sha_and_exact_release_are_distinct_descriptors(self):
        self.assertEqual(reference.descriptor(SHA), {"kind": "sha", "resolved_sha": SHA})
        release = reference.descriptor("v1.0.0", SHA)
        self.assertEqual(reference.caller_ref(release), "v1.0.0")
        self.assertEqual(reference.resolved_sha(release), SHA)
        with self.assertRaisesRegex(ValueError, "exact vX.Y.Z"):
            reference.descriptor("v1", SHA)

    def test_remote_attestation_requires_immutable_published_release_and_peeled_commit(self):
        calls = []

        def runner(args, **kwargs):
            calls.append(args)
            if args[0] == "gh":
                return Result(
                    json.dumps(
                        {
                            "tag_name": "v1.0.0",
                            "draft": False,
                            "prerelease": False,
                            "immutable": True,
                        }
                    )
                )
            return Result(SHA + "\trefs/tags/v1.0.0\n" + SHA + "\trefs/tags/v1.0.0^{}\n")

        value = reference.descriptor("v1.0.0", SHA)
        result = reference.verify_remote("eigger/hass-repo-standards", value, runner=runner)
        self.assertEqual(result["verified"], "remote")
        self.assertEqual(len(calls), 2)

        with tempfile.TemporaryDirectory() as directory:
            proof = Path(directory) / "verified.json"
            reference.write_verification(proof, result)
            self.assertEqual(
                reference.read_verification(proof, "eigger/hass-repo-standards", value), result
            )
            proof.write_text(json.dumps({**result, "resolved_sha": "b" * 40}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "does not match"):
                reference.read_verification(proof, "eigger/hass-repo-standards", value)

    def test_draft_or_moved_peeled_tag_is_rejected(self):
        value = reference.descriptor("v1.0.0", SHA)

        def draft(args, **kwargs):
            if args[0] == "gh":
                return Result(
                    json.dumps(
                        {
                            "tag_name": "v1.0.0",
                            "draft": True,
                            "prerelease": False,
                            "immutable": True,
                        }
                    )
                )
            self.fail("git must not run for a draft")

        with self.assertRaisesRegex(ValueError, "published"):
            reference.verify_remote("eigger/hass-repo-standards", value, runner=draft)

        def moved(args, **kwargs):
            if args[0] == "gh":
                return Result(
                    json.dumps(
                        {
                            "tag_name": "v1.0.0",
                            "draft": False,
                            "prerelease": False,
                            "immutable": True,
                        }
                    )
                )
            return Result("b" * 40 + "\trefs/tags/v1.0.0^{}\n")

        with self.assertRaisesRegex(ValueError, "peeled"):
            reference.verify_remote("eigger/hass-repo-standards", value, runner=moved)


if __name__ == "__main__":
    unittest.main()

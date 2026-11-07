"""Structure contract for the reusable dashboard-card workflows (CARD-03/04)."""

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github/workflows"


def load(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["on"] = data.pop(True, data.get("on"))  # YAML 1.1 parses `on` as True
    return data


class CardWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.check = load(WORKFLOWS / "card-check.yml")
        self.release = load(WORKFLOWS / "card-release.yml")

    def steps(self, workflow):
        return [s for job in workflow["jobs"].values() for s in job.get("steps", [])]

    def test_inputs_have_no_integration_requirements(self):
        for workflow in (self.check, self.release):
            inputs = workflow["on"]["workflow_call"]["inputs"]
            self.assertEqual(
                {"node-version", "check-script", "lint-script", "test-script", "build-script"}
                | {"bundle-path"},
                set(inputs),
            )
            self.assertTrue(inputs["bundle-path"]["required"])
            self.assertFalse(
                [k for k, v in inputs.items() if k != "bundle-path" and v.get("required")]
            )

    def test_permissions_are_split(self):
        self.assertEqual({"contents": "read"}, self.check["permissions"])
        self.assertEqual({"contents": "read"}, self.release["permissions"])
        jobs = self.release["jobs"]
        self.assertEqual({"contents": "read"}, jobs["validate"]["permissions"])
        self.assertEqual({"contents": "write"}, jobs["release"]["permissions"])
        self.assertEqual("validate", jobs["release"]["needs"])

    def test_inputs_are_never_interpolated_into_shell(self):
        for workflow in (self.check, self.release):
            for step in self.steps(workflow):
                self.assertNotIn("${{", step.get("run", ""), step.get("name"))

    def test_external_actions_are_pinned_and_checkout_is_read_only(self):
        for workflow in (self.check, self.release):
            for step in self.steps(workflow):
                use = step.get("uses")
                if not use:
                    continue
                self.assertRegex(use, r"@[0-9a-f]{40}$", use)
                if use.startswith("actions/checkout@"):
                    self.assertIs(step["with"]["persist-credentials"], False)

    def test_release_is_tag_gated_and_attaches_the_validated_bundle(self):
        text = (WORKFLOWS / "card-release.yml").read_text(encoding="utf-8")
        self.assertIn("--verify-tag", text)
        self.assertNotIn("--clobber", text)
        self.assertIn("package.json", text)
        self.assertTrue(re.search(r"ref_type", text))
        download = [s for s in self.steps(self.release) if "download-artifact" in s.get("uses", "")]
        self.assertEqual(1, len(download))

    def test_jobs_have_timeouts(self):
        for workflow in (self.check, self.release):
            for job in workflow["jobs"].values():
                self.assertTrue(job["timeout-minutes"])


if __name__ == "__main__":
    unittest.main()

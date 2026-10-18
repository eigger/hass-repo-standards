"""Exercise the exact inline shared-CI gate before any repository checkout."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import yaml  # noqa: E402
from check_repository import Loader  # noqa: E402


@contextmanager
def working_directory(path):
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


class PayloadWorkflowGate(unittest.TestCase):
    def run_gate(self, requirement, profile="ha", reference="a" * 40, reserved=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            component = root / "custom_components/example"
            component.mkdir(parents=True)
            (component / "manifest.json").write_text(json.dumps({"requirements": [requirement]}))
            if reserved:
                (root / ".hass-standards-tools").mkdir()
                (root / ".hass-standards-tools/user-file").write_text("keep")
            workflow = yaml.load(
                (ROOT / ".github/workflows/python-tests.yml").read_text(), Loader=Loader
            )
            gate = next(
                step["run"]
                for step in workflow["jobs"]["test"]["steps"]
                if step.get("id") == "payload"
            )
            script = gate.split("\n", 1)[1].rsplit("PAYLOAD", 1)[0]
            output = root / "output"
            with (
                working_directory(root),
                patch.dict(
                    os.environ,
                    {
                        "DOMAIN": "example",
                        "TEST_PROFILE": profile,
                        "STANDARDS_REF": reference,
                        "GITHUB_OUTPUT": str(output),
                    },
                ),
            ):
                exec(compile(script, "shared-workflow-payload-gate", "exec"), {})
            return output.read_text()

    def test_inactive_marker_keeps_scaffold_but_no_runtime_coverage(self):
        self.assertEqual(
            self.run_gate('imagespec[extra]>=1.0.1; python_version >= "99"', reference=""),
            "required=true\nactive=false\n",
        )

    def test_unit_profile_does_not_enable_contract(self):
        self.assertEqual(
            self.run_gate("imagespec>=1.0.1", profile="unit", reference=""),
            "required=false\nactive=false\n",
        )

    def test_active_contract_requires_real_ref_and_absent_reserved_path(self):
        self.assertEqual(self.run_gate("imagespec==1.0.1"), "required=true\nactive=true\n")
        with self.assertRaisesRegex(ValueError, "full standards-ref"):
            self.run_gate("imagespec>=1.0.1", reference="main")
        with self.assertRaisesRegex(ValueError, "preserve caller files"):
            self.run_gate("imagespec>=1.0.1", reserved=True)

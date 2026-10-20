"""Exercise optional upstream source validation without network or Docker dependencies."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_repository  # noqa: E402

WORKFLOW = ROOT / ".github/workflows/validate-integration.yml"
SHA = "ec18d8b25d1ee39aa8b85a72a170e42bee33228c"


class HassfestSource(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.caller = self.root / "caller"
        self.caller.mkdir()
        self.manifest = self.caller / "manifest.json"
        self.manifest.write_text('{"categories":["computers_network.printers"]}')
        self.original = self.manifest.read_bytes()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.commands = self.root / "commands.jsonl"
        program = """#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
with open(os.environ["COMMAND_LOG"], "a") as stream:
    stream.write(json.dumps([Path(sys.argv[0]).name, *sys.argv[1:]])+"\\n")
if Path(sys.argv[0]).name == "git":
    if sys.argv[1] == "init":
        Path(sys.argv[2]).mkdir()
    if sys.argv[-2:] == ["rev-parse", "HEAD"]:
        print(os.environ.get("ACTUAL_HEAD", os.environ["HASSFEST_CORE_REF"]))
    if "fetch" in sys.argv and os.environ.get("FAIL_FETCH"):
        sys.exit(17)
else:
    sys.exit(int(os.environ.get("DOCKER_EXIT", "0")))
"""
        for command in ("git", "docker"):
            path = self.bin / command
            path.write_text(program)
            path.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
            "RUNNER_TEMP": str(self.root),
            "GITHUB_RUN_ID": "123",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_WORKSPACE": str(self.caller),
            "HASSFEST_CORE_REF": SHA,
            "HASSFEST_IMAGE": "hassfest-core:" + SHA,
            "COMMAND_LOG": str(self.commands),
        }
        self.data = yaml.load(WORKFLOW.read_text(), Loader=check_repository.Loader)
        self.steps = self.data["jobs"]["hassfest"]["steps"]

    def run_step(self, name, **environment):
        step = next(step for step in self.steps if step.get("name") == name)
        return subprocess.run(
            ["bash", "-e", "-o", "pipefail", "-c", step["run"]],
            env={**self.env, **environment},
            cwd=self.caller,
            capture_output=True,
            text=True,
            check=False,
        )

    def calls(self):
        return [json.loads(line) for line in self.commands.read_text().splitlines()]

    def test_default_is_still_official_action_with_exclusive_source_branch(self):
        spec = self.data["on"]["workflow_call"]["inputs"]["hassfest-core-ref"]
        self.assertEqual(spec["default"], "")
        self.assertFalse(spec["required"])
        default = next(
            step
            for step in self.steps
            if "home-assistant/actions/hassfest@" in step.get("uses", "")
        )
        self.assertEqual(default["if"], "inputs.hassfest-core-ref == ''")
        for step in self.steps:
            if "run" in step:
                self.assertEqual(step["if"], "inputs.hassfest-core-ref != ''")
                self.assertNotIn("continue-on-error", step)
        self.assertEqual(check_repository.check_hassfest_source_contract(self.data), [])

    def test_rejects_branch_short_sha_and_shell_text_before_git(self):
        for ref in ("dev", SHA[:7], SHA.upper(), "a" * 39, SHA + "\n", "$(touch injected)"):
            with self.subTest(ref=ref):
                result = self.run_step(
                    "Fetch reviewed upstream Hassfest source", HASSFEST_CORE_REF=ref
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.commands.exists())
                self.assertFalse((self.caller / "injected").exists())

    def test_exact_source_fetch_and_original_caller_mount(self):
        for name in (
            "Fetch reviewed upstream Hassfest source",
            "Build official Hassfest Dockerfile",
            "Validate caller with reviewed upstream Hassfest",
        ):
            self.assertEqual(self.run_step(name).returncode, 0)
        calls = self.calls()
        self.assertIn(
            [
                "git",
                "-C",
                str(self.root / "hassfest-core-123-1"),
                "remote",
                "add",
                "origin",
                "https://github.com/home-assistant/core.git",
            ],
            calls,
        )
        self.assertIn(
            [
                "git",
                "-C",
                str(self.root / "hassfest-core-123-1"),
                "fetch",
                "--depth=1",
                "origin",
                SHA,
            ],
            calls,
        )
        build = next(call for call in calls if call[:2] == ["docker", "build"])
        self.assertIn(
            str(self.root / "hassfest-core-123-1/script/hassfest/docker/Dockerfile"), build
        )
        run = next(call for call in calls if call[:2] == ["docker", "run"])
        self.assertEqual(
            run,
            [
                "docker",
                "run",
                "--rm",
                "--volume",
                str(self.caller) + ":/github/workspace",
                "hassfest-core:" + SHA,
            ],
        )
        self.assertEqual(self.manifest.read_bytes(), self.original)
        self.assertEqual(sorted(p.name for p in self.caller.iterdir()), ["manifest.json"])

    def test_fetch_failure_and_wrong_head_fail_closed(self):
        self.assertNotEqual(
            self.run_step("Fetch reviewed upstream Hassfest source", FAIL_FETCH="1").returncode, 0
        )
        # A distinct runner attempt is a new reserved source path.
        result = self.run_step(
            "Fetch reviewed upstream Hassfest source", GITHUB_RUN_ATTEMPT="2", ACTUAL_HEAD="a" * 40
        )
        self.assertNotEqual(result.returncode, 0)

    def test_collision_and_symlink_are_preserved(self):
        reserved = self.root / "hassfest-core-123-1"
        reserved.mkdir()
        marker = reserved / "user-data"
        marker.write_text("retain")
        self.assertNotEqual(self.run_step("Fetch reviewed upstream Hassfest source").returncode, 0)
        self.assertEqual(marker.read_text(), "retain")
        self.assertFalse(self.commands.exists())
        marker.unlink()
        reserved.rmdir()
        reserved.symlink_to(self.root / "missing")
        self.assertNotEqual(self.run_step("Fetch reviewed upstream Hassfest source").returncode, 0)
        self.assertTrue(reserved.is_symlink())

    def test_docker_build_and_validation_errors_propagate(self):
        for name in (
            "Build official Hassfest Dockerfile",
            "Validate caller with reviewed upstream Hassfest",
        ):
            with self.subTest(name=name):
                self.assertEqual(self.run_step(name, DOCKER_EXIT="29").returncode, 29)
        self.assertEqual(self.manifest.read_bytes(), self.original)

    def test_contract_checker_detects_weakened_branches(self):
        data = copy.deepcopy(self.data)
        data["jobs"]["hassfest"]["steps"][-1]["continue-on-error"] = True
        self.assertTrue(check_repository.check_hassfest_source_contract(data))
        data = copy.deepcopy(self.data)
        data["jobs"]["hassfest"]["steps"][-1]["if"] = "always()"
        self.assertTrue(check_repository.check_hassfest_source_contract(data))


if __name__ == "__main__":
    unittest.main()

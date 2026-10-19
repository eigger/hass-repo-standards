"""T6 actual local CLI scenarios. Synthetic metadata is not HA/device adoption evidence."""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_integration_planning as fixtures
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests/fixtures/scaffold"


class IntegrationScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.IntegrationPlanning.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.IntegrationPlanning.tearDownClass.__func__(cls)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="standards-T6-scenario-")
        self.addCleanup(self.directory.cleanup)
        self.base = Path(self.directory.name)
        self.target = self.base / "target"
        self.counter = 0

    def write(self, relative, content):
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def input_path(self, data):
        self.counter += 1
        path = self.base / f"input-{self.counter}.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def run_cli(self, *args, expected=0, checker=False):
        script = "check_integration.py" if checker else "manage_integration.py"
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(self.central / "scripts" / script), *map(str, args)],
            capture_output=True,
            encoding="utf-8",
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0", PYTHONDONTWRITEBYTECODE="1"),
            timeout=120,
        )
        diagnostic = result.stdout + result.stderr
        if result.returncode != expected and "--output" in args:
            output = Path(args[args.index("--output") + 1])
            if output.is_file():
                diagnostic += json.dumps(
                    json.loads(output.read_text(encoding="utf-8")).get("conflicts"),
                    ensure_ascii=False,
                )
        self.assertEqual(result.returncode, expected, diagnostic)
        return result

    def plan(self, mode, data, expected=0):
        source = self.input_path(data)
        path = self.base / f"plan-{self.counter}.json"
        self.run_cli(
            "plan",
            self.target,
            "--mode",
            mode,
            "--input",
            source,
            "--standards-ref",
            self.ref,
            "--output",
            path,
            expected=expected,
        )
        return path, json.loads(path.read_text(encoding="utf-8"))

    def apply(self, plan):
        journal = plan.with_suffix(".journal.json")
        result = self.run_cli("apply", self.target, "--plan", plan, "--journal", journal)
        document = json.loads(result.stdout)
        self.assertEqual(document["status"], "completed")
        self.assertTrue(document["pending"])
        self.assertTrue(journal.is_file())
        self.assertTrue(Path(str(journal) + ".plan.json").is_file())
        self.assertFalse(journal.is_relative_to(self.target))
        return document

    def seed_from_central(self, data, existing=False):
        """Generate common files; fixture data never duplicates their managed format."""
        baseline = copy.deepcopy(data)
        if existing:
            baseline["readme"]["value"]["title"] += " before adoption"
        plan, draft = self.plan("create", baseline)
        self.assertTrue(any("actual LICENSE" in pending for pending in draft["pending"]))
        self.assertFalse(any(operation["path"] == "README.md" for operation in draft["operations"]))
        self.apply(plan)
        self.assertFalse((self.target / "LICENSE").exists())
        self.write("LICENSE", (ROOT / "LICENSE").read_bytes())
        for destination, source in (
            ("requirements_minimum.txt", "minimum-requirements.txt"),
            ("constraints/exact-minimum.txt", "minimum-constraints.txt"),
            ("constraints/current.txt", "current-constraints.txt"),
        ):
            if data["environments"]["value"]["minimum"]["ha"] == "2025.3.0":
                source = {
                    "minimum-requirements.txt": "minimum-2025-requirements.txt",
                    "minimum-constraints.txt": "minimum-2025-constraints.txt",
                }.get(source, source)
            self.write(destination, (DATA / "preserved" / source).read_bytes())
        fixtures.initialize(self.target)
        fixtures.commit(self.target)
        fixtures.git(self.target, "remote", "add", "origin", data["remote"]["value"])
        fixtures.git(self.target, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        fixtures.git(
            self.target, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk"
        )
        plan, _ = self.plan("adopt", baseline)
        self.apply(plan)
        fixtures.commit(self.target)

    def add_existing_content(self, existing=False):
        for name, source in (("README.md", "body.en.md"), ("README.ko.md", "body.ko.md")):
            path = self.target / name
            path.write_bytes(
                path.read_bytes().replace(
                    b"<!-- hass-standards:support:start -->",
                    (DATA / "preserved" / source).read_bytes()
                    + b"<!-- hass-standards:support:start -->",
                )
            )
        for destination, source in (
            ("tests/components/example/test_regression.py", "regression.py.txt"),
            (".github/workflows/project-only.yml", "project-ci.yml.txt"),
            ("docs/payload.md", "device-guide.txt"),
            ("docs/payload.ko.md", "device-guide.txt"),
            ("docs/troubleshooting.md", "device-guide.txt"),
            ("docs/troubleshooting.ko.md", "device-guide.txt"),
            ("examples/payload/synthetic.yaml", "payload-example.yml.txt"),
        ):
            self.write(destination, (DATA / "preserved" / source).read_bytes())
        conftest = self.target / "tests/components/example/conftest.py"
        conftest.write_bytes(
            conftest.read_bytes() + (DATA / "preserved/domain-fixture.txt").read_bytes()
        )
        requirements = self.target / "requirements_test.txt"
        requirements.write_bytes(
            b"# Existing project environment rationale\r\n" + requirements.read_bytes()
        )
        if existing:
            self.write(
                "custom_components/example/__init__.py",
                b'# Existing project implementation; behavior is outside this tool fixture.\r\nfrom .const import DOMAIN\r\nPROJECT_CONSTANT = "preserve  bytes"\r\n',
            )
        fixtures.commit(self.target)
        preserved = {
            path: (self.target / path).read_bytes()
            for path in (
                "LICENSE",
                "hacs.json",
                "requirements_minimum.txt",
                "requirements_test.txt",
                "constraints/exact-minimum.txt",
                "constraints/current.txt",
                "tests/components/example/test_regression.py",
                "tests/components/example/conftest.py",
                ".github/workflows/project-only.yml",
                "docs/payload.md",
                "docs/payload.ko.md",
                "docs/troubleshooting.md",
                "docs/troubleshooting.ko.md",
                "examples/payload/synthetic.yaml",
            )
        }
        if existing:
            preserved["custom_components/example/__init__.py"] = (
                self.target / "custom_components/example/__init__.py"
            ).read_bytes()
        return preserved

    def scenario(self, mode, combination):
        data = json.loads(
            (DATA / "inputs" / f"{mode}-{combination}.json").read_text(encoding="utf-8")
        )
        self.seed_from_central(data, existing=mode == "adopt")
        preserved = self.add_existing_content(existing=mode == "adopt")
        unmanaged = {}
        for name in ("README.md", "README.ko.md"):
            content = (self.target / name).read_bytes()
            for area in fixtures.readme.AREAS:
                content = re.sub(
                    rb"<!-- hass-standards:"
                    + area.encode()
                    + rb":start -->.*?<!-- hass-standards:"
                    + area.encode()
                    + rb":end -->",
                    b"MANAGED",
                    content,
                    flags=re.S,
                )
            unmanaged[name] = content
        inventory = self.base / "inventory.json"
        self.run_cli("inspect", self.target, "--output", inventory)
        self.assertEqual(json.loads(inventory.read_text())["domains"], ["example"])
        plan, document = self.plan("adopt", data)
        self.assertEqual(document["conflicts"], [])
        guarded = {item["path"]: item for item in document["guards"]}
        for path, original in preserved.items():
            self.assertEqual(guarded[path]["sha256"], fixtures.planning.digest(original))
            self.assertFalse(
                any(operation["path"] == path for operation in document["operations"]), path
            )
        self.apply(plan)
        for path, original in preserved.items():
            self.assertEqual((self.target / path).read_bytes(), original)
        for name, source in (("README.md", "body.en.md"), ("README.ko.md", "body.ko.md")):
            self.assertIn(
                (DATA / "preserved" / source).read_bytes(), (self.target / name).read_bytes()
            )
        for name, original in unmanaged.items():
            content = (self.target / name).read_bytes()
            for area in fixtures.readme.AREAS:
                content = re.sub(
                    rb"<!-- hass-standards:"
                    + area.encode()
                    + rb":start -->.*?<!-- hass-standards:"
                    + area.encode()
                    + rb":end -->",
                    b"MANAGED",
                    content,
                    flags=re.S,
                )
            self.assertEqual(content, original)
        if mode == "adopt":
            self.assertTrue(
                any(operation["path"] == "README.md" for operation in document["operations"])
            )
        _, repeated = self.plan("adopt", data)
        self.assertEqual(repeated["operations"], [])
        self.assertTrue(repeated["pending"])
        _, invalid_create = self.plan("create", data, expected=2)
        self.assertTrue(any("empty target" in message for message in invalid_create["conflicts"]))
        dependabot = yaml.safe_load((self.target / ".github/dependabot.yml").read_bytes())
        pip = next(
            update for update in dependabot["updates"] if update["package-ecosystem"] == "pip"
        )
        self.assertIn("requirements_minimum.txt", pip["exclude-paths"])
        self.assertIn("constraints/exact-minimum.txt", pip["exclude-paths"])
        self.assertNotIn("requirements_test.txt", pip["exclude-paths"])
        self.assertNotIn("constraints/current.txt", pip["exclude-paths"])
        minimum = data["environments"]["value"]["minimum"]
        self.assertEqual(document["validated_input"]["environments"]["value"]["minimum"], minimum)
        self.assertEqual(
            json.loads((self.target / "hacs.json").read_text())["homeassistant"], minimum["ha"]
        )
        workflow = yaml.safe_load((self.target / ".github/workflows/tests.yml").read_bytes())
        self.assertEqual(workflow["jobs"]["minimum"]["with"]["expected-ha-version"], minimum["ha"])
        self.assertEqual(
            json.loads(workflow["jobs"]["minimum"]["with"]["python-versions"]), [minimum["python"]]
        )
        self.assertIn(
            ("homeassistant==" + minimum["ha"]).encode(),
            (self.target / "requirements_minimum.txt").read_bytes(),
        )
        if mode == "adopt" and combination == "base":
            self.assertNotEqual(minimum["ha"], data["environments"]["value"]["current"]["ha"])
            self.assertIn(b"2025.3.0", (self.target / "README.md").read_bytes())
            self.assertIn(b"2025.3.0", (self.target / "README.ko.md").read_bytes())
        self.assertEqual(
            yaml.safe_load((self.target / ".github/workflows/project-only.yml").read_bytes())["on"][
                "schedule"
            ],
            [{"cron": "17 4 * * 2"}],
        )
        checked = self.run_cli(self.target, "--check", checker=True, expected=1)
        self.assertIn("authoring scaffold", checked.stdout)
        if combination != "base":
            removed = copy.deepcopy(data)
            removed["manifest"]["value"]["requirements"] = []
            removed["environments"]["value"]["libraries"] = {}
            removed.pop("payload", None)
            self.write(
                "custom_components/example/manifest.json",
                json.dumps(removed["manifest"]["value"]).encode(),
            )
            fixtures.commit(self.target)
            output, removed_plan = self.plan("adopt", removed)
            self.assertEqual(removed_plan["conflicts"], [])
            self.apply(output)
            _, removed_repeated = self.plan("adopt", removed)
            self.assertEqual(removed_repeated["operations"], [])
            self.assertFalse(
                any(
                    operation["path"].startswith(("docs/", "examples/payload/"))
                    for operation in removed_plan["operations"]
                )
            )
            for path in (
                "docs/payload.md",
                "docs/payload.ko.md",
                "docs/troubleshooting.md",
                "docs/troubleshooting.ko.md",
                "examples/payload/synthetic.yaml",
            ):
                self.assertEqual((self.target / path).read_bytes(), preserved[path])

        if mode == "adopt" and combination == "base":
            path = self.target / ".github/workflows/tests.yml"
            workflow = yaml.safe_load(path.read_bytes())
            workflow["on"]["schedule"] = [{"cron": "41 3 * * 1"}]
            original = yaml.safe_dump(workflow, sort_keys=False).encode("utf-8")
            path.write_bytes(original)
            fixtures.commit(self.target)
            _, conflicted = self.plan("adopt", data, expected=2)
            self.assertEqual(
                conflicted["conflicts"],
                [
                    "Preserve existing extension; reviewed merge required: .github/workflows/tests.yml"
                ],
            )
            self.assertEqual(path.read_bytes(), original)

    def test_missing_payload_and_required_provenance_fail_without_target_writes(self):
        for variant in ("payload", "source"):
            with self.subTest(variant=variant):
                data = json.loads(
                    (DATA / "inputs/create-imagespec.json").read_text(encoding="utf-8")
                )
                if variant == "payload":
                    del data["payload"]
                else:
                    del data["domain"]["source"]
                source = self.input_path(data)
                output = self.base / f"missing-{variant}.json"
                result = self.run_cli(
                    "plan",
                    self.target,
                    "--mode",
                    "create",
                    "--input",
                    source,
                    "--standards-ref",
                    self.ref,
                    "--output",
                    output,
                    expected=2,
                )
                self.assertIn("payload" if variant == "payload" else "source", result.stderr)
                self.assertFalse(self.target.exists())
                self.assertFalse(output.exists())


for mode in ("create", "adopt"):
    for combination in ("base", "imagespec", "blesession", "both"):

        def run(self, mode=mode, combination=combination):
            self.scenario(mode, combination)

        setattr(IntegrationScenarios, f"test_{mode}_{combination}_cli_scenario", run)


if __name__ == "__main__":
    unittest.main()

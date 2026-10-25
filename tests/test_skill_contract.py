"""Static T5 packaging contracts; these do not prove agent behavior or HA execution."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from standards import contract, planning  # noqa: E402
from test_integration_planning import commit, initialize  # noqa: E402

NAMES = ("create-ha-integration", "adopt-ha-standards")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {path}")
    return yaml.safe_load(match.group(1)), text[match.end() :]


def cli_parser(path):
    """Build the real CLI parser, stopping before any command can run."""
    spec = importlib.util.spec_from_file_location("skill_cli_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    captured = []

    class Captured(Exception):
        pass

    def capture(parser, *args, **kwargs):
        captured.append(parser)
        raise Captured

    with patch.object(argparse.ArgumentParser, "parse_args", autospec=True, side_effect=capture):
        try:
            module.main()
        except Captured:
            pass
    if len(captured) != 1:
        raise AssertionError("Expected one actual CLI parser")
    return captured[0]


class SkillContract(unittest.TestCase):
    def test_skill_identity_and_discovery_metadata(self):
        descriptions = []
        for name in NAMES:
            with self.subTest(name=name):
                directory = ROOT / "skills" / name
                metadata, body = frontmatter(directory / "SKILL.md")
                self.assertEqual(metadata["name"], name)
                self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertIsInstance(metadata["description"], str)
                self.assertTrue(metadata["description"].strip())
                self.assertNotRegex(metadata["description"], r"(?i)TODO|\[.*?\]")
                descriptions.append(metadata["description"])
                self.assertTrue(body.strip())
                ui = yaml.safe_load((directory / "agents/openai.yaml").read_text(encoding="utf-8"))[
                    "interface"
                ]
                self.assertTrue(ui["display_name"].strip())
                self.assertTrue(25 <= len(ui["short_description"]) <= 64)
                if "default_prompt" in ui:
                    self.assertIn("$" + name, ui["default_prompt"])
                    self.assertEqual(
                        re.findall(r"\$([a-z]+(?:-[a-z]+)+)", ui["default_prompt"]), [name]
                    )
        self.assertEqual(len(set(descriptions)), len(NAMES))

    def test_installed_skill_internal_references_are_self_contained(self):
        with tempfile.TemporaryDirectory(prefix="standards-T5-installed-") as temporary:
            installed = Path(temporary)
            for name in NAMES:
                directory = installed / name
                shutil.copytree(ROOT / "skills" / name, directory)
                metadata, body = frontmatter(directory / "SKILL.md")
                references = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)
                self.assertIn("references/workflow.md", references)
                for document in directory.rglob("*.md"):
                    for destination in re.findall(
                        r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")
                    ):
                        if "://" in destination or destination.startswith("#"):
                            continue
                        destination = destination.split("#", 1)[0]
                        path = (document.parent / destination).resolve()
                        self.assertTrue(path.is_relative_to(directory.resolve()), destination)
                        self.assertTrue(path.is_file(), destination)
                # Installable instructions delegate assets to the separately located central checkout.
                files = [path for path in directory.rglob("*") if path.is_file()]
                self.assertTrue(all(path.suffix in {".md", ".yaml"} for path in files))
                self.assertFalse(
                    any(path.name in {"contract.json", "AGENTS.md", "action.yml"} for path in files)
                )

    def test_workflow_commands_parse_with_the_actual_central_clis(self):
        parsers = {
            name: cli_parser(ROOT / "scripts" / name)
            for name in ("manage_integration.py", "check_integration.py")
        }
        for name, mode in zip(NAMES, ("create", "adopt")):
            text = (ROOT / "skills" / name / "references/workflow.md").read_text(encoding="utf-8")
            examples = []
            for block in re.findall(r"```text\n(.*?)```", text, re.S):
                for line in block.splitlines():
                    if line.startswith("python3 "):
                        tokens = shlex.split(line)
                        script = Path(tokens[1].replace("<central>", ROOT.as_posix()))
                        self.assertEqual(script.parent, ROOT / "scripts")
                        self.assertTrue(script.is_file())
                        arguments = parsers[script.name].parse_args(tokens[2:])
                        examples.append((script.name, arguments))
            commands = [
                args.command for script, args in examples if script == "manage_integration.py"
            ]
            self.assertEqual(commands, ["inspect", "plan", "verify-release", "plan", "apply"])
            legacy, release = [
                args for script, args in examples if getattr(args, "command", None) == "plan"
            ]
            self.assertEqual(legacy.mode, mode)
            self.assertEqual(legacy.standards_ref, "<sha>")
            self.assertIsNone(legacy.release_tag)
            self.assertNotEqual(legacy.output.parent, legacy.target)
            verification = next(
                args
                for script, args in examples
                if getattr(args, "command", None) == "verify-release"
            )
            self.assertEqual(
                (verification.repository, verification.tag, verification.resolved_sha),
                ("eigger/hass-repo-standards", "<release>", "<sha>"),
            )
            self.assertEqual((release.release_tag, release.standards_ref), ("<release>", "<sha>"))
            self.assertEqual(release.release_verification.name, "release-verification.json")
            self.assertTrue(
                any(script == "check_integration.py" and args.check for script, args in examples)
            )

    def test_central_references_and_contract_version_match_real_assets(self):
        version = contract.load_contract()["schema_version"]
        schema = json.loads((ROOT / "schemas/integration-input.schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], version)
        for name in NAMES:
            workflow = (ROOT / "skills" / name / "references/workflow.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(
                [int(value) for value in re.findall(r"schema_version: (\d+)", workflow)], [version]
            )
            references = re.findall(
                r"(?<![A-Za-z0-9])((?:scripts|templates|schemas|docs)/[A-Za-z0-9_./-]+\.(?:py|md|json))",
                workflow,
            )
            self.assertTrue(references)
            for reference in references:
                self.assertTrue((ROOT / reference).is_file(), reference)
            self.assertIn("templates/integration/contract.json", references)
            self.assertIn("schemas/integration-input.schema.json", references)

    def test_reviewed_sha_rejects_modified_deleted_and_untracked_skills(self):
        with tempfile.TemporaryDirectory(prefix="standards-T5-sha-") as temporary:
            central = Path(temporary)
            initialize(central)
            path = central / "skills/create-ha-integration/SKILL.md"
            path.parent.mkdir(parents=True)
            original = b"Reviewed skill fixture\n"
            path.write_bytes(original)
            ref = commit(central)
            self.assertEqual(planning.verify_standards(ref, central), central.resolve())
            for value in (b"Unreviewed skill changes\n", None):
                with self.subTest(value=value):
                    if value is None:
                        path.unlink()
                    else:
                        path.write_bytes(value)
                    with self.assertRaisesRegex(ValueError, "clean"):
                        planning.verify_standards(ref, central)
                    path.write_bytes(original)
            new = path.parent / "references/new-workflow.md"
            new.parent.mkdir()
            new.write_text("Unreviewed instruction", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "clean"):
                planning.verify_standards(ref, central)
            new.unlink()
            self.assertEqual(planning.verify_standards(ref, central), central.resolve())


if __name__ == "__main__":
    unittest.main()

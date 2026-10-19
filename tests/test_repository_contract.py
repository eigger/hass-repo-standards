"""Repository integrity checks distinguish central drafts from adopted outputs."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_repository  # noqa: E402
from standards import contract, scaffold  # noqa: E402


class RepositoryContract(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="central-integrity-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in ("scripts", "schemas", "templates", "docs"):
            shutil.copytree(
                ROOT / name, self.root / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
            )
        for target, attribute in ((check_repository, "ROOT"), (contract, "CENTRAL")):
            patcher = patch.object(target, attribute, self.root)
            patcher.start()
            self.addCleanup(patcher.stop)

    def mutate_json(self, relative, change):
        path = self.root / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def assert_invalid(self, message):
        errors = check_repository.check_contract_integrity()
        self.assertTrue(errors)
        self.assertIn(message, "\n".join(errors))

    def test_intentional_draft_todos_are_valid_and_check_is_read_only(self):
        paths = sorted(p for p in self.root.rglob("*") if p.is_file())
        before = {p.relative_to(self.root): p.read_bytes() for p in paths}
        self.assertEqual(check_repository.check_contract_integrity(), [])
        after = {
            p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()
        }
        self.assertEqual(before, after)
        content, pending = scaffold.render(
            next(
                r
                for r in contract.load_contract()["records"]
                if r["id"] == "component-config_flow.py"
            ),
            "custom_components/example/config_flow.py",
            check_repository.contract_probe_input(),
            central=self.root,
        )
        self.assertIn("NotImplementedError", content)
        self.assertTrue(pending)

    def test_contract_invalid_version_and_missing_source_fail(self):
        self.mutate_json(
            "templates/integration/contract.json", lambda d: d.update(schema_version=99)
        )
        self.assert_invalid("version")

    def test_missing_source_fails(self):
        (self.root / "templates/integration/scaffold/const.py.tmpl").unlink()
        self.assert_invalid("Missing")

    def test_schema_unsupported_keyword_and_reference_fail(self):
        self.mutate_json(
            "schemas/integration-input.schema.json",
            lambda d: d["properties"]["domain"].update(invented=True),
        )
        self.assert_invalid("unsupported schema keywords")

    def test_schema_cyclic_and_external_reference_fail(self):
        for reference in (
            "integration-plan.schema.json",
            "https://example.invalid/schema",
            "../outside.json",
        ):
            with self.subTest(reference=reference):
                self.mutate_json(
                    "schemas/integration-plan.schema.json", lambda d: d.update({"$ref": reference})
                )
                self.assert_invalid("reference")

    def test_schema_version_must_match_contract(self):
        self.mutate_json(
            "schemas/integration-plan.schema.json",
            lambda d: d["properties"]["schema_version"].update(const=2),
        )
        self.assert_invalid("schema version")

    def test_unselected_payload_schema_keywords_are_validated(self):
        path = self.root / "schemas/integration-input.schema.json"
        original = path.read_text(encoding="utf-8")
        for keyword, value in (
            ("minimum", "one"),
            ("minimum", True),
            ("minItems", -1),
            ("maxItems", False),
            ("minLength", 1.5),
            ("enum", []),
            ("type", []),
            ("type", ["string", "string"]),
            ("uniqueItems", "yes"),
        ):
            with self.subTest(keyword=keyword, value=value):
                path.write_text(original, encoding="utf-8")

                def mutate(data):
                    branch = data["properties"]["payload"]["properties"]["value"]["properties"][
                        "examples"
                    ]["items"]["properties"]["expected_size"]["items"]
                    branch[keyword] = value

                self.mutate_json("schemas/integration-input.schema.json", mutate)
                self.assert_invalid(f"Schema {keyword}")

    def test_unknown_template_token_and_invalid_python_fail(self):
        path = self.root / "templates/integration/scaffold/const.py.tmpl"
        for content, message in (("@@unknown@@", "token"), ("this is invalid Python!", "syntax")):
            with self.subTest(content=content):
                path.write_text(content, encoding="utf-8")
                self.assert_invalid(message)

    def test_unregistered_template_and_missing_stage_resource_fail(self):
        path = self.root / "templates/integration/scaffold/extra.py.tmpl"
        path.write_text("# unregistered", encoding="utf-8")
        self.assert_invalid("Unregistered")
        path.unlink()
        (self.root / "scripts/manage_integration.py").unlink()
        self.assert_invalid("Missing implemented-stage resource")

    def test_future_skill_absence_is_allowed_but_existing_folder_needs_entry(self):
        self.assertEqual(check_repository.check_contract_integrity(), [])
        (self.root / "skills/future-skill").mkdir(parents=True)
        self.assert_invalid("Missing skill entry point")

    def test_existing_skill_links_use_the_shared_document_checker(self):
        directory = self.root / "skills/future-skill"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("[Workflow](references/workflow.md)", encoding="utf-8")
        self.assert_invalid("missing link references/workflow.md")
        (directory / "references").mkdir()
        (directory / "references/workflow.md").write_text("[Missing](missing.md)", encoding="utf-8")
        self.assert_invalid("missing link missing.md")
        (directory / "references/workflow.md").write_text(
            "[Source](../../../README.md)", encoding="utf-8"
        )
        (self.root / "README.md").write_text("Probe only", encoding="utf-8")
        self.assertEqual(check_repository.check_contract_integrity(), [])


if __name__ == "__main__":
    unittest.main()

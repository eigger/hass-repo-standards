"""HACS README generation/adoption use the same offline installation contract."""

from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

import test_integration_planning as fixtures
from standards import apply as application
from standards import contract, installation, planning, readme


def default_input(data):
    data = copy.deepcopy(data)
    data["hacs"] = {"value": "default", "source": "unit fixture, not listing evidence"}
    data["hacs_default_evidence"] = {
        "value": {
            "url": "https://github.com/hacs/default/blob/master/integration",
            "checked_at": "2026-10-19",
        },
        "source": "synthetic test metadata",
    }
    return data


class HacsInstallation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.IntegrationPlanning.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.IntegrationPlanning.tearDownClass.__func__(cls)

    setUp = fixtures.IntegrationPlanning.setUp
    adopt_fixture = fixtures.IntegrationPlanning.adopt_fixture
    plan = fixtures.IntegrationPlanning.plan

    def apply_document(self, document, name):
        self.assertEqual(document["conflicts"], [])
        path = self.base / f"{name}.json"
        path.write_text(planning.canonical_json(document), encoding="utf-8")
        result = application.apply_plan(self.target, path, central=self.central)
        self.assertEqual(result["status"], "completed")

    def test_create_then_actual_license_generates_both_statuses_and_idempotent_adopt(self):
        for selected in ("custom", "default"):
            with self.subTest(selected=selected):
                self.target = self.base / selected
                data = default_input(self.data) if selected == "default" else self.data
                created = self.plan(data=data)
                self.assertTrue(any("LICENSE required" in item for item in created["pending"]))
                self.apply_document(created, f"create-{selected}")
                (self.target / "LICENSE").write_text("Actual fixture MIT notice", encoding="utf-8")
                adopted = self.plan("adopt", data)
                self.apply_document(adopted, f"readme-{selected}")
                settings = json.loads(
                    (self.target / ".hass-standards.json").read_text(encoding="utf-8")
                )
                for language, name in (("en", "README.md"), ("ko", "README.ko.md")):
                    text = (self.target / name).read_text(encoding="utf-8")
                    self.assertEqual(
                        readme.block(text, "installation"), installation.render(settings, language)
                    )
                    self.assertIn(
                        "hacs_repository.svg"
                        if selected == "default"
                        else "https://github.com/owner/example",
                        text,
                    )
                self.assertEqual(readme.readme_updates(self.target, settings), [])
                self.assertEqual(self.plan("adopt", data)["operations"], [])

    def test_adopt_switches_status_preserves_device_body_and_existing_default_settings(self):
        self.adopt_fixture()
        bodies = {}
        for name in ("README.md", "README.ko.md"):
            path = self.target / name
            body = "\r\n### Device settings / 기기 설정\r\n\r\nKeep YAML, pairing and manual steps.\r\n"
            path.write_bytes(
                path.read_bytes().replace(
                    readme.markers("support")[0].encode(),
                    body.encode() + readme.markers("support")[0].encode(),
                )
            )
            bodies[name] = body.encode()
        fixtures.commit(self.target)
        data = default_input(self.data)
        self.apply_document(self.plan("adopt", data), "default")
        for name, body in bodies.items():
            text = (self.target / name).read_bytes()
            self.assertIn(body, text)
            self.assertIn(b"owner=owner&repository=example&category=integration", text)
            self.assertNotIn(b"Custom repositories", text)
        fixtures.commit(self.target)
        self.assertEqual(self.plan("adopt")["operations"], [])
        custom = copy.deepcopy(self.data)
        custom["hacs"] = {"value": "custom", "source": "unit fixture"}
        self.apply_document(self.plan("adopt", custom), "custom")
        for name, body in bodies.items():
            self.assertIn(body, (self.target / name).read_bytes())
            self.assertNotIn(b"hacs_repository.svg", (self.target / name).read_bytes())

    def test_unmarked_legacy_installation_blocks_plan_without_editing(self):
        self.adopt_fixture()
        for text in (
            "## Installation\n\nExisting manual instructions.",
            "## 설치\n\n기기 준비 조건.",
            "사용자 정의 저장소에서 원래 안내를 따르세요.",
            "Use https://my.home-assistant.io/redirect/hacs_repository/.",
        ):
            with self.subTest(text=text):
                path = self.target / "README.md"
                original = path.read_text(encoding="utf-8")
                start, end = readme.markers("installation")
                left, rest = original.split(start)
                _, right = rest.split(end)
                legacy = left + text + right
                path.write_bytes(legacy.encode("utf-8"))
                fixtures.commit(self.target)
                planned = self.plan("adopt")
                self.assertTrue(
                    any("Unmarked installation" in item for item in planned["conflicts"])
                )
                self.assertEqual(path.read_text(encoding="utf-8"), legacy)
                path.write_bytes(original.encode("utf-8"))
                fixtures.commit(self.target)

    def test_missing_block_is_added_once_and_custom_content_or_orphan_markers_fail(self):
        self.adopt_fixture()
        settings = contract.render_settings(self.data)
        path = self.target / "README.md"
        original = path.read_text(encoding="utf-8")
        start, end = readme.markers("installation")
        left, rest = original.split(start)
        _, right = rest.split(end)
        path.write_bytes((left + right).encode("utf-8"))
        _, _, generated = readme.readme_update(self.target, settings, "en", path.name)
        self.assertEqual(generated.count(start), 1)
        self.assertEqual(readme.render_readme(self.target, settings, "en", generated), generated)
        with self.assertRaisesRegex(ValueError, "Preserve existing installation"):
            readme.render_readme(
                self.target,
                settings,
                "en",
                original.replace(end, "Extra device instruction\n" + end),
            )
        for malformed in (original.replace(start, ""), original.replace(end, "")):
            with self.assertRaisesRegex(ValueError, "marker"):
                readme.render_readme(
                    self.target, {**settings, "installation": False}, "en", malformed
                )

    def test_default_requires_real_shaped_evidence_and_renderer_performs_no_network(self):
        data = default_input(self.data)
        contract.validate_input(data)
        for value in (
            None,
            "verified",
            {},
            {"url": "http://example.org/list", "checked_at": "2026-10-19"},
            {"url": "https://example.org/list", "checked_at": "2026-02-30"},
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                installation.status({"hacs": "default", "hacs_default_evidence": value})
        data.pop("hacs_default_evidence")
        with self.assertRaises(ValueError):
            contract.validate_input(data)
        with patch("socket.socket", side_effect=AssertionError("Network forbidden")):
            for selected in ("custom", "default"):
                settings = contract.render_settings(default_input(self.data))
                settings["hacs"] = selected
                for language in ("en", "ko"):
                    self.assertIn("https://www.hacs.xyz/", installation.render(settings, language))


if __name__ == "__main__":
    unittest.main()

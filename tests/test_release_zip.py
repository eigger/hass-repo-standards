"""Exercise real archive contents, release identity and guarded caller behavior."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_release_zip import build  # noqa: E402
from standards import planning, release, validation  # noqa: E402


class ReleaseZip(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.root.mkdir()
        self.component = self.root / "custom_components/example"
        self.component.mkdir(parents=True)
        self.output = self.root.parent / "assets"
        (self.component / "manifest.json").write_text(
            json.dumps({"domain": "example", "version": "1.2.3"}), encoding="utf-8"
        )
        (self.component / "__init__.py").write_text("# integration\n", encoding="utf-8")
        (self.component / "translations").mkdir()
        (self.component / "translations/ko.json").write_text('{"name":"통합"}', encoding="utf-8")
        (self.root / "hacs.json").write_text(
            json.dumps({"zip_release": True, "filename": "example.zip"}), encoding="utf-8"
        )
        (self.root / "README.md").write_text("Repository documentation", encoding="utf-8")
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.commit()
        self.git("tag", "v1.2.3")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args])

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture")

    def test_zip_has_installable_root_and_only_tracked_integration_content(self):
        (self.component / "untracked.txt").write_text("not shipped")
        archive = build(self.root, self.output, "v1.2.3")
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(
                set(bundle.namelist()),
                {
                    "__init__.py",
                    "manifest.json",
                    "translations/ko.json",
                },
            )
            self.assertEqual(json.loads(bundle.read("translations/ko.json")), {"name": "통합"})
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=no"), b"")
        with self.assertRaises(FileExistsError):
            build(self.root, self.output, "v1.2.3")

    def test_rejects_wrong_tag_or_checkout_and_dirty_source_without_rewriting(self):
        with self.assertRaisesRegex(ValueError, "manifest.version"):
            build(self.root, self.output, "v9.9.9")
        (self.component / "__init__.py").write_text("changed\n")
        with self.assertRaisesRegex(ValueError, "tracked modifications"):
            build(self.root, self.output, "v1.2.3")
        self.commit()
        with self.assertRaisesRegex(ValueError, "tag commit"):
            build(self.root, self.output, "v1.2.3")
        self.assertFalse(self.output.exists())

    def test_cli_exposes_verified_archive_to_the_composite_action(self):
        result_file = self.root.parent / "github-output"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/build_release_zip.py"),
                str(self.root),
                "--output",
                str(self.output),
                "--tag",
                "v1.2.3",
            ],
            env={**os.environ, "GITHUB_OUTPUT": str(result_file)},
            check=True,
            capture_output=True,
        )
        key, path = result_file.read_text(encoding="utf-8").strip().split("=", 1)
        self.assertEqual(key, "archive")
        self.assertEqual(Path(path), self.output / "example.zip")
        with zipfile.ZipFile(path) as bundle:
            self.assertIsNone(bundle.testzip())

    def test_rejects_escaping_filename_and_repository_output(self):
        (self.root / "hacs.json").write_text('{"zip_release":true,"filename":"../escape.zip"}')
        self.commit()
        with self.assertRaisesRegex(ValueError, "safe ZIP"):
            build(self.root, self.output)
        (self.root / "hacs.json").write_text('{"zip_release":true,"filename":"example.zip"}')
        self.commit()
        with self.assertRaisesRegex(ValueError, "outside"):
            build(self.root, self.root / "dist")

    def test_tracked_cache_is_excluded_and_symlinks_are_rejected(self):
        (self.component / "__pycache__").mkdir()
        (self.component / "__pycache__/cached.pyc").write_bytes(b"cache")
        self.commit()
        with zipfile.ZipFile(build(self.root, self.output)) as bundle:
            self.assertNotIn("__pycache__/cached.pyc", bundle.namelist())
        try:
            (self.component / "linked.py").symlink_to(self.root / "README.md")
        except OSError:
            self.skipTest("Symlink creation unavailable; run on Linux")
        self.commit()
        with self.assertRaisesRegex(ValueError, "symlink"):
            build(self.root, self.root.parent / "other-assets")

    def test_caller_preserves_existing_asset_and_validates_security_boundaries(self):
        target = self.root / ".github/workflows/release.yml"
        target.parent.mkdir(parents=True)
        source = ROOT / "templates/integration/.github/workflows/release.yml"
        target.write_text(
            source.read_text(encoding="utf-8").replace("@main", "@" + "a" * 40), encoding="utf-8"
        )
        config = {"hacs": "default"}

        def safe(root, path):
            return root / path

        self.assertEqual(release.errors(self.root, config, "example", safe, ROOT), [])
        original = yaml.safe_load(target.read_text(encoding="utf-8"))
        for mutation in ("event", "clobber", "credentials", "tag", "mutable"):
            data = copy.deepcopy(original)
            steps = data["jobs"]["release"]["steps"]
            if mutation == "event":
                data["on"] = {"push": None}
            elif mutation == "clobber":
                steps[-1]["run"] += " --clobber"
            elif mutation == "credentials":
                steps[0]["with"]["persist-credentials"] = True
            elif mutation == "tag":
                steps[2]["with"]["tag"] = "main"
            else:
                steps[2]["uses"] = steps[2]["uses"].split("@")[0] + "@main"
            target.write_text(yaml.safe_dump(data), encoding="utf-8")
            self.assertTrue(release.errors(self.root, config, "example", safe, ROOT), mutation)

    def test_planner_pins_release_action_once(self):
        from test_standards_contract import input_fixture

        source = ROOT / "templates/integration/.github/workflows/release.yml"
        rendered = yaml.safe_load(
            planning.render_workflow(
                source.read_text(encoding="utf-8"),
                ".github/workflows/release.yml",
                input_fixture(),
                "a" * 40,
            )
        )
        self.assertEqual(
            rendered["jobs"]["release"]["steps"][2]["uses"],
            "eigger/hass-repo-standards/actions/release-zip@" + "a" * 40,
        )

    def test_scoped_release_reference_does_not_upgrade_existing_ci(self):
        primary, scoped = "a" * 40, "b" * 40
        document = self.root / "STANDARDS.md"
        workflows = self.root / ".github/workflows"
        workflows.mkdir(parents=True)
        document.write_text(
            f"- Reviewed standards SHA: `{primary}`\n"
            f"- Reviewed release standards SHA: `{scoped}`\n",
            encoding="utf-8",
        )
        caller = workflows / "tests.yml"
        caller.write_text(
            yaml.safe_dump(
                {
                    "jobs": {
                        "tests": {
                            "uses": "eigger/hass-repo-standards/.github/workflows/python-tests.yml@"
                            + primary,
                            "with": {"standards-ref": primary},
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        release_caller = workflows / "release.yml"
        source = (ROOT / "templates/integration/.github/workflows/release.yml").read_text(
            encoding="utf-8"
        )
        release_caller.write_text(source.replace("@main", "@" + scoped), encoding="utf-8")

        def safe(root, name):
            return root / name

        self.assertEqual(validation.reference_errors(self.root, safe), [])
        # The scoped ref cannot authorize unrelated central actions or workflows.
        caller.write_text(caller.read_text().replace(primary, scoped), encoding="utf-8")
        self.assertTrue(validation.reference_errors(self.root, safe))
        caller.unlink()
        release_caller.write_text(source.replace("@main", "@" + primary), encoding="utf-8")
        self.assertTrue(validation.reference_errors(self.root, safe))
        for field in ("main", "b" * 7, f"`{scoped}`\n- Reviewed release standards SHA: `{scoped}`"):
            document.write_text(
                f"- Reviewed standards SHA: `{primary}`\n- Reviewed release standards SHA: {field}\n",
                encoding="utf-8",
            )
            self.assertTrue(validation.reference_errors(self.root, safe))


if __name__ == "__main__":
    unittest.main()

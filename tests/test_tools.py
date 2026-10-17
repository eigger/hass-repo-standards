"""Offline behavioral checks for dependency proposals and managed document updates."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packaging.markers import default_environment
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


update = load("update", "actions/update-manifest/update.py")
install = load("install", "actions/python-environment/install.py")
badges = load("badges", "scripts/sync_badges.py")
audit = load("audit", "scripts/audit_repositories.py")


def releases(*versions):
    return {"releases": {v: [{"yanked": False, "requires_python": ">=3.9"}] for v in versions}}


class DependencyUpdates(unittest.TestCase):
    def test_extras_marker_and_operator_preserved(self):
        original = 'imagespec[datamatrix] >= 1.0.0; python_version >= "3.9"'
        manifest = {"requirements": [original, "blesession==1.1.0", "untouched==3.0"]}
        changed, notes = update.plan_updates(
            manifest, ["imagespec", "blesession"], lambda _: releases("1.2.0")
        )
        self.assertEqual(
            changed["requirements"],
            [
                'imagespec[datamatrix] >=1.2.0; python_version >= "3.9"',
                "blesession==1.2.0",
                "untouched==3.0",
            ],
        )
        self.assertEqual(manifest["requirements"][0], original)
        self.assertEqual(len(notes), 2)

    def test_no_downgrade_or_operator_conversion(self):
        manifest = {"requirements": ["imagespec==1.4.0"]}
        changed, notes = update.plan_updates(manifest, ["imagespec"], lambda _: releases("1.3.0"))
        self.assertEqual(changed, manifest)
        self.assertEqual(notes, [])

    def test_inactive_markers_fail_before_selecting_an_unvalidated_release(self):
        environment = {
            **default_environment(),
            "python_version": "3.14",
            "python_full_version": "3.14.0",
            "sys_platform": "linux",
        }
        for marker in ['python_version < "3.13"', 'sys_platform == "win32"']:
            with self.subTest(marker=marker):
                manifest = {"requirements": [f"imagespec>=1.0; {marker}"]}
                original = json.loads(json.dumps(manifest))
                with (
                    patch("packaging.markers.default_environment", return_value=environment),
                    patch.object(update, "fetch_package") as fetch,
                    self.assertRaisesRegex(ValueError, "Cannot validate inactive marker"),
                ):
                    update.plan_updates(manifest, ["imagespec"], fetch=fetch)
                fetch.assert_not_called()
                self.assertEqual(manifest, original)

    def test_yanked_proposal_still_reaches_pr_synchronization(self):
        manifest = {"requirements": ["imagespec>=1.0"]}
        data = releases("1.0", "1.1")
        proposal, notes = update.plan_updates(manifest, ["imagespec"], lambda _: data)
        self.assertEqual(proposal["requirements"], ["imagespec>=1.1"])
        self.assertTrue(notes)
        data["releases"]["1.1"][0]["yanked"] = True
        unchanged, notes = update.plan_updates(manifest, ["imagespec"], lambda _: data)
        self.assertEqual(unchanged, manifest)
        self.assertFalse(notes)
        workflow = audit.yaml.load(
            (ROOT / ".github/workflows/dependency-update.yml").read_text(), Loader=audit.Loader
        )
        steps = workflow["jobs"]["update"]["steps"]
        synchronize = next(s for s in steps if s.get("uses", "").startswith("peter-evans/"))
        # No explicit condition: GitHub's implicit success() gate permits
        # no-change cleanup, but still blocks synchronization on earlier failures.
        self.assertNotIn("if", synchronize)
        self.assertTrue(synchronize["with"]["delete-branch"])
        validate = next(s for s in steps if s.get("name") == "Validate proposed dependency changes")
        self.assertEqual(validate["if"], "steps.update.outputs.updated == 'true'")

    def test_major_requires_explicit_opt_in(self):
        manifest = {"requirements": ["imagespec>=1.0"]}
        with self.assertRaisesRegex(ValueError, "Major"):
            update.plan_updates(manifest, ["imagespec"], lambda _: releases("2.0"))
        changed, _ = update.plan_updates(
            manifest, ["imagespec"], lambda _: releases("2.0"), allow_major=True
        )
        self.assertEqual(changed["requirements"], ["imagespec>=2.0"])

    def test_unsupported_requirements_do_not_silently_pass(self):
        for requirement in [
            "imagespec~=1.0",
            "imagespec>=1,<2",
            "imagespec==1.*",
            "imagespec @ https://example.com/a.whl",
        ]:
            with self.subTest(requirement=requirement), self.assertRaises(ValueError):
                update.plan_updates(
                    {"requirements": [requirement]}, ["imagespec"], lambda _: releases("1.5")
                )

    def test_absent_or_duplicate_selected_package_fails(self):
        for requirements in [[], ["imagespec>=1", "imagespec>=1.1"]]:
            with self.assertRaises(ValueError):
                update.plan_updates(
                    {"requirements": requirements}, ["imagespec"], lambda _: releases("1.0")
                )

    def test_pypi_filters_yanked_prerelease_and_python(self):
        data = releases("1.0", "1.1rc1", "1.2", "1.3")
        data["releases"]["1.2"][0]["yanked"] = True
        data["releases"]["1.3"][0]["requires_python"] = ">=3.14"
        self.assertEqual(update.latest_stable(data, "3.13.2"), Version("1.0"))

    def test_minimum_exact_constraints_include_extras_and_skip_false_marker(self):
        exact, expected = install.minimum_requirements(
            ["imagespec[datamatrix]>=1.0.0", 'blesession>=1.2; python_version < "2"'],
            ["imagespec", "blesession"],
        )
        self.assertEqual(exact, ["imagespec[datamatrix]==1.0.0"])
        self.assertEqual(expected, {"imagespec": Version("1.0.0")})

    def test_minimum_missing_or_range_fails(self):
        for reqs in [[], ["imagespec>=1,<2"]]:
            with self.assertRaises(ValueError):
                install.minimum_requirements(reqs, ["imagespec"])

    def test_recursive_ha_requirements_handle_cycles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, reqs, deps in [("one", ["a==1"], ["two"]), ("two", ["b==1"], ["one"])]:
                p = root / "components" / name
                p.mkdir(parents=True)
                (p / "manifest.json").write_text(
                    json.dumps({"requirements": reqs, "dependencies": deps})
                )
            self.assertEqual(install.component_requirements(root, ["one"]), ["a==1", "b==1"])
            with self.assertRaises(ValueError):
                install.component_requirements(root, ["../escape"])

    def test_updater_cli_dry_run_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            original = '{"domain":"example","requirements":["imagespec>=1.0"]}\n'
            path.write_text(original)
            with (
                patch.object(
                    sys,
                    "argv",
                    ["update.py", "--manifest", str(path), "--packages", '["imagespec"]'],
                ),
                patch.object(
                    update,
                    "plan_updates",
                    return_value=({"requirements": ["imagespec>=1.1"]}, ["example update"]),
                ),
                patch.dict("os.environ", {"RUNNER_TEMP": directory}, clear=True),
            ):
                update.main()
            self.assertEqual(path.read_text(), original)


class BadgeSafety(unittest.TestCase):
    def test_only_marked_block_changes(self):
        text = "# Title\n\n" + badges.START + "\nold\n" + badges.END + "\n\nMoved to somewhere.\n"
        updated = badges.replace_block(text, "new")
        self.assertEqual(updated, text.replace("\nold\n", "\nnew\n"))

    def test_duplicate_missing_or_reversed_markers_fail(self):
        for text in [
            "# Title",
            badges.END + badges.START,
            badges.START + badges.START + badges.END,
        ]:
            with self.assertRaises(ValueError):
                badges.replace_block(text, "new")

    def test_badges_use_manifest_domain_and_require_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "custom_components/xiaomi_lywsd"
            path.mkdir(parents=True)
            (path / "manifest.json").write_text('{"domain":"xiaomi_lywsd"}')
            (root / "hacs.json").write_text('{"homeassistant":"2025.1.0"}')
            config = {"repository": "eigger/hass-lywsd02", "default_branch": "master"}
            output = badges.render(root, config)
            self.assertNotIn("github/v/release", output)
            with self.assertRaises(ValueError):
                badges.render(root, {**config, "analytics": True})
            output = badges.render(
                root, {**config, "analytics": True, "analytics_evidence": "checked fixture"}
            )
            self.assertIn("xiaomi_lywsd", output)
            with self.assertRaises(ValueError):
                badges.render(root, {**config, "hacs": "default"})

    def test_all_readmes_preflight_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = badges.START + "\nold\n" + badges.END
            (root / "README.md").write_text(original)
            (root / "README.ko.md").write_text("missing markers")
            (root / ".hass-standards.json").write_text(
                json.dumps({"readmes": ["README.md", "README.ko.md"]})
            )
            with (
                patch.object(sys, "argv", ["sync", directory, "--write"]),
                patch.object(badges, "render", return_value="new"),
                self.assertRaises(ValueError),
            ):
                badges.main()
            self.assertEqual((root / "README.md").read_text(), original)

    def test_workflow_yaml_preserves_on_and_booleans(self):
        data = audit.yaml.load(
            "on: {pull_request: null}\njobs: {test: {strategy: {fail-fast: false}}}",
            Loader=audit.Loader,
        )
        self.assertIn("on", data)
        self.assertIs(data["jobs"]["test"]["strategy"]["fail-fast"], False)


if __name__ == "__main__":
    unittest.main()

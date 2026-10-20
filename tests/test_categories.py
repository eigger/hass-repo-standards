"""HA-02 category decisions are explicit, scoped and checked offline."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from standards import categories, contract  # noqa: E402
from test_standards_contract import input_fixture  # noqa: E402


class Categories(unittest.TestCase):
    def test_pinned_snapshot_contains_product_categories(self):
        known = categories.known_categories()
        self.assertIn("computers_network.printers", known)
        self.assertIn("pets", known)
        self.assertNotIn("sensor", known)

    def test_one_to_three_unique_known_categories_preserve_primary_order(self):
        for selected in (
            ["pets"],
            ["pets", "computers_network.printers"],
            ["pets", "computers_network.printers", "energy.solar_batteries"],
        ):
            manifest = {"categories": list(selected)}
            before = copy.deepcopy(manifest)
            categories.validate_manifest(manifest)
            self.assertEqual(manifest, before)

    def test_missing_invalid_duplicate_unknown_or_parent_child_categories_fail(self):
        for value in (
            None,
            [],
            "pets",
            [True],
            ["pets", "pets"],
            ["sensor"],
            ["pets", "finance", "garden_plants", "diy_makers"],
            ["energy", "energy.solar_batteries"],
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                categories.validate_manifest({"categories": value})
        with self.assertRaises(ValueError):
            categories.validate_manifest({})
        with self.assertRaises(ValueError):
            categories.validate_manifest({"integration_type": [], "categories": ["pets"]})

    def test_exempt_types_omit_key_and_require_recorded_rationale(self):
        for integration_type in ("entity", "system", "virtual"):
            data = input_fixture()
            data["manifest"]["value"].update(integration_type=integration_type)
            del data["manifest"]["value"]["categories"]
            data["categories"] = {
                "value": [],
                "source": "Synthetic exemption rationale: metadata test only.",
            }
            contract.validate_input(data)
            review = contract.render_settings(data)["categories_review"]
            categories.validate_review(data["manifest"]["value"], review)
            for value in ([], ["pets"]):
                with self.assertRaises(ValueError):
                    categories.validate_manifest(
                        {"integration_type": integration_type, "categories": value}
                    )

    def test_input_needs_recorded_category_decision_matching_manifest(self):
        data = input_fixture()
        del data["categories"]
        with self.assertRaisesRegex(ValueError, "categories"):
            contract.validate_input(data)
        data = input_fixture()
        data["categories"]["value"] = ["pets"]
        with self.assertRaisesRegex(ValueError, "differs"):
            contract.validate_input(data)
        data = input_fixture()
        data["categories"]["source"] = "   "
        with self.assertRaises(ValueError):
            contract.validate_input(data)

    def test_review_detects_stale_order_type_and_unfinished_or_missing_evidence(self):
        manifest = {"integration_type": "device", "categories": ["pets", "diy_makers"]}
        review = {
            "integration_type": "device",
            "value": ["pets", "diy_makers"],
            "source": "Synthetic supported product decision for offline contract test.",
        }
        categories.validate_review(manifest, review)
        for changed in (
            None,
            {**review, "source": "TODO"},
            {**review, "source": "미확인"},
            {**review, "source": "작성 필요"},
            {**review, "source": ""},
            {**review, "source": "   "},
            {**review, "integration_type": "hub"},
            {**review, "value": ["diy_makers", "pets"]},
            {**review, "status": "PASS"},
        ):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                categories.validate_review(manifest, changed)
        with self.assertRaises(ValueError):
            categories.validate_review(
                {"integration_type": "device", "categories": ["pets"]},
                {"integration_type": "system", "value": [], "source": "Old exemption."},
            )

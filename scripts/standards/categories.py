"""Offline HA-02 category contract; choices always come from recorded product evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path

EXEMPT_TYPES = {"entity", "system", "virtual"}


def known_categories():
    """Read the reviewed upstream taxonomy snapshot, never infer a category."""
    data = json.loads(Path(__file__).with_name("integration_categories.json").read_text())
    values = data["categories"]
    if (
        not isinstance(values, list)
        or not all(isinstance(item, str) for item in values)
        or values != sorted(set(values))
        or not values
        or not re.fullmatch(
            r"https://github.com/home-assistant/core/blob/[0-9a-f]{40}/homeassistant/generated/integration_categories.json",
            data["source"],
        )
        or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data["verified_on"])
    ):
        raise ValueError("Invalid reviewed integration category snapshot")
    return set(values)


def validate_manifest(manifest):
    """Raise for missing/invalid categories, or prohibited categories on exempt types."""
    integration_type = manifest.get("integration_type")
    if integration_type is not None and not isinstance(integration_type, str):
        raise ValueError("integration_type must be a string when provided")
    if integration_type in EXEMPT_TYPES:
        if "categories" in manifest:
            raise ValueError(
                "categories must be omitted for entity/system/virtual integration_type"
            )
        return
    values = manifest.get("categories")
    if not isinstance(values, list) or not 1 <= len(values) <= 3:
        raise ValueError("categories requires 1–3 actual product categories (HA-02 project policy)")
    if not all(isinstance(value, str) for value in values):
        raise ValueError("categories must be a list of strings")
    if len(set(values)) != len(values):
        raise ValueError("categories must not contain duplicates")
    if unknown := set(values) - known_categories():
        raise ValueError("Unknown categories in reviewed snapshot: " + ", ".join(sorted(unknown)))
    if any(value.split(".")[0] in values for value in values if "." in value):
        raise ValueError("categories must not combine a parent with its own subcategory")


def validate_review(manifest, review):
    """Require a recorded choice and source; semantic correctness needs human review."""
    validate_manifest(manifest)
    if not isinstance(review, dict) or set(review) != {"value", "source", "integration_type"}:
        raise ValueError(
            "categories_review requires value, source and integration_type; record the actual category decision"
        )
    if review["integration_type"] != manifest.get("integration_type"):
        raise ValueError("categories_review integration_type differs from manifest; review again")
    expected = manifest.get("categories", [])
    if review["value"] != expected:
        raise ValueError("categories_review value/order differs from manifest; review again")
    source = review["source"]
    if (
        not isinstance(source, str)
        or not source.strip()
        or re.search(
            r"\b(?:TODO|TBD|FIXME|REPLACE(?:_[A-Z_]+)?|YOUR_[A-Z_]+|UNVERIFIED)\b|작성 필요|미입력|미확인",
            source,
            re.I,
        )
    ):
        raise ValueError(
            "categories_review source must record actual product evidence or exemption rationale"
        )

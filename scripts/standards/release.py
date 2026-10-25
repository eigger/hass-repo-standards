"""Validate the centrally managed HACS ZIP release metadata and caller job."""

from __future__ import annotations

import json
import re

import yaml


def errors(root, config, domain, safe_path, central):
    result = []
    try:
        hacs = json.loads(safe_path(root, "hacs.json").read_text(encoding="utf-8"))
        if config.get("hacs") != "default" and hacs.get("zip_release") is not True:
            return result
        if hacs.get("zip_release") is not True or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]*\.zip", hacs.get("filename", "")
        ):
            result.append(
                ("HACS-04", "hacs.json", "ZIP releases need zip_release: true and a safe filename")
            )
        if hacs.get("content_in_root"):
            result.append(
                ("HACS-04", "hacs.json", "Central ZIP releases require custom_components/<domain>")
            )
        path = ".github/workflows/release.yml"
        actual = yaml.safe_load(safe_path(root, path).read_text(encoding="utf-8"))
        expected = yaml.safe_load(
            (central / "templates/integration" / path).read_text(encoding="utf-8")
        )
        uses = (
            [
                step.get("uses", "")
                for step in actual.get("jobs", {}).get("release", {}).get("steps", [])
                if isinstance(step, dict)
            ]
            if isinstance(actual, dict)
            else []
        )
        standards = config.get("standards", {})
        expected_ref = standards.get("tag") if standards.get("kind") == "release" else None
        allowed_ref = re.escape(expected_ref) if expected_ref else r"[a-f0-9]{40}"
        if not any(
            re.fullmatch(r"eigger/hass-repo-standards/actions/release-zip@" + allowed_ref, use)
            for use in uses
        ):
            result.append(
                (
                    "CI-05",
                    path,
                    "Release ZIP action must use the reviewed full SHA or exact recorded release tag",
                )
            )

        def normalize(value):
            if isinstance(value, dict):
                return {key: normalize(item) for key, item in value.items()}
            if isinstance(value, list):
                return [normalize(item) for item in value]
            if isinstance(value, str):
                value = re.sub(
                    r"(eigger/hass-repo-standards/actions/release-zip@)(?:[a-f0-9]{40}|v[0-9]+\.[0-9]+\.[0-9]+)$",
                    r"\1main",
                    value,
                )
                return re.sub(r"^(actions/[a-z-]+@)[a-f0-9]{40}( #.*)?$", r"\1pinned", value)
            return value

        if (
            not isinstance(actual, dict)
            or any(
                actual.get(key) != expected[key]
                for key in ("name", "on", "permissions", "concurrency")
            )
            or normalize(actual.get("jobs", {}).get("release"))
            != normalize(expected["jobs"]["release"])
        ):
            result.append(
                (
                    "HACS-04",
                    path,
                    "Release event, permissions and ZIP job must match the central template",
                )
            )
    except (OSError, ValueError, TypeError, yaml.YAMLError) as error:
        result.append(("HACS-04", "hacs.json/.github/workflows/release.yml", str(error)))
    return result

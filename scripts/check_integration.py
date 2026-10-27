"""Enforce central integration contracts offline; never rewrite unmarked README text."""

from __future__ import annotations

import argparse
import ast
import datetime
import json
import re
from pathlib import Path

import yaml
from bluetooth_documents import check as bluetooth_document_errors
from bluetooth_documents import syntax_error_message
from check_repository import Loader
from payload_documents import check as payload_document_errors
from standards import readme as _readme
from standards import validation
from standards.planning import workflow_events
from sync_badges import preserve_extra_badges as preserve_extra_badges

CENTRAL = Path(__file__).resolve().parent.parent
TEMPLATES = CENTRAL / "templates/integration"
AREAS = ("header", "support", "related-projects", "license")


BADGES_START = _readme.BADGES_START
BADGES_END = _readme.BADGES_END
render_badges = _readme.render_badges
ReadmeErrors = _readme.ReadmeErrors


def safe_path(root, relative):
    return _readme.safe_path(root, relative)


def markers(area):
    return _readme.markers(area)


def block(text, area):
    return _readme.block(text, area)


def replace(text, area, content):
    return _readme.replace(text, area, content)


def line(value):
    return _readme.line(value)


def render_readme(root, config, language, original):
    return _readme.render_readme(root, config, language, original)


def guard_content(old, new, area):
    return _readme.guard_content(old, new, area)


def readme_update(root, config, language, name):
    return _readme.readme_update(root, config, language, name)


def readme_updates(root, config):
    return _readme.readme_updates(root, config)


def test_errors(root, domain):
    errors = []
    safe_path(root, "tests")
    for file in (root / "tests").rglob("*"):
        safe_path(root, file.relative_to(root))
    prefix = Path("tests/components") / domain
    errors.extend(validation.foundation_errors(root, domain, safe_path, CENTRAL))
    path = prefix / "test_init.py"
    if not (root / path).is_file():
        errors.append(("TEST-08", str(path), "real HA lifecycle tests are required"))
    # Lifecycle semantics and mock boundaries still require independent review and real HA runs.
    for file in (root / "tests").rglob("*.py"):
        try:
            ast.parse(file.read_text(), filename=str(file))
        except SyntaxError as err:
            errors.append(("TEST-08", file.relative_to(root).as_posix(), syntax_error_message(err)))
    return errors


def workflow_errors(root, config, domain):
    errors = []
    workflow_dir = safe_path(root, ".github/workflows")
    expected = {"validate.yml": "Validate", "tests.yml": "Tests"}
    separate_standards = (workflow_dir / "standards.yml").exists()
    if separate_standards:
        expected["standards.yml"] = "Standards"
    if (workflow_dir / "update_dependencies.yml").exists():
        expected["update_dependencies.yml"] = "Update dependencies"
    standards = config.get("standards", {})
    release_tag = standards.get("tag") if standards.get("kind") == "release" else None
    expected_action_ref = release_tag or None
    for path in sorted(workflow_dir.glob("*.y*ml")):
        safe_path(root, path.relative_to(root))
        data = yaml.load(path.read_text(), Loader=Loader)
        if not isinstance(data, dict):
            errors.append(("CI-01", str(path.relative_to(root)), "workflow must be a mapping"))
            continue
        if not re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*\.yml", path.name):
            errors.append(("CI-01", str(path.relative_to(root)), "use snake_case.yml"))
        if not re.fullmatch(r"[A-Z][A-Za-z0-9 /():._+-]*", str(data.get("name", ""))):
            errors.append(
                ("CI-01", str(path.relative_to(root)), "descriptive English workflow name required")
            )
        if path.name not in expected:
            continue
        rel = path.relative_to(root).as_posix()
        template = yaml.load((TEMPLATES / rel).read_text(), Loader=Loader)
        events = workflow_events(template, config["default_branch"])
        if data.get("name") != expected[path.name] or data.get("on") != events:
            errors.append(
                (
                    "CI-02",
                    rel,
                    "name and events must match the central template (actual default branch)",
                )
            )
        required = {
            "validate.yml": "validate-integration.yml",
            "tests.yml": "python-tests.yml",
            "update_dependencies.yml": "dependency-update.yml",
            "standards.yml": None,
        }[path.name]
        jobs = data.get("jobs", {})
        calls = [job for job in jobs.values() if required and required in job.get("uses", "")]
        marker = f"eigger/hass-repo-standards/.github/workflows/{required}@"
        if required and (
            not calls
            or any(
                not re.fullmatch(
                    re.escape(marker)
                    + (re.escape(expected_action_ref) if expected_action_ref else r"[0-9a-f]{40}"),
                    job.get("uses", ""),
                )
                for job in calls
            )
        ):
            errors.append(
                (
                    "CI-01",
                    rel,
                    "central reusable workflow must be pinned to the reviewed full SHA or exact recorded release tag",
                )
            )
        if path.name == "tests.yml" and any(
            job.get("with", {}).get("test-profile") != "ha"
            or job.get("with", {}).get("domain") != domain
            for job in calls
        ):
            errors.append(("CI-07", rel, "HA profile and actual domain required"))
        if path.name == "tests.yml" and len(calls) > 1:
            # With a separate minimum job, `current` follows the test plugin's HA pin.
            current = jobs.get("current")
            if (
                current in calls
                and str(current.get("with", {}).get("expected-ha-version") or "").strip()
            ):
                errors.append(
                    (
                        "CI-07",
                        rel,
                        "current job must leave expected-ha-version empty when a separate "
                        "minimum job exists; it follows the test plugin HA pin",
                    )
                )
        for job in calls:
            if job.get("if") is not None or job.get("needs") or job.get("continue-on-error", False):
                errors.append(
                    ("CI-04", rel, "common calls must not be skipped or suppress failures")
                )
        if path.name in {"validate.yml", "standards.yml"}:
            for job in jobs.values():
                standard_steps = [
                    step
                    for step in job.get("steps", [])
                    if "hass-repo-standards/actions/check-standards@" in step.get("uses", "")
                ]
                if standard_steps and (
                    job.get("if") is not None
                    or job.get("needs")
                    or job.get("continue-on-error", False)
                    or any(
                        step.get("if") is not None or step.get("continue-on-error", False)
                        for step in standard_steps
                    )
                ):
                    errors.append(
                        (
                            "CI-04",
                            rel,
                            "standards check must run without conditional or failure suppression",
                        )
                    )
                if standard_steps and (
                    not job.get("timeout-minutes")
                    or not any(
                        step.get("uses", "").startswith("actions/checkout@")
                        and step.get("with", {}).get("persist-credentials") is False
                        and step.get("if") is None
                        and not step.get("continue-on-error", False)
                        for step in job.get("steps", [])
                    )
                ):
                    errors.append(
                        (
                            "CI-03",
                            rel,
                            "standards job requires timeout and caller checkout without persisted credentials",
                        )
                    )
            actions = [
                step.get("uses", "") for job in jobs.values() for step in job.get("steps", [])
            ]
            action = "eigger/hass-repo-standards/actions/check-standards@"
            if (path.name == "standards.yml" or not separate_standards) and not any(
                re.fullmatch(
                    re.escape(action)
                    + (re.escape(expected_action_ref) if expected_action_ref else r"[0-9a-f]{40}"),
                    value,
                )
                for value in actions
            ):
                errors.append(
                    (
                        "CI-01",
                        rel,
                        "central standards action must be pinned to the reviewed full SHA or exact recorded release tag",
                    )
                )
    for name in expected:
        if not (workflow_dir / name).is_file():
            errors.append(
                ("CI-01", f".github/workflows/{name}", "required common workflow missing")
            )
    return errors


def apply_exceptions(root, config, errors):
    """CI checks recorded evidence; the agent obtains human approval separately."""
    exceptions = config.get("exceptions", [])
    for item in exceptions:
        for key in ("id", "rule", "paths", "reason", "approved_by", "approved_at", "evidence"):
            if not item.get(key):
                raise ValueError(f"Exception missing {key}")
        datetime.date.fromisoformat(item["approved_at"])
        if not isinstance(item["paths"], list) or any(
            "*" in p or ".." in Path(p).parts for p in item["paths"]
        ):
            raise ValueError("Exception paths must be explicit repository paths")
        evidence = item["evidence"]
        if not evidence.startswith("STANDARDS.md#") or not (root / "STANDARDS.md").is_file():
            raise ValueError("Exception evidence must link to STANDARDS.md#anchor")
        if item["id"] not in (root / "STANDARDS.md").read_text():
            raise ValueError("Exception ID must be recorded in STANDARDS.md")
    remaining = []
    for rule, path, message in errors:
        item = next((e for e in exceptions if e["rule"] == rule and path in e["paths"]), None)
        if item:
            print(f"EXCEPTION {item['id']} {rule} {path}: {message}")
        else:
            remaining.append(f"{rule} {path}: {message}")
    return remaining


def check(root, write_readmes=False):
    config = json.loads(safe_path(root, ".hass-standards.json").read_text())
    manifests = list((root / "custom_components").glob("*/manifest.json"))
    if len(manifests) != 1:
        raise ValueError("Exactly one HA integration manifest required")
    safe_path(root, manifests[0].relative_to(root))
    manifest = json.loads(manifests[0].read_text())
    domain = manifest["domain"]
    if not re.fullmatch(r"[a-z][a-z0-9_]*", domain) or manifests[0].parent.name != domain:
        raise ValueError("manifest domain and directory must match")
    errors = []
    try:
        updates = readme_updates(root, config)
    except ReadmeErrors as err:
        updates = []
        errors.extend(("DOC-01", path, message) for path, message in err.errors)
    except (ValueError, KeyError, FileNotFoundError) as err:
        updates = []
        errors.append(("DOC-01", ".hass-standards.json", str(err)))
    for path, _ in updates:
        if not write_readmes:
            errors.append(("DOC-01", path.name, "managed areas differ from central rendering"))
    errors.extend(validation.check(root, config, manifests[0], manifest, safe_path, CENTRAL))
    from standards import release

    errors.extend(release.errors(root, config, domain, safe_path, CENTRAL))
    errors.extend(test_errors(root, domain))
    errors.extend(workflow_errors(root, config, domain))
    errors.extend(bluetooth_document_errors(root, config, manifests[0], manifest, safe_path))
    errors.extend(payload_document_errors(root, config, manifests[0], manifest, safe_path))
    result = apply_exceptions(root, config, errors)
    # All documents preflight above; preserve bytes outside explicitly managed areas.
    if write_readmes and not any(rule == "DOC-01" for rule, _, _ in errors):
        for path, updated in updates:
            path.write_bytes(updated.encode("utf-8"))
            print(f"WRITE {path}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_path", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Check only (default)")
    mode.add_argument("--write-readmes", action="store_true")
    args = parser.parse_args()
    try:
        errors = check(args.repository_path.resolve(), args.write_readmes)
    except (ValueError, KeyError, FileNotFoundError, SyntaxError) as err:
        parser.exit(1, f"ERROR: {err}\n")
    for error in errors:
        print(error)
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()

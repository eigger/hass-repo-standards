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
from sync_badges import END as BADGES_END
from sync_badges import START as BADGES_START
from sync_badges import preserve_extra_badges
from sync_badges import render as render_badges

CENTRAL = Path(__file__).resolve().parent.parent
TEMPLATES = CENTRAL / "templates/integration"
AREAS = ("header", "support", "related-projects", "license")


def safe_path(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes repository: {relative}")
    return path


def markers(area):
    return (f"<!-- hass-standards:{area}:start -->", f"<!-- hass-standards:{area}:end -->")


def block(text, area):
    start, end = markers(area)
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise ValueError(f"Exactly one ordered {area} marker pair required")
    return text.split(start)[1].split(end)[0].strip("\n")


def replace(text, area, content):
    block(text, area)
    start, end = markers(area)
    before, rest = text.split(start)
    _, after = rest.split(end)
    return before + start + "\n" + (content + "\n" if content else "") + end + after


def line(value):
    if not isinstance(value, str) or not value.strip() or "\n" in value or "\r" in value:
        raise ValueError("README metadata must contain nonempty single lines")
    return value


def render_readme(root, config, language, original):
    data = config["readme"]
    name = "README.md" if language == "en" else "README.ko.md"
    title = line(data["title"])
    description = line(data["descriptions"][language])
    language_link = (
        "**English** | [한국어](README.ko.md)"
        if language == "en"
        else "[English](README.md) | **한국어**"
    )
    if not isinstance(data["issues"], bool) or not isinstance(data["discussions"], bool):
        raise ValueError("issues and discussions must be booleans")
    if not safe_path(root, "LICENSE").is_file():
        raise ValueError("Actual LICENSE file required")
    existing_header = block(original, "header")
    block(existing_header, "badges")
    badges = preserve_extra_badges(existing_header, render_badges(root, config, root / name))
    header = (
        f"# {title}\n\n{description}\n\n{language_link}\n\n{BADGES_START}\n{badges}\n{BADGES_END}"
    )
    support = ["## Support" if language == "en" else "## 지원"]
    base = f"https://github.com/{config['repository']}"
    if data["issues"]:
        support.extend(
            [
                "",
                f"- [Issues]({base}/issues): "
                + (
                    "Report bugs or request features."
                    if language == "en"
                    else "버그를 신고하거나 기능을 요청하세요."
                ),
            ]
        )
    if data["discussions"]:
        if len(support) == 1:
            support.append("")
        support.append(
            f"- [Discussions]({base}/discussions): "
            + (
                "Ask questions and share your experience."
                if language == "en"
                else "질문하고 사용 경험을 공유하세요."
            )
        )
    if len(support) == 1:
        support = []
    projects = data.get("related_projects", [])
    related = []
    if projects:
        related = ["## Related Projects" if language == "en" else "## 관련 프로젝트", ""]
        related.extend(
            f"- [{line(p['name'])}]({line(p['url'])}): {line(p['description'][language])}"
            for p in projects
        )
    license_name = line(data["license_name"])
    license_text = (
        f"Released under the [{license_name}](LICENSE)."
        if language == "en"
        else f"[{license_name}](LICENSE) 라이선스로 배포됩니다."
    )
    license_block = ["## License" if language == "en" else "## 라이선스", "", license_text]
    for notice in data.get("license_notices", {}).get(language, []):
        license_block.extend(["", line(notice)])
    for area, content in zip(
        AREAS, [header, "\n".join(support), "\n".join(related), "\n".join(license_block)]
    ):
        guard_content(block(original, area), content, area)
        original = replace(original, area, content)
    return original


def guard_content(old, new, area):
    """Refuse to erase unrecognized prose or existing notices during automated sync."""
    if not old.strip():
        return
    if area == "header":
        start, end = markers("badges")
        before, rest = old.split(start)
        _, after = rest.split(end)
        if after.strip():
            raise ValueError("Preserve extra header content outside the managed area before sync")
        lines = before.strip().split("\n\n") if before.strip() else []
        if lines and (
            len(lines) != 3
            or not lines[0].startswith("# ")
            or "\n" in lines[1]
            or lines[2]
            not in {"**English** | [한국어](README.ko.md)", "[English](README.md) | **한국어**"}
        ):
            raise ValueError("Header contains non-template content; migrate manually without loss")
        return
    for value in old.splitlines():
        if not value.strip() or value in new.splitlines():
            continue
        if area == "support" and (
            value in {"## Support", "## 지원"}
            or re.fullmatch(
                r"- \[(?:Issues|Discussions)\]\(https://github.com/[^)]+/(?:issues|discussions)\): (?:Report bugs or request features\.|Ask questions and share your experience\.|버그를 신고하거나 기능을 요청하세요\.|질문하고 사용 경험을 공유하세요\.)",
                value,
            )
        ):
            continue
        if area == "license" and (
            value in {"## License", "## 라이선스"}
            or re.fullmatch(
                r"(?:Released under the \[[^]]+\]\(LICENSE\)\.|\[[^]]+\]\(LICENSE\) 라이선스로 배포됩니다\.)",
                value,
            )
        ):
            continue
        raise ValueError(
            f"Preserve existing {area} content in metadata or body before sync: {value}"
        )


def readme_update(root, config, language, name):
    path = safe_path(root, name)
    original = path.read_bytes().decode("utf-8")
    # Validate disjoint blocks and their canonical position before any writes.
    spans = []
    for area in AREAS:
        block(original, area)
        start, end = markers(area)
        spans.append((original.index(start), original.index(end) + len(end)))
    if any(a[1] > b[0] for a, b in zip(spans, spans[1:])):
        raise ValueError("README common areas overlap or are out of order")
    if original[: spans[0][0]].strip() or original[spans[-1][1] :].strip():
        raise ValueError("Header must be first and license must be last")
    for a, b in zip(spans[1:], spans[2:]):
        if original[a[1] : b[0]].strip():
            raise ValueError("Support, related projects and license must be contiguous at the end")
    updated = render_readme(root, config, language, original)
    return path, original, updated


class ReadmeErrors(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{path}: {message}" for path, message in errors))


def readme_updates(root, config):
    if config.get("readmes") != ["README.md", "README.ko.md"]:
        raise ValueError("readmes must be [README.md, README.ko.md]")
    for key, expected in (("tests_workflow", "tests.yml"), ("validate_workflow", "validate.yml")):
        if config.get(key, expected) != expected:
            raise ValueError(f"{key} must be {expected}")
    updates, errors = [], []
    for language, name in zip(("en", "ko"), config["readmes"]):
        try:
            path, original, updated = readme_update(root, config, language, name)
            if updated != original:
                updates.append((path, updated))
        except (ValueError, KeyError, FileNotFoundError) as err:
            errors.append((name, str(err)))
    if errors:
        raise ReadmeErrors(errors)
    return updates


def test_errors(root, domain):
    errors = []
    safe_path(root, "tests")
    for file in (root / "tests").rglob("*"):
        safe_path(root, file.relative_to(root))
    prefix = Path("tests/components") / domain
    for path in [
        Path("tests/__init__.py"),
        Path("tests/components/__init__.py"),
        prefix / "__init__.py",
    ]:
        if not (root / path).is_file() or (root / path).read_bytes() != b"":
            errors.append(("TEST-08", str(path), "must exist and be empty"))
    path = Path("tests/conftest.py")
    if not (root / path).is_file() or (root / path).read_bytes() != (TEMPLATES / path).read_bytes():
        errors.append(("TEST-03", str(path), "must match the central template exactly"))
    path = prefix / "conftest.py"
    expected = (TEMPLATES / "tests/components/example/conftest.py").read_text()
    try:
        valid = (root / path).is_file() and block(
            (root / path).read_text(), "domain-fixtures"
        ) == block(expected, "domain-fixtures")
    except ValueError:
        valid = False
    if not valid:
        errors.append(("TEST-08", str(path), "managed domain fixture skeleton is required"))
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
    if (workflow_dir / "update_dependencies.yml").exists():
        expected["update_dependencies.yml"] = "Update dependencies"
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
        events = json.loads(json.dumps(template["on"]))
        if "push" in events:
            events["push"]["branches"] = [config["default_branch"]]
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
        }[path.name]
        jobs = data.get("jobs", {})
        calls = [job for job in jobs.values() if required in job.get("uses", "")]
        marker = f"eigger/hass-repo-standards/.github/workflows/{required}@"
        if not calls or any(
            not re.fullmatch(re.escape(marker) + r"[0-9a-f]{40}", job.get("uses", ""))
            for job in calls
        ):
            errors.append(
                ("CI-01", rel, "central reusable workflow pinned to reviewed full SHA required")
            )
        if path.name == "tests.yml" and any(
            job.get("with", {}).get("test-profile") != "ha"
            or job.get("with", {}).get("domain") != domain
            for job in calls
        ):
            errors.append(("CI-07", rel, "HA profile and actual domain required"))
        for job in calls:
            if job.get("if") is not None or job.get("needs") or job.get("continue-on-error", False):
                errors.append(
                    ("CI-04", rel, "common calls must not be skipped or suppress failures")
                )
        if path.name == "validate.yml":
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
            if not any(
                re.fullmatch(re.escape(action) + r"[0-9a-f]{40}", value) for value in actions
            ):
                errors.append(
                    ("CI-01", rel, "central standards composite action pinned to full SHA required")
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

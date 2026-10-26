"""Structural DOC-08 checks; execution is owned by the shared payload pytest contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from bluetooth_documents import (
    has_local_link,
    links,
    syntax_error_message,
    visible_markdown,
)
from standards.conditions import uses_package
from standards.reference import metadata_input

SOURCE = "https://github.com/eigger/imagespec/blob/main/docs/"
UNFINISHED = re.compile(
    r"\b(?:TODO|TBD|FIXME|REPLACE_[A-Z_]+|YOUR_[A-Z_]+)\b|example\.com|hass-example|작성 필요|미입력",
    re.I,
)
HEADINGS = {
    "en": (
        "Common payload guide",
        "Using payloads in this integration",
        "Minimal working example",
        "Device output settings",
        "Supported features and limitations",
        "Troubleshooting",
    ),
    "ko": (
        "공통 payload 안내",
        "이 통합에서 payload 사용",
        "최소 동작 예제",
        "기기 출력 설정",
        "지원 기능과 제한",
        "문제 해결",
    ),
}
SCAFFOLD = (
    Path(__file__).resolve().parent.parent
    / "templates/integration/tests/components/example/test_payload_examples.py"
).read_text(encoding="utf-8")


class ExampleError(ValueError):
    def __init__(self, path, message):
        self.path = path
        super().__init__(message)


def decoded_payload(value, format_name, *, normalized=False, defer_templates=False):
    if defer_templates and isinstance(value, str) and ("{{" in value or "{%" in value):
        if format_name not in {"list", "yaml"}:
            raise ValueError("payload_format must be list or yaml")
        return None  # Actual HA/schema preparation must resolve this at runtime.
    if format_name == "yaml":
        if isinstance(value, str):
            value = yaml.safe_load(value)
        elif not (normalized and isinstance(value, list)):
            raise ValueError("payload_format yaml requires the actual schema's YAML string")
    elif format_name != "list":
        raise ValueError("payload_format must be list or yaml")
    if not isinstance(value, list) or not value:
        raise ValueError("The decoded payload must be a nonempty element list")
    return value


def examples(root, config, safe_path):
    entries = config["payload"]["examples"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("payload.examples must list actual action YAML examples")
    seen = set()
    for entry in entries:
        name = entry["path"]
        if (
            not isinstance(name, str)
            or not name.startswith("examples/payload/")
            or Path(name).suffix != ".yaml"
            or name in seen
        ):
            raise ValueError("Use unique examples/payload/*.yaml paths")
        seen.add(name)
        try:
            path = safe_path(root, name)
            text = path.read_text(encoding="utf-8")
            if UNFINISHED.search(text):
                raise ValueError("unfinished placeholder")
            data = yaml.safe_load(text)
            if not isinstance(data, dict):
                raise ValueError("full HA action mapping required")
        except (ValueError, OSError, yaml.YAMLError) as err:
            raise ExampleError(name, str(err)) from err
        keys = entry["payload_path"]
        if (
            not isinstance(keys, list)
            or not keys
            or not all(isinstance(k, (str, int)) and not isinstance(k, bool) for k in keys)
        ):
            raise ValueError("payload_path must identify the actual nested payload")
        for key in keys:
            data = data[key]
        try:
            decoded_payload(data, entry.get("payload_format", "list"), defer_templates=True)
        except (ValueError, yaml.YAMLError) as err:
            raise ExampleError(name, str(err)) from err
        size = entry["expected_size"]
        palette = entry["expected_palette"]
        if (
            not isinstance(size, list)
            or len(size) != 2
            or not all(type(n) is int and n > 0 for n in size)
        ):
            raise ValueError("expected_size must contain actual positive output width and height")
        if (
            not isinstance(palette, list)
            or not palette
            or not all(isinstance(c, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in palette)
        ):
            raise ValueError("expected_palette must list actual #RRGGBB device colors")
    return entries


def check(root, config, manifest_path, manifest, safe_path):
    try:
        required = uses_package(root, manifest_path, manifest, safe_path, "imagespec")
    except SyntaxError as err:
        return [
            ("DOC-08", Path(err.filename).relative_to(root).as_posix(), syntax_error_message(err))
        ]
    except (ValueError, OSError) as err:
        return [("DOC-08", manifest_path.relative_to(root).as_posix(), str(err))]
    if not required:
        return []
    errors = []
    try:
        entries = examples(root, config, safe_path)
    except ExampleError as err:
        entries = []
        errors.append(("DOC-08", err.path, str(err)))
    except (ValueError, KeyError, TypeError, IndexError, OSError, yaml.YAMLError) as err:
        entries = []
        errors.append(("DOC-08", ".hass-standards.json", str(err)))
    domain = manifest["domain"]
    test_path = Path("tests/components") / domain / "test_payload_examples.py"
    try:
        if safe_path(root, test_path).read_text() != SCAFFOLD:
            raise ValueError(
                "Use the exact central payload contract scaffold; a caller pass test is insufficient"
            )
    except (ValueError, OSError) as err:
        errors.append(("DOC-08", test_path.as_posix(), str(err)))
    for language, name, other in (
        ("en", "payload.md", "payload.ko.md"),
        ("ko", "payload.ko.md", "payload.md"),
    ):
        relative = Path("docs") / name
        readme = Path("README.md" if language == "en" else "README.ko.md")
        try:
            text = visible_markdown(safe_path(root, relative).read_text(encoding="utf-8"))
            matches = list(re.finditer(r"^## (.+?)\s*$", text, re.M))
            if [m[1] for m in matches] != list(HEADINGS[language]):
                raise ValueError("Use the six central payload H2 headings in order")
            if UNFINISHED.search(text):
                raise ValueError("Unfinished payload documentation placeholder")
            sections = [
                text[
                    m.end() : matches[i + 1].start() if i + 1 < len(matches) else len(text)
                ].strip()
                for i, m in enumerate(matches)
            ]
            if any(
                not section or not re.search(r"[A-Za-z가-힣]", re.sub(r"[|:#*`_-]", "", section))
                for section in sections
            ):
                raise ValueError("Every payload section requires actual content")
            if SOURCE + name not in [link.split("#", 1)[0] for link in links(sections[0])]:
                raise ValueError("Link matching-language imagespec common payload guide")
            if not has_local_link(root, relative, text, readme, safe_path) or not has_local_link(
                root, relative, text, Path("docs") / other, safe_path
            ):
                raise ValueError("Link matching README and alternate-language payload guide")
            declared_paths = {safe_path(root, entry["path"]).resolve() for entry in entries}
            from urllib.parse import unquote, urlsplit

            for link in links(text):
                parsed = urlsplit(link)
                if (
                    not parsed.scheme
                    and not parsed.netloc
                    and Path(unquote(parsed.path)).suffix.lower() in {".yaml", ".yml"}
                ):
                    linked = safe_path(root, relative.parent / unquote(parsed.path)).resolve()
                    if linked not in declared_paths:
                        raise ValueError(
                            "Every linked local action YAML must be registered and executed in payload.examples"
                        )
            for entry in entries:
                if not has_local_link(root, relative, sections[2], Path(entry["path"]), safe_path):
                    raise ValueError("Minimal working example must link every declared action YAML")
            issue = f"https://github.com/{config['repository']}/issues"
            troubleshooting = Path("docs") / (
                "troubleshooting.md" if language == "en" else "troubleshooting.ko.md"
            )
            if issue not in [
                link.split("?", 1)[0]
                .split("#", 1)[0]
                .removesuffix("/new/choose")
                .removesuffix("/new")
                for link in links(sections[5])
            ] and not (
                safe_path(root, troubleshooting).is_file()
                and has_local_link(root, relative, sections[5], troubleshooting, safe_path)
            ):
                raise ValueError(
                    "Troubleshooting must link existing local troubleshooting or integration Issues"
                )
        except (ValueError, KeyError, OSError) as err:
            errors.append(("DOC-08", relative.as_posix(), str(err)))
        try:
            text = visible_markdown(safe_path(root, readme).read_text())
            if not has_local_link(root, readme, text, relative, safe_path):
                raise ValueError("README must link its matching-language local payload guide")
        except (ValueError, OSError) as err:
            errors.append(("DOC-08", readme.as_posix(), str(err)))
    # Every required HA job must run the central plugin at the same reviewed ref.
    from check_repository import Loader

    workflow = root / ".github/workflows/tests.yml"
    data = yaml.load(workflow.read_text(), Loader=Loader)
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name

    selected = next(
        (
            Requirement(r)
            for r in manifest.get("requirements", [])
            if canonicalize_name(Requirement(r).name) == "imagespec"
        ),
        None,
    )
    if (
        sum(
            canonicalize_name(Requirement(r).name) == "imagespec"
            for r in manifest.get("requirements", [])
        )
        > 1
    ):
        errors.append(
            (
                "DOC-08",
                manifest_path.relative_to(root).as_posix(),
                "Multiple conditional imagespec requirements need an explicit branch-aware current/minimum contract adaptation; first-branch coverage alone is insufficient",
            )
        )
    if selected is None:
        errors.append(
            (
                "DOC-08",
                manifest_path.relative_to(root).as_posix(),
                "Actual imagespec import requires a declared runtime requirement and explicit lower-version policy",
            )
        )
    exact = (
        selected is not None
        and len(selected.specifier) == 1
        and next(iter(selected.specifier)).operator == "=="
        and "*" not in str(selected.specifier)
    )
    current, minimum = False, False
    standards = config.get("standards", {})
    release_tag = standards.get("tag") if standards.get("kind") == "release" else None
    resolved_sha = standards.get("resolved_sha") if release_tag else None
    for job in data.get("jobs", {}).values():
        reference = job.get("uses", "")
        if "hass-repo-standards/.github/workflows/python-tests.yml@" not in reference:
            continue
        inputs = job.get("with", {})
        expected_use = release_tag or reference.rsplit("@", 1)[1]
        expected_input = resolved_sha or reference.rsplit("@", 1)[1]
        if (
            reference.rsplit("@", 1)[1] != expected_use
            or metadata_input(config, inputs.get("standards-ref")) != expected_input
        ):
            errors.append(
                (
                    "DOC-08",
                    ".github/workflows/tests.yml",
                    "workflow release/SHA and standards-ref must equal the recorded reviewed descriptor",
                )
            )
        if inputs.get("test-profile") != "ha":
            continue
        modes = json.loads(inputs.get("dependency-modes", '["current"]'))
        packages = json.loads(inputs.get("minimum-packages", "[]"))
        from packaging.markers import default_environment

        def active_python(python):
            if selected is None:
                return False
            if selected.marker is None:
                return True
            marker = str(selected.marker)
            parts = str(python).split(".")
            if (
                any(name in marker for name in ("python_full_version", "implementation_version"))
                and len(parts) != 3
            ):
                return False  # A floating patch cannot prove a full-version marker.
            if any(name in marker for name in ("platform_release", "platform_version")):
                return False  # Runner image values need an explicit compatible environment.
            environment = {
                **default_environment(),
                "python_version": ".".join(parts[:2]),
                "python_full_version": str(python) if len(parts) == 3 else str(python) + ".0",
                "sys_platform": "linux",
                "os_name": "posix",
                "platform_system": "Linux",
                "platform_machine": "x86_64",
                "implementation_name": "cpython",
                "implementation_version": str(python) if len(parts) == 3 else str(python) + ".0",
                "platform_python_implementation": "CPython",
                "extra": "",
            }
            return selected.marker.evaluate(environment)

        active = any(
            active_python(python) for python in json.loads(inputs.get("python-versions", "[]"))
        )
        current |= active and "current" in modes
        minimum |= (
            active
            and "minimum" in modes
            and "imagespec" in [canonicalize_name(p) for p in packages]
        )
    if not current or (not exact and not minimum):
        errors.append(
            (
                "DOC-08",
                ".github/workflows/tests.yml",
                "Required HA jobs collectively need installed current and exact minimum imagespec; one exact pin may reuse current",
            )
        )
    updater = root / ".github/workflows/update_dependencies.yml"
    if updater.is_file():
        for job in yaml.load(updater.read_text(), Loader=Loader).get("jobs", {}).values():
            reference = job.get("uses", "")
            expected_use = release_tag or reference.rsplit("@", 1)[1]
            expected_input = resolved_sha or reference.rsplit("@", 1)[1]
            if "hass-repo-standards/.github/workflows/dependency-update.yml@" in reference and (
                reference.rsplit("@", 1)[1] != expected_use
                or metadata_input(config, job.get("with", {}).get("standards-ref"))
                != expected_input
            ):
                errors.append(
                    (
                        "DOC-08",
                        ".github/workflows/update_dependencies.yml",
                        "Dependency update release/SHA and standards-ref must match the recorded descriptor",
                    )
                )
    return errors

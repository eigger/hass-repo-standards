"""Check the structural DOC-07 contract without claiming to validate device behavior."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

SOURCE = "https://github.com/eigger/blesession/blob/main/docs/"
HEADINGS = {
    "en": (
        "Common troubleshooting",
        "Device-specific checks",
        "Symptoms and actions",
        "Diagnostics and logs",
        "If the problem persists",
    ),
    "ko": (
        "공통 문제 해결",
        "기기별 확인 사항",
        "증상과 조치",
        "진단 및 로그",
        "문제가 계속되는 경우",
    ),
}
TABLES = {
    "en": ("Symptom", "Failing stage", "Checks", "Action"),
    "ko": ("증상", "실패 단계", "확인 사항", "조치"),
}
PLACEHOLDER = re.compile(
    r"\b(?:TODO|TBD|FIXME|YOUR_[A-Z_]+)\b|\{\{[^}]+\}\}|example\.com|hass-example|작성 필요|미입력",
    re.I,
)


def visible_markdown(text):
    """Exclude comments and fenced/indented code from structural evidence."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # Raw HTML pre/code blocks display literal Markdown rather than headings or
    # links. Include non-rendered HTML text containers; an unclosed block also
    # cannot supply structural evidence through the rest of the document.
    text = re.sub(
        r"<(pre|code|script|style|textarea|xmp)\b[^>]*>.*?(?:</\1\s*>|\Z)",
        "",
        text,
        flags=re.S | re.I,
    )
    result, fence = [], None
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None and not line.startswith(("    ", "\t")):
            result.append(line)
    return "\n".join(result)


def links(text):
    text = re.sub(r"`+[^`]*`+", "", text)
    return re.findall(r"(?<!!)\[[^]\n]+\]\(([^\s)]+)\)", text)


def has_local_link(root, current, text, expected, safe_path):
    target = safe_path(root, expected).resolve()
    for link in links(text):
        parsed = urlsplit(link)
        if not parsed.scheme and not parsed.netloc and parsed.path:
            candidate = safe_path(root, current.parent / unquote(parsed.path)).resolve()
            if candidate == target:
                return True
    return False


def has_source_link(text, filename):
    return any(link.split("#", 1)[0] == SOURCE + filename for link in links(text))


def syntax_error_message(error):
    return (
        f"Python {sys.version_info.major}.{sys.version_info.minor} cannot parse this file "
        f"at line {error.lineno}: {error.msg}. Run the checker with Python matching "
        "or newer than the integration's syntax, and correct any remaining syntax error; "
        "this does not change the integration's support minimum."
    )


def uses_package(root, manifest_path, manifest, safe_path, package):
    # Do not evaluate markers on the checker's OS/Python: every declared target
    # environment remains part of the integration's support scope.
    if any(
        canonicalize_name(Requirement(req).name) == canonicalize_name(package)
        for req in manifest.get("requirements", [])
    ):
        return True
    for path in manifest_path.parent.rglob("*.py"):
        safe_path(root, path.relative_to(root))
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                alias.name.split(".")[0] == package for alias in node.names
            ):
                return True
            if (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and (node.module or "").split(".")[0] == package
            ):
                return True
    return False


def uses_blesession(root, manifest_path, manifest, safe_path):
    return uses_package(root, manifest_path, manifest, safe_path, "blesession")


def check(root, config, manifest_path, manifest, safe_path):
    errors = []
    try:
        required = uses_blesession(root, manifest_path, manifest, safe_path)
    except SyntaxError as err:
        return [
            ("DOC-07", Path(err.filename).relative_to(root).as_posix(), syntax_error_message(err))
        ]
    except (ValueError, OSError) as err:
        return [("DOC-07", manifest_path.relative_to(root).as_posix(), str(err))]
    if not required:
        return []
    for language, name, other in (
        ("en", "troubleshooting.md", "troubleshooting.ko.md"),
        ("ko", "troubleshooting.ko.md", "troubleshooting.md"),
    ):
        relative = Path("docs") / name
        readme = Path("README.md" if language == "en" else "README.ko.md")
        try:
            path = safe_path(root, relative)
            text = visible_markdown(path.read_text(encoding="utf-8"))
            headings = list(re.finditer(r"^## (.+?)\s*$", text, re.M))
            if [match[1] for match in headings] != list(HEADINGS[language]):
                raise ValueError("Use the central troubleshooting H2 headings in their fixed order")
            if PLACEHOLDER.search(text):
                raise ValueError(
                    "Replace template placeholders with verified device information or honest N/A"
                )
            sections = [
                text[
                    match.end() : headings[index + 1].start()
                    if index + 1 < len(headings)
                    else len(text)
                ].strip()
                for index, match in enumerate(headings)
            ]
            if any(
                not section or not re.search(r"[A-Za-z가-힣]", re.sub(r"[|:#*`_-]", "", section))
                for section in sections
            ):
                raise ValueError(
                    "Every required section needs actual content; code/comments alone are not evidence"
                )
            table = [line for line in sections[2].splitlines() if line.startswith("|")]

            def cells(line):
                return tuple(value.strip() for value in line.strip().strip("|").split("|"))

            if (
                len(table) < 3
                or cells(table[0]) != TABLES[language]
                or len(cells(table[1])) != 4
                or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in cells(table[1]))
                or any(
                    len(cells(row)) != 4 or any(not cell for cell in cells(row))
                    for row in table[2:]
                )
            ):
                raise ValueError(
                    "Symptoms table needs four central columns, a Markdown delimiter row and populated body rows"
                )
            suffix = "" if language == "en" else ".ko"
            if not has_source_link(sections[0], f"troubleshooting{suffix}.md"):
                raise ValueError(
                    "Common troubleshooting must link to the matching-language blesession source"
                )
            if not has_local_link(root, relative, text, readme, safe_path) or not has_local_link(
                root, relative, text, Path("docs") / other, safe_path
            ):
                raise ValueError(
                    "Include matching README and alternate-language troubleshooting links"
                )
            issue_path = f"/{config['repository']}/issues"
            if not any(
                urlsplit(link).scheme == "https"
                and urlsplit(link).netloc == "github.com"
                and urlsplit(link).path
                in {issue_path, issue_path + "/new", issue_path + "/new/choose"}
                for link in links(sections[4])
            ):
                raise ValueError(
                    "Final section must link to the integration's existing Issues or issue template"
                )
        except (ValueError, KeyError, OSError) as err:
            errors.append(("DOC-07", relative.as_posix(), str(err)))
        try:
            readme_text = visible_markdown(safe_path(root, readme).read_text(encoding="utf-8"))
            if not has_local_link(
                root, readme, readme_text, relative, safe_path
            ) or not has_source_link(
                readme_text, f"bluetooth{'' if language == 'en' else '.ko'}.md"
            ):
                raise ValueError(
                    "README must link to matching-language local troubleshooting and blesession proxy setup"
                )
        except (ValueError, OSError) as err:
            errors.append(("DOC-07", readme.as_posix(), str(err)))
    return errors

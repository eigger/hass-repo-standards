"""Canonical README rendering, managed boundaries and body protection."""

from __future__ import annotations

import re

from .badges import END as BADGES_END
from .badges import START as BADGES_START
from .badges import install_badge, preserve_extra_badges
from .badges import render as render_badges

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


def markdown_headings(text):
    """Find real ATX headings, excluding backtick and tilde fenced examples."""
    headings = []
    fence = None
    for line in re.finditer(r"^.*$", text, re.M):
        value = line.group().rstrip("\r")
        boundary = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", value)
        if fence:
            if boundary and boundary[1][0] == fence[0] and len(boundary[1]) >= len(fence):
                if not boundary[2].strip():
                    fence = None
            continue
        if boundary:
            fence = boundary[1]
            continue
        heading = re.compile(r"^#{1,6} ([^\r\n]+)[ \t]*\r?$", re.M).match(text, line.start())
        if heading:
            headings.append(heading)
    return headings


def installation_update(text, config, language):
    """Add only the install badge, retaining the integration's installation prose."""
    start, end = markers("installation")
    content = install_badge(config)
    heading = "## Installation" if language == "en" else "## 설치"
    name = "README.md" if language == "en" else "README.ko.md"
    anchor = config.get("installation_links", {}).get(name) or config.get("installation_link")
    if anchor and not anchor.startswith("#"):
        raise ValueError("Installation links must name a local README heading anchor")
    expected = anchor[1:] if anchor else ("installation" if language == "en" else "설치")
    headings = markdown_headings(text)

    def slug(value):
        return re.sub(r"[^\w -]", "", value.lower()).replace(" ", "-")

    matches = [match for match in headings if slug(match[1].strip()) == expected]
    if len(matches) > 1:
        raise ValueError("Installation anchor is ambiguous; designate one installation heading")
    if anchor and not matches:
        raise ValueError("Configured installation anchor does not match a README heading")
    section = matches[0] if matches else None
    if start in text or end in text:
        previous = block(text, "installation")
        header_end = text.index(markers("header")[1]) + len(markers("header")[1])
        support_start = text.index(markers("support")[0])
        if not header_end <= text.index(start) < text.index(end) < support_start:
            raise ValueError("Installation badge must be in the README body before support")
        if section:
            following = next(
                (h.start() for h in headings if h.start() > section.start()), support_start
            )
            if not section.end() <= text.index(start) < text.index(end) < following:
                raise ValueError(
                    "Installation badge must be under the configured installation heading"
                )
        # An installation badge block never owns user prose or instructions.
        if previous.strip() and not re.fullmatch(
            r"\[!\[[^]\n]+\]\(https://my\.home-assistant\.io/badges/hacs_repository\.svg\)\]\(https://my\.home-assistant\.io/redirect/hacs_repository/\?[^)\n]+\)",
            previous.strip(),
        ):
            raise ValueError("Installation block contains non-badge content; preserve it manually")
        return replace(text, "installation", content)
    managed = f"{start}\n{content}\n{end}"
    if section:
        return text[: section.end()] + "\n\n" + managed + text[section.end() :]
    if any(re.match(r"(?:installation|설치)\b", h[1], re.I) for h in headings):
        raise ValueError("Set installation_links to the existing installation heading anchor")
    support, _ = markers("support")
    index = text.index(support)
    return text[:index] + f"{heading}\n\n{managed}\n\n" + text[index:]


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
    return installation_update(original, config, language)


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

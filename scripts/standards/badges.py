"""Canonical offline badge renderer and preservation rules."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urlencode

from .installation import status as hacs_status

START = "<!-- hass-standards:badges:start -->"
END = "<!-- hass-standards:badges:end -->"


def git(repo: Path, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def render(repo: Path, config: dict, readme: Path | None = None):
    repository = config.get("repository")
    if not repository:
        origin = git(repo, "remote", "get-url", "origin")
        match = re.fullmatch(
            r"(?:https://github.com/|git@github.com:)([^/]+/[^/]+?)(?:\.git)?", origin
        )
        if not match:
            raise ValueError("Set repository explicitly or use a GitHub origin")
        repository = match[1]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    branch = config.get("default_branch") or git(
        repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"
    ).removeprefix("origin/")
    if not branch:
        raise ValueError("Cannot infer default_branch; set it explicitly")
    manifests = list((repo / "custom_components").glob("*/manifest.json"))
    if len(manifests) != 1:
        raise ValueError("Exactly one integration manifest is required")
    domain = json.loads(manifests[0].read_text(encoding="utf-8"))["domain"]
    hacs = json.loads((repo / "hacs.json").read_text(encoding="utf-8"))
    base = f"https://github.com/{repository}"
    # Repository-file links are relative to the README that receives the block.
    prefix = os.path.relpath(repo, readme.parent).replace(os.sep, "/") if readme else "."
    prefix = "" if prefix == "." else prefix + "/"
    links = config.get("installation_links", {})
    install = links.get(readme.relative_to(repo).as_posix()) if readme else None
    badges = []

    def badge(label, url, link):
        badges.append(f"[![{label}]({url})]({link})")

    status = hacs_status(config)
    if config.get("release", False):
        badge(
            "Release",
            f"https://img.shields.io/github/v/release/{repository}?style=flat",
            base + "/releases",
        )
    badge(
        "HACS " + status.title(),
        f"https://img.shields.io/badge/HACS-{status.title()}-41BDF5?style=flat",
        install or config.get("installation_link", "#installation"),
    )
    if hacs.get("homeassistant"):
        text = quote("≥ " + hacs["homeassistant"], safe="")
        badge(
            "Home Assistant minimum",
            f"https://img.shields.io/badge/HA-{text}-41BDF5?style=flat",
            prefix + "hacs.json",
        )
    for label, key, default in [
        ("Tests", "tests_workflow", "tests.yml"),
        ("Validate", "validate_workflow", "validate.yml"),
    ]:
        name = config.get(key, default)
        if name and (repo / ".github/workflows" / name).is_file():
            query = urlencode({"branch": branch, "style": "flat", "label": label})
            badge(
                label,
                f"https://img.shields.io/github/actions/workflow/status/{repository}/{quote(name, safe='')}?{query}",
                base + "/actions/workflows/" + quote(name, safe=""),
            )
    if (repo / "LICENSE").is_file():
        badge(
            "License",
            f"https://img.shields.io/github/license/{repository}?style=flat",
            prefix + "LICENSE",
        )
    # Every HA integration gets Usage before its domain appears in Analytics.
    # Legacy analytics=False/evidence settings do not suppress the badge.
    query = urlencode(
        {
            "style": "flat",
            "color": "41BDF5",
            "label": "Usage",
            "query": f"$.{domain}.total",
            "url": "https://analytics.home-assistant.io/custom_integrations.json",
        }
    )
    badge(
        "Analytics reporting installs",
        "https://img.shields.io/badge/dynamic/json?" + query,
        "https://analytics.home-assistant.io/",
    )
    return "\n".join(badges)


def preserve_extra_badges(text: str, rendered: str):
    """Keep unique Markdown badges after the centrally generated badge list."""
    replace_block(text, rendered)  # Validate pair count/order before extracting.
    existing = text.split(START)[1].split(END)[0]
    known = {
        "Release",
        "HACS Custom",
        "HACS Default",
        "Home Assistant minimum",
        "Tests",
        "Validate",
        "License",
        "Analytics reporting installs",
    }
    extras = []
    for value in existing.splitlines():
        match = re.fullmatch(r"\[!\[([^]]+)\]\(.+\)\]\(.+\)", value)
        if match and match[1] not in known:
            extras.append(value)
        elif value.strip() and not match:
            raise ValueError(
                "Badge block contains unrecognized non-badge content; migrate manually"
            )
    return "\n".join([rendered, *extras])


def replace_block(text: str, block: str):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError("Exactly one ordered badge marker pair must exist")
    before, rest = text.split(START)
    _, after = rest.split(END)
    return before + START + "\n" + block + "\n" + END + after

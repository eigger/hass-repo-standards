"""Check or write only an explicitly marked README badge block; offline."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urlencode

START = "<!-- hass-standards:badges:start -->"
END = "<!-- hass-standards:badges:end -->"


def git(repo: Path, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def render(repo: Path, config: dict):
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
    badges = []

    def badge(label, url, link):
        badges.append(f"[![{label}]({url})]({link})")

    status = config.get("hacs", "custom")
    if status not in {"custom", "default"}:
        raise ValueError("hacs must be custom or default")
    if status == "default" and not config.get("hacs_default_evidence"):
        raise ValueError("Default needs hacs_default_evidence URL/date")
    badge(
        "HACS " + status.title(),
        f"https://img.shields.io/badge/HACS-{status.title()}-41BDF5?style=flat-square",
        config.get("installation_link", "#installation"),
    )
    if config.get("release", False):
        badge(
            "Release",
            f"https://img.shields.io/github/v/release/{repository}?style=flat-square",
            base + "/releases",
        )
    if hacs.get("homeassistant"):
        text = quote("≥ " + hacs["homeassistant"], safe="")
        badge(
            "Home Assistant minimum",
            f"https://img.shields.io/badge/HA-{text}-41BDF5?style=flat-square",
            "hacs.json",
        )
    for label, key, default in [
        ("Tests", "tests_workflow", "tests.yml"),
        ("Validate", "validate_workflow", "validate.yml"),
    ]:
        name = config.get(key, default)
        if name and (repo / ".github/workflows" / name).is_file():
            query = urlencode({"branch": branch, "style": "flat-square", "label": label})
            badge(
                label,
                f"https://img.shields.io/github/actions/workflow/status/{repository}/{quote(name, safe='')}?{query}",
                base + "/actions/workflows/" + quote(name, safe=""),
            )
    if (repo / "LICENSE").is_file():
        badge(
            "License",
            f"https://img.shields.io/github/license/{repository}?style=flat-square",
            "LICENSE",
        )
    if config.get("analytics", False):
        if not config.get("analytics_evidence"):
            raise ValueError("analytics needs analytics_evidence URL/date")
        query = urlencode(
            {
                "style": "flat-square",
                "color": "41BDF5",
                "label": "Analytics",
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


def replace_block(text: str, block: str):
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ValueError("Exactly one ordered badge marker pair must exist")
    before, rest = text.split(START)
    _, after = rest.split(END)
    return before + START + "\n" + block + "\n" + END + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_path", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.repository_path.resolve()
    config_file = root / ".hass-standards.json"
    config = json.loads(config_file.read_text(encoding="utf-8")) if config_file.exists() else {}
    block = render(root, config)
    # Preflight every language before mutating any file.
    updates = []
    for name in config.get("readmes", ["README.md"]):
        path = (root / name).resolve()
        if not path.is_relative_to(root) or path.suffix.lower() != ".md":
            raise ValueError("README paths must be Markdown files inside the repository")
        original = path.read_text(encoding="utf-8")
        updated = replace_block(original, block)
        if original != updated:
            updates.append((path, updated))
    for path, updated in updates:
        print(("WRITE " if args.write else "DIFF ") + str(path))
        if args.write:
            path.write_text(updated, encoding="utf-8")
    raise SystemExit(1 if args.check and updates else 0)


if __name__ == "__main__":
    main()

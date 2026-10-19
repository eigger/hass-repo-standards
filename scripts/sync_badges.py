"""Check or write only an explicitly marked README badge block; offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from standards import badges as _badges
except ModuleNotFoundError:  # Compatibility with importlib file-based callers.
    from scripts.standards import badges as _badges

START = _badges.START
END = _badges.END


def git(repo: Path, *args):
    return _badges.git(repo, *args)


def render(repo: Path, config: dict, readme: Path | None = None):
    return _badges.render(repo, config, readme)


def preserve_extra_badges(text: str, rendered: str):
    return _badges.preserve_extra_badges(text, rendered)


def replace_block(text: str, block: str):
    return _badges.replace_block(text, block)


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
    render(root, config)  # Validate configuration even when no README is listed.
    # Preflight every language before mutating any file.
    updates = []
    for name in config.get("readmes", ["README.md"]):
        path = (root / name).resolve()
        if not path.is_relative_to(root) or path.suffix.lower() != ".md":
            raise ValueError("README paths must be Markdown files inside the repository")
        original = path.read_bytes().decode("utf-8")
        updated = replace_block(
            original, preserve_extra_badges(original, render(root, config, path))
        )
        if original != updated:
            updates.append((path, updated))
    for path, updated in updates:
        print(("WRITE " if args.write else "DIFF ") + str(path))
        if args.write:
            path.write_bytes(updated.encode("utf-8"))
    raise SystemExit(1 if args.check and updates else 0)


if __name__ == "__main__":
    main()

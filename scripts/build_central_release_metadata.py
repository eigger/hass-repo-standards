"""Create untracked evidence for one central standards release candidate."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def build(root, version):
    if re.fullmatch(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version) is None:
        raise ValueError("version must be an exact vX.Y.Z SemVer tag")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("central release candidate checkout must be clean")
    internal_refs = sorted(
        set(
            re.findall(
                r"eigger/hass-repo-standards/(?:actions|\.github/workflows)/[^@\s]+@([0-9a-f]{40})",
                "\n".join(
                    path.read_text(encoding="utf-8")
                    for directory in (root / ".github", root / "actions")
                    for path in directory.rglob("*")
                    if path.is_file()
                ),
            )
        )
    )
    return {
        "schema_version": 1,
        "release": version,
        "candidate_commit": git(root, "rev-parse", "HEAD"),
        "contract": "exact-release-resolved-sha-v1",
        "distribution_scope": [
            "rules",
            "templates",
            "schemas",
            "scripts",
            "actions",
            "reusable-workflows",
            "skills",
        ],
        "internal_action_resolved_shas": internal_refs,
        "notes": "Generated at release time; this untracked asset avoids a self-referential commit SHA.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--ci-run-url", default="")
    args = parser.parse_args(argv)
    result = build(args.root.resolve(), args.version)
    if args.ci_run_url:
        result["release_gate_ci_run"] = args.ci_run_url
    args.output.write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

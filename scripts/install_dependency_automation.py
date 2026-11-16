"""Plan/install the opt-in manifest merger with an immutable central release."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from standards import manifest_merge, update

CALLER = ".github/workflows/merge_dependencies.yml"


def changes(root, release, templates):
    root = Path(root).resolve()
    result = update.bootstrap_changes(
        root,
        release,
        (templates / update.CALLER).read_text(),
        (templates / update.AUTOMERGE_CALLER).read_text(),
    )
    updater = update.yaml_document((root / ".github/workflows/update_dependencies.yml").read_text())
    jobs = [
        j
        for j in updater.get("jobs", {}).values()
        if "/dependency-update.yml@" in j.get("uses", "")
    ]
    if len(jobs) != 1 or updater.get("name") != "Update dependencies":
        raise ValueError("Expected one standard Update dependencies caller")
    inputs = jobs[0]["with"]
    domain = inputs["domain"]
    packages = json.loads(inputs["packages"])
    if (
        not isinstance(packages, list)
        or not packages
        or any(not isinstance(p, str) for p in packages)
        or len(set(packages)) != len(packages)
        or set(packages) - manifest_merge.ALLOWED
    ):
        raise ValueError("Only blesession/imagespec updater callers can opt in")
    if not isinstance(domain, str) or not re.fullmatch(r"[a-z0-9_]+", domain):
        raise ValueError("Invalid domain")
    template = (templates / CALLER).read_text()
    desired = template.replace("@main", "@" + release["tag"]).replace(
        "domain: example", "domain: " + domain
    )
    desired = desired.replace('["imagespec", "blesession"]', json.dumps(packages))
    destination = root / CALLER
    if destination.is_symlink() or not destination.resolve().is_relative_to(root):
        raise ValueError("Unsafe automation caller path")
    if destination.exists() and update.normalized_workflow(
        destination.read_text()
    ) != update.normalized_workflow(desired):
        raise ValueError("Existing custom merger caller requires explicit review")
    result[CALLER] = desired
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--release", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    release = update.attest_release(args.release)
    planned = changes(
        args.root, release, Path(__file__).resolve().parents[1] / "templates/integration"
    )
    print(json.dumps({"standards": release, "files": sorted(planned)}, indent=2))
    if args.write:
        for relative, text in planned.items():
            target = args.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

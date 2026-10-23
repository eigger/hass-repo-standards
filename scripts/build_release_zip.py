"""Build a HACS release asset from a clean, tracked integration checkout."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def build(root, output, tag=None):
    root = Path(root).resolve()
    output = Path(output).resolve()
    if git(root, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("Release checkout must have no tracked modifications")
    manifests = list((root / "custom_components").glob("*/manifest.json"))
    if len(manifests) != 1:
        raise ValueError("Exactly one custom_components integration is required")
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    domain = manifest.get("domain", "")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", domain) or manifests[0].parent.name != domain:
        raise ValueError("Manifest domain must match the integration directory")
    hacs = json.loads((root / "hacs.json").read_text(encoding="utf-8"))
    filename = hacs.get("filename", "")
    if hacs.get("zip_release") is not True or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]*\.zip", filename
    ):
        raise ValueError("hacs.json needs zip_release: true and a safe ZIP filename")
    if hacs.get("content_in_root"):
        raise ValueError("This release builder requires custom_components/<domain>")
    if tag is not None:
        if not tag or tag.startswith("-") or any(ord(char) < 32 for char in tag):
            raise ValueError("Unsafe release tag")
        version = tag[1:] if tag.startswith("v") else tag
        if version != manifest.get("version"):
            raise ValueError("Release tag and manifest.version must match; source is not rewritten")
        if git(root, "rev-parse", "refs/tags/" + tag + "^{commit}") != git(
            root, "rev-parse", "HEAD"
        ):
            raise ValueError("Checkout HEAD must be the release tag commit")
    prefix = f"custom_components/{domain}/"
    tracked = git(root, "ls-files", "-z", "--", prefix).decode("utf-8").split("\0")
    files = []
    for relative in sorted(filter(None, tracked)):
        member = PurePosixPath(relative.removeprefix(prefix))
        if member.is_absolute() or ".." in member.parts or "\\" in relative:
            raise ValueError("Unsafe archive member")
        if any(part in {"__pycache__", ".pytest_cache", ".git"} for part in member.parts) or (
            member.suffix in {".pyc", ".pyo"}
        ):
            continue
        path = root / relative
        if any(parent.is_symlink() for parent in (path, *path.parents)) or not path.is_file():
            raise ValueError("Release files must be regular files, without symlinks")
        files.append((path, member.as_posix()))
    if not {"manifest.json", "__init__.py"} <= {name for _, name in files}:
        raise ValueError("Tracked manifest.json and __init__.py are required at ZIP root")
    archive = output / filename
    if archive.is_relative_to(root):
        raise ValueError("Archive output must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    # Never replace an existing asset, including during local retries.
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path, name in files:
            bundle.write(path, name)
    with zipfile.ZipFile(archive) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("ZIP integrity verification failed")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tag")
    args = parser.parse_args()
    archive = build(args.repository, args.output, args.tag)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write(f"archive={archive}\n")
    print(archive)


if __name__ == "__main__":
    main()

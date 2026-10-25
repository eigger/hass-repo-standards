"""Admin-run fail-closed gate before publishing a prepared central release draft."""

from __future__ import annotations

import argparse
import json
import re
import subprocess

SHA = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


def call(args, runner=subprocess.run):
    return runner(args, check=True, capture_output=True, text=True).stdout


def check(repository, version, candidate_sha, *, runner=subprocess.run):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    if VERSION.fullmatch(version) is None or SHA.fullmatch(candidate_sha) is None:
        raise ValueError("version and candidate SHA must be exact")
    immutable = json.loads(call(["gh", "api", f"repos/{repository}/immutable-releases"], runner))
    if immutable.get("enabled") is not True:
        raise ValueError("immutable releases are not enabled")
    release = json.loads(call(["gh", "api", f"repos/{repository}/releases/tags/{version}"], runner))
    if release.get("tag_name") != version or release.get("draft") is not True:
        raise ValueError("only the expected prepared draft may be published")
    if release.get("prerelease") is not False or not any(
        asset.get("name") == "release-metadata.json" for asset in release.get("assets", [])
    ):
        raise ValueError("draft is not a complete stable release candidate")
    tags = call(
        [
            "git",
            "ls-remote",
            "--tags",
            f"https://github.com/{repository}.git",
            f"refs/tags/{version}*",
        ],
        runner,
    )
    found = {
        name: sha
        for sha, name in (line.split("\t", 1) for line in tags.splitlines() if "\t" in line)
    }
    actual = found.get(f"refs/tags/{version}^{{}}", found.get(f"refs/tags/{version}"))
    if actual != candidate_sha:
        raise ValueError("prepared draft tag does not peel to the reviewed candidate SHA")
    return {"repository": repository, "version": version, "candidate_sha": candidate_sha}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--candidate-sha", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(check(args.repository, args.version, args.candidate_sha), sort_keys=True))


if __name__ == "__main__":
    main()

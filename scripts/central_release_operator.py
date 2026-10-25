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


def release_endpoint(repository, version, runner):
    """Find a draft by GraphQL-backed CLI lookup, then fetch its REST record.

    GitHub's REST ``/releases/tags/{tag}`` endpoint does not reliably expose
    drafts. ``gh release view`` resolves the release through GraphQL first,
    then gives us the immutable REST URL for that exact draft.
    """
    viewed = json.loads(
        call(
            ["gh", "release", "view", version, "--repo", repository, "--json", "apiUrl"],
            runner,
        )
    )
    api_url = viewed.get("apiUrl") if isinstance(viewed, dict) else None
    prefix = f"https://api.github.com/repos/{repository}/releases/"
    if not isinstance(api_url, str) or re.fullmatch(re.escape(prefix) + r"[0-9]+", api_url) is None:
        raise ValueError("draft lookup did not return this repository's release API URL")
    return api_url.removeprefix("https://api.github.com/")


def metadata_asset(repository, release, version, candidate_sha, runner):
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("draft is not a complete stable release candidate")
    matches = [
        asset
        for asset in assets
        if isinstance(asset, dict) and asset.get("name") == "release-metadata.json"
    ]
    if len(matches) != 1 or not isinstance(matches[0].get("id"), int):
        raise ValueError("draft is not a complete stable release candidate")
    metadata = json.loads(
        call(
            [
                "gh",
                "api",
                f"repos/{repository}/releases/assets/{matches[0]['id']}",
                "-H",
                "Accept: application/octet-stream",
            ],
            runner,
        )
    )
    expected = {
        "release": version,
        "candidate_commit": candidate_sha,
        "contract": "exact-release-resolved-sha-v1",
    }
    if not isinstance(metadata, dict) or any(
        metadata.get(key) != value for key, value in expected.items()
    ):
        raise ValueError("draft release metadata does not bind this version and candidate SHA")


def checked_tag(repository, version, candidate_sha, runner):
    """Accept no draft tag yet, or only a tag that resolves to this candidate."""
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
    if not tags:
        return
    found = {}
    for line in tags.splitlines():
        if "\t" not in line:
            raise ValueError("unexpected git ls-remote release tag response")
        sha, name = line.split("\t", 1)
        if SHA.fullmatch(sha) is None or name not in {
            f"refs/tags/{version}",
            f"refs/tags/{version}^{{}}",
        }:
            raise ValueError("unexpected git ls-remote release tag response")
        found[name] = sha
    actual = found.get(f"refs/tags/{version}^{{}}", found.get(f"refs/tags/{version}"))
    if actual != candidate_sha:
        raise ValueError("prepared draft tag does not peel to the reviewed candidate SHA")


def check(repository, version, candidate_sha, *, runner=subprocess.run):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    if VERSION.fullmatch(version) is None or SHA.fullmatch(candidate_sha) is None:
        raise ValueError("version and candidate SHA must be exact")
    immutable = json.loads(call(["gh", "api", f"repos/{repository}/immutable-releases"], runner))
    if immutable.get("enabled") is not True:
        raise ValueError("immutable releases are not enabled")
    endpoint = release_endpoint(repository, version, runner)
    release = json.loads(call(["gh", "api", endpoint], runner))
    if (
        not isinstance(release, dict)
        or release.get("tag_name") != version
        or release.get("draft") is not True
        or release.get("prerelease") is not False
        or release.get("target_commitish") != candidate_sha
    ):
        raise ValueError("only the expected prepared draft may be published")
    metadata_asset(repository, release, version, candidate_sha, runner)
    checked_tag(repository, version, candidate_sha, runner)
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

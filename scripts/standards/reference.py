"""One release/SHA descriptor used by planning, rendering and offline checks.

The descriptor intentionally records both a human review unit and the immutable
commit it resolved to.  A tag is never resolved during a local plan/apply run:
that would make an already reviewed plan depend on the network or a moved tag.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{40}")
TAG = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
UPDATE_PROVIDER = {"provider": "dependabot", "workflow": "update_standards.yml"}


def metadata_input(config, supplied=None):
    """Allow omitted payload-tool SHA only for explicitly adopted release consumers."""
    if supplied is not None:
        return supplied
    if (config or {}).get("standards_update") != UPDATE_PROVIDER:
        return None
    try:
        value = validate(config.get("standards"))
    except ValueError:
        return None
    return value["resolved_sha"] if value["kind"] == "release" else None


def descriptor(ref, resolved_sha=None):
    """Normalize legacy SHA input or an exact release tag plus its resolved SHA."""
    if resolved_sha is None and isinstance(ref, str) and SHA.fullmatch(ref):
        return {"kind": "sha", "resolved_sha": ref}
    if not isinstance(ref, str) or TAG.fullmatch(ref) is None:
        raise ValueError("standards-ref must be a reviewed full SHA or exact vX.Y.Z release tag")
    if not isinstance(resolved_sha, str) or SHA.fullmatch(resolved_sha) is None:
        raise ValueError("release resolved SHA must be a full lowercase commit SHA")
    return {"kind": "release", "tag": ref, "resolved_sha": resolved_sha}


def validate(value):
    if not isinstance(value, dict) or value.get("kind") not in {"sha", "release"}:
        raise ValueError("invalid standards reference descriptor")
    expected = {"kind", "resolved_sha"}
    if value["kind"] == "release":
        expected.add("tag")
    if set(value) != expected or not isinstance(value.get("resolved_sha"), str):
        raise ValueError("invalid standards reference descriptor fields")
    return descriptor(
        value.get("tag", value["resolved_sha"]),
        value["resolved_sha"] if value["kind"] == "release" else None,
    )


def caller_ref(value):
    """The Actions reference: immutable release tag when recorded, SHA otherwise."""
    return validate(value).get("tag", value["resolved_sha"])


def resolved_sha(value):
    return validate(value)["resolved_sha"]


def verify_remote(repository, value, *, runner=subprocess.run):
    """Network attestation for a published immutable GitHub release.

    This is deliberately explicit CLI work. Offline checks only validate the
    recorded descriptor and never claim GitHub has published a release.
    """
    value = validate(value)
    if value["kind"] != "release":
        raise ValueError("remote release verification requires an exact release descriptor")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    release = runner(
        ["gh", "api", f"repos/{repository}/releases/tags/{value['tag']}"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(release.stdout)
    if (
        not isinstance(data, dict)
        or data.get("tag_name") != value["tag"]
        or data.get("draft") is not False
        or data.get("prerelease") is not False
    ):
        raise ValueError("release must be the published non-prerelease exact tag")
    if data.get("immutable") is not True:
        raise ValueError("release is not immutable")
    remote = f"https://github.com/{repository}.git"
    tags = runner(
        ["git", "ls-remote", "--tags", remote, f"refs/tags/{value['tag']}*"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    found = {}
    for line in tags:
        if "\t" not in line:
            raise ValueError("unexpected git ls-remote release tag response")
        sha, name = line.split("\t", 1)
        if SHA.fullmatch(sha) is None:
            raise ValueError("unexpected git ls-remote commit response")
        found[name] = sha
    tag = f"refs/tags/{value['tag']}"
    actual = found.get(tag + "^{}", found.get(tag))
    if actual != value["resolved_sha"]:
        raise ValueError("release tag peeled commit does not match the recorded resolved SHA")
    return {"repository": repository, **value, "verified": "remote"}


def write_verification(path, result):
    """Write external evidence only after the network attestation succeeds."""
    target = Path(path)
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def read_verification(path, repository, value):
    """Accept only a matching successful remote attestation as release-plan input."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = {"repository", "kind", "tag", "resolved_sha", "verified"}
    if not isinstance(data, dict) or set(data) != expected or data.get("repository") != repository:
        raise ValueError("release verification evidence is malformed or for another repository")
    if data.get("verified") != "remote" or validate(
        {key: data[key] for key in expected - {"repository", "verified"}}
    ) != validate(value):
        raise ValueError("release verification evidence does not match the requested descriptor")
    return data

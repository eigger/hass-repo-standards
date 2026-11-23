"""Merge manifest-only bot proposals after fresh, exact-head validator runs.

PR contents are read as Git data and never imported or executed here. The only
workflow code dispatched is byte-for-byte the trusted default branch's code.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import uuid
from urllib.parse import quote

from packaging.requirements import Requirement
from packaging.version import Version

from . import update

BRANCH = "bot/manifest-dependencies"
BOT = "github-actions[bot]"
ALLOWED = {"blesession", "imagespec"}


def validate_manifest(before, after, packages):
    """Allow stable same-major increases, preserving every other manifest value."""
    if not packages or set(packages) - ALLOWED or len(set(packages)) != len(packages):
        raise ValueError("Auto-merge packages must be unique blesession/imagespec names")
    old = before.get("requirements", [])
    new = after.get("requirements", [])
    if not isinstance(old, list) or not isinstance(new, list) or len(old) != len(new):
        raise ValueError("Requirements cannot be added or removed")
    if {k: v for k, v in before.items() if k != "requirements"} != {
        k: v for k, v in after.items() if k != "requirements"
    }:
        raise ValueError("Only requirement versions may change")
    changes = []
    seen = set()
    for a, b in zip(old, new):
        req = Requirement(a)
        name = req.name.lower().replace("_", "-").replace(".", "-")
        if name in seen:
            raise ValueError("Duplicate manifest requirement")
        seen.add(name)
        if a == b:
            continue
        specs = list(req.specifier)
        nxt = Requirement(b)
        following = list(nxt.specifier)
        if (
            name not in packages
            or req.url
            or nxt.url
            or len(specs) != 1
            or len(following) != 1
            or specs[0].operator not in {">=", "=="}
            or following[0].operator != specs[0].operator
        ):
            raise ValueError("Only selected simple requirement floors may change")
        previous, current = Version(specs[0].version), Version(following[0].version)
        if (
            current <= previous
            or current.major != previous.major
            or current.is_prerelease
            or current.is_devrelease
            or current.local is not None
        ):
            raise ValueError("Only stable same-major upgrades may auto-merge")
        expected, count = re.subn(
            re.escape(specs[0].operator) + r"\s*" + re.escape(specs[0].version),
            specs[0].operator + str(current),
            a,
            count=1,
        )
        if count != 1 or b != expected:
            raise ValueError("Requirement spelling, extras, operator and marker must be preserved")
        changes.append(name)
    if not changes:
        raise ValueError("No eligible dependency version changes")
    return changes


def proposal(repository, number, domain, packages, *, api=update.gh, listing=update.pages):
    """Bind author, branch, base, full diff, regular file modes and data."""
    if not re.fullmatch(r"[a-z0-9_]+", domain):
        raise ValueError("Invalid integration domain")
    meta = api(f"repos/{repository}")
    pr = api(f"repos/{repository}/pulls/{number}")
    if (
        pr["state"] != "open"
        or pr.get("draft")
        or pr["user"]["login"] != BOT
        or pr["head"]["repo"]["full_name"] != repository
        or pr["base"]["repo"]["full_name"] != repository
        or pr["head"]["ref"] != BRANCH
        or pr["base"]["ref"] != meta["default_branch"]
    ):
        raise ValueError("Expected an open same-repository manifest updater bot PR")
    base = api(f"repos/{repository}/git/ref/heads/{quote(meta['default_branch'], safe='')}")[
        "object"
    ]["sha"]
    head = pr["head"]["sha"]
    comparison = api(f"repos/{repository}/compare/{base}...{head}")
    if comparison["merge_base_commit"]["sha"] != base or comparison["ahead_by"] != 1:
        raise ValueError(
            "Bot proposal must be one commit on the current default branch; rerun updater"
        )
    path = f"custom_components/{domain}/manifest.json"
    files = listing(f"repos/{repository}/pulls/{number}/files?per_page=100")
    if len(files) != 1 or files[0]["filename"] != path or files[0]["status"] != "modified":
        raise ValueError("Bot PR must modify only its existing manifest")
    trees = [update.tree_files(repository, sha, api) for sha in (base, head)]
    for tree in trees:
        if tree.get(path, (None, None, None))[1:] != ("100644", "blob"):
            raise ValueError("Manifest must be a regular tracked file")
    unchanged = set(trees[0]) | set(trees[1])
    if any(trees[0].get(p) != trees[1].get(p) for p in unchanged if p != path):
        raise ValueError("Immutable Git trees change content outside the manifest")
    before, after = [json.loads(update.blob(repository, tree[path][0], api)) for tree in trees]
    changed = validate_manifest(before, after, packages)
    workflows = {
        p: update.blob(repository, entry[0], api)
        for p, entry in trees[0].items()
        if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))
    }
    validators = update.dispatchable_workflows(workflows)
    if not {"standards.yml", "tests.yml", "validate.yml"}.issubset(validators):
        raise ValueError("Standards, Tests and Validate must all be dispatchable")
    return {"head": head, "base": base, "validators": validators, "packages": changed}


def delete_ref(repository, branch, head, *, runner=subprocess.run):
    """Compare-and-delete: never remove a branch advanced since validation."""
    runner(
        [
            "git",
            "-c",
            "credential.helper=",
            "-c",
            "credential.helper=!gh auth git-credential",
            "push",
            f"--force-with-lease=refs/heads/{branch}:{head}",
            f"https://github.com/{repository}.git",
            f":refs/heads/{branch}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def cleanup(repository, *, api=update.gh, listing=update.pages, delete=delete_ref):
    """Delete only an unchanged, merged bot head without an open PR."""
    refs = listing(f"repos/{repository}/git/matching-refs/heads/{BRANCH}")
    exact = [r for r in refs if r["ref"] == "refs/heads/" + BRANCH]
    if not exact:
        return False
    head = exact[0]["object"]["sha"]
    owner = repository.split("/")[0]
    prs = listing(f"repos/{repository}/pulls?state=all&head={owner}:{BRANCH}&per_page=100")
    if any(p["state"] == "open" for p in prs):
        return False
    if not any(
        p.get("merged_at")
        and p["user"]["login"] == BOT
        and p["head"]["repo"]["full_name"] == repository
        and p["head"]["sha"] == head
        for p in prs
    ):
        return False
    current = api(f"repos/{repository}/git/ref/heads/{quote(BRANCH, safe='')}")
    if current["object"]["sha"] != head:
        return False
    delete(repository, BRANCH, head)
    return True


def approval_pending(repository, number, bound, *, api):
    """Identify current PR validator runs awaiting GitHub's execution approval."""
    head = bound["head"]
    pending = []
    for workflow in bound["validators"]:
        endpoint = (
            f"repos/{repository}/actions/workflows/{workflow}/runs?event=pull_request"
            f"&branch={quote(BRANCH, safe='')}&head_sha={head}&per_page=100"
        )
        runs = [
            run
            for run in api(endpoint)["workflow_runs"]
            if run["event"] == "pull_request"
            and run["head_branch"] == BRANCH
            and run["head_sha"] == head
            and (run.get("head_repository") or {}).get("full_name") == repository
            and (
                not run["pull_requests"]
                or any(pr["number"] == number for pr in run["pull_requests"])
            )
        ]
        if not runs:
            continue
        # The list shows the latest attempt for each run ID. Superseded runs
        # must not keep deferring a PR whose workflows have since started.
        latest = max(runs, key=lambda run: run["id"])
        if latest["status"] != "completed":
            continue
        if latest["conclusion"] == "action_required":
            pending.append({"workflow": workflow, "url": latest["html_url"]})
        elif latest["conclusion"] not in {"success", "neutral", "skipped"}:
            # Preserve the normal validation and merge checks when a PR
            # workflow already has an unsuccessful result.
            return None
    if pending:
        return {"pr": number, "head": head, "status": "approval_pending", "runs": pending}
    return None


def merge_state(repository, number, bound, *, api):
    owner, name = repository.split("/")
    state = api(
        "graphql",
        method="POST",
        payload={
            "query": "query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){state headRefOid baseRefOid mergeStateStatus}}}",
            "variables": {"owner": owner, "name": name, "number": number},
        },
    )["data"]["repository"]["pullRequest"]
    if (
        state["state"] != "OPEN"
        or state["headRefOid"] != bound["head"]
        or state["baseRefOid"] != bound["base"]
    ):
        raise ValueError("PR identity or base changed while waiting for required checks")
    return state["mergeStateStatus"]


def merge(
    repository,
    number,
    domain,
    packages,
    *,
    api=update.gh,
    listing=update.pages,
    sleep=time.sleep,
    clock=time.monotonic,
    timeout=900,
    delete=delete_ref,
    validation_ref=None,
):
    bound = proposal(repository, number, domain, packages, api=api, listing=listing)
    pending = approval_pending(repository, number, bound, api=api)
    if pending is not None and merge_state(repository, number, bound, api=api) != "CLEAN":
        return pending
    head = bound["head"]
    # A unique ref isolates execution from updates to the reusable bot branch.
    validation_ref = validation_ref or "hass-dependency-validation/" + uuid.uuid4().hex
    api(
        f"repos/{repository}/git/refs",
        method="POST",
        payload={"ref": "refs/heads/" + validation_ref, "sha": head},
    )
    try:
        return validate_and_merge(
            repository,
            number,
            domain,
            packages,
            bound,
            validation_ref,
            api=api,
            listing=listing,
            sleep=sleep,
            clock=clock,
            timeout=timeout,
            delete=delete,
        )
    finally:
        delete(repository, validation_ref, head)


def validate_and_merge(
    repository,
    number,
    domain,
    packages,
    bound,
    validation_ref,
    *,
    api,
    listing,
    sleep,
    clock,
    timeout,
    delete,
):
    head = bound["head"]
    baselines = {}
    for workflow in bound["validators"]:
        endpoint = f"repos/{repository}/actions/workflows/{workflow}/runs?event=workflow_dispatch&head_sha={head}&per_page=100"
        runs = api(endpoint)["workflow_runs"]
        baselines[workflow] = (endpoint, max((r["id"] for r in runs), default=0))
        api(
            f"repos/{repository}/actions/workflows/{workflow}/dispatches",
            method="POST",
            payload={"ref": validation_ref},
        )
    deadline = clock() + timeout
    while True:
        complete = []
        for workflow, (endpoint, baseline) in baselines.items():
            runs = [
                r
                for r in api(endpoint)["workflow_runs"]
                if r["id"] > baseline
                and r["head_sha"] == head
                and r["head_branch"] == validation_ref
                and r["event"] == "workflow_dispatch"
            ]
            if not runs:
                continue
            run = max(runs, key=lambda r: r["id"])
            if run["status"] == "completed":
                if run["conclusion"] != "success":
                    raise ValueError(f"Validation failed: {workflow} {run.get('html_url')}")
                complete.append(workflow)
        if len(complete) == len(baselines):
            break
        if clock() >= deadline:
            raise TimeoutError("Exact-head validation did not complete; leave PR open")
        sleep(15)
    # Required PR checks can be attached to GitHub's test merge commit,
    # independently of successful dispatches on the exact source head.
    while True:
        if merge_state(repository, number, bound, api=api) == "CLEAN":
            # REST atomically binds only the head, not the base. Existing
            # strict up-to-date branch rules remain authoritative at merge.
            latest = proposal(repository, number, domain, packages, api=api, listing=listing)
            if latest != bound:
                raise ValueError("Proposal changed during validation; rerun updater")
            try:
                result = api(
                    f"repos/{repository}/pulls/{number}/merge",
                    method="PUT",
                    payload={"merge_method": "squash", "sha": head},
                )
            except subprocess.CalledProcessError as error:
                detail = (error.stderr or error.stdout or str(error)).strip()
                # Readiness is eventually consistent. Retry only explicit
                # merge-condition/head conflicts; never bypass auth or rules.
                if not any(code in detail for code in ("HTTP 405", "HTTP 409")):
                    raise RuntimeError("GitHub merge request failed: " + detail) from error
                print("GitHub merge conditions changed; waiting: " + detail, flush=True)
            else:
                if not result.get("merged"):
                    raise ValueError(
                        "GitHub refused squash merge; branch requirements remain authoritative"
                    )
                cleanup(repository, api=api, listing=listing, delete=delete)
                return {**bound, "pr": number, "merge": result["sha"]}
        else:
            pending = approval_pending(repository, number, bound, api=api)
            if pending is not None:
                return pending
        if clock() >= deadline:
            raise TimeoutError("Required PR merge conditions did not become ready; leave PR open")
        sleep(15)

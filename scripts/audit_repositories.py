"""Read-only inventory of every local hass* checkout and its workflow steps."""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml


class Loader(yaml.SafeLoader):
    """Preserve YAML 1.2 event key 'on'; retain all other safe constructors."""


Loader.yaml_implicit_resolvers = {
    key: [(tag, pattern) for tag, pattern in values if tag != "tag:yaml.org,2002:bool"]
    for key, values in Loader.yaml_implicit_resolvers.items()
}

for key in "tTfF":
    Loader.add_implicit_resolver(
        "tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$", re.I), [key]
    )


def git(path, *arguments):
    result = subprocess.run(["git", "-C", str(path), *arguments], text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def inventory(root: Path):
    result = []
    for repo in sorted(root.glob("hass*")):
        if not repo.is_dir() or repo.name == "hass-repo-standards":
            continue
        if not git(repo, "rev-parse", "--show-toplevel"):
            continue
        kind = "integration" if (repo / "custom_components").is_dir() else "other"
        kind = {
            "hass-imagespec-card": "frontend",
            "hassble-android": "android",
            "hassble-config": "yaml-config",
            "hassio-apps": "apps",
        }.get(repo.name, kind)
        workflows = []
        for file in sorted((repo / ".github/workflows").glob("*")):
            if file.suffix not in {".yml", ".yaml"}:
                continue
            text = file.read_text(encoding="utf-8")
            data = yaml.load(text, Loader=Loader)
            workflows.append(
                {
                    "file": file.name,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "events": data.get("on"),
                    "permissions": data.get("permissions"),
                    "concurrency": data.get("concurrency"),
                    "jobs": data.get("jobs", {}),
                }
            )
        result.append(
            {
                "directory": repo.name,
                "origin": git(repo, "remote", "get-url", "origin"),
                "head": git(repo, "rev-parse", "HEAD"),
                "dirty": bool(git(repo, "status", "--porcelain")),
                "default_branch": git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"),
                "profile": kind,
                "workflows": workflows,
            }
        )
    return result


def github_inventory(owner: str):
    """Read all matching default-branch workflows through authenticated gh CLI."""
    if not re.fullmatch(r"[A-Za-z0-9-]+", owner):
        raise ValueError("Invalid GitHub owner")

    def api(endpoint):
        result = subprocess.run(["gh", "api", endpoint], text=True, capture_output=True)
        if result.returncode:
            if "HTTP 404" in result.stderr:
                return None
            raise RuntimeError(result.stderr)
        return json.loads(result.stdout)

    raw = subprocess.check_output(
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            "1000",
            "--json",
            "name,url,defaultBranchRef,isArchived",
        ],
        text=True,
    )
    repositories = [
        r
        for r in json.loads(raw)
        if r["name"].startswith("hass") and r["name"] != "hass-repo-standards"
    ]

    def read(repository):
        branch = repository["defaultBranchRef"]["name"]
        files = (
            api(f"repos/{owner}/{repository['name']}/contents/.github/workflows?ref={branch}") or []
        )
        workflows = []
        for file in files:
            if not file["name"].endswith((".yml", ".yaml")):
                continue
            blob = api(f"repos/{owner}/{repository['name']}/git/blobs/{file['sha']}")
            content = base64.b64decode(blob["content"]).decode()
            data = yaml.load(content, Loader=Loader)
            workflows.append(
                {
                    "file": file["name"],
                    "blob_sha": file["sha"],
                    "events": data.get("on"),
                    "permissions": data.get("permissions"),
                    "concurrency": data.get("concurrency"),
                    "jobs": data.get("jobs", {}),
                }
            )
        return {**repository, "workflows": workflows}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return sorted(pool.map(read, repositories), key=lambda r: r["name"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--root", type=Path)
    source.add_argument("--github-owner")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = github_inventory(args.github_owner) if args.github_owner else inventory(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Recorded {len(data)} repositories/checkouts; {sum(len(r['workflows']) for r in data)} workflows"
    )


if __name__ == "__main__":
    main()

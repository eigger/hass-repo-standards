"""Reconcile a grouped Dependabot standards PR with the repository's built-in token."""

from __future__ import annotations

import argparse
import json
import os
import subprocess

from standards import update


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--pr", type=int, default=0)
    parser.add_argument("--manual", action="store_true")
    args = parser.parse_args()
    if not args.repository:
        raise ValueError("A consumer repository is required")
    if args.pr:
        numbers = [args.pr]
    else:
        pulls = update.pages(f"repos/{args.repository}/pulls?state=open&per_page=100")
        numbers = []
        for pr in pulls:
            if pr["user"]["login"] != "dependabot[bot]":
                continue
            files = update.pages(f"repos/{args.repository}/pulls/{pr['number']}/files?per_page=100")
            if any(update.PREFIX in (f.get("patch") or "") for f in files):
                numbers.append(pr["number"])
    results = []
    for number in numbers:
        files = update.pages(f"repos/{args.repository}/pulls/{number}/files?per_page=100")
        if not any(update.PREFIX in (f.get("patch") or "") for f in files):
            continue
        result = update.sync_pr(args.repository, number, manual=args.manual)
        if result is None:
            continue
        results.append(result)
        if result["auto_eligible"]:
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "merge",
                    str(number),
                    "--repo",
                    args.repository,
                    "--auto",
                    "--squash",
                    "--match-head-commit",
                    result["head"],
                ],
                check=True,
            )
    report = json.dumps(results, indent=2)
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("## Central standards PR reconciliation\n\n```json\n" + report + "\n```\n")


if __name__ == "__main__":
    main()

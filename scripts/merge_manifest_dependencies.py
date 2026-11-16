"""Reconcile and clean up the manifest updater's own dependency PR."""

from __future__ import annotations

import argparse
import json
import os

from standards import manifest_merge as automation
from standards import update


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--domain", required=True)
    parser.add_argument("--packages", required=True, type=json.loads)
    args = parser.parse_args()
    if not args.repository or not isinstance(args.packages, list):
        raise ValueError("Repository and package list are required")
    owner = args.repository.split("/")[0]
    prs = update.pages(
        f"repos/{args.repository}/pulls?state=open&head={owner}:{automation.BRANCH}&per_page=100"
    )
    results = []
    for pr in prs:
        results.append(automation.merge(args.repository, pr["number"], args.domain, args.packages))
    cleaned = automation.cleanup(args.repository)
    report = json.dumps({"merged": results, "cleaned": cleaned}, indent=2)
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as stream:
            stream.write("## Manifest dependency automation\n\n```json\n" + report + "\n```\n")


if __name__ == "__main__":
    main()

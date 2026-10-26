"""Read-only account-wide discovery; never silently drop an unregistered consumer."""

import argparse
import json
import os
from pathlib import Path

from standards import reference, update


def inspect(repository, tree, latest):
    def read(path):
        entry = tree[path]
        if entry[1:] != ("100644", "blob"):
            raise ValueError(f"Not a regular managed file: {path}")
        return update.blob(repository, entry[0])

    workflows = {
        p: read(p)
        for p in tree
        if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))
    }
    refs = [pair for text in workflows.values() for pair in update.central_uses(text)]
    if not refs and ".hass-standards.json" not in tree:
        return None
    config = json.loads(read(".hass-standards.json"))
    value = reference.validate(config["standards"])
    if config.get("repository") != repository or config.get("standards_update") != update.PROVIDER:
        raise ValueError("Missing updater adoption or wrong repository descriptor")
    document = read("STANDARDS.md")
    if (
        update.metadata_changes(read(".hass-standards.json"), document, value)["STANDARDS.md"]
        != document
    ):
        raise ValueError("Recorded standards document disagrees with descriptor")
    override = update.recorded_release_override(document)
    if not refs or any(
        ref != value["tag"]
        for path, ref in refs
        if not (path.endswith("actions/release-zip") and ref == override)
    ):
        raise ValueError("Central references disagree with recorded release")
    caller = update.yaml_document(workflows[update.CALLER])
    events = caller.get("on", {})
    if not all(e in events for e in ("pull_request_target", "schedule", "workflow_dispatch")):
        raise ValueError("Missing updater event/reconciliation trigger")
    expected_use = update.PREFIX + ".github/workflows/standards-update.yml@" + value["tag"]
    if caller["jobs"]["update"]["uses"] != expected_use:
        raise ValueError("Missing central updater caller")
    dependencies = update.yaml_document(read(".github/dependabot.yml"))
    update.validate_dependabot(dependencies)
    actions = [u for u in dependencies["updates"] if u["package-ecosystem"] == "github-actions"]
    if not actions:
        raise ValueError("Missing native Dependabot GitHub Actions updater")
    for item in actions:
        groups = item.get("groups", {})
        if (
            item["schedule"]["interval"] != "daily"
            or next(iter(groups), None) != "central-standards"
            or groups["central-standards"].get("patterns") != update.DEPENDENCIES
        ):
            raise ValueError("Missing daily, first-match central Dependabot group")
    update.dispatchable_workflows(workflows)
    if value == latest:
        return {"repository": repository, "status": "current", "release": value["tag"]}
    pulls = update.pages(f"repos/{repository}/pulls?state=open&per_page=100")
    pending = []
    for pr in pulls:
        if pr["user"]["login"] != "dependabot[bot]":
            continue
        files = update.pages(f"repos/{repository}/pulls/{pr['number']}/files?per_page=100")
        if any(
            update.PREFIX in (f.get("patch") or "") and latest["tag"] in (f.get("patch") or "")
            for f in files
        ):
            checks = update.gh(
                f"repos/{repository}/commits/{pr['head']['sha']}/check-runs?per_page=100"
            )
            if checks["total_count"] > len(checks["check_runs"]):
                raise ValueError("Check inventory is incomplete")
            failed = [
                c["name"]
                for c in checks["check_runs"]
                if c.get("conclusion")
                in {
                    "failure",
                    "cancelled",
                    "timed_out",
                    "action_required",
                    "startup_failure",
                    "stale",
                }
            ]
            statuses = update.gh(f"repos/{repository}/commits/{pr['head']['sha']}/status")
            detail = update.gh(f"repos/{repository}/pulls/{pr['number']}")
            if (
                failed
                or statuses.get("state") == "failure"
                or detail.get("mergeable_state") == "dirty"
            ):
                raise ValueError(
                    f"Update PR {pr['html_url']} has failed/conflicted checks: {failed}"
                )
            pending.append(
                {
                    "url": pr["html_url"],
                    "head": pr["head"]["sha"],
                    "mergeable_state": detail.get("mergeable_state"),
                    "checks": [
                        {"name": c["name"], "status": c["status"], "conclusion": c["conclusion"]}
                        for c in checks["check_runs"]
                    ],
                }
            )
    if not pending:
        raise ValueError(f"Latest {latest['tag']} has no update PR; inspect Dependabot jobs")
    return {
        "repository": repository,
        "status": "pending",
        "release": value["tag"],
        "pull_requests": pending,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "standards-consumers.json",
    )
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text())
    owner = registry["owner"]
    latest_tag = update.gh(f"repos/{update.CENTRAL}/releases/latest")["tag_name"]
    latest = update.attest_release(latest_tag)
    expected = {f"{owner}/{name}" for name in registry["repositories"]}
    seen, report, errors = set(), [], []
    for repo in update.pages(f"users/{owner}/repos?per_page=100&type=owner"):
        name = repo["full_name"]
        if repo["fork"] or repo["archived"] or name == update.CENTRAL:
            continue
        try:
            result = inspect(name, update.tree_files(name, repo["default_branch"]), latest)
            if result:
                seen.add(name)
                report.append(result)
        except Exception as error:
            errors.append({"repository": name, "error": str(error)})
    if seen != expected:
        errors.append(
            {"unregistered": sorted(seen - expected), "missing_or_invalid": sorted(expected - seen)}
        )
    result = {"latest": latest, "consumers": report, "errors": errors}
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as stream:
            stream.write("## Standards consumer audit\n\n```json\n" + rendered + "\n```\n")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

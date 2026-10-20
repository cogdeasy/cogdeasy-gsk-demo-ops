"""Creates the Track B demo issues in Jira from jira/seed.json (or another seed file).

Needs JIRA_BASE_URL (default https://cog-gtm.atlassian.net), JIRA_EMAIL, JIRA_API_TOKEN.
Trigger labels are NOT applied: adding them is the live demo moment. With --file pointing at
jira/backlog.json or jira/roles.json only summary, type, labels, description and parent are
created; status, priority, assignee, points, comments and links are not.

    demo-ops-seed --dry-run
    demo-ops-seed --file jira/backlog.json --dry-run
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from demo_ops import REPO_ROOT
from demo_ops._cli import guarded, load_json
from demo_ops.jira_client import Fields, JiraClient, adf

SEED = REPO_ROOT / "jira" / "seed.json"
NOT_APPLIED = ("status", "priority", "assignee", "points", "comment", "key", "trigger_label")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="demo-ops-seed", description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print issues, create nothing")
    parser.add_argument(
        "--file", type=Path, default=SEED, help="seed file (default jira/seed.json)"
    )
    return parser


def issue_fields(issue: dict[str, Any], project: str, keys: dict[str, str]) -> Fields:
    """Jira create-issue fields; a parent ref resolves to a key created earlier in this run."""
    fields: Fields = {
        "project": {"key": project},
        "issuetype": {"name": issue["type"]},
        "summary": issue["summary"],
        "labels": issue["labels"],
        "description": adf(issue["description"]),
    }
    if "parent" in issue:
        fields["parent"] = {"key": keys.get(issue["parent"], issue["parent"])}
    return fields


def not_applied(seed: dict[str, Any]) -> list[str]:
    present = {name for issue in seed["issues"] for name in NOT_APPLIED if issue.get(name)}
    if seed.get("links"):
        present.add("links")
    return sorted(present)


def seed_issues(
    seed: dict[str, Any],
    create: Callable[[Fields], str] | None,
    out: Callable[[str], None] = print,
) -> dict[str, str]:
    """Create every issue in file order (parents first); create=None is a dry run."""
    keys: dict[str, str] = {}
    for issue in seed["issues"]:
        fields = issue_fields(issue, seed["project"], keys)
        if create is None:
            out(f"{issue['ref']:8} {issue['type']:6} {issue['summary']}")
            keys[issue["ref"]] = issue["ref"]
            continue
        keys[issue["ref"]] = create(fields)
        out(f"{issue['ref']} {keys[issue['ref']]}")
    return keys


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    seed = load_json(args.file)
    skipped = not_applied(seed)
    if skipped:
        print(f"note: not applied by seed: {', '.join(skipped)}", file=sys.stderr)

    def run() -> None:
        if args.dry_run:
            seed_issues(seed, None)
            return
        from demo_ops.http import HttpClient
        from demo_ops.settings import JiraSettings

        settings = JiraSettings.from_env()
        with HttpClient() as http:
            seed_issues(seed, JiraClient(settings, http).create_issue)

    guarded(run)


if __name__ == "__main__":
    main()

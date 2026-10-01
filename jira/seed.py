"""Creates the Track B demo issues in Jira from seed.json.

Needs JIRA_BASE_URL (https://cog-gtm.atlassian.net), JIRA_EMAIL, JIRA_API_TOKEN.
Trigger labels are NOT applied: adding them is the live demo moment.

    python3 jira/seed.py --dry-run
    python3 jira/seed.py
    python3 jira/seed.py --file jira/backlog.json --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.request
from pathlib import Path

SEED = Path(__file__).with_name("seed.json")


def adf(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": block}]}
            for block in text.split("\n\n")
        ],
    }


def create(base: str, auth: str, fields: dict) -> str:
    request = urllib.request.Request(
        f"{base}/rest/api/3/issue",
        data=json.dumps({"fields": fields}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())["key"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file", type=Path, default=SEED)
    args = parser.parse_args()

    seed = json.loads(args.file.read_text())
    base = os.environ.get("JIRA_BASE_URL", "https://cog-gtm.atlassian.net").rstrip("/")
    auth = ""
    if not args.dry_run:
        auth = base64.b64encode(
            f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode()
        ).decode()

    keys: dict[str, str] = {}
    for issue in seed["issues"]:
        fields = {
            "project": {"key": seed["project"]},
            "issuetype": {"name": issue["type"]},
            "summary": issue["summary"],
            "labels": issue["labels"],
            "description": adf(issue["description"]),
        }
        if "parent" in issue:
            fields["parent"] = {"key": keys.get(issue["parent"], issue["parent"])}
        if args.dry_run:
            print(f"{issue['ref']:8} {issue['type']:6} {issue['summary']}")
            keys[issue["ref"]] = issue["ref"]
            continue
        keys[issue["ref"]] = create(base, auth, fields)
        print(issue["ref"], keys[issue["ref"]])


if __name__ == "__main__":
    main()

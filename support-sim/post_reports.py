"""Posts the simulated R&D support reports to Jira (label rd-support) or a Slack webhook.

Jira:  JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, optional JIRA_PROJECT (default GSK)
Slack: SLACK_WEBHOOK_URL (incoming webhook for the support channel)

    python3 support-sim/post_reports.py --target jira --dry-run
    python3 support-sim/post_reports.py --target slack --delay 5
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.request
from pathlib import Path

REPORTS = Path(__file__).with_name("reports.json")


def post_json(url: str, body: dict, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        payload = response.read()
    return json.loads(payload) if payload.strip().startswith(b"{") else {}


def jira_issue(report: dict, project: str) -> dict:
    return {
        "fields": {
            "project": {"key": project},
            "issuetype": {"name": "Task"},
            "summary": f"[{report['id']}] R&D support: {report['text'][:80]}",
            "labels": ["rd-support"],
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Two-line explainer: User report from the R&D AI-scientist "
                                    "platform. Devin triages it: duplicate or new, reproduce, "
                                    "likely code path, fix PR if in scope.\n\n"
                                    f"Reporter: {report['reporter']}\n\n{report['text']}"
                                ),
                            }
                        ],
                    }
                ],
            },
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["jira", "slack"], required=True)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    reports = json.loads(REPORTS.read_text())["reports"]
    for report in reports:
        if args.target == "jira":
            body = jira_issue(report, os.environ.get("JIRA_PROJECT", "GSK"))
            if args.dry_run:
                print(json.dumps(body["fields"]["summary"]))
                continue
            token = base64.b64encode(
                f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode()
            ).decode()
            created = post_json(
                f"{os.environ['JIRA_BASE_URL'].rstrip('/')}/rest/api/3/issue",
                body,
                {"Authorization": f"Basic {token}"},
            )
            print(report["id"], created.get("key"))
        else:
            body = {"text": f"*{report['reporter']}*: {report['text']}"}
            if args.dry_run:
                print(body["text"])
                continue
            post_json(os.environ["SLACK_WEBHOOK_URL"], body, {})
            print(report["id"], "posted")
        time.sleep(args.delay)


if __name__ == "__main__":
    main()

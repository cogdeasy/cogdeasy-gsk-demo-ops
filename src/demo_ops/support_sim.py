"""Posts the simulated R&D support reports to Jira (label rd-support) or a Slack webhook.

Jira:  JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, optional JIRA_PROJECT (default GSK)
Slack: SLACK_WEBHOOK_URL (incoming webhook for the support channel)

    demo-ops-support-sim --target jira --dry-run
    demo-ops-support-sim --target slack --delay 5
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections.abc import Callable, Sequence
from typing import Any

from demo_ops import REPO_ROOT
from demo_ops._cli import guarded, load_json, non_negative_float
from demo_ops.jira_client import adf
from demo_ops.settings import DEFAULT_JIRA_PROJECT

REPORTS = REPO_ROOT / "support-sim" / "reports.json"
EXPLAINER = (
    "Two-line explainer: User report from the R&D AI-scientist platform. Devin triages it: "
    "duplicate or new, reproduce, likely code path, fix PR if in scope."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-ops-support-sim", description=__doc__.splitlines()[0]
    )
    parser.add_argument("--target", choices=["jira", "slack"], required=True)
    parser.add_argument(
        "--delay", type=non_negative_float, default=2.0, help="seconds between reports"
    )
    parser.add_argument("--dry-run", action="store_true", help="print payloads, post nothing")
    return parser


def jira_issue(report: dict[str, Any], project: str) -> dict[str, Any]:
    text = f"{EXPLAINER}\n\nReporter: {report['reporter']}\n\n{report['text']}"
    description = adf(text)
    # One paragraph, as the triage playbook reads the description as a single block.
    description["content"] = [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]
    return {
        "fields": {
            "project": {"key": project},
            "issuetype": {"name": "Task"},
            "summary": f"[{report['id']}] R&D support: {report['text'][:80]}",
            "labels": ["rd-support"],
            "description": description,
        }
    }


def slack_message(report: dict[str, Any]) -> dict[str, Any]:
    return {"text": f"*{report['reporter']}*: {report['text']}"}


def post_reports(
    reports: list[dict[str, Any]],
    target: str,
    send: Callable[[dict[str, Any]], str | None] | None,
    delay: float,
    project: str = DEFAULT_JIRA_PROJECT,
    out: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """send=None is a dry run. dup_of is the answer key and is never posted."""
    for report in reports:
        body = jira_issue(report, project) if target == "jira" else slack_message(report)
        if send is None:
            out(json.dumps(body["fields"]["summary"]) if target == "jira" else body["text"])
            continue
        out(f"{report['id']} {send(body)}")
        sleep(delay)


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    reports = load_json(REPORTS)["reports"]

    def run() -> None:
        if args.dry_run:
            project = os.environ.get("JIRA_PROJECT", "").strip() or DEFAULT_JIRA_PROJECT
            post_reports(reports, args.target, None, args.delay, project)
            return
        from demo_ops.http import HttpClient
        from demo_ops.jira_client import JiraClient
        from demo_ops.settings import JiraSettings, SlackSettings

        with HttpClient() as http:
            if args.target == "jira":
                jira_settings = JiraSettings.from_env()
                jira = JiraClient(jira_settings, http)
                post_reports(
                    reports,
                    "jira",
                    lambda body: jira.create_issue(body["fields"]),
                    args.delay,
                    jira_settings.project,
                )
            else:
                slack = SlackSettings.from_env()

                def send_slack(body: dict[str, Any]) -> str:
                    http.post_json(slack.webhook_url, body, secret_url=True)
                    return "posted"

                post_reports(reports, "slack", send_slack, args.delay)

    guarded(run)


if __name__ == "__main__":
    main()

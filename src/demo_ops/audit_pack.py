"""Starts the GSK audit pack for one change through the Devin API (v3).

Env: GSK_AUDIT_PLAYBOOK_ID (uuid part of the playbook id, needed for --dry-run too),
     DEVIN_API_KEY (service user with session permissions), DEVIN_ORG_ID (org-...),
     optional DEVIN_API_URL (default https://api.devin.ai)

    demo-ops-audit-pack GSK-1 --dry-run
    demo-ops-audit-pack GSK-1

Prints the created session (session_id, url). The pack lands later as a PR comment and in the
session; poll GET /v3/organizations/$DEVIN_ORG_ID/sessions/<session_id> for status.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from typing import Any

from demo_ops._cli import guarded
from demo_ops.settings import audit_playbook_id

SUBJECT_REPO = "cogdeasy/cogdeasy-gsk-ohdsi-webapi"
OPS_REPO = "cogdeasy/cogdeasy-gsk-demo-ops"
ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9]+-[0-9]+$")


def issue_key(value: str) -> str:
    if not ISSUE_KEY.fullmatch(value):
        raise argparse.ArgumentTypeError(f"not a Jira issue key: {value!r} (e.g. GSK-1)")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-ops-audit-pack", description=__doc__.splitlines()[0]
    )
    parser.add_argument("key", type=issue_key, help="Jira issue key, e.g. GSK-1")
    parser.add_argument("--dry-run", action="store_true", help="print the request body only")
    return parser


def session_body(key: str, playbook_uuid: str) -> dict[str, Any]:
    return {
        "title": f"GSK audit pack {key}",
        "prompt": f"Build the inspection-readiness pack for {key} on {SUBJECT_REPO}. Read-only.",
        "playbook_id": f"playbook-{playbook_uuid}",
        "repos": [SUBJECT_REPO, OPS_REPO],
        "tags": ["gsk-demo", "audit"],
    }


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    def run() -> None:
        body = session_body(args.key, audit_playbook_id())
        if args.dry_run:
            print(json.dumps(body))
            return
        from demo_ops.devin_client import DevinClient
        from demo_ops.http import HttpClient
        from demo_ops.settings import DevinApiSettings

        settings = DevinApiSettings.from_env()
        with HttpClient() as http:
            print(json.dumps(DevinClient(settings, http).create_session(body)))

    guarded(run)


if __name__ == "__main__":
    main()

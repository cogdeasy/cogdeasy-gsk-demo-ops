"""Posts the synthetic WebAPI alerts to a Devin automation Webhook trigger.

Env: DEVIN_ONCALL_WEBHOOK_URL (webhook URL from the automation's Webhook trigger)
     DEVIN_ONCALL_WEBHOOK_SECRET (the trigger's secret, sent as X-Webhook-Secret)

    python3 oncall-sim/post_alert.py --dry-run
    python3 oncall-sim/post_alert.py --alert A3
    python3 oncall-sim/post_alert.py --all --delay 30
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ALERTS = Path(__file__).with_name("alerts.json")


def post_json(url: str, body: dict, secret: str) -> int:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "X-Webhook-Secret": secret},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return response.status


def main() -> None:
    parser = argparse.ArgumentParser()
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--alert", help="alert id, e.g. A1")
    which.add_argument("--all", action="store_true", help="post every alert (default)")
    parser.add_argument("--delay", type=float, default=5.0, help="seconds between alerts")
    parser.add_argument("--dry-run", action="store_true", help="print payloads, post nothing")
    args = parser.parse_args()

    alerts = json.loads(ALERTS.read_text())["alerts"]
    if args.alert:
        alerts = [a for a in alerts if a["id"] == args.alert]
        if not alerts:
            sys.exit(f"unknown alert id: {args.alert}")

    if args.dry_run:
        for alert in alerts:
            print(json.dumps(alert, indent=2))
        return

    url = os.environ.get("DEVIN_ONCALL_WEBHOOK_URL")
    secret = os.environ.get("DEVIN_ONCALL_WEBHOOK_SECRET")
    if not url or not secret:
        sys.exit("set DEVIN_ONCALL_WEBHOOK_URL and DEVIN_ONCALL_WEBHOOK_SECRET, or use --dry-run")

    for i, alert in enumerate(alerts):
        if i:
            time.sleep(args.delay)
        status = post_json(url, alert, secret)
        print(alert["id"], status, alert["title"])


if __name__ == "__main__":
    main()

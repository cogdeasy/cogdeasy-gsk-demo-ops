"""Posts the synthetic WebAPI alerts to a Devin automation Webhook trigger.

Env: DEVIN_ONCALL_WEBHOOK_URL (webhook URL from the automation's Webhook trigger)
     DEVIN_ONCALL_WEBHOOK_SECRET (the trigger's secret, sent as X-Webhook-Secret)

    demo-ops-oncall-sim --dry-run
    demo-ops-oncall-sim --alert A3
    demo-ops-oncall-sim --all --delay 30
"""

from __future__ import annotations

import argparse
import json
import time
from collections.abc import Callable, Sequence
from typing import Any

from demo_ops import REPO_ROOT
from demo_ops._cli import guarded, load_json, non_negative_float

ALERTS = REPO_ROOT / "oncall-sim" / "alerts.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo-ops-oncall-sim", description=__doc__.splitlines()[0]
    )
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--alert", help="alert id, e.g. A1")
    which.add_argument("--all", action="store_true", help="post every alert (default)")
    parser.add_argument(
        "--delay", type=non_negative_float, default=5.0, help="seconds between alerts"
    )
    parser.add_argument("--dry-run", action="store_true", help="print payloads, post nothing")
    return parser


def select_alerts(alerts: list[dict[str, Any]], alert_id: str | None) -> list[dict[str, Any]]:
    if alert_id is None:
        return alerts
    chosen = [a for a in alerts if a["id"] == alert_id]
    if not chosen:
        raise SystemExit(f"unknown alert id: {alert_id}")
    return chosen


def post_alerts(
    alerts: list[dict[str, Any]],
    send: Callable[[dict[str, Any]], int],
    delay: float,
    out: Callable[[str], None] = print,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    for i, alert in enumerate(alerts):
        if i:
            sleep(delay)
        out(f"{alert['id']} {send(alert)} {alert['title']}")


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    alerts = select_alerts(load_json(ALERTS)["alerts"], args.alert)

    if args.dry_run:
        for alert in alerts:
            print(json.dumps(alert, indent=2))
        return

    def run() -> None:
        from demo_ops.http import HttpClient
        from demo_ops.settings import OncallWebhookSettings

        webhook = OncallWebhookSettings.from_env()
        headers = {"X-Webhook-Secret": webhook.secret}
        with HttpClient() as http:
            post_alerts(
                alerts,
                lambda a: http.post_json(webhook.url, a, headers)[0],
                args.delay,
            )

    guarded(run)


if __name__ == "__main__":
    main()

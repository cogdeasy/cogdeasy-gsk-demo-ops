from __future__ import annotations

import json

import httpx
import pytest

from conftest import MockHttp
from demo_ops import REPO_ROOT, oncall_sim

ALERTS = json.loads((REPO_ROOT / "oncall-sim/alerts.json").read_text())["alerts"]


def test_alert_and_all_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        oncall_sim.build_parser().parse_args(["--alert", "A1", "--all"])


def test_select_alerts() -> None:
    assert oncall_sim.select_alerts(ALERTS, None) == ALERTS
    assert [a["id"] for a in oncall_sim.select_alerts(ALERTS, "A3")] == ["A3"]
    with pytest.raises(SystemExit, match="unknown alert id: A9"):
        oncall_sim.select_alerts(ALERTS, "A9")


def test_dry_run_prints_payload(capsys: pytest.CaptureFixture[str]) -> None:
    oncall_sim.main(["--dry-run", "--alert", "A2"])
    assert json.loads(capsys.readouterr().out) == ALERTS[1]


def test_live_requires_webhook_env() -> None:
    with pytest.raises(SystemExit, match="DEVIN_ONCALL_WEBHOOK_URL, DEVIN_ONCALL_WEBHOOK_SECRET"):
        oncall_sim.main([])


def test_live_posts_with_secret_header(
    mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEVIN_ONCALL_WEBHOOK_URL", "https://hooks.devin.test/w/1")
    monkeypatch.setenv("DEVIN_ONCALL_WEBHOOK_SECRET", "s3cret")
    mock_http.handler = lambda r: httpx.Response(202)
    oncall_sim.main(["--all", "--delay", "0"])
    assert mock_http.bodies() == ALERTS
    assert {r.headers["X-Webhook-Secret"] for r in mock_http.requests} == {"s3cret"}
    out = capsys.readouterr().out
    assert out.splitlines()[0] == f"A1 202 {ALERTS[0]['title']}"
    assert "s3cret" not in out


def test_webhook_error_echoes_no_secret(
    mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEVIN_ONCALL_WEBHOOK_URL", "https://hooks.devin.test/w/HOOKID")
    monkeypatch.setenv("DEVIN_ONCALL_WEBHOOK_SECRET", "s3")
    mock_http.handler = lambda r: httpx.Response(401, json={"detail": "bad s3 for w/HOOKID"})
    with pytest.raises(SystemExit) as exc:
        oncall_sim.main(["--alert", "A1"])
    captured = capsys.readouterr()
    printed = f"{exc.value.code}{captured.out}{captured.err}"
    assert "HTTP 401 from hooks.devin.test" in printed
    assert "HOOKID" not in printed
    assert "bad s3" not in printed


def test_delay_only_between_alerts() -> None:
    sleeps: list[float] = []
    oncall_sim.post_alerts(ALERTS, lambda a: 200, 3, out=lambda _: None, sleep=sleeps.append)
    assert sleeps == [3] * (len(ALERTS) - 1)

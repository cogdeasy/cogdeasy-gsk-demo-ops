from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from conftest import MockHttp
from demo_ops import REPO_ROOT, support_sim

REPORTS = json.loads((REPO_ROOT / "support-sim/reports.json").read_text())["reports"]


def parse(*argv: str) -> Any:
    return support_sim.build_parser().parse_args(list(argv))


def test_target_is_required_and_restricted(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        parse()
    with pytest.raises(SystemExit):
        parse("--target", "email")
    assert "invalid choice" in capsys.readouterr().err


def test_flag_defaults_and_types() -> None:
    args = parse("--target", "jira")
    assert (args.target, args.delay, args.dry_run) == ("jira", 2.0, False)
    args = parse("--target", "slack", "--delay", "0.5", "--dry-run")
    assert (args.target, args.delay, args.dry_run) == ("slack", 0.5, True)


@pytest.mark.parametrize("delay", ["-1", "soon"])
def test_bad_delay_is_rejected(delay: str) -> None:
    with pytest.raises(SystemExit):
        parse("--target", "jira", "--delay", delay)


def test_jira_issue_payload() -> None:
    report = {"id": "R7", "reporter": "sci", "text": "x" * 100, "dup_of": "R1"}
    fields = support_sim.jira_issue(report, "ABC")["fields"]
    assert fields["project"] == {"key": "ABC"}
    assert fields["issuetype"] == {"name": "Task"}
    assert fields["labels"] == ["rd-support"]
    assert fields["summary"] == "[R7] R&D support: " + "x" * 80
    paragraphs = fields["description"]["content"]
    assert len(paragraphs) == 1
    text = paragraphs[0]["content"][0]["text"]
    assert text.startswith("Two-line explainer:")
    assert "Reporter: sci" in text
    assert "R1" not in json.dumps(fields)


def test_dry_run_prints_without_network_or_sleep(capsys: pytest.CaptureFixture[str]) -> None:
    support_sim.main(["--target", "slack", "--dry-run", "--delay", "999"])
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == len(REPORTS)
    assert lines[0] == f"*{REPORTS[0]['reporter']}*: {REPORTS[0]['text']}"


def test_dry_run_jira_uses_project_override(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("JIRA_PROJECT", "OPS")
    printed: list[str] = []
    support_sim.post_reports(REPORTS[:1], "jira", None, 0, "OPS", out=printed.append)
    assert printed == [json.dumps(support_sim.jira_issue(REPORTS[0], "OPS")["fields"]["summary"])]


def test_sleeps_between_live_posts() -> None:
    sleeps: list[float] = []
    support_sim.post_reports(
        REPORTS[:3], "slack", lambda b: "posted", 1.5, out=lambda _: None, sleep=sleeps.append
    )
    assert sleeps == [1.5, 1.5, 1.5]


def test_live_slack(mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.test/services/T/B/S")
    mock_http.handler = lambda r: httpx.Response(200, text="ok")
    support_sim.main(["--target", "slack", "--delay", "0"])
    assert len(mock_http.requests) == len(REPORTS)
    assert all("Authorization" not in r.headers for r in mock_http.requests)
    assert mock_http.bodies()[0] == {"text": f"*{REPORTS[0]['reporter']}*: {REPORTS[0]['text']}"}


def test_live_jira(mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JIRA_BASE_URL", "https://jira.test")
    monkeypatch.setenv("JIRA_EMAIL", "e@x.test")
    monkeypatch.setenv("JIRA_API_TOKEN", "t")
    monkeypatch.setenv("JIRA_PROJECT", "OPS")
    mock_http.handler = lambda r: httpx.Response(201, json={"key": "OPS-1"})
    support_sim.main(["--target", "jira", "--delay", "0"])
    assert {str(r.url) for r in mock_http.requests} == {"https://jira.test/rest/api/3/issue"}
    assert {b["fields"]["project"]["key"] for b in mock_http.bodies()} == {"OPS"}


@pytest.mark.parametrize(("target", "missing"), [("jira", "JIRA_EMAIL"), ("slack", "SLACK")])
def test_live_fails_fast_without_env(target: str, missing: str) -> None:
    with pytest.raises(SystemExit, match=missing):
        support_sim.main(["--target", target])

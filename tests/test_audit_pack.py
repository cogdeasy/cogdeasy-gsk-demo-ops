from __future__ import annotations

import json

import httpx
import pytest

from conftest import MockHttp
from demo_ops import audit_pack


def test_session_body() -> None:
    assert audit_pack.session_body("GSK-1", "abc") == {
        "title": "GSK audit pack GSK-1",
        "prompt": "Build the inspection-readiness pack for GSK-1 on "
        "cogdeasy/cogdeasy-gsk-ohdsi-webapi. Read-only.",
        "playbook_id": "playbook-abc",
        "repos": ["cogdeasy/cogdeasy-gsk-ohdsi-webapi", "cogdeasy/cogdeasy-gsk-demo-ops"],
        "tags": ["gsk-demo", "audit"],
    }


@pytest.mark.parametrize("key", ["gsk-1", "GSK", "GSK-1; rm -rf /", ""])
def test_rejects_non_issue_keys(key: str) -> None:
    with pytest.raises(SystemExit):
        audit_pack.build_parser().parse_args([key])


def test_dry_run_needs_playbook_id() -> None:
    with pytest.raises(SystemExit, match="GSK_AUDIT_PLAYBOOK_ID"):
        audit_pack.main(["GSK-1", "--dry-run"])


def test_dry_run_prints_body(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("GSK_AUDIT_PLAYBOOK_ID", "abc")
    audit_pack.main(["GSK-1", "--dry-run"])
    assert json.loads(capsys.readouterr().out) == audit_pack.session_body("GSK-1", "abc")


def test_live_creates_session(
    mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("GSK_AUDIT_PLAYBOOK_ID", "abc")
    monkeypatch.setenv("DEVIN_API_KEY", "key-123")
    monkeypatch.setenv("DEVIN_ORG_ID", "org-xyz")
    mock_http.handler = lambda r: httpx.Response(200, json={"session_id": "s1", "url": "u"})
    audit_pack.main(["GSK-1"])
    request = mock_http.requests[0]
    assert str(request.url) == "https://api.devin.ai/v3/organizations/org-xyz/sessions"
    assert request.headers["Authorization"] == "Bearer key-123"
    assert mock_http.bodies()[0]["playbook_id"] == "playbook-abc"
    assert json.loads(capsys.readouterr().out) == {"session_id": "s1", "url": "u"}


def test_live_requires_api_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GSK_AUDIT_PLAYBOOK_ID", "abc")
    with pytest.raises(SystemExit, match="DEVIN_API_KEY, DEVIN_ORG_ID"):
        audit_pack.main(["GSK-1"])

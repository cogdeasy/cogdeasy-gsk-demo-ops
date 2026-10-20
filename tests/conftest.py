from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx
import pytest

import demo_ops.http

ENV_VARS = (
    "JIRA_BASE_URL",
    "JIRA_EMAIL",
    "JIRA_API_TOKEN",
    "JIRA_PROJECT",
    "SLACK_WEBHOOK_URL",
    "DEVIN_ONCALL_WEBHOOK_URL",
    "DEVIN_ONCALL_WEBHOOK_SECRET",
    "DEVIN_API_KEY",
    "DEVIN_ORG_ID",
    "DEVIN_API_URL",
    "GSK_AUDIT_PLAYBOOK_ID",
)

Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@dataclass
class MockHttp:
    requests: list[httpx.Request] = field(default_factory=list)
    handler: Handler = lambda _: httpx.Response(200, json={})

    def bodies(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requests]

    def transport(self) -> httpx.MockTransport:
        def record(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return self.handler(request)

        return httpx.MockTransport(record)


@pytest.fixture
def mock_http(monkeypatch: pytest.MonkeyPatch) -> Iterator[MockHttp]:
    """Every HttpClient built by the CLIs talks to an in-memory transport; no real network."""
    mock = MockHttp()
    real = demo_ops.http.HttpClient

    class Patched(real):  # type: ignore[valid-type,misc]
        def __init__(self, **kwargs: Any) -> None:
            kwargs.setdefault("transport", mock.transport())
            kwargs.setdefault("sleep", lambda _: None)
            super().__init__(**kwargs)

    monkeypatch.setattr(demo_ops.http, "HttpClient", Patched)
    yield mock

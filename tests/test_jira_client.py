from __future__ import annotations

import base64

import httpx
import pytest

from demo_ops.http import HttpClient
from demo_ops.jira_client import JiraClient, adf
from demo_ops.settings import JiraSettings

SETTINGS = JiraSettings("https://jira.test", "me@x.test", "tok", "GSK")


def test_adf_splits_paragraphs_on_blank_lines() -> None:
    doc = adf("one\n\ntwo\nlines")
    assert doc["type"] == "doc"
    assert doc["version"] == 1
    assert [p["content"][0]["text"] for p in doc["content"]] == ["one", "two\nlines"]


def test_create_issue_posts_to_v3_with_basic_auth() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(201, json={"id": "1", "key": "GSK-57"})

    http = HttpClient(transport=httpx.MockTransport(handler))
    assert JiraClient(SETTINGS, http).create_issue({"summary": "s"}) == "GSK-57"
    request = seen[0]
    assert str(request.url) == "https://jira.test/rest/api/3/issue"
    assert request.method == "POST"
    expected = base64.b64encode(b"me@x.test:tok").decode()
    assert request.headers["Authorization"] == f"Basic {expected}"
    assert request.content == b'{"fields":{"summary":"s"}}'


def test_create_issue_without_key_fails() -> None:
    http = HttpClient(transport=httpx.MockTransport(lambda r: httpx.Response(201, json={})))
    with pytest.raises(RuntimeError, match="no issue key"):
        JiraClient(SETTINGS, http).create_issue({})

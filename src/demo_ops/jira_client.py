"""Jira Cloud REST v3 calls (Basic auth with an API token)."""

from __future__ import annotations

import base64
from typing import Any

from demo_ops.http import HttpClient
from demo_ops.settings import JiraSettings

Fields = dict[str, Any]


def adf(text: str) -> dict[str, Any]:
    """Atlassian Document Format: one paragraph per blank-line-separated block."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": block}]}
            for block in text.split("\n\n")
        ],
    }


class JiraClient:
    def __init__(self, settings: JiraSettings, http: HttpClient) -> None:
        self._base = settings.base_url
        self._http = http
        token = base64.b64encode(f"{settings.email}:{settings.api_token}".encode()).decode()
        self._headers = {"Authorization": f"Basic {token}"}

    def create_issue(self, fields: Fields) -> str:
        """Create an issue and return its key (e.g. GSK-57)."""
        _, created = self._http.post_json(
            f"{self._base}/rest/api/3/issue",
            {"fields": fields},
            self._headers,
            echo_error_body=True,
        )
        key = created.get("key")
        if not isinstance(key, str):
            raise RuntimeError("Jira create-issue response had no issue key")
        return key

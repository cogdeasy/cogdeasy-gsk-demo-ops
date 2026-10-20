"""Devin API v3 calls (service-user bearer token)."""

from __future__ import annotations

from typing import Any

from demo_ops.http import HttpClient
from demo_ops.settings import DevinApiSettings


class DevinClient:
    def __init__(self, settings: DevinApiSettings, http: HttpClient) -> None:
        self._sessions_url = f"{settings.api_url}/v3/organizations/{settings.org_id}/sessions"
        self._http = http
        self._headers = {"Authorization": f"Bearer {settings.api_key}"}

    def create_session(self, body: dict[str, Any]) -> dict[str, Any]:
        _, created = self._http.post_json(self._sessions_url, body, self._headers)
        return created

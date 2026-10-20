"""Environment-driven settings. Secrets are only ever read from the environment."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self

DEFAULT_JIRA_BASE_URL = "https://cog-gtm.atlassian.net"
DEFAULT_JIRA_PROJECT = "GSK"
DEFAULT_DEVIN_API_URL = "https://api.devin.ai"
ORG_ID = re.compile(r"^org-[A-Za-z0-9]+$")


class SettingsError(RuntimeError):
    """Raised when required environment variables are missing or invalid."""


class _Env:
    def __init__(self, env: Mapping[str, str] | None) -> None:
        self._env = os.environ if env is None else env
        self.missing: list[str] = []
        self.invalid: list[str] = []

    def required(self, name: str) -> str:
        value = self._env.get(name, "").strip()
        if not value:
            self.missing.append(name)
        return value

    def optional(self, name: str, default: str) -> str:
        return self._env.get(name, "").strip() or default

    def https_url(self, name: str, value: str) -> str:
        if value and not value.startswith("https://"):
            self.invalid.append(f"{name} must be an https:// URL")
        return value.rstrip("/")

    def check(self) -> None:
        problems = []
        if self.missing:
            problems.append("missing " + ", ".join(self.missing))
        problems.extend(self.invalid)
        if problems:
            raise SettingsError("; ".join(problems) + " (see .env.example, or use --dry-run)")


@dataclass(frozen=True, slots=True)
class JiraSettings:
    base_url: str
    email: str
    api_token: str
    project: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Self:
        e = _Env(env)
        settings = cls(
            base_url=e.https_url(
                "JIRA_BASE_URL", e.optional("JIRA_BASE_URL", DEFAULT_JIRA_BASE_URL)
            ),
            email=e.required("JIRA_EMAIL"),
            api_token=e.required("JIRA_API_TOKEN"),
            project=e.optional("JIRA_PROJECT", DEFAULT_JIRA_PROJECT),
        )
        e.check()
        return settings


@dataclass(frozen=True, slots=True)
class SlackSettings:
    webhook_url: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Self:
        e = _Env(env)
        settings = cls(
            webhook_url=e.https_url("SLACK_WEBHOOK_URL", e.required("SLACK_WEBHOOK_URL"))
        )
        e.check()
        return settings


@dataclass(frozen=True, slots=True)
class OncallWebhookSettings:
    url: str
    secret: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Self:
        e = _Env(env)
        settings = cls(
            url=e.https_url("DEVIN_ONCALL_WEBHOOK_URL", e.required("DEVIN_ONCALL_WEBHOOK_URL")),
            secret=e.required("DEVIN_ONCALL_WEBHOOK_SECRET"),
        )
        e.check()
        return settings


@dataclass(frozen=True, slots=True)
class DevinApiSettings:
    api_url: str
    api_key: str
    org_id: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Self:
        e = _Env(env)
        settings = cls(
            api_url=e.https_url(
                "DEVIN_API_URL", e.optional("DEVIN_API_URL", DEFAULT_DEVIN_API_URL)
            ),
            api_key=e.required("DEVIN_API_KEY"),
            org_id=e.required("DEVIN_ORG_ID"),
        )
        if settings.org_id and not ORG_ID.fullmatch(settings.org_id):
            e.invalid.append("DEVIN_ORG_ID must look like org-<id>")
        e.check()
        return settings


def audit_playbook_id(env: Mapping[str, str] | None = None) -> str:
    e = _Env(env)
    value = e.required("GSK_AUDIT_PLAYBOOK_ID")
    e.check()
    return value

from __future__ import annotations

from typing import Any

import pytest

from demo_ops.settings import (
    DevinApiSettings,
    JiraSettings,
    OncallWebhookSettings,
    SettingsError,
    SlackSettings,
    audit_playbook_id,
)


def test_jira_defaults_and_trailing_slash() -> None:
    s = JiraSettings.from_env(
        {"JIRA_EMAIL": "a@b.c", "JIRA_API_TOKEN": "t", "JIRA_BASE_URL": "https://x.net/"}
    )
    assert (s.base_url, s.project) == ("https://x.net", "GSK")
    assert JiraSettings.from_env({"JIRA_EMAIL": "e", "JIRA_API_TOKEN": "t"}).base_url == (
        "https://cog-gtm.atlassian.net"
    )


def test_missing_values_are_all_reported_at_once() -> None:
    with pytest.raises(SettingsError, match="missing JIRA_EMAIL, JIRA_API_TOKEN"):
        JiraSettings.from_env({})


def test_blank_value_counts_as_missing() -> None:
    with pytest.raises(SettingsError, match="JIRA_API_TOKEN"):
        JiraSettings.from_env({"JIRA_EMAIL": "e", "JIRA_API_TOKEN": "  "})


@pytest.mark.parametrize(
    ("cls", "env"),
    [
        (JiraSettings, {"JIRA_EMAIL": "e", "JIRA_API_TOKEN": "t", "JIRA_BASE_URL": "http://x"}),
        (SlackSettings, {"SLACK_WEBHOOK_URL": "http://hooks.slack.com/x"}),
        (
            OncallWebhookSettings,
            {"DEVIN_ONCALL_WEBHOOK_URL": "ftp://x", "DEVIN_ONCALL_WEBHOOK_SECRET": "s"},
        ),
    ],
)
def test_urls_must_be_https(cls: Any, env: dict[str, str]) -> None:
    with pytest.raises(SettingsError, match="https://"):
        cls.from_env(env)


def test_devin_org_id_shape_is_checked() -> None:
    ok = DevinApiSettings.from_env({"DEVIN_API_KEY": "k", "DEVIN_ORG_ID": "org-abc123"})
    assert ok.api_url == "https://api.devin.ai"
    with pytest.raises(SettingsError, match="org-<id>"):
        DevinApiSettings.from_env({"DEVIN_API_KEY": "k", "DEVIN_ORG_ID": "org-1/../x"})


def test_secret_values_never_appear_in_errors() -> None:
    with pytest.raises(SettingsError) as err:
        OncallWebhookSettings.from_env({"DEVIN_ONCALL_WEBHOOK_URL": "http://h/secret-path"})
    assert "secret-path" not in str(err.value)


def test_audit_playbook_id() -> None:
    assert audit_playbook_id({"GSK_AUDIT_PLAYBOOK_ID": "abc"}) == "abc"
    with pytest.raises(SettingsError, match="GSK_AUDIT_PLAYBOOK_ID"):
        audit_playbook_id({})

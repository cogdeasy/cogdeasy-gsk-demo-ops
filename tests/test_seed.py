from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from conftest import MockHttp
from demo_ops import REPO_ROOT, seed

SEED = json.loads((REPO_ROOT / "jira/seed.json").read_text())
BACKLOG = json.loads((REPO_ROOT / "jira/backlog.json").read_text())


def test_parser_defaults_to_seed_file() -> None:
    args = seed.build_parser().parse_args([])
    assert args.file == REPO_ROOT / "jira" / "seed.json"
    assert args.dry_run is False
    assert seed.build_parser().parse_args(["--file", "x.json", "--dry-run"]).file == Path("x.json")


def test_issue_fields_shape() -> None:
    issue = {"ref": "Q9", "type": "Bug", "summary": "S", "labels": ["a"], "description": "p1\n\np2"}
    fields = seed.issue_fields(issue, "GSK", {})
    assert fields == {
        "project": {"key": "GSK"},
        "issuetype": {"name": "Bug"},
        "summary": "S",
        "labels": ["a"],
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "p1"}]},
                {"type": "paragraph", "content": [{"type": "text", "text": "p2"}]},
            ],
        },
    }


def test_parent_ref_resolves_to_created_key_or_passes_through() -> None:
    issue = {"ref": "C", "type": "Story", "summary": "s", "labels": [], "description": "d"}
    assert seed.issue_fields({**issue, "parent": "E"}, "GSK", {"E": "GSK-7"})["parent"] == {
        "key": "GSK-7"
    }
    assert seed.issue_fields({**issue, "parent": "GSK-3"}, "GSK", {})["parent"] == {"key": "GSK-3"}


def test_seed_mode_never_applies_trigger_labels() -> None:
    created: list[dict[str, Any]] = []

    def create(fields: dict[str, Any]) -> str:
        created.append(fields)
        return f"GSK-{len(created)}"

    keys = seed.seed_issues(SEED, create, out=lambda _: None)
    assert len(created) == len(SEED["issues"])
    triggers = {i["trigger_label"] for i in SEED["issues"] if "trigger_label" in i}
    assert triggers
    assert not triggers & {label for f in created for label in f["labels"]}
    epic = keys["Q2-EPIC"]
    children = [f for f in created if f.get("parent")]
    assert children
    assert all(f["parent"] == {"key": epic} for f in children)


def test_backlog_mode_sends_only_create_fields() -> None:
    created: list[dict[str, Any]] = []

    def create(fields: dict[str, Any]) -> str:
        created.append(fields)
        return "GSK-0"

    seed.seed_issues(BACKLOG, create, out=lambda _: None)
    assert len(created) == len(BACKLOG["issues"])
    allowed = {"project", "issuetype", "summary", "labels", "description", "parent"}
    assert all(set(f) <= allowed for f in created)
    assert seed.not_applied(BACKLOG) == [
        "assignee",
        "comment",
        "links",
        "points",
        "priority",
        "status",
    ]


@pytest.mark.parametrize(
    ("argv", "data"),
    [([], SEED), (["--file", str(REPO_ROOT / "jira/backlog.json")], BACKLOG)],
    ids=["seed", "backlog"],
)
def test_dry_run_lists_every_issue(
    argv: list[str], data: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    seed.main([*argv, "--dry-run"])
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == len(data["issues"])
    first = data["issues"][0]
    assert lines[0] == f"{first['ref']:8} {first['type']:6} {first['summary']}"


def test_live_run_fails_fast_without_credentials() -> None:
    with pytest.raises(SystemExit, match="missing JIRA_EMAIL, JIRA_API_TOKEN"):
        seed.main([])


def test_live_run_posts_through_shared_client(
    mock_http: MockHttp, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("JIRA_EMAIL", "me@x.test")
    monkeypatch.setenv("JIRA_API_TOKEN", "tok")
    counter = iter(range(100, 200))
    mock_http.handler = lambda r: httpx.Response(201, json={"key": f"GSK-{next(counter)}"})
    seed.main([])
    assert len(mock_http.requests) == len(SEED["issues"])
    assert {str(r.url) for r in mock_http.requests} == {
        "https://cog-gtm.atlassian.net/rest/api/3/issue"
    }
    bodies = mock_http.bodies()
    epic_index = [i["ref"] for i in SEED["issues"]].index("Q2-EPIC")
    epic_key = f"GSK-{100 + epic_index}"
    assert any(b["fields"].get("parent") == {"key": epic_key} for b in bodies)
    assert capsys.readouterr().out.splitlines()[0] == f"{SEED['issues'][0]['ref']} GSK-100"

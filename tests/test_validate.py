from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from demo_ops import REPO_ROOT, validate


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    for rel in validate.SCHEMAS:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, tmp_path / rel)
    shutil.copytree(REPO_ROOT / "playbooks", tmp_path / "playbooks")
    shutil.copytree(REPO_ROOT / "api", tmp_path / "api")
    return tmp_path


def edit(root: Path, rel: str, change: Callable[[dict[str, Any]], None]) -> None:
    path = root / rel
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def test_repo_data_is_valid() -> None:
    assert validate.validate(REPO_ROOT) == []


def test_cli_ok(capsys: pytest.CaptureFixture[str]) -> None:
    validate.main([])
    assert capsys.readouterr().out.strip() == f"ok: {len(validate.SCHEMAS)} file(s) valid"


def test_cli_accepts_paths(capsys: pytest.CaptureFixture[str]) -> None:
    validate.main([str(REPO_ROOT / "jira/backlog.json")])
    assert "ok: 1 file(s)" in capsys.readouterr().out


def test_cli_fails_on_problems(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    edit(repo, "oncall-sim/alerts.json", lambda d: d["alerts"][0].pop("title"))
    with pytest.raises(SystemExit, match="1 problem"):
        validate.main(["--root", str(repo)])
    assert "'title' is a required property" in capsys.readouterr().out


def test_unknown_file(repo: Path) -> None:
    assert validate.validate(repo, ["docs/x.json"])[0].startswith("docs/x.json: no schema")


@pytest.mark.parametrize(
    ("rel", "change", "message"),
    [
        (
            "automations/automations.json",
            lambda d: d["automations"][0]["trigger"].update(type="email"),
            "is not one of",
        ),
        (
            "automations/automations.json",
            lambda d: d["automations"][0]["trigger"].update(lable="x"),
            "Additional properties",
        ),
        (
            "automations/automations.json",
            lambda d: d["automations"][0].update(playbook="playbooks/missing.md"),
            "playbook playbooks/missing.md does not exist",
        ),
        (
            "automations/automations.json",
            lambda d: d["automations"].append(d["automations"][0]),
            "duplicate automation name gsk-ticket-to-pr",
        ),
        ("jira/seed.json", lambda d: d["issues"][0].update(type="Feature"), "is not one of"),
        ("jira/seed.json", lambda d: d["issues"].reverse(), "is defined later in the file"),
        (
            "jira/seed.json",
            lambda d: d["issues"][0]["labels"].append(d["issues"][0]["trigger_label"]),
            "must not be pre-applied",
        ),
        (
            "jira/backlog.json",
            lambda d: d["links"].append({"type": "Blocks", "from": "S-HIKARI", "to": "NOPE"}),
            "unknown to NOPE",
        ),
        ("jira/roles.json", lambda d: d["issues"][1].update(key="GSK-42"), "duplicate key GSK-42"),
        (
            "jira/roles.json",
            lambda d: d["issues"][0].update(assignee="not-an-email"),
            "is not a 'email'",
        ),
        (
            "support-sim/reports.json",
            lambda d: d["reports"][1].update(dup_of="R99"),
            "dup_of R99 is not a report id",
        ),
        (
            "oncall-sim/alerts.json",
            lambda d: d["alerts"][0].update(started_at="yesterday"),
            "does not match",
        ),
        ("oncall-sim/expected.json", lambda d: d["expected"].pop(), "do not match alerts"),
    ],
)
def test_detects(
    repo: Path, rel: str, change: Callable[[dict[str, Any]], None], message: str
) -> None:
    edit(repo, rel, change)
    problems = validate.validate(repo)
    assert any(message in p for p in problems), problems


def test_answer_key_alone_is_checked_against_alerts(repo: Path) -> None:
    edit(repo, "oncall-sim/expected.json", lambda d: d["expected"].pop())
    problems = validate.validate(repo, ["oncall-sim/expected.json"])
    assert any("do not match alerts" in p for p in problems)

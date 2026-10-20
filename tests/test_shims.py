"""The old script paths must keep working for --dry-run on a bare python3 (no site-packages)."""

from __future__ import annotations

import subprocess
import sys

import pytest

from demo_ops import REPO_ROOT


@pytest.mark.parametrize(
    "argv",
    [
        ["jira/seed.py", "--dry-run"],
        ["jira/seed.py", "--file", "jira/backlog.json", "--dry-run"],
        ["support-sim/post_reports.py", "--target", "jira", "--dry-run"],
        ["support-sim/post_reports.py", "--target", "slack", "--dry-run"],
        ["oncall-sim/post_alert.py", "--dry-run"],
    ],
)
def test_dry_run_without_dependencies(argv: list[str]) -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-S", *argv],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()

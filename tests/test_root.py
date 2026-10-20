from __future__ import annotations

import importlib
from pathlib import Path

import pytest

import demo_ops


def test_root_from_checkout() -> None:
    assert (demo_ops.REPO_ROOT / "automations" / "automations.json").is_file()


def test_root_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEMO_OPS_ROOT", str(tmp_path))
    try:
        assert tmp_path.resolve() == importlib.reload(demo_ops).REPO_ROOT
    finally:
        monkeypatch.delenv("DEMO_OPS_ROOT")
        importlib.reload(demo_ops)

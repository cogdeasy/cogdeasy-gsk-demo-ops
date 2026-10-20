from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, NoReturn

from demo_ops.http import HttpError
from demo_ops.settings import SettingsError


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return data


def non_negative_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return number


def guarded(run: Callable[[], None]) -> None:
    """Turn configuration and HTTP failures into a one-line error and exit code 1."""
    try:
        run()
    except (SettingsError, HttpError) as exc:
        _fail(exc)


def _fail(exc: Exception) -> NoReturn:
    raise SystemExit(f"error: {exc}")

"""Track B demo control plane: thin CLIs over the playbooks and JSON data in this repo."""

import os
from pathlib import Path


def _repo_root() -> Path:
    # The data lives in the checkout, not the wheel. Source/editable installs find it next to
    # src/; a non-editable install needs DEMO_OPS_ROOT or a run from the checkout root.
    if env := os.environ.get("DEMO_OPS_ROOT", "").strip():
        return Path(env).resolve()
    here = Path(__file__).resolve().parents[2]
    if (here / "automations" / "automations.json").is_file():
        return here
    return Path.cwd()


REPO_ROOT = _repo_root()

"""Shim for `python3 jira/seed.py`; code in demo_ops.seed."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from demo_ops.seed import main

if __name__ == "__main__":
    main()

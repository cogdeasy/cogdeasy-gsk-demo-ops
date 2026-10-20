"""Shim for `python3 oncall-sim/post_alert.py`; code in demo_ops.oncall_sim."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from demo_ops.oncall_sim import main

if __name__ == "__main__":
    main()

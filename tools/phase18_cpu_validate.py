#!/usr/bin/env python3
"""Discover-based CPU validation for Phase 18.

Unlike a hand-maintained test-module list, this entrypoint automatically includes
new `test_phase18_*.py` regressions. It is safe to run before any GPU work.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "-m", "py_compile", *[str(p) for p in sorted((ROOT / "engine" / "intelligence").glob("*.py"))]],
        [sys.executable, "-m", "unittest", "discover", "-v", "-s", str(ROOT / "tests"), "-p", "test_phase18_*.py"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, text=True)
        if completed.returncode != 0:
            print(json.dumps({
                "status": "PHASE18_CPU_VALIDATION_FAILED",
                "returncode": completed.returncode,
                "command": command,
            }, ensure_ascii=False, indent=2))
            return completed.returncode

    print(json.dumps({
        "status": "PHASE18_CPU_VALIDATION_PASSED",
        "test_pattern": "test_phase18_*.py",
        "production_entrypoint_touched": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

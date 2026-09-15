#!/usr/bin/env python3
"""Discover-based CPU validation for Phase 18.

Unlike a hand-maintained test-module list, this entrypoint automatically includes
new `test_phase18_*.py` regressions. It is safe to run before any GPU work.

The validator also persists a deterministic diagnostic report. This does not
weaken failure semantics: any compile or unittest failure still returns the
original non-zero status, while CI can retain the exact stdout/stderr needed to
identify the blocker without rerunning GPU-adjacent workflows.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "output" / "phase18_cpu_validation" / "report.json"


def _write_report(payload: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _echo_stream(text: str | None, *, stderr: bool = False) -> None:
    if not text:
        return
    stream = sys.stderr if stderr else sys.stdout
    print(text, end="" if text.endswith("\n") else "\n", file=stream)


def main() -> int:
    commands = [
        [
            sys.executable,
            "-m",
            "py_compile",
            *[
                str(p)
                for p in sorted(
                    (ROOT / "engine" / "intelligence").glob("*.py")
                )
            ],
        ],
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-v",
            "-s",
            str(ROOT / "tests"),
            "-p",
            "test_phase18_*.py",
        ],
    ]
    command_results: list[dict[str, Any]] = []

    for index, command in enumerate(commands):
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        _echo_stream(completed.stdout)
        _echo_stream(completed.stderr, stderr=True)

        result = {
            "index": index,
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
        }
        command_results.append(result)

        if completed.returncode != 0:
            payload = {
                "status": "PHASE18_CPU_VALIDATION_FAILED",
                "failed_command_index": index,
                "returncode": completed.returncode,
                "command": command,
                "test_pattern": "test_phase18_*.py",
                "production_entrypoint_touched": False,
                "commands": command_results,
            }
            _write_report(payload)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return completed.returncode

    payload = {
        "status": "PHASE18_CPU_VALIDATION_PASSED",
        "test_pattern": "test_phase18_*.py",
        "production_entrypoint_touched": False,
        "commands": command_results,
    }
    _write_report(payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

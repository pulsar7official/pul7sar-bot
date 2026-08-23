#!/usr/bin/env python3
"""One-command Colab entrypoint for Phase 18.

Flow:
1. verify the protected Phase 18 branch,
2. fast-forward from GitHub,
3. discover/run all Phase 18 CPU tests,
4. invoke the existing GPU runner with duplicate test execution disabled.

A CPU failure stops before GPU time is spent.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    root = str(ROOT)
    existing = [item for item in env.get("PYTHONPATH", "").split(os.pathsep) if item]
    if root not in existing:
        existing.insert(0, root)
    env["PYTHONPATH"] = os.pathsep.join(existing)
    return env


def _run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT, env=_env()).returncode


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, env=_env(), text=True, capture_output=True
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 one-command Colab flow")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    print("=== PUL7SAR PHASE 18 — ONE COMMAND ===")
    print("1/3 Updating protected Phase 18 branch...")
    if _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]) != 0:
        raise RuntimeError("COLAB_UPDATE_FAILED")

    print("2/3 Discovering and running all Phase 18 CPU validation...")
    if _run([sys.executable, str(ROOT / "tools" / "phase18_cpu_validate.py")]) != 0:
        raise RuntimeError("COLAB_CPU_VALIDATION_FAILED: GPU execution blocked")

    print("3/3 Entering locked Golden runner...")
    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_runner.py"),
        "--candidate", str(args.candidate),
        "--skip-targeted-tests",
    ]
    if args.force:
        command.append("--force")
    if args.prepare_only:
        command.append("--prepare-only")
    return _run(command)


if __name__ == "__main__":
    raise SystemExit(main())

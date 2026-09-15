#!/usr/bin/env python3
"""Fail-closed, non-authoritative source-identity probe for first Golden v6.

The probe performs no model loading, generation, downloads, queue mutation, or
publication. It proves that execution is rooted at the dedicated Phase 18 branch,
that HEAD is an immutable commit, that tracked source files are clean, and that
main.py is not part of the Phase 18 diff from origin/main.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
GitRunner = Callable[[list[str]], tuple[int, str, str]]


def _git(command: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *command],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def inspect(*, expected_commit: str | None = None, git_runner: GitRunner | None = None) -> dict[str, object]:
    run = _git if git_runner is None else git_runner
    blockers: list[str] = []

    rc, branch, _ = run(["branch", "--show-current"])
    if rc != 0 or branch != EXPECTED_BRANCH:
        blockers.append("PHASE18_EXECUTION_BRANCH_MISMATCH")

    rc, head, _ = run(["rev-parse", "HEAD"])
    if rc != 0 or _SHA40.fullmatch(head) is None:
        blockers.append("PHASE18_EXECUTION_HEAD_UNPROVEN")
        head = ""

    if expected_commit is not None:
        if _SHA40.fullmatch(expected_commit) is None:
            blockers.append("EXPECTED_COMMIT_INVALID")
        elif head and head != expected_commit:
            blockers.append("PHASE18_EXECUTION_COMMIT_MISMATCH")

    rc, tracked_status, _ = run(["status", "--porcelain", "--untracked-files=no"])
    if rc != 0:
        blockers.append("PHASE18_TRACKED_WORKTREE_STATUS_UNAVAILABLE")
    elif tracked_status:
        blockers.append("PHASE18_TRACKED_WORKTREE_DIRTY")

    rc, merge_base, _ = run(["merge-base", "origin/main", "HEAD"])
    if rc != 0 or _SHA40.fullmatch(merge_base) is None:
        blockers.append("PHASE18_MAIN_MERGE_BASE_UNPROVEN")
        merge_base = ""

    main_py_modified = None
    if merge_base:
        rc, diff_names, _ = run(["diff", "--name-only", f"{merge_base}...HEAD"])
        if rc != 0:
            blockers.append("PHASE18_MAIN_DIFF_UNAVAILABLE")
        else:
            names = {line.strip() for line in diff_names.splitlines() if line.strip()}
            main_py_modified = "main.py" in names
            if main_py_modified:
                blockers.append("PHASE18_MAIN_PY_MODIFIED")

    return {
        "schema": "pul7sar-phase18-first-golden-source-identity-probe-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "branch_required": EXPECTED_BRANCH,
        "branch_observed": branch if rc == 0 or branch else branch,
        "head_commit": head or None,
        "expected_commit": expected_commit,
        "merge_base_with_origin_main": merge_base or None,
        "tracked_worktree_clean": "PHASE18_TRACKED_WORKTREE_DIRTY" not in blockers and "PHASE18_TRACKED_WORKTREE_STATUS_UNAVAILABLE" not in blockers,
        "main_py_modified": main_py_modified,
        "source_identity_ready": not blockers,
        "blockers": blockers,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove Phase 18 first-Golden source identity before GPU execution")
    parser.add_argument("--expected-commit")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = inspect(expected_commit=args.expected_commit)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target = target.resolve()
        root = ROOT.resolve()
        if target != root and root not in target.parents:
            raise RuntimeError("FIRST_GOLDEN_SOURCE_IDENTITY_OUTPUT_ESCAPES_REPOSITORY")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["source_identity_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

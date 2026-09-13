#!/usr/bin/env python3
"""Lock one explicitly reviewed football pitch preset to exact diagnostic bytes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_REVIEW_ROOT = ROOT / "output" / "phase18_visual_proof" / "pitch-review"
DEFAULT_LOCK_ROOT = ROOT / "output" / "phase18_visual_proof" / "pitch-selection"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.football_pitch_selection import FootballPitchSelectionLock


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lock an explicit Phase 18 pitch-review selection without rerunning FLUX or Qwen"
    )
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--review", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    if args.candidate <= 0:
        raise ValueError("candidate must be positive")
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("PHASE18_PITCH_SELECTION_BRANCH_BLOCKED")

    review = Path(args.review) if args.review else (
        DEFAULT_REVIEW_ROOT / f"candidate-{args.candidate:02d}" / "colab-pitch-review.json"
    )
    if not review.is_absolute():
        review = ROOT / review
    output_dir = Path(args.output_dir) if args.output_dir else (
        DEFAULT_LOCK_ROOT / f"candidate-{args.candidate:02d}"
    )
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    payload = FootballPitchSelectionLock().lock(
        review_path=str(review),
        output_dir=str(output_dir),
    )
    if payload.get("candidate") != args.candidate:
        raise RuntimeError("PHASE18_PITCH_SELECTION_CANDIDATE_MISMATCH")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

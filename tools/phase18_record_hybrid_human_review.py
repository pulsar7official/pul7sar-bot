#!/usr/bin/env python3
"""Record a fail-closed human decision on the exact SHA-bound Hybrid review bytes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from engine.intelligence.hybrid_human_review_decision import HybridHumanReviewDecisionGate

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_BUNDLE = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-bundle.json"
DEFAULT_REVIEW = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-template.json"
DEFAULT_OUTPUT = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-decision.json"


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError("HYBRID_HUMAN_DECISION_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def run(
    *,
    bundle_path: Path = DEFAULT_BUNDLE,
    review_path: Path = DEFAULT_REVIEW,
    output_path: Path = DEFAULT_OUTPUT,
) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("HYBRID_HUMAN_DECISION_BRANCH_BLOCKED")
    return HybridHumanReviewDecisionGate(root=ROOT).evaluate(
        bundle_path=bundle_path,
        review_path=review_path,
        output_path=output_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Record the explicit human visual decision for Candidate 1 Hybrid proof")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(bundle_path=args.bundle, review_path=args.review, output_path=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("human_visual_review_approved") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())

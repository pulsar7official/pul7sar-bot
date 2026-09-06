#!/usr/bin/env python3
"""Prepare a SHA-bound human review bundle from the strict Hybrid semantic proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from engine.intelligence.hybrid_human_review_bundle import HybridHumanReviewBundleBuilder

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_CONTINUATION = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-semantic-continuation.json"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "phase18_visual_proof" / "hybrid-human-review" / "candidate-01"
DEFAULT_RECEIPT = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-bundle.json"


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("HYBRID_HUMAN_REVIEW_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def run(*, continuation_path: Path, output_dir: Path, receipt_path: Path) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("HYBRID_HUMAN_REVIEW_BRANCH_BLOCKED")
    if not continuation_path.is_file():
        raise RuntimeError("HYBRID_HUMAN_REVIEW_CONTINUATION_RECEIPT_MISSING")
    continuation = json.loads(continuation_path.read_text(encoding="utf-8"))
    receipt = HybridHumanReviewBundleBuilder(root=ROOT).build(
        continuation=continuation,
        output_dir=output_dir,
    )
    payload = receipt.__dict__
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare exact Hybrid-vs-base PNGs for explicit human visual review")
    parser.add_argument("--continuation", type=Path, default=DEFAULT_CONTINUATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    payload = run(
        continuation_path=args.continuation,
        output_dir=args.output_dir,
        receipt_path=args.receipt,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

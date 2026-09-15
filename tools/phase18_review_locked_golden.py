#!/usr/bin/env python3
"""Evaluate human Golden scores for the exact locked semantic artifact."""
from __future__ import annotations

import argparse
import json

from engine.intelligence.locked_golden_visual_review import LockedGoldenVisualReviewGate


def main() -> int:
    parser = argparse.ArgumentParser(description="Review locked PUL7SAR Golden Visual candidate")
    parser.add_argument("--semantic-review", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--output-dir", default="output/phase18_visual_proof/locked-golden")
    args = parser.parse_args()
    result = LockedGoldenVisualReviewGate().evaluate(
        semantic_review_path=args.semantic_review,
        review_path=args.review,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["golden_quality_approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

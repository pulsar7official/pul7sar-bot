#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.human_approved_golden_visual_review import HumanApprovedGoldenVisualReviewGate

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply the Golden scorecard to the accepted Hybrid review artifact")
    parser.add_argument("--handoff", default="output/phase18_colab/latest.json")
    parser.add_argument("--continuation", default="output/phase18_gpu_smoke/hybrid-semantic-continuation.json")
    parser.add_argument("--human-decision", default="output/phase18_gpu_smoke/hybrid-human-review-decision.json")
    parser.add_argument("--review", required=True)
    parser.add_argument("--output-dir", default="output/phase18_visual_proof/human-approved-golden")
    args = parser.parse_args()
    result = HumanApprovedGoldenVisualReviewGate(root=ROOT).evaluate(
        handoff_path=args.handoff,
        continuation_path=args.continuation,
        human_decision_path=args.human_decision,
        review_path=args.review,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["golden_quality_approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

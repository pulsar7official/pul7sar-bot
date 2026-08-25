#!/usr/bin/env python3
"""Build a Golden scorecard only after accepted SHA-bound human Hybrid review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.human_approved_golden_visual_review import HumanApprovedGoldenVisualReviewGate


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR human-approved Golden Visual review template")
    parser.add_argument("--handoff", default="output/phase18_colab/latest.json")
    parser.add_argument("--continuation", default="output/phase18_gpu_smoke/hybrid-semantic-continuation.json")
    parser.add_argument("--human-decision", default="output/phase18_gpu_smoke/hybrid-human-review-decision.json")
    parser.add_argument("--output", default="output/phase18_visual_proof/human-approved-golden-review.json")
    args = parser.parse_args()

    gate = HumanApprovedGoldenVisualReviewGate(root=ROOT)
    template = gate.build_template(
        handoff_path=args.handoff,
        continuation_path=args.continuation,
        human_decision_path=args.human_decision,
    )
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    output = output.resolve()
    if output != ROOT.resolve() and ROOT.resolve() not in output.parents:
        raise RuntimeError("HUMAN_GOLDEN_OUTPUT_ESCAPES_REPOSITORY")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": "HUMAN_APPROVED_GOLDEN_REVIEW_TEMPLATE_READY",
        "candidate": template["candidate"],
        "request_id": template["request_id"],
        "seed": template["seed"],
        "hybrid_png_sha256": template["hybrid_png_sha256"],
        "output": str(output),
        "golden_quality_approved": False,
        "publication_ready": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

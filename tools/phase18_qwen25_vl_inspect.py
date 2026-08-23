#!/usr/bin/env python3
"""Run optional local Qwen2.5-VL semantic inspection on one generated image."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen25_vl_inspector import Qwen25VLSemanticInspector
from engine.intelligence.semantic_visual_verdict import SemanticVisualVerdictGate


def _check_payload(check):
    return {"state": check.state.value, "confidence": check.confidence, "detail": check.detail}


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 local Qwen semantic visual inspector")
    parser.add_argument("--image", required=True)
    parser.add_argument("--expected-subject", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--minimum-confidence", type=float, default=0.85)
    args = parser.parse_args()

    verdict = Qwen25VLSemanticInspector().inspect_file(args.image, expected_subject=args.expected_subject)
    approved, failures = SemanticVisualVerdictGate().evaluate(
        verdict,
        identity_required=False,
        minimum_confidence=args.minimum_confidence,
    )
    payload = {
        "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE",
        "verifier_id": verdict.verifier_id,
        "approved_non_identity": approved,
        "failures": list(failures),
        "checks": {
            "readable_text_absent": _check_payload(verdict.readable_text_absent),
            "platform_brand_absent": _check_payload(verdict.platform_brand_absent),
            "fake_entity_marks_absent": _check_payload(verdict.fake_entity_marks_absent),
            "single_scene": _check_payload(verdict.single_scene),
            "severe_defects_absent": _check_payload(verdict.severe_defects_absent),
            "subject_framing_valid": _check_payload(verdict.subject_framing_valid),
        },
    }
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if approved else 2


if __name__ == "__main__":
    raise SystemExit(main())

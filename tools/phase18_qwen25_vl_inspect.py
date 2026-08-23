#!/usr/bin/env python3
"""Run optional local Qwen2.5-VL semantic/layer inspection on one generated image."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen25_vl_inspector import Qwen25VLSemanticInspector
from engine.intelligence.semantic_layer_evidence import SemanticLayerEvidenceAdapter
from engine.intelligence.semantic_visual_verdict import SemanticVisualVerdictGate


def _check_payload(check):
    if check is None:
        return None
    return {"state": check.state.value, "confidence": check.confidence, "detail": check.detail}


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 local Qwen semantic visual inspector")
    parser.add_argument("--image", required=True)
    parser.add_argument("--expected-subject", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--minimum-confidence", type=float, default=0.85)
    parser.add_argument("--require-exact-number-check", action="store_true")
    parser.add_argument("--require-sport-geometry-check", action="store_true")
    args = parser.parse_args()

    verdict = Qwen25VLSemanticInspector().inspect_file(args.image, expected_subject=args.expected_subject)
    approved, failures = SemanticVisualVerdictGate().evaluate(
        verdict,
        identity_required=False,
        geometry_alignment_required=args.require_sport_geometry_check,
        minimum_confidence=args.minimum_confidence,
    )
    layer = SemanticLayerEvidenceAdapter(minimum_confidence=args.minimum_confidence).adapt(
        verdict,
        require_exact_number_check=args.require_exact_number_check,
        require_sport_geometry_check=args.require_sport_geometry_check,
    )
    payload = {
        "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE",
        "verifier_id": verdict.verifier_id,
        "approved_non_identity": approved,
        "failures": list(failures),
        "layer_inspection_complete": layer.complete,
        "layer_inspection_blockers": list(layer.blockers),
        "layer_leakage": {
            "generated_text_detected": layer.evidence.generated_text_detected,
            "generated_platform_brand_detected": layer.evidence.generated_platform_brand_detected,
            "generated_exact_numbers_detected": layer.evidence.generated_exact_numbers_detected,
            "generated_entity_mark_detected": layer.evidence.generated_entity_mark_detected,
            "generated_unverified_identity_detected": layer.evidence.generated_unverified_identity_detected,
            "generated_sport_geometry_detected": layer.evidence.generated_sport_geometry_detected,
            "notes": list(layer.evidence.notes),
        },
        "checks": {
            "readable_text_absent": _check_payload(verdict.readable_text_absent),
            "platform_brand_absent": _check_payload(verdict.platform_brand_absent),
            "fake_entity_marks_absent": _check_payload(verdict.fake_entity_marks_absent),
            "exact_numbers_absent": _check_payload(verdict.exact_numbers_absent),
            "generated_sport_geometry_absent": _check_payload(verdict.generated_sport_geometry_absent),
            "single_scene": _check_payload(verdict.single_scene),
            "severe_defects_absent": _check_payload(verdict.severe_defects_absent),
            "subject_framing_valid": _check_payload(verdict.subject_framing_valid),
            "sport_geometry_alignment_valid": _check_payload(verdict.sport_geometry_alignment_valid),
        },
    }
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if approved and layer.complete else 2


if __name__ == "__main__":
    raise SystemExit(main())

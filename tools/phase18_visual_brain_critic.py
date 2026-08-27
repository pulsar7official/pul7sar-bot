#!/usr/bin/env python3
"""Apply the fail-closed Visual Brain critic contract to structured vision evidence.

The evidence may come from a local vision model or a human review adapter.  This
CLI never fabricates evidence and never upgrades a rejected image to publishable.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.visual_brain import VisualCriticEvidence, VisualCriticGate


def evaluate(payload: dict[str, object]) -> dict[str, object]:
    evidence = VisualCriticEvidence(
        concept_id=str(payload.get("concept_id") or ""),
        geometry_violation=bool(payload.get("geometry_violation", False)),
        pseudo_text_detected=bool(payload.get("pseudo_text_detected", False)),
        identity_violation=bool(payload.get("identity_violation", False)),
        factual_violation=bool(payload.get("factual_violation", False)),
        generation_defect=bool(payload.get("generation_defect", False)),
        editorial_specificity=float(payload.get("editorial_specificity", 0.0)),
        visual_impact=float(payload.get("visual_impact", 0.0)),
        composition_quality=float(payload.get("composition_quality", 0.0)),
        photographic_coherence=float(payload.get("photographic_coherence", 0.0)),
        concept_fidelity=float(payload.get("concept_fidelity", 0.0)),
        ordinary_stock_risk=float(payload.get("ordinary_stock_risk", 1.0)),
    )
    decision = VisualCriticGate().evaluate(evidence)
    return {
        "status": "VISUAL_CRITIC_ACCEPTED" if decision.accepted else "VISUAL_CRITIC_REJECTED",
        "concept_id": evidence.concept_id,
        "accepted": decision.accepted,
        "score": decision.score,
        "failures": list(decision.failures),
        "publication_ready": False,
        "note": "critic acceptance is necessary but not sufficient for publication; deterministic brand/editorial composition gates remain",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate PUL7SAR Visual Brain critic evidence")
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    payload = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    result = evaluate(payload)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

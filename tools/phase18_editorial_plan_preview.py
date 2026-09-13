#!/usr/bin/env python3
"""Preview the complete CPU-only editorial plan from a JSON story package.

Expected input contains `sport` and `candidates`; each candidate must carry
fact-locked fields required by `EditorialAngleCandidate`. This command is a safe
pre-GPU boundary for testing arbitrary sports-news scenarios.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.story_visual_editorial import EditorialEvent


def _candidate(raw: dict[str, object]) -> EditorialAngleCandidate:
    return EditorialAngleCandidate(
        angle_id=str(raw["angle_id"]),
        event=EditorialEvent(str(raw["event"])),
        story_core=str(raw["story_core"]),
        fact_phrase=str(raw["fact_phrase"]),
        primary_subject=str(raw["primary_subject"]),
        secondary_subjects=tuple(str(item) for item in raw.get("secondary_subjects", [])),
        editorial_importance=float(raw.get("editorial_importance", 1.0)),
        fact_confidence=float(raw.get("fact_confidence", 1.0)),
        identity_confidence=(None if raw.get("identity_confidence") is None else float(raw["identity_confidence"])),
        requires_exact_text=bool(raw.get("requires_exact_text", False)),
        requires_exact_geometry=bool(raw.get("requires_exact_geometry", False)),
        requires_unverified_identity=bool(raw.get("requires_unverified_identity", False)),
        requires_invented_scene=bool(raw.get("requires_invented_scene", False)),
        metadata=dict(raw.get("metadata", {})),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview PUL7SAR editorial + visual planning without GPU")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    candidates = tuple(_candidate(item) for item in raw.get("candidates", []))
    result = EditorialPlanningService().plan(
        sport=str(raw["sport"]),
        candidates=candidates,
        tone=HeadlineTone(str(raw.get("tone", "neutral"))),
        competition=raw.get("competition"),
        number=raw.get("number"),
        stakes=str(raw.get("stakes", "normal")),
        exact_assets=tuple(str(item) for item in raw.get("exact_assets", [])),
    )
    payload: dict[str, object] = {
        "status": result.status,
        "rejected_angle_ids": list(result.rejected_angle_ids),
        "publication_ready": False,
    }
    if result.selected_angle is not None:
        payload["selected_angle_id"] = result.selected_angle.candidate.angle_id
        payload["angle_score"] = result.selected_angle.combined_score
    if result.decision is not None:
        payload.update({
            "headline": result.decision.headline,
            "editorial_angle": result.decision.editorial_angle,
            "visual_anchor": result.decision.visual_anchor,
            "visual_family": result.decision.plan.visual_family.value,
            "production_mode": result.decision.plan.production_mode.value,
            "geometry_requirements": list(result.decision.sport_geometry_requirements),
            "high_risk_generated_elements": list(result.decision.high_risk_generated_elements),
            "fallback_reason": result.decision.fallback_reason,
        })
    if result.complexity is not None:
        payload["scene_complexity"] = {
            "surface_visibility": result.complexity.surface_visibility.value,
            "max_hero_subjects": result.complexity.max_hero_subjects,
            "background_strategy": result.complexity.background_strategy,
            "avoid_full_venue_generation": result.complexity.avoid_full_venue_generation,
            "rationale": result.complexity.rationale,
        }
    if result.layers is not None:
        payload["layers"] = [
            {"name": item.name, "source": item.source.value, "purpose": item.purpose, "required": item.required}
            for item in result.layers.layers
        ]
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

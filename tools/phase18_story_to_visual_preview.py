#!/usr/bin/env python3
"""CPU-only preview of PUL7SAR Story-to-Visual planning.

Accepts verified editorial slots and prints the exact headline/visual production
contract without loading an image model or using GPU time.
"""
from __future__ import annotations

import argparse
import json

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview PUL7SAR Story-to-Visual editorial planning")
    parser.add_argument("--event", required=True, choices=[item.value for item in EditorialEvent])
    parser.add_argument("--sport", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--fact", required=True)
    parser.add_argument("--story-core", required=True)
    parser.add_argument("--tone", default="neutral", choices=[item.value for item in HeadlineTone])
    parser.add_argument("--secondary", action="append", default=[])
    parser.add_argument("--competition")
    parser.add_argument("--number")
    parser.add_argument("--stakes", default="normal")
    parser.add_argument("--asset", action="append", default=[])
    parser.add_argument("--confidence", type=float, default=1.0)
    args = parser.parse_args()

    story = VerifiedEditorialStory(
        event=EditorialEvent(args.event),
        sport=args.sport,
        subject=args.subject,
        fact_phrase=args.fact,
        story_core=args.story_core,
        tone=HeadlineTone(args.tone),
        secondary_subjects=tuple(args.secondary),
        competition=args.competition,
        number=args.number,
        stakes=args.stakes,
        exact_assets=tuple(args.asset),
        confidence=args.confidence,
    )
    decision = StoryToVisualOrchestrator().decide(story)
    plan = decision.plan
    payload = {
        "status": "STORY_TO_VISUAL_PLAN_READY",
        "headline": decision.headline,
        "editorial_angle": decision.editorial_angle,
        "visual_anchor": decision.visual_anchor,
        "event": plan.event.value,
        "sport": plan.sport,
        "visual_family": plan.visual_family.value,
        "production_mode": plan.production_mode.value,
        "primary_subject": plan.primary_subject,
        "secondary_subjects": list(plan.secondary_subjects),
        "stakes": plan.stakes,
        "sentiment": plan.sentiment,
        "exact_assets": list(plan.exact_assets),
        "generated_elements": list(plan.generated_elements),
        "forbidden_generated_elements": list(plan.forbidden_generated_elements),
        "sport_geometry_requirements": list(decision.sport_geometry_requirements),
        "high_risk_generated_elements": list(decision.high_risk_generated_elements),
        "fallback_reason": decision.fallback_reason,
        "confidence": plan.confidence,
        "publication_ready": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

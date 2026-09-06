#!/usr/bin/env python3
"""Build a zero-cost, no-image audit matrix for Result Statement composition."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.platform_editorial_composition import PlatformEditorialCompositionResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


def _box(box) -> dict[str, float]:
    return {"x": box.x, "y": box.y, "width": box.width, "height": box.height}


def build(output: str) -> dict[str, object]:
    orchestrator = StoryToVisualOrchestrator()
    resolver = PlatformEditorialCompositionResolver()
    profiles = PlatformProfileRegistry()
    story = VerifiedEditorialStory(
        event=EditorialEvent.RESULT,
        sport="football",
        subject="Verified Winner",
        secondary_subjects=("Verified Opponent",),
        fact_phrase="verified final result",
        story_core="verified final result benchmark",
        tone=HeadlineTone.NEUTRAL,
        confidence=0.99,
    )
    decision = orchestrator.decide(story)
    platforms = []
    for platform in SocialPlatform:
        profile = profiles.get(platform)
        composition = resolver.resolve(decision, profile)
        result = composition.result_statement
        if result is None:
            raise RuntimeError("RESULT_COMPOSITION_MISSING")
        platforms.append({
            "platform": platform.value,
            "canvas": {"width": profile.width, "height": profile.height},
            "score_box": _box(result.score_box),
            "home_identity_box": _box(result.home_identity_box),
            "away_identity_box": _box(result.away_identity_box),
            "headline_box": _box(result.headline_box),
            "brand": {
                "zone": result.brand.zone.value,
                "center_x_ratio": result.brand.center_x_ratio,
                "center_y_ratio": result.brand.center_y_ratio,
                "max_width_ratio": result.brand.max_width_ratio,
                "max_height_ratio": result.brand.max_height_ratio,
                "contract": result.brand.contract,
            },
            "score_is_primary": result.score_is_primary,
            "club_identity_scale_equal": result.club_identity_scale_equal,
            "winner_emphasis_mode": result.winner_emphasis_mode,
            "loser_treatment": result.loser_treatment,
            "generated_score_allowed": result.generated_score_allowed,
            "generated_crest_allowed": result.generated_crest_allowed,
            "publication_ready": result.publication_ready,
        })

    manifest = {
        "manifest_version": "pul7sar-result-composition-matrix-v1",
        "benchmark_id": "result-statement-v1",
        "family": decision.sports_editorial_scene.family.value,
        "platform_count": len(platforms),
        "zero_cost": True,
        "network_used": False,
        "image_generator_used": False,
        "image_created": False,
        "inherits_transfer_layout": False,
        "publication_ready": False,
        "platforms": platforms,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/phase18_result_composition_matrix/manifest.json")
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the six-family x seven-platform Phase 18 composition audit matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.platform_editorial_composition import PlatformEditorialCompositionResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


CASES = (
    ("transfer-signature-v1", EditorialEvent.TRANSFER_CONFIRMED, "transfer_signature"),
    ("result-statement-v1", EditorialEvent.RESULT, "result_statement"),
    ("verified-subject-news-v1", EditorialEvent.INJURY, "verified_subject_news"),
    ("tactical-intelligence-v1", EditorialEvent.TACTICS, "tactical_board"),
    ("data-monument-v1", EditorialEvent.TABLE, "data_monument"),
    ("football-editorial-atmosphere-v1", EditorialEvent.GENERAL, "event_editorial"),
)


def _story(event: EditorialEvent) -> VerifiedEditorialStory:
    return VerifiedEditorialStory(
        event=event,
        sport="football",
        subject="Verified Subject",
        secondary_subjects=("Verified Secondary",),
        fact_phrase="verified fact",
        story_core="verified benchmark story core",
        tone=HeadlineTone.NEUTRAL,
        confidence=0.99,
    )


def _dedicated_contract(composition) -> str:
    for name in (
        "transfer_signature",
        "result_statement",
        "verified_subject_news",
        "tactical_intelligence",
        "data_monument",
        "event_editorial",
    ):
        item = getattr(composition, name)
        if item is not None:
            return item.contract
    raise RuntimeError("DEDICATED_COMPOSITION_MISSING")


def build(output: str) -> dict[str, object]:
    orchestrator = StoryToVisualOrchestrator()
    resolver = PlatformEditorialCompositionResolver()
    profiles = PlatformProfileRegistry()
    entries = []
    family_contracts: dict[str, str] = {}

    for benchmark_id, event, expected_family in CASES:
        decision = orchestrator.decide(_story(event))
        if decision.sports_editorial_scene.family.value != expected_family:
            raise RuntimeError(f"FAMILY_DRIFT:{benchmark_id}")
        for platform in SocialPlatform:
            profile = profiles.get(platform)
            composition = resolver.resolve(decision, profile)
            contract = _dedicated_contract(composition)
            previous = family_contracts.setdefault(expected_family, contract)
            if previous != contract:
                raise RuntimeError(f"FAMILY_CONTRACT_DRIFT:{expected_family}")
            entries.append({
                "benchmark_id": benchmark_id,
                "event": event.value,
                "family": expected_family,
                "platform": platform.value,
                "canvas": f"{profile.width}x{profile.height}",
                "composition_contract": contract,
                "platform_contract": composition.contract,
                "brand_contract": composition.brand.contract,
                "brand_zone": composition.brand.zone.value,
                "brand_max_width_ratio": composition.brand.max_width_ratio,
                "brand_max_height_ratio": composition.brand.max_height_ratio,
                "inherits_transfer_layout": composition.inherits_transfer_layout,
            })

    manifest = {
        "manifest_version": "pul7sar-story-family-composition-matrix-v1",
        "family_count": len(CASES),
        "platform_count": len(tuple(SocialPlatform)),
        "decision_count": len(entries),
        "expected_decision_count": len(CASES) * len(tuple(SocialPlatform)),
        "all_families_have_distinct_contracts": len(set(family_contracts.values())) == len(CASES),
        "inherits_transfer_layout_anywhere": any(e["inherits_transfer_layout"] for e in entries),
        "zero_cost": True,
        "network_used": False,
        "image_generator_used": False,
        "image_created": False,
        "publication_ready": False,
        "family_contracts": family_contracts,
        "entries": entries,
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/phase18_story_family_composition_matrix/manifest.json")
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

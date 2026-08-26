#!/usr/bin/env python3
"""Build the current PUL7SAR Golden Visual editorial base-scene handoff.

Golden v6 is story-first. A generic football PREVIEW may use stadium atmosphere,
light, crowd depth and a hint of turf, but it does not reserve or require a
playing-surface region. Exact football geometry remains available to stories
whose semantics require it; it is not a default football template.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json

from engine.intelligence.assets import AssetBundle
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.golden_prompt_budget import GoldenPromptBudget
from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContractCompiler
from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner, LayerSource
from engine.intelligence.layout_planner import DeterministicLayoutPlanner
from engine.intelligence.local_backend_execution import LocalBackendRequestCompiler
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.models import Sentiment
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.sports_editorial_scene import SportsEditorialSceneDirector
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine
from engine.intelligence.visual_concept_director import VisualConceptDirector, VisualConceptSignals
from engine.intelligence.visual_grammar import VisualGrammar
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


GOLDEN_BENCHMARK_ID = "golden-visual-season-opener-editorial-v6"
GOLDEN_MANIFEST_VERSION = "pul7sar-golden-batch-v6"
GOLDEN_SPORT_GEOMETRY = "contextual_optional_not_required"
GOLDEN_CAMERA_PRESET = "editorial_environmental_oblique"


def build_request(*, seed: int, request_id: str):
    platform = SocialPlatform.INSTAGRAM_FEED
    profile = PlatformProfileRegistry().get(platform)

    editorial = StoryVisualEditorialEngine().plan(
        event=EditorialEvent.PREVIEW,
        sport="football",
        story_core="verified general football season-opening anticipation",
        editorial_angle="the major domestic football season is returning",
        headline_short="The season returns",
        confidence=1.0,
    )
    sport_rule = SportVisualRuleRegistry().get("football")
    layer_plan = HybridVisualLayerPlanner().plan(editorial, sport_rule)
    surface_layer = layer_plan.by_name("sport_surface_geometry")
    if surface_layer.source is not LayerSource.OPTIONAL or surface_layer.required:
        raise RuntimeError("GOLDEN_V6_PREVIEW_SURFACE_POLICY_REGRESSED")

    # Current Phase 18 editorial API order is deliberate: the approved story plan
    # produces provider-agnostic visual grammar first; the scene family consumes
    # that grammar; only then can the visual-concept director select picture idea.
    visual_grammar = VisualGrammar().direct(editorial)
    if visual_grammar.surface_visibility.value != "context_only":
        raise RuntimeError("GOLDEN_V6_PREVIEW_VISUAL_GRAMMAR_REGRESSED")
    scene = SportsEditorialSceneDirector().direct(editorial.event, visual_grammar)

    layout = DeterministicLayoutPlanner().plan(
        platform=platform,
        sentiment=Sentiment.NEUTRAL,
        exact_score_required=False,
        dominant_entity=None,
    )

    visual_concept = VisualConceptDirector().direct(
        scene.family,
        VisualConceptSignals(
            verified_subject_asset=False,
            verified_context_photo=False,
            exact_club_assets=False,
            exact_tactical_data=False,
            exact_data_anchor=False,
            story_requires_person=False,
            story_requires_pitch=False,
            safe_generated_context=True,
        ),
    )
    base_contract = HybridBaseSceneContractCompiler().compile(layer_plan)

    assets = AssetBundle()
    specification = OriginalSceneSpecification(
        platform=platform.value,
        width=profile.width,
        height=profile.height,
        scene_description=(
            "premium football season-opening anticipation at dusk; one asymmetric editorial hierarchy built around a dominant atmospheric focal anchor, "
            "layered stadium architecture and crowd depth; oblique three-quarter environmental camera; turf only as subordinate context if present"
        ),
        factual_constraints=(
            "the story is a general season-opening preview, not a result or a specific match",
            "the scene must remain non-identifying and must not claim a specific real venue, club or person",
            "playing-surface geometry is not a story dependency for this preview and must not dominate the composition",
            "all platform branding and typography remain absent from AI generation",
        ),
        forbidden_visual_elements=(
            "no invented result",
            "no specific identifiable real venue",
            "no specific real-person depiction",
            "no collage or multi-panel layout",
            "no split-screen, grid, diptych, triptych or contact-sheet framing",
            "no image-within-image composition",
            "no full football pitch as the main visual subject",
            "no centered broadcast-style pitch composition",
            "no tactical diagram or prominent centre-circle/halfway-line geometry",
            "no generated branding, wordmarks, readable text, numerals or pseudo-text",
        ),
        metadata={
            "benchmark": GOLDEN_BENCHMARK_ID,
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": GOLDEN_SPORT_GEOMETRY,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": False,
            "football_camera_preset": GOLDEN_CAMERA_PRESET,
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "hybrid_surface_visibility": visual_grammar.surface_visibility.value,
            "visual_grammar_contract": visual_grammar.metadata["contract"],
            "visual_concept_contract": visual_concept.contract,
            "visual_concept_archetype": visual_concept.archetype.value,
            "visual_concept_selected_before_renderer": True,
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
            "visual_failures_addressed": (
                "full-pitch template dominance, central broadcast framing, geometry-first composition, collage composition, generic-template fallback, "
                "incorrect generated platform wordmark, and accidental implication of a specific real venue"
            ),
        },
    )
    package = GenerationPackageCompiler().compile(
        specification,
        assets,
        planned_layout=layout,
        base_scene_contract=base_contract,
        visual_grammar=visual_grammar,
        visual_concept=visual_concept,
    )

    # GenerationPackageCompiler is intentionally generic and does not propagate
    # arbitrary benchmark labels. Re-bind only the trusted Golden-v6 ownership
    # fields here, after generic compilation and before benchmark compaction.
    trusted_golden_metadata = {
        "benchmark": GOLDEN_BENCHMARK_ID,
        "composition_grammar": "single_continuous_scene",
        "sport_geometry": GOLDEN_SPORT_GEOMETRY,
        "generated_sport_geometry_allowed": False,
        "hybrid_surface_replacement_required": False,
        "football_camera_preset": GOLDEN_CAMERA_PRESET,
        "generated_branding_allowed": False,
        "brand_composition_policy": "dynamic_deterministic_after_generation",
        "visual_grammar_surface_visibility": visual_grammar.surface_visibility.value,
        "visual_priority": "story_focal_hierarchy_before_sport_surface",
        "visual_concept_selected_before_renderer": True,
    }
    package = replace(package, metadata={**package.metadata, **trusted_golden_metadata})
    package = GoldenPromptBudget().compact(package, benchmark_id=GOLDEN_BENCHMARK_ID)
    return LocalBackendRequestCompiler().compile_portable_handoff(
        package=package,
        model=FLUX2_KLEIN_4B_LOCAL,
        backend="diffusers",
        seed=seed,
        request_id=request_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden editorial v6 portable FLUX.2 handoff")
    parser.add_argument("--output", default="output/phase18_handoffs/golden-season-opener-editorial-v6.json")
    parser.add_argument("--seed", type=int, default=7007001)
    parser.add_argument("--request-id", default="golden-season-opener-editorial-v6-001")
    args = parser.parse_args()
    request = build_request(seed=args.seed, request_id=args.request_id)
    output = LocalGenerationHandoff.write(request, args.output)
    print(json.dumps({
        "status": "GOLDEN_EDITORIAL_HANDOFF_READY",
        "benchmark": GOLDEN_BENCHMARK_ID,
        "manifest_version": GOLDEN_MANIFEST_VERSION,
        "output": output,
        "model": request.model_id,
        "seed": request.seed,
        "canvas": f"{request.width}x{request.height}",
        "cost_mode": request.metadata["cost_mode"],
        "generated_sport_geometry_allowed": request.metadata.get("generated_sport_geometry_allowed"),
        "hybrid_surface_replacement_required": request.metadata.get("hybrid_surface_replacement_required"),
        "visual_grammar_surface_visibility": request.metadata.get("visual_grammar_surface_visibility"),
        "football_camera_preset": request.metadata.get("football_camera_preset"),
        "publication_ready": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

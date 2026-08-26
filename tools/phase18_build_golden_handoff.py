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

    visual_grammar = VisualGrammar().direct(editorial)
    if visual_grammar.surface_visibility.value != "context_only":
        raise RuntimeError("GOLDEN_V6_PREVIEW_VISUAL_GRAMMAR_REGRESSED")
    scene = SportsEditorialSceneDirector().direct(editorial.event, visual_grammar)

    # Instagram Feed portrait planning reserves the right-center for headline copy
    # and upper-left for the compact PUL7SAR brand. The generated focal anchor is
    # therefore deliberately placed lower-left/mid-left rather than centered.
    layout = DeterministicLayoutPlanner().plan(profile)

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

    # Golden Editorial v6 deliberately generates no exact brand/entity assets in
    # the base scene. AssetBundle requires an explicit tuple so that an empty
    # bundle is intentional rather than an implicit legacy default.
    assets = AssetBundle(assets=())
    safe_area = {
        "top": profile.safe_area.top,
        "right": profile.safe_area.right,
        "bottom": profile.safe_area.bottom,
        "left": profile.safe_area.left,
    }
    specification = OriginalSceneSpecification(
        platform=platform,
        width=profile.width,
        height=profile.height,
        aspect_ratio=profile.aspect_ratio,
        safe_area=safe_area,
        family=scene.family.value,
        concept=visual_concept.hero,
        subject=None,
        identity_reference=None,
        environment=(
            "premium football season-opening anticipation at dusk in a deliberately generic stadium; one illuminated players' tunnel mouth "
            "as the dominant environmental anchor, layered stand architecture and crowd depth receding diagonally, believable floodlights as "
            "secondary depth only, cinematic air, and optional subordinate turf context"
        ),
        composition=(
            "one asymmetric editorial hierarchy: dominant illuminated tunnel lower-left to mid-left, diagonal depth into the stands, quiet "
            "low-detail right-center reserved for later headline typography, restrained upper-left reserved for later brand placement; "
            "single continuous physical scene; no centered pitch-template dominance"
        ),
        camera_direction=(
            "oblique three-quarter environmental camera aimed across the tunnel/stand depth; explicitly not high-wide-central broadcast framing"
        ),
        emotional_mood="premium anticipatory global-football energy without invented outcome or identity claims",
        palette_strategy=None,
        required_assets=(),
        visual_copy=None,
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
            "profile_version": PlatformProfileRegistry.VERSION,
            "crop_strategy": profile.crop_strategy,
            "surface": profile.metadata.get("surface"),
            "benchmark": GOLDEN_BENCHMARK_ID,
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": GOLDEN_SPORT_GEOMETRY,
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": False,
            "football_camera_preset": GOLDEN_CAMERA_PRESET,
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
            "focal_anchor": "illuminated_tunnel_lower_left",
            "copy_negative_space": "right_center",
            "brand_quiet_zone": "upper_left",
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
        "focal_anchor": "illuminated_tunnel_lower_left",
        "copy_negative_space": "right_center",
        "brand_quiet_zone": "upper_left",
    }
    package = replace(package, metadata={**package.metadata, **trusted_golden_metadata})
    package = GoldenPromptBudget().compact(package, benchmark_id=GOLDEN_BENCHMARK_ID)
    return LocalBackendRequestCompiler().compile_portable_handoff(
        package=package,
        model=FLUX2_KLEIN_4B_LOCAL,
        backend=FLUX2_KLEIN_4B_LOCAL.runtime_adapter,
        seed=seed,
        request_id=request_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden editorial v6 GPU handoff")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=7007001)
    parser.add_argument("--request-id", default="golden-season-opener-editorial-v6-001")
    args = parser.parse_args()

    request = build_request(seed=args.seed, request_id=args.request_id)
    digest = LocalGenerationHandoff().write(request, args.output)
    print(json.dumps({
        "status": "GOLDEN_EDITORIAL_V6_HANDOFF_READY",
        "benchmark": GOLDEN_BENCHMARK_ID,
        "manifest_version": GOLDEN_MANIFEST_VERSION,
        "request_id": request.request_id,
        "provider": request.provider_id,
        "model": request.model_id,
        "cost_mode": request.metadata.get("cost_mode"),
        "visual_priority": request.metadata.get("visual_priority"),
        "visual_grammar_surface_visibility": request.metadata.get("visual_grammar_surface_visibility"),
        "hybrid_surface_replacement_required": request.metadata.get("hybrid_surface_replacement_required"),
        "focal_anchor": request.metadata.get("focal_anchor"),
        "copy_negative_space": request.metadata.get("copy_negative_space"),
        "brand_quiet_zone": request.metadata.get("brand_quiet_zone"),
        "seed": request.seed,
        "output": args.output,
        "payload_sha256": digest,
        "publication_ready": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

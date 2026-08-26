#!/usr/bin/env python3
"""Build the current PUL7SAR Golden Visual editorial base-scene handoff.

Golden v6 is story-first. A generic football PREVIEW may use stadium atmosphere,
light, crowd depth and a hint of turf, but it does not reserve or require a
playing-surface region. Exact football geometry remains available to stories
whose semantics require it; it is not a default football template.
"""
from __future__ import annotations

import argparse
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
GOLDEN_CAMERA_PRESET = "editorial_environmental_oblique"
GOLDEN_SPORT_GEOMETRY = "context_only_no_exact_surface_required"


def build_request(*, seed: int, request_id: str):
    platform = SocialPlatform.INSTAGRAM_FEED
    profile = PlatformProfileRegistry().get(platform)
    layout = DeterministicLayoutPlanner().plan(profile, entity_accent_hex="#E10600")

    editorial = StoryVisualEditorialEngine().plan(
        event=EditorialEvent.PREVIEW,
        sport="football",
        story_core="verified general football season-opening anticipation",
        editorial_angle="the major domestic football season is returning",
        headline_short="The season returns",
        confidence=1.0,
    )
    visual_grammar = VisualGrammar().direct(editorial)
    sports_scene = SportsEditorialSceneDirector().direct(EditorialEvent.PREVIEW, visual_grammar)
    visual_concept = VisualConceptDirector().direct(
        sports_scene.family,
        VisualConceptSignals(safe_generated_context=True),
    )
    sport_rule = SportVisualRuleRegistry().get("football")
    layers = HybridVisualLayerPlanner().plan(editorial, sport_rule)
    surface_layer = layers.by_name("sport_surface_geometry")
    if surface_layer.source is not LayerSource.OPTIONAL or surface_layer.required:
        raise RuntimeError("Golden v6 PREVIEW must not require deterministic football-surface geometry")
    base_contract = HybridBaseSceneContractCompiler().compile(layers)

    # Dynamic brand geometry/color remains a later deterministic layer.
    assets = AssetBundle(())
    specification = OriginalSceneSpecification(
        platform=platform,
        width=profile.width,
        height=profile.height,
        aspect_ratio=profile.aspect_ratio,
        safe_area={
            "top": profile.safe_area.top,
            "right": profile.safe_area.right,
            "bottom": profile.safe_area.bottom,
            "left": profile.safe_area.left,
        },
        family="general_world",
        concept=(
            "premium European football season-opening anticipation expressed through one cinematic editorial environment: "
            "stadium lights waking at dusk, layered architecture and supporter atmosphere creating expectation, with a clear visual focal anchor "
            "and no requirement to show the playing field"
        ),
        subject=None,
        identity_reference=None,
        environment=(
            "one photorealistic but deliberately non-identifying elite European football stadium world at dusk. Use coherent architecture, "
            "floodlight glow, deep stands, tunnel or concourse light, realistic supporter atmosphere and cinematic air. The scene must not imply a "
            "specific real venue, club, match or person. Turf may appear only as a minor contextual glimpse if it naturally improves depth; it is not "
            "a required surface and must never become the subject. Advertising boards, screens, banners and sponsor surfaces stay visually neutral "
            "with no readable words, numerals, logos or pseudo-text"
        ),
        composition=(
            "single full-bleed premium sports-magazine scene with an asymmetric editorial hierarchy. Use one dominant atmospheric focal anchor such as "
            "an illuminated tunnel opening, floodlight bank or luminous stand entrance, supported by foreground silhouettes/railings and layered crowd depth. "
            "Prefer an oblique three-quarter environmental view rather than a central stadium master shot. Preserve useful negative space for later headline "
            "and brand composition. If turf enters frame, keep it incidental and visually subordinate, roughly no more than the lower 15 percent of the image. "
            "Do not center the composition on a pitch, centre circle, halfway line or field diagram"
        ),
        camera_direction=(
            "cinematic environmental wide-to-medium-wide camera from an oblique concourse or lower/upper-stand viewpoint; natural perspective, stable horizon, "
            "strong foreground-to-background depth and purposeful asymmetry. No high-wide-central broadcast framing, no full-pitch master shot, no extreme "
            "fisheye and no artificial framing devices"
        ),
        emotional_mood=Sentiment.ANTICIPATORY.value,
        palette_strategy="premium dark dusk atmosphere, natural floodlight whites, subtle warm concourse glow and restrained contextual red accents",
        factual_constraints=(
            "the domestic football season is approaching rather than already decided",
            "the scene is general and must not imply a result, champion, transfer, specific real venue, club or real-person claim",
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
        "portable_handoff": request.metadata["portable_handoff"],
        "visual_grammar_surface_visibility": request.metadata["visual_grammar_surface_visibility"],
        "visual_concept_archetype": request.metadata["visual_concept_archetype"],
        "golden_prompt_contract": request.metadata["golden_prompt_contract"],
        "golden_scene_prompt_budget_chars": request.metadata["golden_scene_prompt_budget_chars"],
        "golden_scene_prompt_chars": request.metadata["golden_scene_prompt_chars"],
        "compiled_local_prompt_chars": len(request.prompt),
        "sport_geometry": GOLDEN_SPORT_GEOMETRY,
        "generated_sport_geometry_allowed": False,
        "hybrid_surface_replacement_required": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

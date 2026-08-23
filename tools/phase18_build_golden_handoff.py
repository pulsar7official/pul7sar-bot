#!/usr/bin/env python3
"""Build the current PUL7SAR Golden Visual hybrid base-scene handoff.

Golden v5 deliberately stops asking diffusion to draw exact football markings or
platform branding. The model owns stadium atmosphere and an unmarked reserved
surface plane; regulation pitch geometry is composited deterministically after
GPU generation.
"""
from __future__ import annotations

import argparse
import json

from engine.intelligence.assets import AssetBundle
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContractCompiler
from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.layout_planner import DeterministicLayoutPlanner
from engine.intelligence.local_backend_execution import LocalBackendRequestCompiler
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.models import Sentiment
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


GOLDEN_BENCHMARK_ID = "golden-visual-season-opener-hybrid-v5"


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
    sport_rule = SportVisualRuleRegistry().get("football")
    layers = HybridVisualLayerPlanner().plan(editorial, sport_rule)
    base_contract = HybridBaseSceneContractCompiler().compile(layers)

    # No fixed raster logo is required for base generation. Dynamic brand
    # geometry/color is a later deterministic layer.
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
            "premium European football season-opening anticipation inside one continuous elite stadium world, "
            "with the stadium atmosphere as the generative hero and a clean reserved pitch plane for later exact geometry"
        ),
        subject=None,
        identity_reference=None,
        environment=(
            "one photorealistic elite European football stadium at dusk, coherent architecture, floodlights, realistic supporter atmosphere, "
            "deep stands and cinematic air. A broad grass-colored playing-surface plane may occupy the lower-middle frame but it must remain plain, "
            "unmarked and visually simple because deterministic code will replace that entire region with regulation pitch geometry after generation. "
            "Advertising boards, screens, banners and sponsor surfaces must be visually neutral with no readable words, numerals, logos or pseudo-text"
        ),
        composition=(
            "single full-bleed cinematic magazine-cover composition from a high wide central lower-stand/endline-oriented camera. Preserve a clear "
            "symmetrical trapezoidal surface region extending from the lower foreground toward the middle distance, suitable for deterministic projective "
            "pitch replacement. Keep one coherent vanishing direction, strong foreground-to-background depth and clean overlay space. Do not paint any "
            "football markings into the reserved surface plane"
        ),
        camera_direction=(
            "high wide central stadium camera with the long axis of the reserved playing surface receding into depth; no extreme fisheye, no tilted horizon, "
            "no low touchline distortion and no artificial framing devices"
        ),
        emotional_mood=Sentiment.ANTICIPATORY.value,
        palette_strategy="premium dark stadium atmosphere, natural floodlight whites and restrained contextual red accents outside the reserved surface plane",
        factual_constraints=(
            "the domestic football season is approaching rather than already decided",
            "the scene is general and must not imply a result, champion, transfer or specific real-person claim",
            "exact football geometry is not generated and will be applied deterministically after generation",
            "all platform branding and typography remain absent from AI generation",
        ),
        forbidden_visual_elements=(
            "no invented result",
            "no collage or multi-panel layout",
            "no split-screen, grid, diptych, triptych or contact-sheet framing",
            "no image-within-image composition",
            "no football pitch markings in the reserved surface plane",
            "no centre circle, halfway line, penalty boxes, goal-area markings or painted touchlines",
            "no generated branding, wordmarks, readable text, numerals or pseudo-text",
        ),
        metadata={
            "benchmark": GOLDEN_BENCHMARK_ID,
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": "deterministic_football_pitch_projective_v1",
            "generated_sport_geometry_allowed": False,
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": "high_wide_central",
            "visual_failures_addressed": (
                "collage composition, malformed generated pitch proportions/markings, and incorrect generated platform wordmark"
            ),
        },
    )
    package = GenerationPackageCompiler().compile(
        specification,
        assets,
        planned_layout=layout,
        base_scene_contract=base_contract,
    )
    return LocalBackendRequestCompiler().compile_portable_handoff(
        package=package,
        model=FLUX2_KLEIN_4B_LOCAL,
        backend="diffusers",
        seed=seed,
        request_id=request_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden Hybrid v5 portable FLUX.2 handoff")
    parser.add_argument("--output", default="output/phase18_handoffs/golden-season-opener-hybrid-v5.json")
    parser.add_argument("--seed", type=int, default=7007001)
    parser.add_argument("--request-id", default="golden-season-opener-hybrid-v5-001")
    args = parser.parse_args()
    request = build_request(seed=args.seed, request_id=args.request_id)
    output = LocalGenerationHandoff.write(request, args.output)
    print(json.dumps({
        "status": "GOLDEN_HYBRID_HANDOFF_READY",
        "benchmark": GOLDEN_BENCHMARK_ID,
        "output": output,
        "model": request.model_id,
        "seed": request.seed,
        "canvas": f"{request.width}x{request.height}",
        "cost_mode": request.metadata["cost_mode"],
        "portable_handoff": request.metadata["portable_handoff"],
        "generated_sport_geometry_allowed": False,
        "hybrid_surface_replacement_required": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build the first portable PUL7SAR Golden Visual generation handoff.

This is a deterministic non-person identity benchmark for the first real GPU
proof. It exercises the actual platform/layout/generation package path and writes
no image; the resulting JSON is later executed by `phase18_flux2_execute.py` on
a compatible $0-local GPU runtime.
"""

from __future__ import annotations

import argparse
import json

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.layout_planner import DeterministicLayoutPlanner
from engine.intelligence.local_backend_execution import LocalBackendRequestCompiler
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.models import Sentiment
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


GOLDEN_BENCHMARK_ID = "golden-visual-general-season-opener-v4"


def build_request(*, seed: int, request_id: str):
    platform = SocialPlatform.INSTAGRAM_FEED
    profile = PlatformProfileRegistry().get(platform)
    layout = DeterministicLayoutPlanner().plan(profile, entity_accent_hex="#E10600")
    assets = AssetBundle((
        AssetReference("pul7sar-wordmark", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
        AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
    ))
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
            "European football season opener expressed as one unified premium editorial stadium world: "
            "the feeling of the major leagues returning, captured in a single continuous scene with one dominant visual hierarchy"
        ),
        subject=None,
        identity_reference=None,
        environment=(
            "one photorealistic elite European association-football stadium at dusk with continuous architecture, floodlights, realistic "
            "supporter atmosphere and one regulation football pitch. The playing surface must be structurally authentic: straight touchlines "
            "and goal lines, exactly one halfway line, exactly one centre circle centered on that halfway line, one centre mark, two aligned penalty "
            "areas, two aligned goal areas, two goals on the goal lines, physically plausible corner arcs, and all white markings obeying the same "
            "camera perspective. Advertising boards, screens, banners and sponsor surfaces must remain neutral and unbranded with no readable words, "
            "logos or pseudo-text. Evoke England, Spain, Italy, Germany and France only through harmonized environmental mood, crowd energy, lighting "
            "nuance and football culture inside the same physical stadium world, never as separate league zones, pictures, or repeated player frames"
        ),
        composition=(
            "single full-bleed cinematic magazine-cover composition with one uninterrupted camera view, one coherent vanishing point, strong "
            "foreground-to-background depth, one main focal axis across the pitch and elegant negative space for later exact PUL7SAR headline and "
            "branding in deterministic post-composition; the generated base scene itself must contain no PUL7SAR wordmark, no number-7 logo treatment, "
            "no pulse mark, no platform name and no generated lettering. The entire canvas must read instantly as one photograph-like editorial artwork. "
            "The pitch itself must read immediately as one physically correct regulation association-football field rather than an approximate or decorative field graphic"
        ),
        camera_direction=(
            "premium wide-to-medium sports editorial lens from a low touchline or lower-stand perspective, realistic stadium depth, controlled "
            "highlights, subtle atmospheric separation, perspective-correct field geometry and no artificial framing devices"
        ),
        emotional_mood=Sentiment.ANTICIPATORY.value,
        palette_strategy="PUL7SAR premium red accent with natural stadium blacks, graphite, grass and floodlight whites",
        factual_constraints=(
            "the European domestic league season is approaching rather than already decided",
            "the scene is general and must not imply a result, champion, transfer, or specific real-person claim",
            "the visible playing surface must be a physically plausible regulation association-football pitch",
            "all exact PUL7SAR branding must be absent from AI generation and added later by deterministic composition",
        ),
        forbidden_visual_elements=(
            "no invented result",
            "no collage or multi-panel layout",
            "no split-screen, grid, diptych, triptych, or contact-sheet framing",
            "no image-within-image composition",
            "no malformed football pitch geometry",
            "no duplicate, missing, warped, or invented field markings",
            "no generated branding, wordmarks, readable text, or pseudo-text",
        ),
        metadata={
            "benchmark": GOLDEN_BENCHMARK_ID,
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": "association_football_regulation_pitch",
            "generated_branding_allowed": False,
            "brand_composition_policy": "exact_assets_only_after_generation",
            "visual_failure_addressed": (
                "first proof produced a four-panel collage; second proof produced malformed football pitch markings and an incorrect generated PUL7SAR wordmark"
            ),
        },
    )
    package = GenerationPackageCompiler().compile(specification, assets, planned_layout=layout)
    return LocalBackendRequestCompiler().compile_portable_handoff(
        package=package,
        model=FLUX2_KLEIN_4B_LOCAL,
        backend="diffusers",
        seed=seed,
        request_id=request_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden Visual #0 portable FLUX.2 handoff")
    parser.add_argument("--output", default="output/phase18_handoffs/golden-general-season-opener.json")
    parser.add_argument("--seed", type=int, default=7007001)
    parser.add_argument("--request-id", default="golden-general-season-opener-v4-001")
    args = parser.parse_args()
    request = build_request(seed=args.seed, request_id=args.request_id)
    output = LocalGenerationHandoff.write(request, args.output)
    print(json.dumps({
        "status": "GOLDEN_HANDOFF_READY",
        "benchmark": GOLDEN_BENCHMARK_ID,
        "output": output,
        "model": request.model_id,
        "seed": request.seed,
        "canvas": f"{request.width}x{request.height}",
        "cost_mode": request.metadata["cost_mode"],
        "portable_handoff": request.metadata["portable_handoff"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

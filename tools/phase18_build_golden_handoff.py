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


GOLDEN_BENCHMARK_ID = "golden-visual-general-season-opener-v2"


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
            "one photorealistic elite European football stadium at dusk with continuous architecture, continuous pitch geometry, "
            "floodlights, realistic supporter atmosphere and subtle tactical markings; evoke the breadth of England, Spain, Italy, "
            "Germany and France only through harmonized environmental mood, crowd energy, lighting nuance and football culture inside "
            "the same physical stadium world, never as separate league zones, separate pictures, or repeated player frames"
        ),
        composition=(
            "single full-bleed cinematic magazine-cover composition with one uninterrupted camera view, one coherent vanishing point, "
            "strong foreground-to-background depth, one main focal axis across the pitch and elegant negative space for later PUL7SAR "
            "headline and branding; the entire canvas must read instantly as one photograph-like editorial artwork"
        ),
        camera_direction=(
            "premium wide-to-medium sports editorial lens from a low touchline perspective, realistic stadium depth, controlled highlights, "
            "subtle atmospheric separation and no artificial framing devices"
        ),
        emotional_mood=Sentiment.ANTICIPATORY.value,
        palette_strategy="PUL7SAR premium red accent with natural stadium blacks, graphite, grass and floodlight whites",
        factual_constraints=(
            "the European domestic league season is approaching rather than already decided",
            "the scene is general and must not imply a result, champion, transfer, or specific real-person claim",
        ),
        forbidden_visual_elements=(
            "no invented result",
            "no collage or multi-panel layout",
            "no split-screen, grid, diptych, triptych, or contact-sheet framing",
            "no image-within-image composition",
        ),
        metadata={
            "benchmark": GOLDEN_BENCHMARK_ID,
            "composition_grammar": "single_continuous_scene",
            "visual_failure_addressed": "first proof produced a four-panel football collage",
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
    parser.add_argument("--request-id", default="golden-general-season-opener-v2-001")
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

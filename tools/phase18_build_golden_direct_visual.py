#!/usr/bin/env python3
"""Build a genuine CPU-only Golden Direct Visual candidate for human review.

This is an engineering visual proof, not publication-ready news. It exercises the
real generator-bypass path and binds output to exact PNG bytes and repo asset
checksums. Repository brand rasters are screened before use; opaque-background
assets are recorded as rejected rather than silently composited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.direct_visual_execution import DirectVisualExecutionPlanner
from engine.intelligence.direct_visual_layout import DirectDataLayoutPlanner
from engine.intelligence.direct_visual_quality import DirectRenderQualityGate
from engine.intelligence.direct_visual_renderer import DirectVisualRenderer, RenderAsset
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


BENCHMARK_ID = "golden-direct-visual-data-v1"
BRAND_CANDIDATES = ("logo.png", "pulsar7.PNG")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _transparent_brand_asset(path: Path) -> bool:
    with Image.open(path) as image:
        if image.mode not in {"RGBA", "LA"} and "transparency" not in image.info:
            return False
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        lo, _hi = alpha.getextrema()
        return lo < 255


def build(output_dir: str) -> dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    layout = DirectDataLayoutPlanner().plan(profile, accent_hex="#E10600")
    story = VerifiedEditorialStory(
        event=EditorialEvent.TABLE,
        sport="football",
        subject="PUL7SAR",
        fact_phrase="VISUAL INTELLIGENCE SYSTEM",
        story_core="verified non-news engineering benchmark for deterministic data composition",
        tone=HeadlineTone.NEUTRAL,
        confidence=1.0,
    )
    decision = StoryToVisualOrchestrator().decide(story)
    if decision.execution_route.generator_required:
        raise RuntimeError("Golden Direct Visual benchmark unexpectedly requires a generator")

    renderer = DirectVisualRenderer()
    planner = DirectVisualExecutionPlanner()
    gate = DirectRenderQualityGate()
    accepted: list[dict[str, object]] = []
    rejected_assets: list[dict[str, object]] = []
    system_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_path = system_font if Path(system_font).is_file() else None

    for asset_name in BRAND_CANDIDATES:
        asset_path = Path(asset_name)
        if not asset_path.is_file():
            raise FileNotFoundError(asset_path)
        if not _transparent_brand_asset(asset_path):
            rejected_assets.append({
                "brand_asset": asset_name,
                "brand_sha256": _sha(asset_path),
                "reason": "opaque_background_not_allowed_for_direct_brand_composition",
            })
            continue

        asset_id = "repo-brand-golden-direct"
        assets = AssetBundle((
            AssetReference(
                asset_id=asset_id,
                role=AssetRole.PUL7SAR_LOGO,
                treatment=AssetTreatment.EXACT,
                source_reference=asset_name,
                metadata={"sha256": _sha(asset_path), "engineering_candidate_only": True},
            ),
        ))
        plan = planner.compile(
            decision.execution_route,
            layout,
            assets,
            headline="VISUAL INTELLIGENCE SYSTEM",
            exact_data=(
                "STORY INTELLIGENCE",
                "VERIFIED DATA OWNERSHIP",
                "DIRECT CPU RENDER",
                "SHA-LOCKED OUTPUT",
            ),
        )
        render_asset = RenderAsset(asset_id, str(asset_path), _sha(asset_path))
        output_path = out / "candidate-01-golden-direct.png"
        receipt = renderer.render(
            plan,
            layout,
            output_path=str(output_path),
            assets={asset_id: render_asset},
            font_path=font_path,
        )
        quality = gate.evaluate(plan, layout, receipt)
        if not quality.allowed:
            raise RuntimeError("Golden Direct Visual quality gate failed: " + "; ".join(quality.failures))
        accepted.append({
            "candidate": 1,
            "brand_asset": asset_name,
            "brand_sha256": _sha(asset_path),
            "png": output_path.name,
            "png_sha256": receipt.sha256,
            "width": receipt.width,
            "height": receipt.height,
            "layout_strategy": layout.strategy,
            "route": receipt.route,
            "base_source": receipt.base_source,
            "generator_used": False,
            "provider_used": False,
            "gpu_used": False,
            "publication_ready": False,
            "review_required": True,
        })
        break

    if len(accepted) != 1:
        raise RuntimeError("no transparent repository brand asset is eligible for Golden Direct Visual")

    manifest = {
        "manifest_version": "pul7sar-golden-direct-visual-v1",
        "benchmark": BENCHMARK_ID,
        "purpose": "human visual review of genuine deterministic CPU-rendered candidate",
        "cost_mode": "$0-local",
        "publication_ready": False,
        "candidate_count": 1,
        "candidates": accepted,
        "rejected_brand_assets": rejected_assets,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden Direct Visual candidate")
    parser.add_argument("--output-dir", default="output/phase18_visual_proof/golden-direct-v1")
    args = parser.parse_args()
    manifest = build(args.output_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

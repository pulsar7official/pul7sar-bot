#!/usr/bin/env python3
"""Build genuine CPU-only Golden Direct Visual candidates for human review.

These are engineering visual proofs, not publication-ready news. They exercise the
real generator-bypass path and bind every output to exact PNG bytes and repo asset
checksums. Two existing repository brand files are rendered as separate candidates
so visual review can decide which asset, if either, matches the approved identity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

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
    candidates: list[dict[str, object]] = []
    system_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_path = system_font if Path(system_font).is_file() else None

    for index, asset_name in enumerate(BRAND_CANDIDATES, start=1):
        asset_path = Path(asset_name)
        if not asset_path.is_file():
            raise FileNotFoundError(asset_path)
        asset_id = f"repo-brand-candidate-{index}"
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
            headline=decision.headline,
            exact_data=(
                "STORY INTELLIGENCE",
                "VERIFIED DATA OWNERSHIP",
                "DIRECT CPU RENDER",
                "SHA-LOCKED OUTPUT",
            ),
        )
        render_asset = RenderAsset(asset_id, str(asset_path), _sha(asset_path))
        output_path = out / f"candidate-{index:02d}-{asset_path.stem.lower()}.png"
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
        candidates.append({
            "candidate": index,
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

    manifest = {
        "manifest_version": "pul7sar-golden-direct-visual-v1",
        "benchmark": BENCHMARK_ID,
        "purpose": "human visual review of genuine deterministic CPU-rendered candidates",
        "cost_mode": "$0-local",
        "publication_ready": False,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden Direct Visual candidates")
    parser.add_argument("--output-dir", default="output/phase18_visual_proof/golden-direct-v1")
    args = parser.parse_args()
    manifest = build(args.output_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

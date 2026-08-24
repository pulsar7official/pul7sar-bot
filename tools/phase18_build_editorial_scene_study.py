#!/usr/bin/env python3
"""Build PUL7SAR transfer composition study v5 for human visual review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_reference_scene_study_renderer import EditorialReferenceSceneStudyRenderer
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_study_handoff import VisualStudyHandoffCompiler


def build(output_dir: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if not font.is_file():
        font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not font.is_file():
        raise FileNotFoundError("required CI study font unavailable")

    decision = StoryToVisualOrchestrator().decide(VerifiedEditorialStory(
        event=EditorialEvent.TRANSFER_CONFIRMED,
        sport="football",
        subject="Benchmark Player",
        fact_phrase="joins destination club",
        story_core="fictional Phase 18 transfer composition benchmark",
        tone=HeadlineTone.NEUTRAL,
        confidence=1.0,
    ))
    handoff = VisualStudyHandoffCompiler().compile(
        decision,
        headline="صفقة جديدة",
        supporting_copy="وجه جديد يصل إلى النادي",
    )
    VisualStudyHandoffCompiler.verify(handoff)

    output = root / "pul7sar-transfer-study-v5-reference-brand.png"
    receipt = EditorialReferenceSceneStudyRenderer().render(
        handoff, output_path=str(output), accent_hex="#034694", font_path=str(font), seed=7007,
    )
    manifest = {
        "manifest_version": "pul7sar-editorial-scene-study-v5-reference-brand",
        "renderer_contract": receipt.contract,
        "benchmark_id": "transfer-signature-v1",
        "png": output.name,
        "png_sha256": receipt.output_sha256,
        "handoff_sha256": receipt.handoff_sha256,
        "accent_hex": receipt.accent_hex,
        "width": receipt.width,
        "height": receipt.height,
        "generator_used_for_scene": receipt.generator_used_for_scene,
        "verified_player_asset_used": receipt.verified_player_asset_used,
        "subject_placeholder_used": receipt.subject_placeholder_used,
        "subject_placeholder_is_identity_evidence": False,
        "arabic_raqm_used": receipt.arabic_raqm_used,
        "study_only": receipt.study_only,
        "publication_ready": receipt.publication_ready,
        "brand_geometry_mode": "embedded-reference-derived-layered-master-v1",
        "brand_source_mode": receipt.brand_source_mode,
        "embedded_bundle_sha256": receipt.embedded_bundle_sha256,
        "approximate_brand_zone_removed": receipt.approximate_brand_zone_removed,
        "identity_shelf_used": receipt.identity_shelf_used,
        "exact_reference_shape_used": receipt.exact_reference_shape_used,
        "transparent_reference_layers_used": receipt.transparent_reference_layers_used,
        "final_brand_font_recreation_used": receipt.final_brand_font_recreation_used,
        "final_brand_generic_ecg_recreation_used": receipt.final_brand_generic_ecg_recreation_used,
        "final_brand_generator_used": receipt.final_brand_generator_used,
        "final_brand_network_used": receipt.final_brand_network_used,
        "metallic_wordmark_fixed": True,
        "seven_and_pulse_tintable": True,
        "football_fixed": True,
        "exact_publication_master_still_requires_owner_approval": True,
        "verified_subject_asset_still_required_for_real_transfer_publication": True,
        "human_visual_review_required": True,
    }
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/phase18_editorial_scene_study")
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

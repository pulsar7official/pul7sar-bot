#!/usr/bin/env python3
"""Build the first story-aware deterministic PUL7SAR editorial visual study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_scene_study_renderer import EditorialSceneStudyRenderer
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
        event=EditorialEvent.GENERAL,
        sport="football",
        subject="Football Editorial Study",
        fact_phrase="non-publication visual study",
        story_core="Phase 18 general football editorial atmosphere benchmark",
        tone=HeadlineTone.NEUTRAL,
        confidence=1.0,
    ))
    handoff = VisualStudyHandoffCompiler().compile(
        decision,
        headline="نبض كرة القدم يبدأ هنا",
    )
    VisualStudyHandoffCompiler.verify(handoff)

    output = root / "pul7sar-editorial-study-v1.png"
    receipt = EditorialSceneStudyRenderer().render(
        handoff,
        output_path=str(output),
        accent_hex="#034694",
        font_path=str(font),
        seed=7007,
    )
    manifest = {
        "manifest_version": "pul7sar-editorial-scene-study-v1",
        "png": output.name,
        "png_sha256": receipt.output_sha256,
        "handoff_sha256": receipt.handoff_sha256,
        "accent_hex": receipt.accent_hex,
        "width": receipt.width,
        "height": receipt.height,
        "generator_used": receipt.generator_used,
        "legacy_logo_used": receipt.legacy_logo_used,
        "study_only": receipt.study_only,
        "publication_ready": receipt.publication_ready,
        "brand_geometry_mode": "approximate-study-only",
        "exact_brand_master_still_required_for_publication": True,
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

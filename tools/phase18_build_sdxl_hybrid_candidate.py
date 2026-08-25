"""Build a 1080x1350 hybrid family candidate from an SDXL atmosphere image.

Benchmark facts are intentionally explicit and synthetic/non-news-specific. They
exercise exact composition only. Base-scene semantic cleanliness is deliberately
left unverified until a separate visual gate inspects the generated pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.hybrid_family_compositor import HybridEditorialFacts, HybridFamilyCompositor
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


FACTS = {
    EditorialSceneFamily.RESULT_STATEMENT: HybridEditorialFacts(
        EditorialSceneFamily.RESULT_STATEMENT, "MATCH RESULT",
        home_name="NORTH CITY", away_name="SOUTH UNITED", home_score=3, away_score=1,
        accent_hex="#E10600",
    ),
    EditorialSceneFamily.TRANSFER_SIGNATURE: HybridEditorialFacts(
        EditorialSceneFamily.TRANSFER_SIGNATURE, "NEW DESTINATION",
        primary="NORTH CITY", secondary="TRANSFER UPDATE", accent_hex="#E10600",
    ),
    EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: HybridEditorialFacts(
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "TEAM UPDATE",
        primary="VERIFIED SUBJECT LAYER RESERVED", accent_hex="#E10600",
    ),
    EditorialSceneFamily.DATA_MONUMENT: HybridEditorialFacts(
        EditorialSceneFamily.DATA_MONUMENT, "SEASON RECORD",
        primary="27", secondary="MATCHES UNBEATEN", tertiary="EXACT DATA LAYER", accent_hex="#E10600",
    ),
    EditorialSceneFamily.EVENT_EDITORIAL: HybridEditorialFacts(
        EditorialSceneFamily.EVENT_EDITORIAL, "MATCHDAY",
        primary="NORTH CITY vs SOUTH UNITED", secondary="28 AUG · 20:00", accent_hex="#E10600",
    ),
}


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True, choices=[f.value for f in FACTS])
    p.add_argument("--base", required=True)
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def main():
    q = parse()
    family = EditorialSceneFamily(q.family)
    out = Path(q.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"{family.value}-hybrid.png"
    receipt = HybridFamilyCompositor().compose(
        base_path=q.base,
        output_path=str(target),
        facts=FACTS[family],
        repository_root=Path(__file__).resolve().parents[1],
    )
    (out / "hybrid-manifest.json").write_text(json.dumps({
        "contract": receipt.contract,
        "family": receipt.family,
        "png": target.name,
        "png_sha256": receipt.output_sha256,
        "exact_brand_used": receipt.exact_brand_used,
        "deterministic_facts_used": receipt.deterministic_facts_used,
        "fabricated_crest_used": receipt.fabricated_crest_used,
        "placeholder_used": receipt.placeholder_used,
        "compositor_generated_text_used": receipt.compositor_generated_text_used,
        "source_photo_used": receipt.source_photo_used,
        "base_scene_semantic_verified": receipt.base_scene_semantic_verified,
        "base_scene_text_absence_verified": receipt.base_scene_text_absence_verified,
        "base_scene_identity_absence_verified": receipt.base_scene_identity_absence_verified,
        "base_scene_geometry_absence_verified": receipt.base_scene_geometry_absence_verified,
        "semantic_gate_required_before_publication": True,
        "publication_ready": receipt.publication_ready,
        "base_role": "original_generated_atmosphere_only",
        "study_only": True,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

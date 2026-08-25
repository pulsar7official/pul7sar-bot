from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.generated_base_provenance import GeneratedBaseProvenance
from engine.intelligence.hybrid_final_composer import HybridFinalComposer
from engine.intelligence.hybrid_pixel_composer import HybridPixelComposer, HybridPixelRequest
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--base-manifest", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--seed", type=int, default=21801)
    return p.parse_args()


def main():
    q = parse()
    family = EditorialSceneFamily.RESULT_STATEMENT
    provenance = GeneratedBaseProvenance.from_manifest(
        manifest_path=q.base_manifest,
        family=family,
        image_path=q.base,
    )
    plan = HybridFinalComposer.compile(
        family=family,
        story_key="phase18-hybrid-result-study-3-1",
        recent_archetypes=("score_monument",),
        seed=q.seed,
    )
    receipt = HybridPixelComposer().compose(HybridPixelRequest(
        plan=plan,
        generated_base_path=q.base,
        output_path=q.output,
        headline="FULL TIME",
        primary_label="NORTH CITY",
        secondary_label="SOUTH UNITED",
        primary_value="3-1",
        generated_base_provenance=provenance,
    ))
    payload = {
        "contract": "pul7sar-hybrid-result-pixel-study-v2-provenance",
        "family": plan.family.value,
        "archetype_id": plan.archetype_id,
        "generated_base": q.base,
        "generated_base_manifest": q.base_manifest,
        "synthesis_contract": provenance.synthesis_contract,
        "sport_lock": provenance.sport_lock,
        "prompt_token_count": provenance.prompt_token_count,
        "prompt_usable_limit": provenance.prompt_usable_limit,
        "output": receipt.output_path,
        "output_sha256": receipt.output_sha256,
        "generated_base_used": receipt.generated_base_used,
        "provenance_verified": receipt.provenance_verified,
        "brand_applied": receipt.brand_applied,
        "verified_assets_applied": list(receipt.verified_assets_applied),
        "fabricated_crest_used": False,
        "publication_ready": False,
        "human_visual_review_required": True,
    }
    m = Path(q.manifest); m.parent.mkdir(parents=True, exist_ok=True)
    m.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

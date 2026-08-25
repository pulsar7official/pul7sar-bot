from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.hybrid_final_composer import HybridFinalComposer
from engine.intelligence.hybrid_pixel_composer import HybridPixelComposer, HybridPixelRequest
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--seed", type=int, default=21801)
    return p.parse_args()


def main():
    q = parse()
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.RESULT_STATEMENT,
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
        generated_base_verified_unbranded=True,
        generated_base_verified_no_readable_facts=True,
    ))
    payload = {
        "contract": "pul7sar-hybrid-result-pixel-study-v1",
        "family": plan.family.value,
        "archetype_id": plan.archetype_id,
        "generated_base": q.base,
        "output": receipt.output_path,
        "output_sha256": receipt.output_sha256,
        "generated_base_used": receipt.generated_base_used,
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

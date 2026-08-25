from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.generated_base_provenance import GeneratedBaseProvenance
from engine.intelligence.hybrid_final_composer import HybridFinalComposer
from engine.intelligence.hybrid_pixel_composer import HybridPixelComposer, HybridPixelRequest
from engine.intelligence.result_spatial_monument import SpatialResultMonument, SpatialResultSpec
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_candidate_quality_gate import VisualCandidateQualityGate
from tools.phase18_compose_result_candidate_board import _result_candidates


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--seed-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--headline", default="FULL TIME")
    p.add_argument("--home", default="NORTH CITY")
    p.add_argument("--away", default="SOUTH UNITED")
    p.add_argument("--score", default="3-1")
    return p.parse_args()


def main():
    q = parse()
    seed_dir = Path(q.seed_dir)
    out = Path(q.output_dir); out.mkdir(parents=True, exist_ok=True)
    manifest_path = seed_dir / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = _result_candidates(payload)
    family = EditorialSceneFamily.RESULT_STATEMENT
    plan = HybridFinalComposer.compile(
        family=family,
        story_key="phase18-result-architecture-comparison",
        recent_archetypes=("score_monument",),
        seed=22817,
    )

    rows = []
    images = []
    for item in candidates:
        seed = int(item["seed"])
        base = seed_dir / item["file"]
        provenance = GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest_path), family=family, image_path=str(base)
        )

        flat = out / f"result_flat_seed_{seed}.jpg"
        receipt = HybridPixelComposer().compose(HybridPixelRequest(
            plan=plan,
            generated_base_path=str(base),
            output_path=str(flat),
            headline=q.headline,
            primary_label=q.home,
            secondary_label=q.away,
            primary_value=q.score,
            generated_base_provenance=provenance,
        ))
        spatial = out / f"result_spatial_seed_{seed}.jpg"
        SpatialResultMonument.compose(
            str(base), str(spatial),
            SpatialResultSpec(headline=q.headline, home=q.home, away=q.away, score=q.score),
        )
        flat_q = VisualCandidateQualityGate.inspect(str(flat))
        spatial_q = VisualCandidateQualityGate.inspect(str(spatial))
        rows.append({
            "seed": seed,
            "provenance_verified": receipt.provenance_verified,
            "flat": {"file": flat.name, "pixel_health": flat_q.passed, "entropy": flat_q.entropy},
            "spatial": {"file": spatial.name, "pixel_health": spatial_q.passed, "entropy": spatial_q.entropy},
        })
        images.append((seed, "flat", Image.open(flat).convert("RGB")))
        images.append((seed, "spatial", Image.open(spatial).convert("RGB")))

    if not any(r["spatial"]["pixel_health"] for r in rows):
        raise ValueError("ALL_SPATIAL_RESULT_CANDIDATES_FAILED_PIXEL_HEALTH")

    w, h = images[0][2].size
    sheet = Image.new("RGB", (w * 2, h * len(candidates)), (8, 8, 8))
    font = ImageFont.load_default()
    for row_idx, item in enumerate(candidates):
        seed = int(item["seed"])
        pair = [x for x in images if x[0] == seed]
        for col, (_, mode, image) in enumerate(pair):
            x = col * w; y = row_idx * h
            sheet.paste(image, (x, y))
            d = ImageDraw.Draw(sheet)
            d.rectangle((x, y, x + 180, y + 24), fill=(0,0,0))
            d.text((x+7, y+6), f"seed {seed} | {mode}", font=font, fill=(255,255,255))
    board = out / "result_architecture_comparison.jpg"
    sheet.save(board, quality=95)

    result = {
        "contract": "pul7sar-result-composition-architecture-comparison-v1",
        "source_contract": payload.get("contract"),
        "flat_contract": HybridPixelComposer.CONTRACT,
        "spatial_contract": SpatialResultMonument.CONTRACT,
        "candidate_count": len(rows),
        "pairs": rows,
        "board": board.name,
        "publication_ready": False,
        "human_visual_review_required": True,
        "decision_rule": "pixel health may reject; aesthetic architecture selection requires visual review",
    }
    (out / "manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

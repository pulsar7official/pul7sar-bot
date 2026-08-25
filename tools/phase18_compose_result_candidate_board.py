from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.generated_base_provenance import GeneratedBaseProvenance
from engine.intelligence.hybrid_final_composer import HybridFinalComposer
from engine.intelligence.hybrid_pixel_composer import HybridPixelComposer, HybridPixelRequest
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_candidate_quality_gate import VisualCandidateQualityGate


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--seed-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--headline", default="FULL TIME")
    p.add_argument("--home", default="NORTH CITY")
    p.add_argument("--away", default="SOUTH UNITED")
    p.add_argument("--score", default="3-1")
    return p.parse_args()


def _result_candidates(payload: dict) -> list[dict]:
    if payload.get("contract") != "pul7sar-result-seed-sweep-v2-provenance":
        raise ValueError(f"UNTRUSTED_RESULT_SWEEP_CONTRACT:{payload.get('contract')}")
    scenes = payload.get("scenes")
    if not isinstance(scenes, list):
        raise ValueError("RESULT_SEED_SWEEP_SCENES_MISSING")
    candidates = [s for s in scenes if s.get("family") == EditorialSceneFamily.RESULT_STATEMENT.value]
    if not candidates:
        raise ValueError("RESULT_SEED_SWEEP_HAS_NO_RESULT_SCENES")
    names = [str(c.get("file", "")) for c in candidates]
    if any(not name for name in names) or len(set(names)) != len(names):
        raise ValueError("RESULT_SEED_SWEEP_FILE_BINDINGS_INVALID")
    seeds = [c.get("seed") for c in candidates]
    if any(seed is None for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("RESULT_SEED_SWEEP_SEEDS_INVALID")
    return candidates


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
        story_key="phase18-result-candidate-board-3-1",
        recent_archetypes=("score_monument",),
        seed=21801,
    )

    composed = []
    images = []
    for item in candidates:
        seed = int(item["seed"])
        base = seed_dir / item["file"]
        provenance = GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest_path),
            family=family,
            image_path=str(base),
        )
        output = out / f"result_hybrid_seed_{seed}.jpg"
        receipt = HybridPixelComposer().compose(HybridPixelRequest(
            plan=plan,
            generated_base_path=str(base),
            output_path=str(output),
            headline=q.headline,
            primary_label=q.home,
            secondary_label=q.away,
            primary_value=q.score,
            generated_base_provenance=provenance,
        ))
        quality = VisualCandidateQualityGate.inspect(str(output))
        composed.append({
            "seed": seed,
            "base": base.name,
            "output": output.name,
            "sha256": receipt.output_sha256,
            "provenance_verified": receipt.provenance_verified,
            "pixel_health_passed": quality.passed,
            "pixel_health_reasons": list(quality.reasons),
            "mean_luma": quality.mean_luma,
            "dark_fraction": quality.dark_fraction,
            "bright_fraction": quality.bright_fraction,
            "entropy": quality.entropy,
        })
        images.append((seed, quality.passed, Image.open(output).convert("RGB")))

    if not any(c["pixel_health_passed"] for c in composed):
        raise ValueError("ALL_RESULT_CANDIDATES_FAILED_PIXEL_HEALTH_GATE")

    w, h = images[0][2].size
    cols = 2
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (10, 10, 10))
    font = ImageFont.load_default()
    for i, (seed, passed, image) in enumerate(images):
        x = (i % cols) * w; y = (i // cols) * h
        sheet.paste(image, (x, y))
        d = ImageDraw.Draw(sheet)
        label = f"seed {seed} | {'pixel-ok' if passed else 'reject'}"
        d.rectangle((x, y, x + 190, y + 24), fill=(0, 0, 0))
        d.text((x + 7, y + 6), label, font=font, fill=(255, 255, 255))
    sheet_path = out / "result_hybrid_candidate_board.jpg"
    sheet.save(sheet_path, quality=95)

    result = {
        "contract": "pul7sar-result-hybrid-candidate-board-v3-scene-contract",
        "source_contract": payload.get("contract"),
        "quality_gate_contract": "pul7sar-visual-candidate-quality-gate-v1",
        "family": family.value,
        "candidate_count": len(composed),
        "pixel_healthy_candidate_count": sum(1 for c in composed if c["pixel_health_passed"]),
        "candidates": composed,
        "board": sheet_path.name,
        "exact_score": q.score,
        "brand_applied": False,
        "fabricated_crest_used": False,
        "publication_ready": False,
        "human_visual_review_required": True,
    }
    (out / "manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

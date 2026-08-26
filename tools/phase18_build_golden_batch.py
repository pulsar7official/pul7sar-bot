#!/usr/bin/env python3
"""Build a deterministic quality-first batch of Golden editorial v6 handoffs.

Only the seed varies. Candidates are compared under identical story-first visual
direction. A PREVIEW keeps football surface geometry contextual and optional;
PUL7SAR branding remains deterministic after generation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_handoff import (
    GOLDEN_BENCHMARK_ID,
    GOLDEN_CAMERA_PRESET,
    GOLDEN_MANIFEST_VERSION,
    GOLDEN_SPORT_GEOMETRY,
    build_request,
)


DEFAULT_SEEDS = (7007001, 7007002, 7007003, 7007004)


def build_batch(output_dir: str, seeds: tuple[int, ...] = DEFAULT_SEEDS) -> dict[str, object]:
    if not seeds:
        raise ValueError("at least one Golden Visual seed is required")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Golden Visual seeds must be unique")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    candidates: list[dict[str, object]] = []
    observed_surface_visibility: str | None = None
    observed_visual_grammar_contract: str | None = None
    observed_focal_anchor: str | None = None
    observed_copy_space: str | None = None
    observed_brand_quiet_zone: str | None = None
    for index, seed in enumerate(seeds, start=1):
        request_id = f"golden-season-opener-editorial-v6-{index:03d}"
        request = build_request(seed=seed, request_id=request_id)
        surface_visibility = str(request.metadata["visual_grammar_surface_visibility"])
        visual_grammar_contract = str(request.metadata["visual_grammar_contract"])
        focal_anchor = str(request.metadata["focal_anchor"])
        copy_space = str(request.metadata["copy_negative_space"])
        brand_quiet_zone = str(request.metadata["brand_quiet_zone"])
        if observed_surface_visibility is None:
            observed_surface_visibility = surface_visibility
            observed_visual_grammar_contract = visual_grammar_contract
            observed_focal_anchor = focal_anchor
            observed_copy_space = copy_space
            observed_brand_quiet_zone = brand_quiet_zone
        elif (
            surface_visibility != observed_surface_visibility
            or visual_grammar_contract != observed_visual_grammar_contract
            or focal_anchor != observed_focal_anchor
            or copy_space != observed_copy_space
            or brand_quiet_zone != observed_brand_quiet_zone
        ):
            raise RuntimeError("Golden candidate visual-composition contract drift detected across seeds")

        filename = f"candidate-{index:02d}-seed-{seed}.json"
        path = target / filename
        LocalGenerationHandoff.write(request, str(path))
        data = json.loads(path.read_text(encoding="utf-8"))
        target_width = int(request.metadata["target_width"])
        target_height = int(request.metadata["target_height"])
        candidates.append({
            "candidate": index,
            "seed": seed,
            "request_id": request_id,
            "handoff": filename,
            "payload_sha256": data["payload_sha256"],
            "model_id": request.model_id,
            "native_canvas": f"{request.width}x{request.height}",
            "target_canvas": f"{target_width}x{target_height}",
            "canvas_normalization_required": bool(request.metadata["canvas_normalization_required"]),
            "visual_grammar_surface_visibility": surface_visibility,
            "focal_anchor": focal_anchor,
            "copy_negative_space": copy_space,
            "brand_quiet_zone": brand_quiet_zone,
        })

    if observed_surface_visibility != "context_only":
        raise RuntimeError(
            f"Golden v6 season-opener preview must remain context_only, found {observed_surface_visibility!r}"
        )
    if (observed_focal_anchor, observed_copy_space, observed_brand_quiet_zone) != (
        "illuminated_tunnel_lower_left", "right_center", "upper_left"
    ):
        raise RuntimeError("Golden v6 focal hierarchy drifted from the locked Instagram editorial composition")

    manifest = {
        "manifest_version": GOLDEN_MANIFEST_VERSION,
        "benchmark": GOLDEN_BENCHMARK_ID,
        "cost_mode": "$0-local",
        "composition_grammar": "single_continuous_scene",
        "visual_grammar_contract": observed_visual_grammar_contract,
        "visual_grammar_surface_visibility": observed_surface_visibility,
        "sport_geometry": GOLDEN_SPORT_GEOMETRY,
        "generated_sport_geometry_allowed": False,
        "hybrid_surface_replacement_required": False,
        "football_camera_preset": GOLDEN_CAMERA_PRESET,
        "generated_branding_allowed": False,
        "brand_composition_policy": "dynamic_deterministic_after_generation",
        "visual_priority": "story_focal_hierarchy_before_sport_surface",
        "focal_anchor": observed_focal_anchor,
        "copy_negative_space": observed_copy_space,
        "brand_quiet_zone": observed_brand_quiet_zone,
        "selection_rule": (
            "quality-first; compare focal hierarchy, atmosphere, depth, negative space and editorial coherence under identical visual grammar; "
            "never prefer a candidate merely because it exposes more playing surface or because of seed order"
        ),
        "candidates": candidates,
    }
    manifest_path = target / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Golden editorial v6 candidate batch")
    parser.add_argument("--output-dir", default="output/phase18_handoffs/golden-batch")
    parser.add_argument("--seeds", nargs="*", type=int, default=list(DEFAULT_SEEDS))
    args = parser.parse_args()
    manifest = build_batch(args.output_dir, tuple(args.seeds))
    print(json.dumps({
        "status": "GOLDEN_EDITORIAL_BATCH_READY",
        "benchmark": manifest["benchmark"],
        "manifest_version": manifest["manifest_version"],
        "output_dir": args.output_dir,
        "candidate_count": len(manifest["candidates"]),
        "cost_mode": manifest["cost_mode"],
        "composition_grammar": manifest["composition_grammar"],
        "visual_grammar_contract": manifest["visual_grammar_contract"],
        "visual_grammar_surface_visibility": manifest["visual_grammar_surface_visibility"],
        "sport_geometry": manifest["sport_geometry"],
        "hybrid_surface_replacement_required": manifest["hybrid_surface_replacement_required"],
        "generated_branding_allowed": manifest["generated_branding_allowed"],
        "focal_anchor": manifest["focal_anchor"],
        "copy_negative_space": manifest["copy_negative_space"],
        "brand_quiet_zone": manifest["brand_quiet_zone"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

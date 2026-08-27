#!/usr/bin/env python3
"""Verify a Golden Visual handoff batch without CUDA or model downloads.

Legacy v1-v5 manifests remain readable. v6 adds a story-first ownership contract:
a generic PREVIEW must stay context-only, must not require deterministic surface
replacement, must reject central/full-pitch template framing, and must hard-block
invented partial regulation sport geometry.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL

SUPPORTED_MANIFEST_VERSIONS = {
    "pul7sar-golden-batch-v1", "pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3",
    "pul7sar-golden-batch-v4", "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6",
}

V6_SPORT_GEOMETRY = "contextual_optional_not_required"
V6_GEOMETRY_INTEGRITY = "exact_verified_or_visually_indeterminate"
V6_FOCAL_ANCHOR = "illuminated_tunnel_lower_left"
V6_COPY_NEGATIVE_SPACE = "right_center"
V6_BRAND_QUIET_ZONE = "upper_left"


def _mismatches(data: dict[str, object], expected: dict[str, object]) -> list[str]:
    return [f"{key}={data.get(key)!r}" for key, value in expected.items() if data.get(key) != value]


def verify_batch(manifest_path: str) -> dict[str, object]:
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest_version = manifest.get("manifest_version")
    if manifest_version not in SUPPORTED_MANIFEST_VERSIONS:
        raise ValueError("unsupported Golden Visual batch manifest version")
    if manifest.get("cost_mode") != "$0-local":
        raise ValueError("Golden Visual batch must remain locked to $0-local")

    if manifest_version in {
        "pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4",
        "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6",
    } and manifest.get("composition_grammar") != "single_continuous_scene":
        raise ValueError("Golden Visual v2+ batch must lock single_continuous_scene")
    if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"} and manifest.get("sport_geometry") != "association_football_regulation_pitch":
        raise ValueError("Golden Visual v3/v4 must lock regulation pitch geometry")
    if manifest_version == "pul7sar-golden-batch-v4":
        if manifest.get("generated_branding_allowed") is not False:
            raise ValueError("Golden Visual v4 must forbid generated platform branding")
        if manifest.get("brand_composition_policy") != "exact_assets_only_after_generation":
            raise ValueError("Golden Visual v4 must lock exact post-generation branding")
    if manifest_version == "pul7sar-golden-batch-v5":
        expected = {
            "sport_geometry": "deterministic_football_pitch_projective_v1",
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": "high_wide_central",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
        }
        failures = _mismatches(manifest, expected)
        if failures:
            raise ValueError("Golden Hybrid v5 contract mismatch: " + "; ".join(failures))
    if manifest_version == "pul7sar-golden-batch-v6":
        expected = {
            "visual_grammar_surface_visibility": "context_only",
            "sport_geometry": V6_SPORT_GEOMETRY,
            "generated_sport_geometry_allowed": False,
            "partial_sport_geometry_allowed": False,
            "sport_geometry_integrity_policy": V6_GEOMETRY_INTEGRITY,
            "partial_sport_geometry_hallucination_is_hard_failure": True,
            "hybrid_surface_replacement_required": False,
            "football_camera_preset": "editorial_environmental_oblique",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
            "focal_anchor": V6_FOCAL_ANCHOR,
            "copy_negative_space": V6_COPY_NEGATIVE_SPACE,
            "brand_quiet_zone": V6_BRAND_QUIET_ZONE,
        }
        failures = _mismatches(manifest, expected)
        if failures:
            raise ValueError("Golden editorial v6 contract mismatch: " + "; ".join(failures))

    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden Visual batch manifest contains no candidates")

    root = path.resolve().parent
    seen_ids: set[str] = set(); seen_seeds: set[int] = set(); seen_files: set[str] = set()
    verified: list[dict[str, object]] = []

    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("invalid Golden Visual candidate manifest entry")
        request_id = str(item.get("request_id") or "")
        seed = item.get("seed")
        handoff_name = str(item.get("handoff") or "")
        declared_hash = str(item.get("payload_sha256") or "")
        if not request_id or request_id in seen_ids:
            raise ValueError("candidate request IDs must be non-empty and unique")
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0 or seed in seen_seeds:
            raise ValueError("candidate seeds must be unique non-negative integers")
        if not handoff_name or handoff_name in seen_files or Path(handoff_name).name != handoff_name:
            raise ValueError("candidate handoff filenames must be unique simple filenames")
        seen_ids.add(request_id); seen_seeds.add(seed); seen_files.add(handoff_name)

        if manifest_version == "pul7sar-golden-batch-v6":
            candidate_contract = {
                "visual_grammar_surface_visibility": "context_only",
                "partial_sport_geometry_allowed": False,
                "sport_geometry_integrity_policy": V6_GEOMETRY_INTEGRITY,
                "partial_sport_geometry_hallucination_is_hard_failure": True,
                "focal_anchor": V6_FOCAL_ANCHOR,
                "copy_negative_space": V6_COPY_NEGATIVE_SPACE,
                "brand_quiet_zone": V6_BRAND_QUIET_ZONE,
            }
            failures = _mismatches(item, candidate_contract)
            if failures:
                raise ValueError(f"candidate {request_id} manifest metadata drifted: " + "; ".join(failures))

        handoff_path = root / handoff_name
        if not handoff_path.is_file():
            raise FileNotFoundError(f"Golden Visual handoff is missing: {handoff_name}")
        raw = json.loads(handoff_path.read_text(encoding="utf-8"))
        if raw.get("payload_sha256") != declared_hash:
            raise ValueError(f"manifest/handoff SHA-256 mismatch for {request_id}")
        request = LocalGenerationHandoff.read(str(handoff_path))
        if request.request_id != request_id or request.seed != seed:
            raise ValueError(f"candidate identity mismatch for {handoff_name}")
        if request.provider_id != FLUX2_KLEIN_4B_LOCAL.provider_id or request.model_id != FLUX2_KLEIN_4B_LOCAL.model_id or request.backend != "diffusers":
            raise ValueError(f"unexpected local generation route for {request_id}")
        if request.metadata.get("cost_mode") != "$0-local":
            raise ValueError(f"candidate {request_id} escaped $0-local mode")

        prompt = request.prompt.casefold()
        if manifest_version in {"pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4", "pul7sar-golden-batch-v5", "pul7sar-golden-batch-v6"}:
            required = ("one single continuous full-bleed editorial image", "never use collage, montage, split-screen, grid, diptych, triptych")
            if any(marker not in prompt for marker in required):
                raise ValueError(f"candidate {request_id} is missing the unified-scene prompt lock")
        if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"}:
            geometry = ("regulation association-football pitch geometry", "exactly one halfway line", "exactly one circular centre circle", "do not duplicate the halfway line or centre circle")
            if any(marker not in prompt for marker in geometry):
                raise ValueError(f"candidate {request_id} is missing the legacy v3/v4 geometry lock")
        if manifest_version == "pul7sar-golden-batch-v5":
            semantic = ("reserved surface region plain and unmarked", "no field/court/rink lines", "the exact surface will be replaced by deterministic code after generation", "fully unbranded", "platform names")
            if any(marker not in prompt for marker in semantic):
                raise ValueError(f"candidate {request_id} is missing Golden Hybrid v5 semantic safeguards")
        if manifest_version == "pul7sar-golden-batch-v6":
            semantic = (
                "single illuminated players' tunnel mouth", "lower-left to mid-left", "right-center calm and low-detail", "upper-left restrained",
                "no high-wide-central broadcast framing", "no full-pitch master shot", "show no goal frame or goal net",
                "no penalty-area or goal-area lines", "no corner arc or corner flag", "no centre circle or halfway line",
                "keep it outside the frame, fully occluded, or visually indeterminate", "fully unbranded", "platform names",
            )
            if any(marker not in prompt for marker in semantic):
                raise ValueError(f"candidate {request_id} is missing Golden editorial v6 visual safeguards")
            if "pul7sar" in prompt or "pulsar" in prompt:
                raise ValueError(f"candidate {request_id} leaked protected platform name into v6 generation prompt")
            if any(marker in prompt for marker in ("the exact surface will be replaced by deterministic code after generation", "high wide central stadium camera")):
                raise ValueError(f"candidate {request_id} regressed to the Golden v5 pitch-first contract")
            structured = {
                "brand_name_redacted_from_generation_prompt": True,
                "generated_branding_allowed": False,
                "composition_grammar": "single_continuous_scene",
                "hybrid_base_scene_contract": True,
                "generated_sport_geometry_allowed": False,
                "partial_sport_geometry_allowed": False,
                "sport_geometry_integrity_policy": V6_GEOMETRY_INTEGRITY,
                "partial_sport_geometry_hallucination_is_hard_failure": True,
                "hybrid_surface_replacement_required": False,
                "visual_grammar_surface_visibility": "context_only",
                "sport_geometry": V6_SPORT_GEOMETRY,
                "football_camera_preset": "editorial_environmental_oblique",
                "visual_priority": "story_focal_hierarchy_before_sport_surface",
                "focal_anchor": V6_FOCAL_ANCHOR,
                "copy_negative_space": V6_COPY_NEGATIVE_SPACE,
                "brand_quiet_zone": V6_BRAND_QUIET_ZONE,
            }
            failures = _mismatches(request.metadata, structured)
            if failures:
                raise ValueError(f"candidate {request_id} structured Golden editorial v6 ownership mismatch: " + "; ".join(failures))

        target_width = request.metadata.get("target_width"); target_height = request.metadata.get("target_height")
        actual_target = f"{target_width}x{target_height}"
        if item.get("target_canvas") != actual_target or item.get("native_canvas") != f"{request.width}x{request.height}":
            raise ValueError(f"canvas metadata mismatch for {request_id}")
        verified.append({"request_id": request_id, "seed": seed, "payload_sha256": declared_hash, "native_canvas": f"{request.width}x{request.height}", "target_canvas": actual_target})

    json_files = {entry.name for entry in root.glob("candidate-*.json") if entry.is_file()}
    if json_files != seen_files:
        extras = sorted(json_files - seen_files); missing = sorted(seen_files - json_files); details = []
        if extras: details.append("unmanifested=" + ",".join(extras))
        if missing: details.append("missing=" + ",".join(missing))
        raise ValueError("candidate file coverage mismatch: " + "; ".join(details))

    return {
        "status": "GOLDEN_BATCH_INTEGRITY_VERIFIED",
        "manifest_version": manifest_version,
        "composition_grammar": manifest.get("composition_grammar", "legacy_unspecified"),
        "visual_grammar_surface_visibility": manifest.get("visual_grammar_surface_visibility", "legacy_unspecified"),
        "sport_geometry": manifest.get("sport_geometry", "legacy_unspecified"),
        "generated_sport_geometry_allowed": manifest.get("generated_sport_geometry_allowed", "legacy_unspecified"),
        "partial_sport_geometry_allowed": manifest.get("partial_sport_geometry_allowed", "legacy_unspecified"),
        "sport_geometry_integrity_policy": manifest.get("sport_geometry_integrity_policy", "legacy_unspecified"),
        "partial_sport_geometry_hallucination_is_hard_failure": manifest.get("partial_sport_geometry_hallucination_is_hard_failure", "legacy_unspecified"),
        "hybrid_surface_replacement_required": manifest.get("hybrid_surface_replacement_required", "legacy_unspecified"),
        "generated_branding_allowed": manifest.get("generated_branding_allowed", "legacy_unspecified"),
        "brand_composition_policy": manifest.get("brand_composition_policy", "legacy_unspecified"),
        "visual_priority": manifest.get("visual_priority", "legacy_unspecified"),
        "focal_anchor": manifest.get("focal_anchor", "legacy_unspecified"),
        "copy_negative_space": manifest.get("copy_negative_space", "legacy_unspecified"),
        "brand_quiet_zone": manifest.get("brand_quiet_zone", "legacy_unspecified"),
        "cost_mode": "$0-local",
        "candidate_count": len(verified),
        "candidates": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a PUL7SAR Golden Visual batch before GPU execution")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    print(json.dumps(verify_batch(args.manifest), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

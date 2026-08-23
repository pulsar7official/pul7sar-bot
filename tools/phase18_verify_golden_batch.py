#!/usr/bin/env python3
"""Verify a Golden Visual handoff batch without CUDA or model downloads.

v5 validates hybrid ownership: diffusion must not own exact football geometry or
platform branding, deterministic pitch replacement is required, and the actual
image-model prompt must not contain the protected platform-name token.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL

SUPPORTED_MANIFEST_VERSIONS = {
    "pul7sar-golden-batch-v1",
    "pul7sar-golden-batch-v2",
    "pul7sar-golden-batch-v3",
    "pul7sar-golden-batch-v4",
    "pul7sar-golden-batch-v5",
}


def verify_batch(manifest_path: str) -> dict[str, object]:
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest_version = manifest.get("manifest_version")
    if manifest_version not in SUPPORTED_MANIFEST_VERSIONS:
        raise ValueError("unsupported Golden Visual batch manifest version")
    if manifest.get("cost_mode") != "$0-local":
        raise ValueError("Golden Visual batch must remain locked to $0-local")

    if manifest_version in {"pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4", "pul7sar-golden-batch-v5"}:
        if manifest.get("composition_grammar") != "single_continuous_scene":
            raise ValueError("Golden Visual v2+ batch must lock single_continuous_scene")
    if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"}:
        if manifest.get("sport_geometry") != "association_football_regulation_pitch":
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
        failures = [f"{key}={manifest.get(key)!r}" for key, value in expected.items() if manifest.get(key) != value]
        if failures:
            raise ValueError("Golden Hybrid v5 contract mismatch: " + "; ".join(failures))

    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden Visual batch manifest contains no candidates")

    root = path.resolve().parent
    seen_ids: set[str] = set()
    seen_seeds: set[int] = set()
    seen_files: set[str] = set()
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
        seen_ids.add(request_id)
        seen_seeds.add(seed)
        seen_files.add(handoff_name)

        handoff_path = root / handoff_name
        if not handoff_path.is_file():
            raise FileNotFoundError(f"Golden Visual handoff is missing: {handoff_name}")
        raw = json.loads(handoff_path.read_text(encoding="utf-8"))
        if raw.get("payload_sha256") != declared_hash:
            raise ValueError(f"manifest/handoff SHA-256 mismatch for {request_id}")
        request = LocalGenerationHandoff.read(str(handoff_path))
        if request.request_id != request_id:
            raise ValueError(f"request ID mismatch for {handoff_name}")
        if request.seed != seed:
            raise ValueError(f"seed mismatch for {request_id}")
        if request.provider_id != FLUX2_KLEIN_4B_LOCAL.provider_id:
            raise ValueError(f"unexpected provider for {request_id}")
        if request.model_id != FLUX2_KLEIN_4B_LOCAL.model_id:
            raise ValueError(f"unexpected model for {request_id}")
        if request.backend != "diffusers":
            raise ValueError(f"unexpected backend for {request_id}")
        if request.metadata.get("cost_mode") != "$0-local":
            raise ValueError(f"candidate {request_id} escaped $0-local mode")

        prompt = request.prompt.casefold()
        if manifest_version in {"pul7sar-golden-batch-v2", "pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4", "pul7sar-golden-batch-v5"}:
            required_prompt_markers = (
                "one single continuous full-bleed editorial image",
                "never use collage, montage, split-screen, grid, diptych, triptych",
            )
            if any(marker not in prompt for marker in required_prompt_markers):
                raise ValueError(f"candidate {request_id} is missing the unified-scene prompt lock")
        if manifest_version in {"pul7sar-golden-batch-v3", "pul7sar-golden-batch-v4"}:
            geometry_markers = (
                "regulation association-football pitch geometry",
                "exactly one halfway line",
                "exactly one circular centre circle",
                "do not duplicate the halfway line or centre circle",
            )
            if any(marker not in prompt for marker in geometry_markers):
                raise ValueError(f"candidate {request_id} is missing the legacy v3/v4 geometry lock")
        if manifest_version == "pul7sar-golden-batch-v4":
            branding_markers = (
                "zero pul7sar lettering",
                "never spell pul7sar, pulsar, or any approximation",
                "no legible words, letters, numerals, pseudo-text, fake logos",
                "exact branding and typography are added only by deterministic post-composition",
            )
            if any(marker not in prompt for marker in branding_markers):
                raise ValueError(f"candidate {request_id} is missing the v4 brand-exclusion lock")
        if manifest_version == "pul7sar-golden-batch-v5":
            hybrid_markers = (
                "unmarked neutral sport-surface region reserved for deterministic overlay",
                "no field/court/rink lines",
                "the exact surface will be replaced by deterministic code after generation",
                "fully unbranded",
                "platform names",
                "exact branding and typography can be added later by deterministic post-composition",
            )
            if any(marker not in prompt for marker in hybrid_markers):
                raise ValueError(f"candidate {request_id} is missing the Golden Hybrid v5 ownership lock")
            if "pul7sar" in prompt or "pulsar" in prompt:
                raise ValueError(f"candidate {request_id} leaked protected platform name into v5 generation prompt")
            if request.metadata.get("brand_name_redacted_from_generation_prompt") is not True:
                raise ValueError(f"candidate {request_id} did not attest brand-name prompt redaction")

        target_width = request.metadata.get("target_width")
        target_height = request.metadata.get("target_height")
        expected_target = item.get("target_canvas")
        actual_target = f"{target_width}x{target_height}"
        if expected_target != actual_target:
            raise ValueError(f"target canvas mismatch for {request_id}")
        if item.get("native_canvas") != f"{request.width}x{request.height}":
            raise ValueError(f"native canvas mismatch for {request_id}")

        verified.append({
            "request_id": request_id,
            "seed": seed,
            "payload_sha256": declared_hash,
            "native_canvas": f"{request.width}x{request.height}",
            "target_canvas": actual_target,
        })

    json_files = {entry.name for entry in root.glob("candidate-*.json") if entry.is_file()}
    if json_files != seen_files:
        extras = sorted(json_files - seen_files)
        missing = sorted(seen_files - json_files)
        details = []
        if extras:
            details.append("unmanifested=" + ",".join(extras))
        if missing:
            details.append("missing=" + ",".join(missing))
        raise ValueError("candidate file coverage mismatch: " + "; ".join(details))

    return {
        "status": "GOLDEN_BATCH_INTEGRITY_VERIFIED",
        "manifest_version": manifest_version,
        "composition_grammar": manifest.get("composition_grammar", "legacy_unspecified"),
        "sport_geometry": manifest.get("sport_geometry", "legacy_unspecified"),
        "generated_sport_geometry_allowed": manifest.get("generated_sport_geometry_allowed", "legacy_unspecified"),
        "hybrid_surface_replacement_required": manifest.get("hybrid_surface_replacement_required", "legacy_unspecified"),
        "generated_branding_allowed": manifest.get("generated_branding_allowed", "legacy_unspecified"),
        "brand_composition_policy": manifest.get("brand_composition_policy", "legacy_unspecified"),
        "cost_mode": "$0-local",
        "candidate_count": len(verified),
        "candidates": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a PUL7SAR Golden Visual batch before GPU execution")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    result = verify_batch(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

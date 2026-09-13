"""Build a fail-closed Hybrid v5 handoff from a proven first Golden PNG.

The GPU smoke path and the Colab Hybrid v5 path historically used different
summary artifacts. This bridge lets the exact Candidate 1 bytes that passed the
first-PNG provenance postflight become the base consumed by the existing Hybrid
semantic/composition flow without regenerating FLUX pixels.

It never grants semantic, Golden-quality, brand, typography or publication
approval. It only proves that the same provenance-locked base may enter those
later gates.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.golden_smoke import GOLDEN_COST_MODE, GoldenSmokeCandidate

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v5"
EXPECTED_POSTFLIGHT_STATUS = "FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED"
EXPECTED_DTYPE = "bfloat16"
EXPECTED_STATUS = "FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(root: Path, value: str | Path, *, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if path != root and root not in path.parents:
        raise RuntimeError(f"FIRST_PNG_HYBRID_HANDOFF_{label}_ESCAPES_REPOSITORY")
    return path


class FirstPngHybridHandoffBuilder:
    """Bind Candidate 1 provenance evidence to the existing Hybrid v5 base contract."""

    def build(
        self,
        *,
        repository_root: str | Path,
        candidate: GoldenSmokeCandidate,
        manifest: dict[str, Any],
        postflight: dict[str, Any],
        branch: str,
    ) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        if branch != EXPECTED_BRANCH:
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_BRANCH_BLOCKED")
        if candidate.candidate != 1:
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_REQUIRES_CANDIDATE_1")

        expected_manifest = {
            "manifest_version": EXPECTED_MANIFEST_VERSION,
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": "deterministic_football_pitch_projective_v1",
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": "high_wide_central",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "cost_mode": GOLDEN_COST_MODE,
        }
        manifest_failures = [
            f"{key}={manifest.get(key)!r}" for key, expected in expected_manifest.items()
            if manifest.get(key) != expected
        ]
        if manifest_failures:
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_MANIFEST_DRIFT: " + "; ".join(manifest_failures))

        expected_postflight = {
            "status": EXPECTED_POSTFLIGHT_STATUS,
            "candidate": 1,
            "request_id": candidate.request_id,
            "seed": candidate.seed,
            "model_id": candidate.model_id,
            "payload_sha256": candidate.payload_sha256,
            "cost_mode": GOLDEN_COST_MODE,
            "resolved_dtype": EXPECTED_DTYPE,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        postflight_failures = [
            f"{key}={postflight.get(key)!r}" for key, expected in expected_postflight.items()
            if postflight.get(key) != expected
        ]
        if postflight_failures:
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_POSTFLIGHT_DRIFT: " + "; ".join(postflight_failures))

        png_value = postflight.get("png")
        if not isinstance(png_value, str) or not png_value.strip():
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_PNG_MISSING")
        png = _inside(root, png_value, label="PNG")
        if not png.is_file() or png.suffix.lower() != ".png":
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_PNG_INVALID")
        if png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_PNG_SIGNATURE_INVALID")
        png_sha = _sha256(png)
        if postflight.get("png_sha256") != png_sha:
            raise RuntimeError("FIRST_PNG_HYBRID_HANDOFF_PNG_SHA256_MISMATCH")

        executor = _inside(root, str(postflight.get("executor_result", "")), label="EXECUTOR")
        metadata = _inside(root, str(postflight.get("proof_metadata", "")), label="METADATA")
        for path, sha_field, label in (
            (executor, "executor_result_sha256", "EXECUTOR"),
            (metadata, "proof_metadata_sha256", "METADATA"),
        ):
            if not path.is_file():
                raise RuntimeError(f"FIRST_PNG_HYBRID_HANDOFF_{label}_MISSING")
            if _sha256(path) != postflight.get(sha_field):
                raise RuntimeError(f"FIRST_PNG_HYBRID_HANDOFF_{label}_SHA256_MISMATCH")

        return {
            "schema": "pul7sar-first-png-hybrid-handoff-v1",
            "status": EXPECTED_STATUS,
            "branch": branch,
            "manifest_version": EXPECTED_MANIFEST_VERSION,
            "benchmark": manifest.get("benchmark"),
            "composition_grammar": manifest.get("composition_grammar"),
            "sport_geometry": manifest.get("sport_geometry"),
            "generated_sport_geometry_allowed": False,
            "hybrid_surface_replacement_required": True,
            "football_camera_preset": manifest.get("football_camera_preset"),
            "generated_branding_allowed": False,
            "brand_composition_policy": manifest.get("brand_composition_policy"),
            "candidate": 1,
            "request_id": candidate.request_id,
            "seed": candidate.seed,
            "model_id": candidate.model_id,
            "payload_sha256": candidate.payload_sha256,
            "cost_mode": GOLDEN_COST_MODE,
            "resolved_dtype": EXPECTED_DTYPE,
            "png": str(png),
            "base_png_sha256": png_sha,
            "executor_result": str(executor),
            "executor_result_sha256": postflight["executor_result_sha256"],
            "proof_metadata": str(metadata),
            "proof_metadata_sha256": postflight["proof_metadata_sha256"],
            "generation_provenance_status": postflight["status"],
            "semantic_layer_gate_approved": False,
            "hybrid_semantic_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "next_gate": "Qwen BASE_SCENE semantic/layer ownership before deterministic football composition",
        }

    @staticmethod
    def write(path: str | Path, payload: dict[str, Any]) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

"""Replay and lock provenance for one genuine Phase 18 GPU visual proof.

This verifier binds the Colab generation summary to the durable executor result,
registered proof PNG, proof metadata, and the immutable approved upstream FLUX
model revision by path, identity fields, and SHA-256. It never grants semantic,
Golden-quality, or publication approval. Golden-reference BF16 and explicit T4
FP16 engineering previews are verified as distinct provenance tiers.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)

EXPECTED_MODEL = FLUX2_KLEIN_4B_MODEL_ID
EXPECTED_MODEL_REVISION = FLUX2_KLEIN_4B_REVISION
EXPECTED_COST_MODE = "$0-local"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    repository = root.resolve()
    if resolved != repository and repository not in resolved.parents:
        raise RuntimeError("GENERATION_PROVENANCE_PATH_ESCAPES_REPOSITORY")
    return resolved


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


class GenerationProvenanceLock:
    """Recompute durable proof hashes and bind them to one visual candidate."""

    def verify(
        self,
        *,
        repository_root: str,
        summary: dict[str, Any],
        base_png: str,
    ) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        candidate = summary.get("candidate")
        if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate <= 0:
            raise RuntimeError("GENERATION_PROVENANCE_CANDIDATE_INVALID")
        if summary.get("publication_ready") is not False:
            raise RuntimeError("GENERATION_PROVENANCE_REQUIRES_UNPUBLISHED_INPUT")
        if summary.get("model_id") != EXPECTED_MODEL:
            raise RuntimeError("GENERATION_PROVENANCE_MODEL_MISMATCH")
        if not _is_sha256(summary.get("payload_sha256")):
            raise RuntimeError("GENERATION_PROVENANCE_PAYLOAD_SHA_INVALID")

        proof = _inside(root, base_png)
        if not proof.is_file():
            raise FileNotFoundError(proof)
        with proof.open("rb") as handle:
            if handle.read(len(_PNG_SIGNATURE)) != _PNG_SIGNATURE:
                raise RuntimeError("GENERATION_PROVENANCE_PROOF_NOT_PNG")

        executor_value = summary.get("executor_result")
        if isinstance(executor_value, str) and executor_value.strip():
            executor = _inside(root, executor_value)
        else:
            executor = _inside(root, root / "output" / "phase18_visual_proof" / f"colab-candidate-{candidate:02d}-result.json")
        if not executor.is_file():
            raise RuntimeError("GENERATION_PROVENANCE_EXECUTOR_RESULT_MISSING")
        result = json.loads(executor.read_text(encoding="utf-8"))

        required_equal = {
            "request_id": summary.get("request_id"),
            "seed": summary.get("seed"),
            "model_id": summary.get("model_id"),
            "payload_sha256": summary.get("payload_sha256"),
        }
        if result.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            raise RuntimeError("GENERATION_PROVENANCE_EXECUTOR_STATUS_INVALID")
        for key, expected in required_equal.items():
            if result.get(key) != expected:
                raise RuntimeError(f"GENERATION_PROVENANCE_{key.upper()}_MISMATCH")
        if result.get("cost_mode") != EXPECTED_COST_MODE:
            raise RuntimeError("GENERATION_PROVENANCE_COST_MODE_DRIFT")

        result_tier = result.get("precision_quality_tier", "golden_reference")
        summary_tier = summary.get("precision_quality_tier", result_tier)
        if summary_tier != result_tier:
            raise RuntimeError("GENERATION_PROVENANCE_PRECISION_TIER_MISMATCH")
        if result_tier == "golden_reference":
            if result.get("resolved_dtype") != "bfloat16":
                raise RuntimeError("GENERATION_PROVENANCE_DTYPE_DRIFT")
            status = "GENERATION_PROVENANCE_LOCK_VERIFIED"
        elif result_tier == "t4_engineering_preview":
            if result.get("resolved_dtype") != "float16":
                raise RuntimeError("GENERATION_PROVENANCE_PREVIEW_DTYPE_DRIFT")
            if result.get("golden_reference_precision") is not False:
                raise RuntimeError("GENERATION_PROVENANCE_PREVIEW_MUST_NOT_CLAIM_GOLDEN_PRECISION")
            status = "GENERATION_PROVENANCE_ENGINEERING_PREVIEW_VERIFIED"
        else:
            raise RuntimeError("GENERATION_PROVENANCE_PRECISION_TIER_UNKNOWN")

        result_png = result.get("png")
        if not isinstance(result_png, str) or not result_png.strip():
            raise RuntimeError("GENERATION_PROVENANCE_EXECUTOR_PNG_MISSING")
        if _inside(root, result_png) != proof:
            raise RuntimeError("GENERATION_PROVENANCE_PNG_PATH_MISMATCH")

        metadata_value = result.get("metadata")
        if not isinstance(metadata_value, str) or not metadata_value.strip():
            raise RuntimeError("GENERATION_PROVENANCE_METADATA_MISSING")
        metadata_path = _inside(root, metadata_value)
        if not metadata_path.is_file():
            raise RuntimeError("GENERATION_PROVENANCE_METADATA_FILE_MISSING")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata_expected = {
            "request_id": summary.get("request_id"),
            "seed": summary.get("seed"),
            "model": summary.get("model_id"),
            "model_revision": EXPECTED_MODEL_REVISION,
            "cost_mode": EXPECTED_COST_MODE,
        }
        for key, expected in metadata_expected.items():
            if metadata.get(key) != expected:
                raise RuntimeError(f"GENERATION_PROVENANCE_METADATA_{key.upper()}_MISMATCH")
        output_ref = metadata.get("output_ref")
        if not isinstance(output_ref, str) or _inside(root, output_ref) != proof:
            raise RuntimeError("GENERATION_PROVENANCE_METADATA_OUTPUT_MISMATCH")

        return {
            "status": status,
            "candidate": candidate,
            "request_id": summary.get("request_id"),
            "seed": summary.get("seed"),
            "model_id": summary.get("model_id"),
            "model_revision": EXPECTED_MODEL_REVISION,
            "payload_sha256": summary.get("payload_sha256"),
            "cost_mode": EXPECTED_COST_MODE,
            "resolved_dtype": result.get("resolved_dtype"),
            "precision_quality_tier": result_tier,
            "base_png": str(proof),
            "base_png_sha256": _sha256(proof),
            "executor_result": str(executor),
            "executor_result_sha256": _sha256(executor),
            "metadata": str(metadata_path),
            "metadata_sha256": _sha256(metadata_path),
            "publication_ready": False,
        }

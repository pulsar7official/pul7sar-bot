"""Bind pre-model FLUX offload policy to the mode used by the real executor.

A capability preflight proves which CPU-offload mode is safe before model work.
That is not sufficient Golden evidence by itself: the executor that produced the
PNG must report the same mode after the Diffusers pipeline is constructed. This
module replays both receipts and fails closed on any identity, revision, cost,
precision, hash, or offload-mode drift.

It never grants semantic, Golden-quality, brand, typography, export, or
publication approval.
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

EXPECTED_PREFLIGHT_SCHEMA = "pul7sar-phase18-flux2-offload-preflight-v1"
EXPECTED_STAGING_SCHEMA = "pul7sar-first-genuine-golden-staging-v3"
EXPECTED_COST_MODE = "$0-local"
_ALLOWED_MODES = {"sequential_cpu", "model_cpu"}


def _inside(root: Path, value: str | Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    repository = root.resolve()
    if resolved != repository and repository not in resolved.parents:
        raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_PATH_ESCAPES_REPOSITORY")
    return resolved


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"GOLDEN_OFFLOAD_PROVENANCE_EVIDENCE_MISSING:{path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EVIDENCE_INVALID")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GoldenOffloadProvenanceLock:
    """Prove that the executor used the preflight-selected safe offload mode."""

    def verify(
        self,
        *,
        repository_root: str | Path,
        preflight_receipt: str | Path,
        staging_receipt: str | Path,
    ) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        preflight_path = _inside(root, preflight_receipt)
        staging_path = _inside(root, staging_receipt)
        preflight = _load(preflight_path)
        staging = _load(staging_path)

        if preflight.get("schema") != EXPECTED_PREFLIGHT_SCHEMA or preflight.get("ready") is not True:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_PREFLIGHT_NOT_READY")
        if preflight.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_PREFLIGHT_MODEL_DRIFT")
        if preflight.get("cost_mode") != EXPECTED_COST_MODE:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_PREFLIGHT_COST_DRIFT")
        for field in (
            "model_loaded",
            "downloads_performed",
            "generation_authorized",
            "queue_mutated",
            "png_created",
            "semantic_approved",
            "golden_quality_approved",
            "publication_ready",
        ):
            if preflight.get(field) is not False:
                raise RuntimeError(f"GOLDEN_OFFLOAD_PROVENANCE_PREFLIGHT_AUTHORITY_DRIFT:{field}")
        selected_mode = preflight.get("selected_safe_mode")
        if selected_mode not in _ALLOWED_MODES:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_SAFE_MODE_UNPROVEN")
        if preflight.get("low_vram_host") is True and selected_mode != "sequential_cpu":
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_LOW_VRAM_MODE_DRIFT")

        if staging.get("schema") != EXPECTED_STAGING_SCHEMA:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_SCHEMA_DRIFT")
        if staging.get("candidate") != 1:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_REQUIRES_CANDIDATE_1")
        if staging.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_MODEL_DRIFT")
        if staging.get("model_revision") != FLUX2_KLEIN_4B_REVISION:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_REVISION_DRIFT")
        if staging.get("cost_mode") != EXPECTED_COST_MODE:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_COST_DRIFT")
        if staging.get("resolved_dtype") != "bfloat16" or staging.get("precision_quality_tier") != "golden_reference":
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_PRECISION_DRIFT")
        if staging.get("publication_ready") is not False or staging.get("golden_quality_approved") is not False:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_STAGING_AUTHORITY_DRIFT")

        executor_value = staging.get("executor_result")
        if not isinstance(executor_value, str) or not executor_value.strip():
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_RESULT_MISSING")
        executor_path = _inside(root, executor_value)
        executor = _load(executor_path)
        executor_sha = _sha256(executor_path)
        if staging.get("executor_result_sha256") != executor_sha:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_SHA_DRIFT")

        if executor.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_STATUS_INVALID")
        if executor.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_MODEL_DRIFT")
        if executor.get("model_revision") != FLUX2_KLEIN_4B_REVISION:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_REVISION_DRIFT")
        if executor.get("cost_mode") != EXPECTED_COST_MODE:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_COST_DRIFT")
        if executor.get("resolved_dtype") != "bfloat16" or executor.get("precision_quality_tier") != "golden_reference":
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_PRECISION_DRIFT")
        if executor.get("offload_mode_proven") is not True:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_ACTUAL_MODE_NOT_PROVEN")
        actual_mode = executor.get("actual_offload_mode")
        if actual_mode not in _ALLOWED_MODES:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_ACTUAL_MODE_INVALID")
        if actual_mode != selected_mode:
            raise RuntimeError("GOLDEN_OFFLOAD_PROVENANCE_SELECTED_ACTUAL_MODE_MISMATCH")

        for field in ("request_id", "seed", "payload_sha256"):
            if executor.get(field) != staging.get(field):
                raise RuntimeError(f"GOLDEN_OFFLOAD_PROVENANCE_EXECUTOR_{field.upper()}_DRIFT")

        return {
            "schema": "pul7sar-golden-offload-provenance-v1",
            "status": "GOLDEN_FLUX_ACTUAL_OFFLOAD_PROVENANCE_VERIFIED",
            "candidate": 1,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "cost_mode": EXPECTED_COST_MODE,
            "selected_safe_offload_mode": selected_mode,
            "actual_offload_mode": actual_mode,
            "actual_offload_mode_bound": True,
            "preflight_receipt": str(preflight_path),
            "preflight_receipt_sha256": _sha256(preflight_path),
            "executor_result": str(executor_path),
            "executor_result_sha256": executor_sha,
            "staging_receipt": str(staging_path),
            "staging_receipt_sha256": _sha256(staging_path),
            "request_id": staging.get("request_id"),
            "seed": staging.get("seed"),
            "payload_sha256": staging.get("payload_sha256"),
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

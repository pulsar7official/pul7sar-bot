"""Fail-closed Qwen Image 2512 pipeline-load measurement evidence.

This module sits strictly between measurement admission and any future image
inference experiment.  A successful receipt proves only that the exact pinned
Qwen Image snapshot could be instantiated by the measured local software stack
inside an isolated process.  It does NOT prove an inference/runtime floor and
never authorizes canonical generation, Golden approval, or publication.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
    assert_snapshot_revision,
)
from engine.intelligence.qwen_image_measurement_admission import MEASUREMENT_SCHEMA


LOAD_MEASUREMENT_SCHEMA = "pul7sar-phase18-qwen-image-2512-runtime-load-measurement-v1"
COST_MODE = "$0-local"


def sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_measurement_admission(receipt: dict[str, Any]) -> str:
    if receipt.get("schema") != MEASUREMENT_SCHEMA:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_SCHEMA_MISMATCH")
    if receipt.get("status") != "QWEN_IMAGE_2512_LOCAL_MEASUREMENT_ADMISSION_READY":
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_NOT_READY")
    if receipt.get("measurement_ready") is not True:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_READY_FALSE")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_MODEL_MISMATCH")
    if receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_REVISION_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_COST_MODE_MISMATCH")
    if receipt.get("exact_snapshot_cached") is not True:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_EXACT_SNAPSHOT_REQUIRED")
    snapshot_raw = receipt.get("exact_snapshot_path")
    if not isinstance(snapshot_raw, str) or not snapshot_raw:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_SNAPSHOT_PATH_MISSING")
    snapshot = Path(snapshot_raw).expanduser().resolve()
    assert_snapshot_revision(snapshot, QWEN_IMAGE_2512_REVISION)
    if not (snapshot / "model_index.json").is_file() or not any(snapshot.rglob("*.safetensors")):
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_SNAPSHOT_INCOMPLETE")

    forbidden_true = (
        "runtime_floor_proven",
        "local_runtime_qualified",
        "model_loaded",
        "generation_authorized",
        "queue_mutated",
        "png_created",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    )
    if any(receipt.get(field) is not False for field in forbidden_true):
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_AUTHORITY_DRIFT")
    if receipt.get("measurement_only") is not True:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_BOUNDARY_MISSING")

    claimed = receipt.get("receipt_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_SHA_INVALID")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_IMAGE_RUNTIME_MEASUREMENT_ADMISSION_SHA_MISMATCH")
    return actual


@dataclass(frozen=True)
class QwenImagePipelineLoadObservation:
    child_exit_code: int
    pipeline_load_succeeded: bool
    pipeline_class: str | None
    torch_version: str | None
    cuda_version: str | None
    diffusers_version: str | None
    native_bf16: bool | None
    gpu_name: str | None
    gpu_total_vram_gb: float | None
    gpu_free_vram_gb_before: float | None
    gpu_free_vram_gb_after: float | None
    max_cuda_allocated_gb: float | None
    max_cuda_reserved_gb: float | None
    process_max_rss_gb: float | None
    elapsed_seconds: float | None
    failure_type: str | None = None
    failure_message: str | None = None


@dataclass(frozen=True)
class QwenImageRuntimeLoadMeasurement:
    admission_sha256: str
    admission_file_sha256: str
    exact_snapshot_path: str
    observation: QwenImagePipelineLoadObservation

    def as_receipt(self) -> dict[str, Any]:
        load_ok = self.observation.pipeline_load_succeeded and self.observation.child_exit_code == 0
        payload = {
            "schema": LOAD_MEASUREMENT_SCHEMA,
            "status": "QWEN_IMAGE_2512_PIPELINE_LOAD_MEASURED" if load_ok else "QWEN_IMAGE_2512_PIPELINE_LOAD_FAILED",
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "admission_sha256": self.admission_sha256,
            "admission_file_sha256": self.admission_file_sha256,
            "exact_snapshot_path": self.exact_snapshot_path,
            "measurement_kind": "isolated_pipeline_load_only",
            **asdict(self.observation),
            "pipeline_load_proven": bool(load_ok),
            "inference_executed": False,
            "runtime_floor_proven": False,
            "local_runtime_qualified": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["receipt_sha256"] = sha256_json(payload)
        return payload


def verify_runtime_load_receipt(receipt: dict[str, Any]) -> str:
    if receipt.get("schema") != LOAD_MEASUREMENT_SCHEMA:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_SCHEMA_MISMATCH")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_MODEL_IDENTITY_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_COST_MODE_MISMATCH")
    if receipt.get("measurement_kind") != "isolated_pipeline_load_only":
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_MEASUREMENT_KIND_MISMATCH")
    if receipt.get("inference_executed") is not False or receipt.get("runtime_floor_proven") is not False:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_RUNTIME_FLOOR_AUTHORITY_FORBIDDEN")
    for field in ("local_runtime_qualified", "generation_authorized", "queue_mutated", "png_created", "semantic_approved", "golden_quality_approved", "publication_ready"):
        if receipt.get(field) is not False:
            raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_AUTHORITY_FORBIDDEN")
    claimed = receipt.get("receipt_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_SHA_INVALID")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_IMAGE_RUNTIME_LOAD_SHA_MISMATCH")
    return actual

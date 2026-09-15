"""Byte-bound admission into a future Qwen Image runtime-envelope experiment.

This module does not run Qwen Image and does not establish a runtime floor.
It only proves that a successful Change Set 226/227 single-inference receipt
still points to the exact engineering PNG bytes that were measured, and that
its basic hardware telemetry is structurally usable for the next controlled
measurement stage.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import (
    COST_MODE,
    INFERENCE_MEASUREMENT_SCHEMA,
    sha256_file,
    sha256_json,
    verify_inference_measurement_receipt,
)


RUNTIME_ENVELOPE_ADMISSION_SCHEMA = "pul7sar-phase18-qwen-image-2512-runtime-envelope-admission-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _repo_bound_path(raw: Any, repo_root: Path) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ARTIFACT_PATH_INVALID")
    root = repo_root.resolve()
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_relative_to(root):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ARTIFACT_PATH_ESCAPE")
    return path


def verify_single_inference_artifact(receipt: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    receipt_sha = verify_inference_measurement_receipt(receipt)
    if receipt.get("schema") != INFERENCE_MEASUREMENT_SCHEMA:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_INFERENCE_SCHEMA_MISMATCH")
    if receipt.get("status") != "QWEN_IMAGE_2512_SINGLE_INFERENCE_MEASURED":
        raise ValueError("QWEN_RUNTIME_ENVELOPE_SUCCESSFUL_INFERENCE_REQUIRED")
    if receipt.get("single_inference_proven") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_SINGLE_INFERENCE_UNPROVEN")

    png_path = _repo_bound_path(receipt.get("output_png_path"), repo_root)
    if not png_path.is_file():
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PNG_MISSING")
    if png_path.read_bytes()[:8] != PNG_SIGNATURE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PNG_SIGNATURE_INVALID")
    actual_size = png_path.stat().st_size
    if actual_size <= 8 or actual_size != receipt.get("output_png_size_bytes"):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PNG_SIZE_MISMATCH")
    actual_sha = sha256_file(png_path)
    if actual_sha != receipt.get("output_png_sha256"):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PNG_SHA_MISMATCH")

    positive_telemetry = (
        "gpu_total_vram_gb",
        "gpu_free_vram_gb_before",
        "gpu_free_vram_gb_after",
        "max_cuda_allocated_gb",
        "max_cuda_reserved_gb",
        "process_max_rss_gb",
        "elapsed_seconds",
    )
    for field in positive_telemetry:
        value = receipt.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
            raise ValueError(f"QWEN_RUNTIME_ENVELOPE_TELEMETRY_INVALID:{field}")
    if float(receipt["max_cuda_allocated_gb"]) > float(receipt["max_cuda_reserved_gb"]):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_CUDA_TELEMETRY_INCONSISTENT")
    if float(receipt["gpu_free_vram_gb_before"]) > float(receipt["gpu_total_vram_gb"]):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_VRAM_BEFORE_INCONSISTENT")
    if float(receipt["gpu_free_vram_gb_after"]) > float(receipt["gpu_total_vram_gb"]):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_VRAM_AFTER_INCONSISTENT")

    return {
        "receipt_sha256": receipt_sha,
        "png_path": str(png_path),
        "png_sha256": actual_sha,
        "png_size_bytes": actual_size,
    }


def build_runtime_envelope_admission(
    inference_receipt: dict[str, Any],
    *,
    inference_receipt_file_sha256: str,
    repo_root: Path,
) -> dict[str, Any]:
    if not _is_sha256(inference_receipt_file_sha256):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_RECEIPT_FILE_SHA_INVALID")
    evidence = verify_single_inference_artifact(inference_receipt, repo_root=repo_root)
    payload = {
        "schema": RUNTIME_ENVELOPE_ADMISSION_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_MEASUREMENT_ADMITTED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_inference_receipt_sha256": evidence["receipt_sha256"],
        "source_inference_receipt_file_sha256": inference_receipt_file_sha256,
        "source_engineering_png_path": evidence["png_path"],
        "source_engineering_png_sha256": evidence["png_sha256"],
        "source_engineering_png_size_bytes": evidence["png_size_bytes"],
        "gpu_name": inference_receipt.get("gpu_name"),
        "torch_version": inference_receipt.get("torch_version"),
        "cuda_version": inference_receipt.get("cuda_version"),
        "diffusers_version": inference_receipt.get("diffusers_version"),
        "native_bf16": True,
        "observed_gpu_total_vram_gb": inference_receipt.get("gpu_total_vram_gb"),
        "observed_gpu_free_vram_gb_before": inference_receipt.get("gpu_free_vram_gb_before"),
        "observed_gpu_free_vram_gb_after": inference_receipt.get("gpu_free_vram_gb_after"),
        "observed_max_cuda_allocated_gb": inference_receipt.get("max_cuda_allocated_gb"),
        "observed_max_cuda_reserved_gb": inference_receipt.get("max_cuda_reserved_gb"),
        "observed_process_max_rss_gb": inference_receipt.get("process_max_rss_gb"),
        "observed_elapsed_seconds": inference_receipt.get("elapsed_seconds"),
        "runtime_envelope_measurement_admitted": True,
        "engineering_evidence_only": True,
        "source_pixels_canonical_reusable": False,
        "runtime_floor_proven": False,
        "local_runtime_qualified": False,
        "canonical_generation_authorized": False,
        "queue_mutated": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    payload["admission_sha256"] = sha256_json(payload)
    return payload


def verify_runtime_envelope_admission(admission: dict[str, Any]) -> str:
    if admission.get("schema") != RUNTIME_ENVELOPE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_SCHEMA_MISMATCH")
    if admission.get("status") != "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_MEASUREMENT_ADMITTED":
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_STATUS_MISMATCH")
    if admission.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or admission.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_MODEL_MISMATCH")
    if admission.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_COST_MODE_MISMATCH")
    for field in (
        "source_inference_receipt_sha256",
        "source_inference_receipt_file_sha256",
        "source_engineering_png_sha256",
    ):
        if not _is_sha256(admission.get(field)):
            raise ValueError(f"QWEN_RUNTIME_ENVELOPE_ADMISSION_SHA_INVALID:{field}")
    if admission.get("runtime_envelope_measurement_admitted") is not True or admission.get("engineering_evidence_only") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_BOUNDARY_MISSING")
    for field in (
        "source_pixels_canonical_reusable",
        "runtime_floor_proven",
        "local_runtime_qualified",
        "canonical_generation_authorized",
        "queue_mutated",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if admission.get(field) is not False:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_AUTHORITY_FORBIDDEN")
    claimed = admission.get("admission_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_DIGEST_INVALID")
    unsigned = dict(admission)
    unsigned.pop("admission_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_ADMISSION_DIGEST_MISMATCH")
    return actual

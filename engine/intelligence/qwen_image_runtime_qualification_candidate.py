"""Fail-closed normalization of a measured Qwen Image 2512 runtime envelope.

This CPU-only layer accepts only a complete Change Set 230 envelope from one
coherent runtime environment, derives conservative measured bounds, and emits a
SHA-bound qualification *candidate*. It never grants runtime, canonical, Golden,
or publication authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_runtime_envelope_executor import RUNTIME_ENVELOPE_EXECUTION_SCHEMA, verify_runtime_envelope_execution_receipt
from engine.intelligence.qwen_image_runtime_envelope_plan import PROBES

RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA = "pul7sar-phase18-qwen-image-2512-runtime-qualification-candidate-v1"
_AUTHORITY_FIELDS = (
    "runtime_floor_proven", "local_runtime_qualified", "canonical_generation_authorized",
    "canonical_pixels_reusable", "queue_mutated", "semantic_approved",
    "human_visual_review_approved", "golden_quality_approved", "publication_ready",
)
_IDENTITY_FIELDS = (
    "gpu_name", "gpu_total_vram_gb", "torch_version", "cuda_version",
    "diffusers_version", "pipeline_class", "dtype", "offload_mode", "native_bf16",
)
_SUMMARY_FIELDS = (
    "largest_successful_width", "largest_successful_height", "largest_successful_steps",
    "minimum_free_vram_before_gb", "minimum_free_vram_after_gb",
    "maximum_cuda_allocated_gb", "maximum_cuda_reserved_gb",
    "maximum_process_rss_gb", "maximum_elapsed_seconds",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) > 0


def _coherent_runtime_identity(results: list[dict[str, Any]]) -> dict[str, Any]:
    identity: dict[str, Any] = {}
    for field in _IDENTITY_FIELDS:
        values = [item.get(field) for item in results]
        first = values[0]
        if any(value != first for value in values[1:]):
            raise ValueError(f"QWEN_RUNTIME_QUALIFICATION_CANDIDATE_MIXED_RUNTIME_EVIDENCE:{field}")
        identity[field] = first
    if identity.get("pipeline_class") != "QwenImagePipeline":
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_PIPELINE_MISMATCH")
    if identity.get("native_bf16") is not True:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_BF16_UNPROVEN")
    if not _positive_number(identity.get("gpu_total_vram_gb")):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_TOTAL_VRAM_INVALID")
    return identity


def _derive_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    telemetry = (
        "gpu_free_vram_gb_before", "gpu_free_vram_gb_after", "max_cuda_allocated_gb",
        "max_cuda_reserved_gb", "process_max_rss_gb", "elapsed_seconds",
    )
    for item in results:
        for field in telemetry:
            if not _positive_number(item.get(field)):
                raise ValueError(f"QWEN_RUNTIME_QUALIFICATION_CANDIDATE_TELEMETRY_INVALID:{field}")
    summary = {
        "largest_successful_width": max(int(item["width"]) for item in results),
        "largest_successful_height": max(int(item["height"]) for item in results),
        "largest_successful_steps": max(int(item["steps"]) for item in results),
        "minimum_free_vram_before_gb": min(float(item["gpu_free_vram_gb_before"]) for item in results),
        "minimum_free_vram_after_gb": min(float(item["gpu_free_vram_gb_after"]) for item in results),
        "maximum_cuda_allocated_gb": max(float(item["max_cuda_allocated_gb"]) for item in results),
        "maximum_cuda_reserved_gb": max(float(item["max_cuda_reserved_gb"]) for item in results),
        "maximum_process_rss_gb": max(float(item["process_max_rss_gb"]) for item in results),
        "maximum_elapsed_seconds": max(float(item["elapsed_seconds"]) for item in results),
    }
    return summary


def _validate_summary(summary: Any, identity: dict[str, Any]) -> None:
    if not isinstance(summary, dict) or set(summary) != set(_SUMMARY_FIELDS):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_INVALID")
    for field in _SUMMARY_FIELDS:
        if not _positive_number(summary.get(field)):
            raise ValueError(f"QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_INVALID:{field}")
    if int(summary["largest_successful_width"]) != max(int(item["width"]) for item in PROBES):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_GEOMETRY_DRIFT")
    if int(summary["largest_successful_height"]) != max(int(item["height"]) for item in PROBES):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_GEOMETRY_DRIFT")
    if int(summary["largest_successful_steps"]) != max(int(item["steps"]) for item in PROBES):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_STEPS_DRIFT")
    if float(summary["maximum_cuda_allocated_gb"]) > float(summary["maximum_cuda_reserved_gb"]):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_CUDA_INCONSISTENT")
    total_vram = float(identity["gpu_total_vram_gb"])
    if float(summary["minimum_free_vram_before_gb"]) > total_vram or float(summary["minimum_free_vram_after_gb"]) > total_vram:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SUMMARY_VRAM_INCONSISTENT")


def build_runtime_qualification_candidate(execution_receipt: dict[str, Any], *, execution_file_sha256: str, repo_root: Path | None = None) -> dict[str, Any]:
    execution_sha = verify_runtime_envelope_execution_receipt(execution_receipt, repo_root=repo_root)
    if execution_receipt.get("schema") != RUNTIME_ENVELOPE_EXECUTION_SCHEMA:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_EXECUTION_SCHEMA_MISMATCH")
    if not _is_sha256(execution_file_sha256):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_FILE_SHA_INVALID")
    if execution_receipt.get("status") != "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_MEASURED" or execution_receipt.get("all_planned_probes_completed") is not True:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_ENVELOPE_NOT_COMPLETE")
    results = execution_receipt.get("probe_results")
    if not isinstance(results, list) or len(results) != len(PROBES):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_PROBE_COUNT_MISMATCH")
    if any(item.get("inference_succeeded") is not True for item in results):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_PROBE_FAILURE_PRESENT")

    identity = _coherent_runtime_identity(results)
    summary = _derive_summary(results)
    _validate_summary(summary, identity)
    payload = {
        "schema": RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_QUALIFICATION_CANDIDATE_READY",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_execution_sha256": execution_sha,
        "source_execution_file_sha256": execution_file_sha256,
        "runtime_identity": identity,
        "measured_envelope_summary": summary,
        "same_runtime_environment_proven": True,
        "all_locked_probes_succeeded": True,
        "candidate_ready_for_explicit_qualification_review": True,
        "engineering_evidence_only": True,
        **{field: False for field in _AUTHORITY_FIELDS},
    }
    payload["candidate_sha256"] = sha256_json(payload)
    return payload


def verify_runtime_qualification_candidate(candidate: dict[str, Any]) -> str:
    if candidate.get("schema") != RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA_MISMATCH")
    if candidate.get("status") != "QWEN_IMAGE_2512_RUNTIME_QUALIFICATION_CANDIDATE_READY":
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_STATUS_MISMATCH")
    if candidate.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or candidate.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_MODEL_MISMATCH")
    if candidate.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_COST_MODE_MISMATCH")
    for field in ("source_execution_sha256", "source_execution_file_sha256"):
        if not _is_sha256(candidate.get(field)):
            raise ValueError(f"QWEN_RUNTIME_QUALIFICATION_CANDIDATE_SOURCE_SHA_INVALID:{field}")
    if candidate.get("same_runtime_environment_proven") is not True or candidate.get("all_locked_probes_succeeded") is not True:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_EVIDENCE_UNPROVEN")
    if candidate.get("candidate_ready_for_explicit_qualification_review") is not True or candidate.get("engineering_evidence_only") is not True:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_REVIEW_BOUNDARY_MISSING")

    identity = candidate.get("runtime_identity")
    if not isinstance(identity, dict) or set(identity) != set(_IDENTITY_FIELDS):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_IDENTITY_INVALID")
    if identity.get("pipeline_class") != "QwenImagePipeline" or identity.get("native_bf16") is not True:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_IDENTITY_INVALID")
    if not _positive_number(identity.get("gpu_total_vram_gb")):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_TOTAL_VRAM_INVALID")
    _validate_summary(candidate.get("measured_envelope_summary"), identity)

    for field in _AUTHORITY_FIELDS:
        if candidate.get(field) is not False:
            raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_AUTHORITY_FORBIDDEN")
    claimed = candidate.get("candidate_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_DIGEST_INVALID")
    unsigned = dict(candidate)
    unsigned.pop("candidate_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_DIGEST_MISMATCH")
    return actual

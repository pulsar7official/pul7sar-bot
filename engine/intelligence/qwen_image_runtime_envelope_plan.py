"""Immutable, non-authoritative Qwen Image 2512 runtime-envelope measurement plan.

This module never runs CUDA or inference. It converts a verified Change Set 228
admission into a byte-addressed experiment plan for a future compatible $0-local
host. The plan cannot qualify a runtime, create canonical pixels, or authorize
publication.
"""
from __future__ import annotations

from typing import Any

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_runtime_envelope_admission import (
    RUNTIME_ENVELOPE_ADMISSION_SCHEMA,
    verify_runtime_envelope_admission,
)

RUNTIME_ENVELOPE_PLAN_SCHEMA = "pul7sar-phase18-qwen-image-2512-runtime-envelope-plan-v1"
OFFLOAD_MODE = "sequential_cpu"
DTYPE = "bfloat16"
# Ordered low-risk engineering probes. These are measurement points, not Golden settings.
PROBES = (
    {"probe_id": "env-512x512-s4", "width": 512, "height": 512, "steps": 4},
    {"probe_id": "env-768x768-s6", "width": 768, "height": 768, "steps": 6},
    {"probe_id": "env-1024x1024-s8", "width": 1024, "height": 1024, "steps": 8},
)
STOP_CONDITIONS = (
    "cuda_oom",
    "child_nonzero_exit",
    "missing_or_invalid_png",
    "native_bf16_lost",
    "offload_contract_drift",
    "telemetry_missing_or_inconsistent",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def build_runtime_envelope_plan(admission: dict[str, Any], *, admission_file_sha256: str) -> dict[str, Any]:
    admission_sha = verify_runtime_envelope_admission(admission)
    if admission.get("schema") != RUNTIME_ENVELOPE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_ADMISSION_SCHEMA_MISMATCH")
    if not _is_sha256(admission_file_sha256):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_ADMISSION_FILE_SHA_INVALID")
    payload = {
        "schema": RUNTIME_ENVELOPE_PLAN_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_PLAN_LOCKED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_admission_sha256": admission_sha,
        "source_admission_file_sha256": admission_file_sha256,
        "source_engineering_png_sha256": admission.get("source_engineering_png_sha256"),
        "required_dtype": DTYPE,
        "required_offload_mode": OFFLOAD_MODE,
        "probe_order": [dict(item) for item in PROBES],
        "stop_conditions": list(STOP_CONDITIONS),
        "stop_on_first_failure": True,
        "reuse_same_seed_and_identity_neutral_prompt_family": True,
        "measurement_plan_only": True,
        "engineering_evidence_only": True,
        "runtime_floor_proven": False,
        "local_runtime_qualified": False,
        "canonical_generation_authorized": False,
        "canonical_pixels_reusable": False,
        "queue_mutated": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    payload["plan_sha256"] = sha256_json(payload)
    return payload


def verify_runtime_envelope_plan(plan: dict[str, Any]) -> str:
    if plan.get("schema") != RUNTIME_ENVELOPE_PLAN_SCHEMA or plan.get("status") != "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_PLAN_LOCKED":
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_SCHEMA_OR_STATUS_MISMATCH")
    if plan.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or plan.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_MODEL_MISMATCH")
    if plan.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_COST_MODE_MISMATCH")
    for field in ("source_admission_sha256", "source_admission_file_sha256", "source_engineering_png_sha256"):
        if not _is_sha256(plan.get(field)):
            raise ValueError(f"QWEN_RUNTIME_ENVELOPE_PLAN_SHA_INVALID:{field}")
    if plan.get("required_dtype") != DTYPE or plan.get("required_offload_mode") != OFFLOAD_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_RUNTIME_CONTRACT_DRIFT")
    if plan.get("probe_order") != [dict(item) for item in PROBES]:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_PROBE_ORDER_DRIFT")
    if plan.get("stop_conditions") != list(STOP_CONDITIONS) or plan.get("stop_on_first_failure") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_STOP_POLICY_DRIFT")
    if plan.get("reuse_same_seed_and_identity_neutral_prompt_family") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_COMPARABILITY_BOUNDARY_MISSING")
    if plan.get("measurement_plan_only") is not True or plan.get("engineering_evidence_only") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_BOUNDARY_MISSING")
    for field in (
        "runtime_floor_proven", "local_runtime_qualified", "canonical_generation_authorized",
        "canonical_pixels_reusable", "queue_mutated", "semantic_approved",
        "human_visual_review_approved", "golden_quality_approved", "publication_ready",
    ):
        if plan.get(field) is not False:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_AUTHORITY_FORBIDDEN")
    claimed = plan.get("plan_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_DIGEST_INVALID")
    unsigned = dict(plan)
    unsigned.pop("plan_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_PLAN_DIGEST_MISMATCH")
    return actual

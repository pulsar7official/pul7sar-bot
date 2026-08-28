"""Fail-closed evidence contract for Qwen Image 2512 runtime-envelope execution.

This module does not itself run CUDA. It validates a locked Change Set 229 plan,
records the ordered observations produced by a future compatible $0-local host,
and byte-binds any engineering PNGs. A successful envelope is engineering
evidence only: it does not establish a production runtime floor, authorize
canonical generation, or create Golden/publication evidence.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import (
    COST_MODE,
    PROBE_GUIDANCE_SCALE,
    PROBE_PROMPT,
    PROBE_SEED,
    sha256_file,
    sha256_json,
    validate_probe_prompt,
)
from engine.intelligence.qwen_image_runtime_envelope_plan import (
    DTYPE,
    OFFLOAD_MODE,
    PROBES,
    RUNTIME_ENVELOPE_PLAN_SCHEMA,
    verify_runtime_envelope_plan,
)

RUNTIME_ENVELOPE_EXECUTION_SCHEMA = "pul7sar-phase18-qwen-image-2512-runtime-envelope-execution-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and float(value) > 0


def _repo_bound_path(raw: Any, repo_root: Path) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_PATH_INVALID")
    root = repo_root.resolve()
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.is_relative_to(root):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_PATH_ESCAPE")
    return path


def validate_plan_for_execution(plan: dict[str, Any], *, plan_file_sha256: str) -> str:
    plan_sha = verify_runtime_envelope_plan(plan)
    if plan.get("schema") != RUNTIME_ENVELOPE_PLAN_SCHEMA:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PLAN_SCHEMA_MISMATCH")
    if not _is_sha256(plan_file_sha256):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PLAN_FILE_SHA_INVALID")
    return plan_sha


def _expected_probe(index: int) -> dict[str, Any]:
    return dict(PROBES[index])


def _validate_probe_observation(observation: dict[str, Any], expected: dict[str, Any], *, repo_root: Path | None) -> bool:
    for field in ("probe_id", "width", "height", "steps"):
        if observation.get(field) != expected[field]:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PROBE_PARAMETER_DRIFT")
    if observation.get("seed") != PROBE_SEED or observation.get("guidance_scale") != PROBE_GUIDANCE_SCALE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_COMPARABILITY_DRIFT")
    if observation.get("dtype") != DTYPE or observation.get("offload_mode") != OFFLOAD_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_RUNTIME_CONTRACT_DRIFT")
    if observation.get("prompt_sha256") != hashlib.sha256(validate_probe_prompt(PROBE_PROMPT).encode("utf-8")).hexdigest():
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PROMPT_DRIFT")

    exit_code = observation.get("child_exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_CHILD_EXIT_INVALID")
    succeeded = observation.get("inference_succeeded") is True
    if succeeded != (exit_code == 0):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_OUTCOME_INCONSISTENT")

    if succeeded:
        if observation.get("pipeline_class") != "QwenImagePipeline" or observation.get("native_bf16") is not True:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PIPELINE_OR_BF16_UNPROVEN")
        for field in (
            "gpu_total_vram_gb", "gpu_free_vram_gb_before", "gpu_free_vram_gb_after",
            "max_cuda_allocated_gb", "max_cuda_reserved_gb", "process_max_rss_gb", "elapsed_seconds",
        ):
            if not _positive_number(observation.get(field)):
                raise ValueError(f"QWEN_RUNTIME_ENVELOPE_EXECUTION_TELEMETRY_INVALID:{field}")
        if float(observation["max_cuda_allocated_gb"]) > float(observation["max_cuda_reserved_gb"]):
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_CUDA_TELEMETRY_INCONSISTENT")
        if float(observation["gpu_free_vram_gb_before"]) > float(observation["gpu_total_vram_gb"]) or float(observation["gpu_free_vram_gb_after"]) > float(observation["gpu_total_vram_gb"]):
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_VRAM_TELEMETRY_INCONSISTENT")
        if not _is_sha256(observation.get("output_png_sha256")):
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_SHA_INVALID")
        if not isinstance(observation.get("output_png_size_bytes"), int) or observation["output_png_size_bytes"] <= 8:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_SIZE_INVALID")
        if observation.get("failure_type") is not None or observation.get("failure_message") is not None:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_SUCCESS_FAILURE_FIELDS_PRESENT")
        if repo_root is not None:
            png = _repo_bound_path(observation.get("output_png_path"), repo_root)
            if not png.is_file() or png.read_bytes()[:8] != PNG_SIGNATURE:
                raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_MISSING_OR_INVALID")
            if png.stat().st_size != observation["output_png_size_bytes"]:
                raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_SIZE_MISMATCH")
            if sha256_file(png) != observation["output_png_sha256"]:
                raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_PNG_SHA_MISMATCH")
    else:
        if observation.get("output_png_path") is not None or observation.get("output_png_sha256") is not None or observation.get("output_png_size_bytes") is not None:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_FAILED_PROBE_HAS_PNG")
        if not isinstance(observation.get("failure_type"), str) or not observation["failure_type"].strip():
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_FAILURE_TYPE_REQUIRED")
    return succeeded


def build_runtime_envelope_execution_receipt(
    plan: dict[str, Any],
    *,
    plan_file_sha256: str,
    exact_snapshot_path: str,
    observations: list[dict[str, Any]],
    repo_root: Path | None = None,
) -> dict[str, Any]:
    plan_sha = validate_plan_for_execution(plan, plan_file_sha256=plan_file_sha256)
    snapshot = Path(str(exact_snapshot_path)).expanduser().resolve()
    if snapshot.name != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_SNAPSHOT_REVISION_MISMATCH")
    if not observations or len(observations) > len(PROBES):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_OBSERVATION_COUNT_INVALID")

    normalized: list[dict[str, Any]] = []
    failure_seen = False
    for index, raw in enumerate(observations):
        if failure_seen:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_CONTINUED_AFTER_FAILURE")
        item = dict(raw)
        succeeded = _validate_probe_observation(item, _expected_probe(index), repo_root=repo_root)
        normalized.append(item)
        failure_seen = not succeeded
    completed_all = len(normalized) == len(PROBES) and not failure_seen
    if not completed_all and not failure_seen:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_INCOMPLETE_WITHOUT_FAILURE")

    payload = {
        "schema": RUNTIME_ENVELOPE_EXECUTION_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_MEASURED" if completed_all else "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_STOPPED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_plan_sha256": plan_sha,
        "source_plan_file_sha256": plan_file_sha256,
        "source_admission_sha256": plan.get("source_admission_sha256"),
        "source_admission_file_sha256": plan.get("source_admission_file_sha256"),
        "exact_snapshot_path": str(snapshot),
        "required_dtype": DTYPE,
        "required_offload_mode": OFFLOAD_MODE,
        "probe_prompt_sha256": hashlib.sha256(validate_probe_prompt(PROBE_PROMPT).encode("utf-8")).hexdigest(),
        "probe_seed": PROBE_SEED,
        "probe_guidance_scale": PROBE_GUIDANCE_SCALE,
        "probe_results": normalized,
        "completed_probe_count": len(normalized),
        "all_planned_probes_completed": completed_all,
        "stopped_on_first_failure": failure_seen,
        "observed_envelope_only": True,
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
    payload["execution_sha256"] = sha256_json(payload)
    return payload


def verify_runtime_envelope_execution_receipt(receipt: dict[str, Any], *, repo_root: Path | None = None) -> str:
    if receipt.get("schema") != RUNTIME_ENVELOPE_EXECUTION_SCHEMA:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_SCHEMA_MISMATCH")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_MODEL_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_COST_MODE_MISMATCH")
    for field in ("source_plan_sha256", "source_plan_file_sha256", "source_admission_sha256", "source_admission_file_sha256"):
        if not _is_sha256(receipt.get(field)):
            raise ValueError(f"QWEN_RUNTIME_ENVELOPE_EXECUTION_SOURCE_SHA_INVALID:{field}")
    snapshot = receipt.get("exact_snapshot_path")
    if not isinstance(snapshot, str) or Path(snapshot).name != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_SNAPSHOT_REVISION_MISMATCH")
    if receipt.get("required_dtype") != DTYPE or receipt.get("required_offload_mode") != OFFLOAD_MODE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_RUNTIME_CONTRACT_DRIFT")
    expected_prompt_sha = hashlib.sha256(validate_probe_prompt(PROBE_PROMPT).encode("utf-8")).hexdigest()
    if receipt.get("probe_prompt_sha256") != expected_prompt_sha or receipt.get("probe_seed") != PROBE_SEED or receipt.get("probe_guidance_scale") != PROBE_GUIDANCE_SCALE:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_COMPARABILITY_DRIFT")

    results = receipt.get("probe_results")
    if not isinstance(results, list) or not results or len(results) > len(PROBES):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_RESULTS_INVALID")
    failure_seen = False
    for index, item in enumerate(results):
        if failure_seen:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_CONTINUED_AFTER_FAILURE")
        if not isinstance(item, dict):
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_RESULT_NOT_OBJECT")
        succeeded = _validate_probe_observation(item, _expected_probe(index), repo_root=repo_root)
        failure_seen = not succeeded
    completed_all = len(results) == len(PROBES) and not failure_seen
    expected_status = "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_MEASURED" if completed_all else "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_STOPPED"
    if receipt.get("status") != expected_status or receipt.get("completed_probe_count") != len(results):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_OUTCOME_MISMATCH")
    if receipt.get("all_planned_probes_completed") is not completed_all or receipt.get("stopped_on_first_failure") is not failure_seen:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_STOP_POLICY_MISMATCH")
    if not completed_all and not failure_seen:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_INCOMPLETE_WITHOUT_FAILURE")
    if receipt.get("observed_envelope_only") is not True or receipt.get("engineering_evidence_only") is not True:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_BOUNDARY_MISSING")
    for field in (
        "runtime_floor_proven", "local_runtime_qualified", "canonical_generation_authorized",
        "canonical_pixels_reusable", "queue_mutated", "semantic_approved",
        "human_visual_review_approved", "golden_quality_approved", "publication_ready",
    ):
        if receipt.get(field) is not False:
            raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_AUTHORITY_FORBIDDEN")
    claimed = receipt.get("execution_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_DIGEST_INVALID")
    unsigned = dict(receipt)
    unsigned.pop("execution_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_RUNTIME_ENVELOPE_EXECUTION_DIGEST_MISMATCH")
    return actual

"""Fail-closed same-host Qwen Image 2512 pipeline-load/offload recheck.

Change Set 260 consumes one exact Change Set 259 receipt, reopens its byte-bound
controlled-trial preflight, and validates an observation that can only be produced
after the pinned QwenImagePipeline has loaded successfully on that same host and
``enable_sequential_cpu_offload()`` has returned successfully.

This is the final live runtime preflight boundary before a *separate* canonical
-generation authorization.  It never executes inference, creates pixels, mutates
publication queues, or grants semantic/Golden/publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_host_identity_recheck import (
    LIVE_HOST_IDENTITY_RECHECK_SCHEMA,
    LIVE_OBSERVABLE_IDENTITY_FIELDS,
)

LIVE_PIPELINE_LOAD_RECHECK_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-live-pipeline-load-recheck-v1"
)
PIPELINE_OBSERVATION_FIELDS = (
    "gpu_name",
    "gpu_total_vram_gb",
    "torch_version",
    "cuda_version",
    "diffusers_version",
    "pipeline_class",
    "dtype",
    "offload_mode",
    "native_bf16",
    "model_id",
    "model_revision",
    "weights_loaded",
    "sequential_cpu_offload_enabled",
)

_FORBIDDEN_TRUE_AUTHORITY = (
    "canonical_generation_authorized",
    "inference_executed",
    "genuine_canonical_inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class LivePipelineLoadRecheckRun:
    output_dir: Path
    story_snapshot_sha256: str
    receipt_path: Path


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if not isinstance(path, Path) or path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload


def _binding(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _inside_repo(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _verify_digest(payload: Mapping[str, Any], field: str, code: str) -> str:
    claimed = payload.get(field)
    if not _is_sha256(claimed):
        raise ValueError(code)
    unsigned = dict(payload)
    unsigned.pop(field, None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError(code)
    return actual


def _load_preflight_from_host_receipt(
    host_receipt: Mapping[str, Any], repo_root: Path
) -> tuple[Path, dict[str, Any]]:
    source = host_receipt.get("source_preflight_contract")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_BINDING_INVALID")
    relative = source.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_PATH_INVALID")
    path = repo_root.resolve() / relative
    canonical = _inside_repo(
        repo_root, path, "QWEN_PIPELINE_RECHECK_PREFLIGHT_OUTSIDE_REPOSITORY"
    )
    if canonical != Path(relative).as_posix():
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_PATH_DRIFT")
    current = _binding(path, "QWEN_PIPELINE_RECHECK_PREFLIGHT_INVALID")
    if source.get("sha256") != current["sha256"] or source.get("byte_size") != current["byte_size"]:
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_BYTE_DRIFT")
    preflight = _read_json(path, "QWEN_PIPELINE_RECHECK_PREFLIGHT_INVALID")
    if preflight.get("schema") != CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA:
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_SCHEMA_DRIFT")
    claimed = source.get("preflight_contract_sha256")
    actual = _verify_digest(
        preflight,
        "preflight_contract_sha256",
        "QWEN_PIPELINE_RECHECK_PREFLIGHT_DIGEST_MISMATCH",
    )
    if claimed != actual:
        raise ValueError("QWEN_PIPELINE_RECHECK_PREFLIGHT_BINDING_DRIFT")
    return path, preflight


def _validate_host_receipt(
    path: Path, repo_root: Path
) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    canonical = _inside_repo(
        repo_root, path, "QWEN_PIPELINE_RECHECK_HOST_RECEIPT_OUTSIDE_REPOSITORY"
    )
    if canonical != path.resolve().relative_to(repo_root.resolve()).as_posix():
        raise ValueError("QWEN_PIPELINE_RECHECK_HOST_RECEIPT_PATH_DRIFT")
    receipt = _read_json(path, "QWEN_PIPELINE_RECHECK_HOST_RECEIPT_INVALID")
    if receipt.get("schema") != LIVE_HOST_IDENTITY_RECHECK_SCHEMA:
        raise ValueError("QWEN_PIPELINE_RECHECK_HOST_RECEIPT_SCHEMA_DRIFT")
    if receipt.get("status") != "QWEN_IMAGE_2512_LIVE_HOST_IDENTITY_SUBSET_RECHECK_PASSED":
        raise ValueError("QWEN_PIPELINE_RECHECK_HOST_RECEIPT_STATUS_DRIFT")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_PIPELINE_RECHECK_MODEL_DRIFT")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_PIPELINE_RECHECK_COST_MODE_DRIFT")
    if receipt.get("live_observable_host_identity_matched") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_HOST_IDENTITY_UNPROVEN")
    if receipt.get("pipeline_load_recheck_required") is not True or receipt.get("offload_execution_recheck_required") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_BOUNDARY_MISSING")
    if receipt.get("production_semantic_replay_executed") is not True or receipt.get("fresh_story_gates_passed") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_FRESH_STORY_AUTHORITY_MISSING")
    if receipt.get("live_host_recheck_passed") is not False or receipt.get("controlled_trial_preflight_valid") is not False:
        raise ValueError("QWEN_PIPELINE_RECHECK_PREMATURE_PREFLIGHT_AUTHORITY")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if receipt.get(field) is not False:
            raise ValueError("QWEN_PIPELINE_RECHECK_HOST_RECEIPT_AUTHORITY_DRIFT")
    _verify_digest(receipt, "receipt_sha256", "QWEN_PIPELINE_RECHECK_HOST_RECEIPT_DIGEST_MISMATCH")
    preflight_path, preflight = _load_preflight_from_host_receipt(receipt, repo_root)
    return receipt, preflight_path, preflight


def _validate_pipeline_observation(
    observation: Mapping[str, Any],
    host_receipt: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(observation, Mapping) or set(observation) != set(PIPELINE_OBSERVATION_FIELDS):
        raise ValueError("QWEN_PIPELINE_RECHECK_OBSERVATION_FIELDS_INVALID")
    expected = preflight.get("expected_runtime_identity")
    host_observed = host_receipt.get("observed_runtime_identity")
    if not isinstance(expected, Mapping) or not isinstance(host_observed, Mapping):
        raise ValueError("QWEN_PIPELINE_RECHECK_RUNTIME_IDENTITY_INVALID")

    for field in LIVE_OBSERVABLE_IDENTITY_FIELDS:
        observed = observation.get(field)
        previous = host_observed.get(field)
        wanted = expected.get(field)
        if field == "gpu_total_vram_gb":
            if not isinstance(observed, (int, float)) or isinstance(observed, bool):
                raise ValueError("QWEN_PIPELINE_RECHECK_VRAM_INVALID")
            if abs(float(observed) - float(previous)) > 0.05 or abs(float(observed) - float(wanted)) > 0.05:
                raise ValueError("QWEN_PIPELINE_RECHECK_HOST_IDENTITY_DRIFT:gpu_total_vram_gb")
        elif observed != previous or observed != wanted:
            raise ValueError(f"QWEN_PIPELINE_RECHECK_HOST_IDENTITY_DRIFT:{field}")

    if observation.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or observation.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_PIPELINE_RECHECK_MODEL_DRIFT")
    for field in ("pipeline_class", "dtype", "offload_mode"):
        if observation.get(field) != expected.get(field):
            raise ValueError(f"QWEN_PIPELINE_RECHECK_RUNTIME_IDENTITY_DRIFT:{field}")
    if observation.get("pipeline_class") != "QwenImagePipeline":
        raise ValueError("QWEN_PIPELINE_RECHECK_PIPELINE_CLASS_INVALID")
    if observation.get("native_bf16") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_NATIVE_BF16_UNPROVEN")
    if observation.get("weights_loaded") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_WEIGHTS_UNPROVEN")
    if observation.get("sequential_cpu_offload_enabled") is not True:
        raise ValueError("QWEN_PIPELINE_RECHECK_OFFLOAD_UNPROVEN")
    if observation.get("offload_mode") != "sequential_cpu_offload":
        raise ValueError("QWEN_PIPELINE_RECHECK_OFFLOAD_MODE_INVALID")
    return dict(observation)


def build_live_pipeline_load_recheck(
    live_host_recheck_path: Path,
    observation: Mapping[str, Any],
    output_dir: Path,
    *,
    repo_root: Path,
) -> LivePipelineLoadRecheckRun:
    """Validate same-host pipeline load/offload evidence without executing inference."""
    if output_dir.exists():
        raise ValueError("QWEN_PIPELINE_RECHECK_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_PIPELINE_RECHECK_OUTPUT_PARENT_INVALID")

    host_receipt, preflight_path, preflight = _validate_host_receipt(
        live_host_recheck_path, repo_root
    )
    observed = _validate_pipeline_observation(observation, host_receipt, preflight)
    story_sha = host_receipt.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_PIPELINE_RECHECK_STORY_SHA_INVALID")

    payload = {
        "schema": LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
        "status": "QWEN_IMAGE_2512_LIVE_PIPELINE_LOAD_RECHECK_PASSED",
        "story_snapshot_sha256": story_sha,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_live_host_recheck": {
            "repository_relative_path": _inside_repo(
                repo_root,
                live_host_recheck_path,
                "QWEN_PIPELINE_RECHECK_HOST_RECEIPT_OUTSIDE_REPOSITORY",
            ),
            **_binding(live_host_recheck_path, "QWEN_PIPELINE_RECHECK_HOST_RECEIPT_INVALID"),
            "receipt_sha256": host_receipt["receipt_sha256"],
        },
        "source_preflight_contract": {
            "repository_relative_path": _inside_repo(
                repo_root,
                preflight_path,
                "QWEN_PIPELINE_RECHECK_PREFLIGHT_OUTSIDE_REPOSITORY",
            ),
            **_binding(preflight_path, "QWEN_PIPELINE_RECHECK_PREFLIGHT_INVALID"),
            "preflight_contract_sha256": preflight["preflight_contract_sha256"],
        },
        "expected_runtime_fingerprint_sha256": preflight.get("expected_runtime_fingerprint_sha256"),
        "observed_runtime_identity": observed,
        "production_semantic_replay_executed": True,
        "fresh_story_gates_passed": True,
        "live_observable_host_identity_matched": True,
        "model_weights_loaded": True,
        "sequential_cpu_offload_enabled": True,
        "live_host_recheck_passed": True,
        "controlled_trial_preflight_valid": True,
        "canonical_generation_authorized": False,
        "inference_executed": False,
        "genuine_canonical_inference_executed": False,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    if not _is_sha256(payload["expected_runtime_fingerprint_sha256"]):
        raise ValueError("QWEN_PIPELINE_RECHECK_EXPECTED_FINGERPRINT_INVALID")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if payload[field] is not False:
            raise RuntimeError("QWEN_PIPELINE_RECHECK_INTERNAL_AUTHORITY_DRIFT")
    payload["receipt_sha256"] = sha256_json(payload)

    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent)))
    published = False
    try:
        receipt_path = staging / "live_pipeline_load_recheck.json"
        receipt_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output_dir)
        published = True
        return LivePipelineLoadRecheckRun(
            output_dir=output_dir,
            story_snapshot_sha256=story_sha,
            receipt_path=output_dir / receipt_path.name,
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)

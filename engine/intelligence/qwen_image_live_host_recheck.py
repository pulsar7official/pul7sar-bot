"""Fail-closed live same-host recheck for Qwen Image 2512 Golden trials.

Change Set 234 turns Change Set 233's live-host requirement into executable evidence.
It does not load the model or run inference. It observes the currently executing CUDA
host/runtime and proves only whether that live identity still matches the exact runtime
identity qualified by Change Set 232 and locked by Change Set 233.

A passing receipt is necessary but never sufficient for canonical generation.
"""
from __future__ import annotations

from typing import Any

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    verify_controlled_golden_trial_preflight_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

LIVE_HOST_RECHECK_SCHEMA = "pul7sar-phase18-qwen-image-2512-live-host-recheck-v1"
_IDENTITY_FIELDS = (
    "gpu_name",
    "gpu_total_vram_gb",
    "torch_version",
    "cuda_version",
    "diffusers_version",
    "pipeline_class",
    "dtype",
    "offload_mode",
    "native_bf16",
)
_FORBIDDEN_AUTHORITY_FIELDS = (
    "runtime_floor_proven",
    "local_runtime_qualified",
    "canonical_generation_authorized",
    "canonical_pixels_reusable",
    "queue_mutated",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def observe_live_runtime_identity() -> dict[str, Any]:
    """Observe the live runtime without loading model weights or running inference."""
    try:
        import torch
    except Exception as exc:  # pragma: no cover - depends on host
        raise RuntimeError(f"QWEN_LIVE_HOST_RECHECK_TORCH_UNAVAILABLE:{type(exc).__name__}") from exc

    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_CUDA_UNAVAILABLE")
    if torch.cuda.device_count() < 1:
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_NO_CUDA_DEVICE")

    try:
        import diffusers
        from diffusers import QwenImagePipeline
    except Exception as exc:  # pragma: no cover - depends on host
        raise RuntimeError(f"QWEN_LIVE_HOST_RECHECK_DIFFUSERS_UNAVAILABLE:{type(exc).__name__}") from exc

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    native_bf16 = bool(torch.cuda.is_bf16_supported())
    if not native_bf16:
        raise RuntimeError("QWEN_LIVE_HOST_RECHECK_NATIVE_BF16_UNAVAILABLE")

    total_vram_gb = float(props.total_memory) / (1024 ** 3)
    return {
        "gpu_name": str(props.name),
        "gpu_total_vram_gb": total_vram_gb,
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda),
        "diffusers_version": str(diffusers.__version__),
        "pipeline_class": QwenImagePipeline.__name__,
        "dtype": "bfloat16",
        "offload_mode": "sequential_cpu",
        "native_bf16": True,
    }


def _validate_identity(identity: Any) -> dict[str, Any]:
    if not isinstance(identity, dict) or set(identity) != set(_IDENTITY_FIELDS):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_IDENTITY_INVALID")
    if identity.get("pipeline_class") != "QwenImagePipeline":
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PIPELINE_MISMATCH")
    if identity.get("dtype") != "bfloat16" or identity.get("offload_mode") != "sequential_cpu":
        raise ValueError("QWEN_LIVE_HOST_RECHECK_RUNTIME_MODE_DRIFT")
    if identity.get("native_bf16") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_BF16_UNPROVEN")
    vram = identity.get("gpu_total_vram_gb")
    if not isinstance(vram, (int, float)) or isinstance(vram, bool) or float(vram) <= 0:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_TOTAL_VRAM_INVALID")
    return dict(identity)


def build_live_host_recheck_receipt(
    contract: dict[str, Any],
    qualification: dict[str, Any],
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    qualification_file_sha256: str,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    live_identity: dict[str, Any] | None = None,
    repo_root=None,
) -> dict[str, Any]:
    contract_sha = verify_controlled_golden_trial_preflight_contract(
        contract,
        qualification,
        candidate,
        execution_receipt,
        qualification_file_sha256=qualification_file_sha256,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )
    observed = _validate_identity(live_identity if live_identity is not None else observe_live_runtime_identity())
    expected = _validate_identity(contract.get("expected_runtime_identity"))
    if observed != expected:
        mismatches = [field for field in _IDENTITY_FIELDS if observed.get(field) != expected.get(field)]
        raise ValueError("QWEN_LIVE_HOST_RECHECK_IDENTITY_MISMATCH:" + ",".join(mismatches))

    expected_fingerprint = contract.get("expected_runtime_fingerprint_sha256")
    live_fingerprint = sha256_json({"runtime_identity": observed})
    if not _is_sha256(expected_fingerprint) or live_fingerprint != expected_fingerprint:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_FINGERPRINT_MISMATCH")

    payload = {
        "schema": LIVE_HOST_RECHECK_SCHEMA,
        "status": "QWEN_IMAGE_2512_LIVE_HOST_IDENTITY_RECHECK_PASSED",
        "cost_mode": COST_MODE,
        "source_preflight_contract_sha256": contract_sha,
        "expected_runtime_fingerprint_sha256": expected_fingerprint,
        "live_runtime_identity": observed,
        "live_runtime_fingerprint_sha256": live_fingerprint,
        "live_host_recheck_passed": True,
        "exact_observed_runtime_match": True,
        "model_weights_loaded": False,
        "inference_executed": False,
        "fresh_story_gates_passed": False,
        "controlled_trial_preflight_valid": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["live_host_recheck_sha256"] = sha256_json(payload)
    return payload


def verify_live_host_recheck_receipt(receipt: dict[str, Any], contract: dict[str, Any]) -> str:
    if receipt.get("schema") != LIVE_HOST_RECHECK_SCHEMA:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_SCHEMA_MISMATCH")
    if receipt.get("status") != "QWEN_IMAGE_2512_LIVE_HOST_IDENTITY_RECHECK_PASSED":
        raise ValueError("QWEN_LIVE_HOST_RECHECK_STATUS_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_COST_MODE_MISMATCH")
    if receipt.get("source_preflight_contract_sha256") != contract.get("preflight_contract_sha256"):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_CONTRACT_SHA_MISMATCH")

    live = _validate_identity(receipt.get("live_runtime_identity"))
    expected = _validate_identity(contract.get("expected_runtime_identity"))
    if live != expected:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_IDENTITY_DRIFT")
    fingerprint = sha256_json({"runtime_identity": live})
    if receipt.get("live_runtime_fingerprint_sha256") != fingerprint:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_LIVE_FINGERPRINT_DRIFT")
    if receipt.get("expected_runtime_fingerprint_sha256") != contract.get("expected_runtime_fingerprint_sha256"):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_EXPECTED_FINGERPRINT_DRIFT")
    if fingerprint != contract.get("expected_runtime_fingerprint_sha256"):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_FINGERPRINT_MISMATCH")

    if receipt.get("live_host_recheck_passed") is not True or receipt.get("exact_observed_runtime_match") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_MATCH_UNPROVEN")
    required_false = (
        "model_weights_loaded",
        "inference_executed",
        "fresh_story_gates_passed",
        "controlled_trial_preflight_valid",
        "genuine_golden_png_created",
        *_FORBIDDEN_AUTHORITY_FIELDS,
    )
    if any(receipt.get(field) is not False for field in required_false):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_AUTHORITY_FORBIDDEN")

    claimed = receipt.get("live_host_recheck_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_DIGEST_INVALID")
    unsigned = dict(receipt)
    unsigned.pop("live_host_recheck_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_DIGEST_MISMATCH")
    return actual

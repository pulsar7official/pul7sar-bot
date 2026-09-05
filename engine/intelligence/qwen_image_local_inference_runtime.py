"""Local-only runtime loader for story-authorized Qwen Image canonical inference.

CS289 closes the network/mutable-model gap at the actual inference edge. The
loader accepts only the exact already-local approved snapshot, requires the
$0-local execution lock, re-runs CS287 static preflight, loads in native BF16
with ``local_files_only=True``, enables sequential CPU offload, and replays the
runtime identity expected by the CS260/CS261 authorization chain.

CS296 adds an exact pre-model-load host-identity replay. GPU identity, VRAM,
PyTorch/CUDA versions, Diffusers version, pipeline class availability, dtype,
offload contract, BF16 requirement, and pinned model identity must already match
CS260 before ``from_pretrained`` is allowed to run. Resource sufficiency itself
is still proven only by a genuine model-load/inference attempt; no VRAM floor is
invented here.

It does not call the pipeline and grants no factual, semantic, quality, Golden,
or publication authority.
"""
from __future__ import annotations

from importlib import import_module
import os
from pathlib import Path
from typing import Any, Mapping

from .approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from .qwen_image_gpu_readiness import inspect_qwen_image_gpu_readiness
from .qwen_image_runtime_envelope_plan import DTYPE, OFFLOAD_MODE

REQUIRED_COST_MODE = "$0-local"


def _expected_identity(cs260: Mapping[str, Any]) -> Mapping[str, Any]:
    expected = cs260.get("observed_runtime_identity")
    if not isinstance(expected, Mapping):
        raise RuntimeError("QWEN_LOCAL_INFERENCE_RUNTIME_IDENTITY_FIELDS_DRIFT")
    return expected


def _pre_model_load_identity(*, torch: Any, diffusers: Any) -> dict[str, Any]:
    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    return {
        "gpu_name": torch.cuda.get_device_name(device),
        "gpu_total_vram_gb": float(props.total_memory) / float(1024 ** 3),
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda),
        "diffusers_version": str(diffusers.__version__),
        "pipeline_class": "QwenImagePipeline",
        "dtype": DTYPE,
        "offload_mode": OFFLOAD_MODE,
        "native_bf16": True,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
    }


def _assert_identity_fields(
    observed: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    prefix: str,
) -> None:
    for field, value in observed.items():
        wanted = expected.get(field)
        if field == "gpu_total_vram_gb":
            if not isinstance(wanted, (int, float)) or isinstance(wanted, bool):
                raise RuntimeError(f"{prefix}_VRAM_INVALID")
            if abs(float(value) - float(wanted)) > 0.05:
                raise RuntimeError(f"{prefix}_IDENTITY_DRIFT:gpu_total_vram_gb")
        elif value != wanted:
            raise RuntimeError(f"{prefix}_IDENTITY_DRIFT:{field}")


def load_local_inference_runtime(
    *,
    cs260: Mapping[str, Any],
    snapshot_path: str | Path,
    cost_mode: str | None = None,
):
    """Return ``(torch, pipeline, live_identity)`` for one authorized attempt.

    No network fallback is permitted. Any mismatch fails before inference, and
    all host-observable identity drift fails before model weights are loaded.
    """
    effective_cost_mode = cost_mode if cost_mode is not None else os.environ.get("PUL7SAR_PHASE18_COST_MODE", "")
    if effective_cost_mode != REQUIRED_COST_MODE:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_ZERO_COST_MODE_NOT_LOCKED")

    normalized_snapshot = str(Path(snapshot_path).expanduser().resolve())
    readiness = inspect_qwen_image_gpu_readiness(snapshot_path=normalized_snapshot)
    if not readiness.static_preflight_passed:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_STATIC_PREFLIGHT_FAILED:" + ",".join(readiness.blockers))
    if not readiness.snapshot_revision_verified:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_SNAPSHOT_REVISION_UNVERIFIED")

    try:
        torch = import_module("torch")
        diffusers = import_module("diffusers")
        pipeline_cls = getattr(diffusers, "QwenImagePipeline")
    except Exception as exc:
        raise RuntimeError(f"QWEN_LOCAL_INFERENCE_SOFTWARE_IMPORT_FAILED:{type(exc).__name__}") from exc

    expected = _expected_identity(cs260)
    required_fields = {
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
    }
    if set(expected) != required_fields:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_RUNTIME_IDENTITY_FIELDS_DRIFT")
    if expected.get("weights_loaded") is not True:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_EXPECTED_MODEL_LOAD_AUTHORITY_INVALID")
    if expected.get("sequential_cpu_offload_enabled") is not True:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_EXPECTED_OFFLOAD_AUTHORITY_INVALID")
    if pipeline_cls.__name__ != "QwenImagePipeline":
        raise RuntimeError("QWEN_LOCAL_INFERENCE_PIPELINE_CLASS_INVALID")

    pre_load_live = _pre_model_load_identity(torch=torch, diffusers=diffusers)
    _assert_identity_fields(
        pre_load_live,
        expected,
        prefix="QWEN_LOCAL_INFERENCE_PRE_MODEL_LOAD_RUNTIME",
    )

    pipeline = pipeline_cls.from_pretrained(
        normalized_snapshot,
        torch_dtype=torch.bfloat16,
        local_files_only=True,
    )
    if pipeline.__class__.__name__ != "QwenImagePipeline":
        raise RuntimeError("QWEN_LOCAL_INFERENCE_PIPELINE_CLASS_INVALID")
    pipeline.enable_sequential_cpu_offload()

    live = dict(pre_load_live)
    live["weights_loaded"] = True
    live["sequential_cpu_offload_enabled"] = True
    _assert_identity_fields(
        live,
        expected,
        prefix="QWEN_LOCAL_INFERENCE_RUNTIME",
    )

    return torch, pipeline, live

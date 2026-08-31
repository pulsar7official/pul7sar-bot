"""Local-only runtime loader for story-authorized Qwen Image canonical inference.

CS289 closes the network/mutable-model gap at the actual inference edge. The
loader accepts only the exact already-local approved snapshot, requires the
$0-local execution lock, re-runs CS287 static preflight, loads in native BF16
with ``local_files_only=True``, enables sequential CPU offload, and replays the
runtime identity expected by the CS260/CS261 authorization chain.

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


def load_local_inference_runtime(
    *,
    cs260: Mapping[str, Any],
    snapshot_path: str | Path,
    cost_mode: str | None = None,
):
    """Return ``(torch, pipeline, live_identity)`` for one authorized attempt.

    No network fallback is permitted. Any mismatch fails before inference.
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

    pipeline = pipeline_cls.from_pretrained(
        normalized_snapshot,
        torch_dtype=torch.bfloat16,
        local_files_only=True,
    )
    if pipeline.__class__.__name__ != "QwenImagePipeline":
        raise RuntimeError("QWEN_LOCAL_INFERENCE_PIPELINE_CLASS_INVALID")
    pipeline.enable_sequential_cpu_offload()

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    total_gib = float(props.total_memory) / float(1024 ** 3)
    live = {
        "gpu_name": torch.cuda.get_device_name(device),
        "gpu_total_vram_gb": total_gib,
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda),
        "diffusers_version": str(diffusers.__version__),
        "pipeline_class": pipeline.__class__.__name__,
        "dtype": DTYPE,
        "offload_mode": OFFLOAD_MODE,
        "native_bf16": True,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "weights_loaded": True,
        "sequential_cpu_offload_enabled": True,
    }
    expected = cs260.get("observed_runtime_identity")
    if not isinstance(expected, Mapping) or set(live) != set(expected):
        raise RuntimeError("QWEN_LOCAL_INFERENCE_RUNTIME_IDENTITY_FIELDS_DRIFT")
    for field, value in live.items():
        wanted = expected.get(field)
        if field == "gpu_total_vram_gb":
            if not isinstance(wanted, (int, float)) or isinstance(wanted, bool):
                raise RuntimeError("QWEN_LOCAL_INFERENCE_RUNTIME_VRAM_INVALID")
            if abs(float(value) - float(wanted)) > 0.05:
                raise RuntimeError("QWEN_LOCAL_INFERENCE_RUNTIME_IDENTITY_DRIFT:gpu_total_vram_gb")
        elif value != wanted:
            raise RuntimeError(f"QWEN_LOCAL_INFERENCE_RUNTIME_IDENTITY_DRIFT:{field}")

    return torch, pipeline, live

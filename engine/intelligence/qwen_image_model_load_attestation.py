"""Fail-closed attestation for a genuine local Qwen-Image model-load attempt.

CS288 is deliberately narrower than inference. It may prove that the exact
approved Qwen/Qwen-Image-2512 snapshot can be loaded on a compatible zero-cost
CUDA/BF16 host and that sequential CPU offload can be enabled. It never calls
the pipeline, never creates image pixels, and grants no factual, visual, Golden,
semantic-publication, materialization, or publication-readiness authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import import_module
import os
from pathlib import Path
from typing import Optional

from .approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from .qwen_image_gpu_readiness import inspect_qwen_image_gpu_readiness

SCHEMA = "pul7sar.phase18.qwen_image_model_load_attestation.v1"
REQUIRED_COST_MODE = "$0-local"


@dataclass(frozen=True)
class QwenImageModelLoadAttestation:
    schema: str
    model_id: str
    model_revision: str
    snapshot_path: str
    cost_mode: str
    zero_cost_local_only: bool
    network_allowed: bool
    local_files_only: bool
    static_preflight_passed: bool
    model_load_attempted: bool
    model_loaded: bool
    torch_dtype: str
    sequential_cpu_offload_requested: bool
    sequential_cpu_offload_enabled: bool
    pipeline_class: Optional[str]
    cuda_available: bool
    native_bf16_supported: bool
    genuine_inference_executed: bool
    png_created: bool
    semantic_approved: bool
    genuine_golden_png_created: bool
    publication_ready: bool
    load_error_type: Optional[str]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        return data


def _attestation(
    *,
    snapshot_path: str,
    cost_mode: str,
    static_preflight_passed: bool,
    model_load_attempted: bool,
    model_loaded: bool,
    pipeline_class: Optional[str],
    cuda_available: bool,
    native_bf16_supported: bool,
    sequential_cpu_offload_enabled: bool,
    load_error_type: Optional[str],
    blockers: list[str],
) -> QwenImageModelLoadAttestation:
    return QwenImageModelLoadAttestation(
        schema=SCHEMA,
        model_id=QWEN_IMAGE_2512_MODEL_ID,
        model_revision=QWEN_IMAGE_2512_REVISION,
        snapshot_path=snapshot_path,
        cost_mode=cost_mode,
        zero_cost_local_only=True,
        network_allowed=False,
        local_files_only=True,
        static_preflight_passed=static_preflight_passed,
        model_load_attempted=model_load_attempted,
        model_loaded=model_loaded,
        torch_dtype="bfloat16",
        sequential_cpu_offload_requested=True,
        sequential_cpu_offload_enabled=sequential_cpu_offload_enabled,
        pipeline_class=pipeline_class,
        cuda_available=cuda_available,
        native_bf16_supported=native_bf16_supported,
        genuine_inference_executed=False,
        png_created=False,
        semantic_approved=False,
        genuine_golden_png_created=False,
        publication_ready=False,
        load_error_type=load_error_type,
        blockers=tuple(dict.fromkeys(blockers)),
    )


def attempt_qwen_image_model_load(
    *,
    snapshot_path: str | Path,
    cost_mode: str | None = None,
) -> QwenImageModelLoadAttestation:
    """Attempt one genuine local model load without running inference.

    The approved snapshot must already exist in the local Hugging Face cache.
    No download fallback is permitted. Static preflight and ``$0-local`` cost
    mode must both pass before ``from_pretrained`` is called.
    """
    normalized_snapshot = str(Path(snapshot_path).expanduser().resolve())
    effective_cost_mode = cost_mode if cost_mode is not None else os.environ.get("PUL7SAR_PHASE18_COST_MODE", "")
    readiness = inspect_qwen_image_gpu_readiness(snapshot_path=normalized_snapshot)
    blockers = list(readiness.blockers)

    if effective_cost_mode != REQUIRED_COST_MODE:
        blockers.append("zero_cost_mode_not_locked")

    if blockers:
        return _attestation(
            snapshot_path=normalized_snapshot,
            cost_mode=effective_cost_mode,
            static_preflight_passed=readiness.static_preflight_passed,
            model_load_attempted=False,
            model_loaded=False,
            pipeline_class=None,
            cuda_available=readiness.cuda_available,
            native_bf16_supported=readiness.bf16_supported,
            sequential_cpu_offload_enabled=False,
            load_error_type=None,
            blockers=blockers,
        )

    pipeline = None
    pipeline_class_name: Optional[str] = None
    try:
        torch = import_module("torch")
        diffusers = import_module("diffusers")
        pipeline_cls = getattr(diffusers, "QwenImagePipeline")
        pipeline_class_name = f"{pipeline_cls.__module__}.{pipeline_cls.__name__}"
        pipeline = pipeline_cls.from_pretrained(
            normalized_snapshot,
            torch_dtype=torch.bfloat16,
            local_files_only=True,
        )
        pipeline.enable_sequential_cpu_offload()
        return _attestation(
            snapshot_path=normalized_snapshot,
            cost_mode=effective_cost_mode,
            static_preflight_passed=True,
            model_load_attempted=True,
            model_loaded=True,
            pipeline_class=pipeline_class_name,
            cuda_available=True,
            native_bf16_supported=True,
            sequential_cpu_offload_enabled=True,
            load_error_type=None,
            blockers=[],
        )
    except Exception as exc:  # Real host/resource failures must be recorded, never fabricated away.
        blockers.append("model_load_failed")
        return _attestation(
            snapshot_path=normalized_snapshot,
            cost_mode=effective_cost_mode,
            static_preflight_passed=True,
            model_load_attempted=True,
            model_loaded=False,
            pipeline_class=pipeline_class_name,
            cuda_available=True,
            native_bf16_supported=True,
            sequential_cpu_offload_enabled=False,
            load_error_type=type(exc).__name__,
            blockers=blockers,
        )
    finally:
        if pipeline is not None:
            del pipeline
        try:
            torch = import_module("torch")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

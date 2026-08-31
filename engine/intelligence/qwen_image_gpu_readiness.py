"""Fail-closed, zero-cost static preflight for genuine Qwen-Image execution.

The probe performs local inspection only. It never downloads a model, allocates a
Qwen pipeline, runs inference, or grants any visual/publication authority.
Resource sufficiency is deliberately *not* inferred from an invented VRAM
threshold: only a genuine model-load/inference attempt can prove that.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
import shutil
import subprocess
from typing import Optional

from .approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
    assert_snapshot_revision,
)

SCHEMA = "pul7sar.phase18.qwen_image_gpu_readiness.v1"


@dataclass(frozen=True)
class QwenImageGpuReadiness:
    schema: str
    model_id: str
    model_revision: str
    torch_version: str
    torch_cuda_version: Optional[str]
    cuda_available: bool
    cuda_device_count: int
    bf16_supported: bool
    gpu_name: Optional[str]
    gpu_memory_gib_observed: Optional[float]
    nvidia_smi_available: bool
    qwen_image_pipeline_importable: bool
    sequential_cpu_offload_supported: bool
    snapshot_path: Optional[str]
    snapshot_revision_verified: bool
    network_required: bool
    zero_cost_local_only: bool
    static_preflight_passed: bool
    ready_for_model_load_attempt: bool
    genuine_inference_executed: bool
    ready_for_genuine_inference_claim: bool
    blockers: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        return data


def _nvidia_smi_available() -> bool:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return False
    try:
        completed = subprocess.run(
            [exe, "--query-gpu=name", "--format=csv,noheader"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def inspect_qwen_image_gpu_readiness(*, snapshot_path: str | Path | None = None) -> QwenImageGpuReadiness:
    blockers: list[str] = []
    try:
        torch = import_module("torch")
    except Exception:
        torch = None
        blockers.append("torch_unavailable")

    torch_version = str(getattr(torch, "__version__", "unavailable")) if torch else "unavailable"
    torch_cuda_version = getattr(getattr(torch, "version", None), "cuda", None) if torch else None
    cuda_available = bool(torch and torch.cuda.is_available())
    device_count = int(torch.cuda.device_count()) if cuda_available else 0
    bf16_supported = bool(cuda_available and torch.cuda.is_bf16_supported())
    gpu_name: Optional[str] = None
    gpu_memory_gib: Optional[float] = None
    if cuda_available and device_count > 0:
        props = torch.cuda.get_device_properties(0)
        gpu_name = str(props.name)
        gpu_memory_gib = round(float(props.total_memory) / (1024 ** 3), 2)

    if not cuda_available:
        blockers.append("cuda_unavailable")
    if not torch_cuda_version:
        blockers.append("torch_cuda_runtime_unavailable")
    if device_count < 1:
        blockers.append("no_cuda_device")
    if not bf16_supported:
        blockers.append("native_bf16_unavailable")

    pipeline_importable = False
    sequential_offload_supported = False
    try:
        diffusers = import_module("diffusers")
        pipeline_cls = getattr(diffusers, "QwenImagePipeline", None)
        pipeline_importable = pipeline_cls is not None
        sequential_offload_supported = bool(
            pipeline_cls and hasattr(pipeline_cls, "enable_sequential_cpu_offload")
        )
    except Exception:
        pass
    if not pipeline_importable:
        blockers.append("qwen_image_pipeline_unavailable")
    if not sequential_offload_supported:
        blockers.append("sequential_cpu_offload_unsupported")

    snapshot_verified = False
    normalized_snapshot: Optional[str] = None
    if snapshot_path is None:
        blockers.append("approved_model_snapshot_not_supplied")
    else:
        normalized_snapshot = str(Path(snapshot_path).expanduser().resolve())
        try:
            assert_snapshot_revision(normalized_snapshot, QWEN_IMAGE_2512_REVISION)
            snapshot_verified = True
        except (RuntimeError, ValueError):
            blockers.append("approved_model_snapshot_revision_unverified")

    smi = _nvidia_smi_available()
    if not smi:
        blockers.append("nvidia_smi_unavailable")

    blockers = list(dict.fromkeys(blockers))
    static_pass = not blockers
    return QwenImageGpuReadiness(
        schema=SCHEMA,
        model_id=QWEN_IMAGE_2512_MODEL_ID,
        model_revision=QWEN_IMAGE_2512_REVISION,
        torch_version=torch_version,
        torch_cuda_version=torch_cuda_version,
        cuda_available=cuda_available,
        cuda_device_count=device_count,
        bf16_supported=bf16_supported,
        gpu_name=gpu_name,
        gpu_memory_gib_observed=gpu_memory_gib,
        nvidia_smi_available=smi,
        qwen_image_pipeline_importable=pipeline_importable,
        sequential_cpu_offload_supported=sequential_offload_supported,
        snapshot_path=normalized_snapshot,
        snapshot_revision_verified=snapshot_verified,
        network_required=False,
        zero_cost_local_only=True,
        static_preflight_passed=static_pass,
        ready_for_model_load_attempt=static_pass,
        genuine_inference_executed=False,
        ready_for_genuine_inference_claim=False,
        blockers=tuple(blockers),
    )

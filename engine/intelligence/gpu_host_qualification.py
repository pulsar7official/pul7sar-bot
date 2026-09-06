"""Fail-closed qualification for a Phase 18 Golden GPU host.

This module does not install drivers, PyTorch, Diffusers, model weights, or GitHub
runner software. It turns already-observed host facts into a deterministic receipt
so PUL7SAR can reject unsuitable GPU hosts before enqueueing the first Golden
Visual job.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.zero_cost_models import LocalModelCandidate


@dataclass(frozen=True)
class GpuHostQualification:
    eligible: bool
    reasons: tuple[str, ...]
    model_id: str
    gpu_name: str | None
    gpu_vram_gb: float | None
    gpu_free_vram_gb: float | None
    bf16_supported: bool | None
    compute_capability: str | None
    torch_available: bool
    cuda_available: bool
    runtime_kind: str
    required_vram_gb: float
    cost_mode: str = "$0-local"

    def as_dict(self) -> dict[str, object]:
        return {
            "eligible": self.eligible,
            "reasons": list(self.reasons),
            "model_id": self.model_id,
            "gpu_name": self.gpu_name,
            "gpu_vram_gb": self.gpu_vram_gb,
            "gpu_free_vram_gb": self.gpu_free_vram_gb,
            "bf16_supported": self.bf16_supported,
            "compute_capability": self.compute_capability,
            "torch_available": self.torch_available,
            "cuda_available": self.cuda_available,
            "runtime_kind": self.runtime_kind,
            "required_vram_gb": self.required_vram_gb,
            "cost_mode": self.cost_mode,
        }


class GpuHostQualificationPolicy:
    """Require every hardware property used by the Golden BF16 path to be proven."""

    def evaluate(
        self,
        *,
        runtime: RuntimeHardwareSnapshot,
        model: LocalModelCandidate,
    ) -> GpuHostQualification:
        if not isinstance(runtime, RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")
        if not isinstance(model, LocalModelCandidate):
            raise TypeError("model must be LocalModelCandidate")
        if model.minimum_vram_gb is None:
            raise ValueError("model minimum_vram_gb must be proven before GPU host qualification")

        metadata: Mapping[str, Any] = runtime.metadata
        bf16_supported = metadata.get("bf16_supported")
        compute_capability = metadata.get("compute_capability")
        free_vram = metadata.get("gpu_free_vram_gb")
        free_vram_gb = float(free_vram) if isinstance(free_vram, (int, float)) and not isinstance(free_vram, bool) else None
        reasons: list[str] = []

        if runtime.kind is not RuntimeKind.LOCAL_CUDA:
            reasons.append("runtime kind is not local_cuda")
        if not runtime.torch_available:
            reasons.append("CUDA-enabled PyTorch is not available")
        if not runtime.cuda_available:
            reasons.append("CUDA is not available")
        if not runtime.gpu_name:
            reasons.append("GPU identity could not be proven")
        if runtime.gpu_vram_gb is None:
            reasons.append("GPU VRAM could not be proven")
        elif runtime.gpu_vram_gb < model.minimum_vram_gb:
            reasons.append(
                f"GPU VRAM {runtime.gpu_vram_gb:.3f} GB is below required "
                f"{model.minimum_vram_gb:.3f} GB"
            )
        if free_vram_gb is None:
            reasons.append("live free GPU VRAM could not be proven")
        elif free_vram_gb < model.minimum_vram_gb:
            reasons.append(
                f"live free GPU VRAM {free_vram_gb:.3f} GB is below required "
                f"{model.minimum_vram_gb:.3f} GB"
            )
        if bf16_supported is not True:
            reasons.append("native BF16 support is not proven")
        if not isinstance(compute_capability, str) or not compute_capability.strip():
            reasons.append("CUDA compute capability is not proven")

        return GpuHostQualification(
            eligible=not reasons,
            reasons=tuple(reasons),
            model_id=model.model_id,
            gpu_name=runtime.gpu_name,
            gpu_vram_gb=runtime.gpu_vram_gb,
            gpu_free_vram_gb=free_vram_gb,
            bf16_supported=bf16_supported if isinstance(bf16_supported, bool) else None,
            compute_capability=compute_capability if isinstance(compute_capability, str) else None,
            torch_available=runtime.torch_available,
            cuda_available=runtime.cuda_available,
            runtime_kind=runtime.kind.value,
            required_vram_gb=model.minimum_vram_gb,
        )

    def assert_eligible(self, qualification: GpuHostQualification) -> None:
        if not isinstance(qualification, GpuHostQualification):
            raise TypeError("qualification must be GpuHostQualification")
        if not qualification.eligible:
            raise RuntimeError("GPU host is not Golden-qualified: " + "; ".join(qualification.reasons))

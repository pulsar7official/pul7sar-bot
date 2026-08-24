"""Local zero-cost runtime probing and compatibility checks.

The domain can describe/evaluate local hardware without assuming that PyTorch,
CUDA, or a specific image backend is installed. Runtime probing is best-effort;
provider execution remains blocked unless the declared model requirements are
proven compatible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from importlib import import_module
from types import MappingProxyType
from typing import Any, Mapping

from engine.intelligence.zero_cost_models import LocalModelCandidate


class RuntimeKind(str, Enum):
    LOCAL_CUDA = "local_cuda"
    LOCAL_CPU = "local_cpu"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RuntimeHardwareSnapshot:
    kind: RuntimeKind
    cuda_available: bool
    gpu_name: str | None = None
    gpu_vram_gb: float | None = None
    torch_available: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.kind, RuntimeKind):
            raise TypeError("kind must be RuntimeKind")
        if self.gpu_name is not None and (not isinstance(self.gpu_name, str) or not self.gpu_name.strip()):
            raise ValueError("gpu_name must be non-empty or None")
        if self.gpu_vram_gb is not None and self.gpu_vram_gb < 0:
            raise ValueError("gpu_vram_gb cannot be negative")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class RuntimeCompatibilityDecision:
    compatible: bool
    reasons: tuple[str, ...]
    runtime: RuntimeHardwareSnapshot
    model_id: str


class LocalRuntimeProbe:
    """Best-effort stdlib-safe probe. Missing torch is a valid observation."""

    def detect(self) -> RuntimeHardwareSnapshot:
        try:
            torch = import_module("torch")
        except (ImportError, ModuleNotFoundError):
            return RuntimeHardwareSnapshot(
                kind=RuntimeKind.LOCAL_CPU,
                cuda_available=False,
                torch_available=False,
                metadata={"probe": "torch-not-installed"},
            )

        cuda = bool(torch.cuda.is_available())
        if not cuda:
            return RuntimeHardwareSnapshot(
                kind=RuntimeKind.LOCAL_CPU,
                cuda_available=False,
                torch_available=True,
                metadata={"torch_version": getattr(torch, "__version__", None)},
            )

        device = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(device)
        total_memory = float(props.total_memory) / (1024 ** 3)
        bf16_supported = None
        bf16_probe = getattr(torch.cuda, "is_bf16_supported", None)
        if callable(bf16_probe):
            try:
                bf16_supported = bool(bf16_probe())
            except Exception:
                bf16_supported = None
        compute_capability = None
        capability_probe = getattr(torch.cuda, "get_device_capability", None)
        if callable(capability_probe):
            try:
                major, minor = capability_probe(device)
                compute_capability = f"{int(major)}.{int(minor)}"
            except Exception:
                compute_capability = None
        return RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name=str(props.name),
            gpu_vram_gb=round(total_memory, 3),
            torch_available=True,
            metadata={
                "device_index": int(device),
                "torch_version": getattr(torch, "__version__", None),
                "bf16_supported": bf16_supported,
                "compute_capability": compute_capability,
            },
        )


class LocalModelRuntimeGate:
    """Fail closed unless local hardware proves the candidate can run as declared."""

    def evaluate(
        self,
        candidate: LocalModelCandidate,
        runtime: RuntimeHardwareSnapshot,
    ) -> RuntimeCompatibilityDecision:
        if not isinstance(candidate, LocalModelCandidate):
            raise TypeError("candidate must be LocalModelCandidate")
        if not isinstance(runtime, RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")

        reasons: list[str] = []
        if not runtime.cuda_available:
            reasons.append("CUDA GPU runtime is not available")
        if candidate.minimum_vram_gb is None or not candidate.runtime_floor_proven:
            reasons.append("model VRAM floor has not been proven for PUL7SAR local execution")
        elif runtime.gpu_vram_gb is None:
            reasons.append("GPU VRAM could not be proven")
        elif runtime.gpu_vram_gb < candidate.minimum_vram_gb:
            reasons.append(
                f"GPU VRAM {runtime.gpu_vram_gb:.3f} GB is below declared minimum {candidate.minimum_vram_gb:.3f} GB"
            )
        return RuntimeCompatibilityDecision(
            compatible=not reasons,
            reasons=tuple(reasons),
            runtime=runtime,
            model_id=candidate.model_id,
        )

    def assert_compatible(
        self,
        candidate: LocalModelCandidate,
        runtime: RuntimeHardwareSnapshot,
    ) -> None:
        decision = self.evaluate(candidate, runtime)
        if not decision.compatible:
            raise ValueError("local model runtime is not compatible: " + "; ".join(decision.reasons))

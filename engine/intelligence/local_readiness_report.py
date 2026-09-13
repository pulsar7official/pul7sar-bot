"""Human- and machine-readable readiness reporting for local $0 generation."""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_backend import LocalBackendReadiness, LocalBackendSnapshot
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot
from engine.intelligence.zero_cost_models import LocalModelCandidate


@dataclass(frozen=True)
class LocalGenerationReadinessReport:
    ready: bool
    provider_id: str
    model_id: str
    backend: str
    runtime_kind: str
    gpu_name: str | None
    gpu_vram_gb: float | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    @classmethod
    def build(
        cls,
        *,
        model: LocalModelCandidate,
        runtime: RuntimeHardwareSnapshot,
        backend: LocalBackendSnapshot,
        readiness: LocalBackendReadiness,
    ) -> "LocalGenerationReadinessReport":
        return cls(
            ready=readiness.ready,
            provider_id=model.provider_id,
            model_id=model.model_id,
            backend=backend.kind.value,
            runtime_kind=runtime.kind.value,
            gpu_name=runtime.gpu_name,
            gpu_vram_gb=runtime.gpu_vram_gb,
            blockers=readiness.failures,
            warnings=readiness.warnings,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "backend": self.backend,
            "runtime_kind": self.runtime_kind,
            "gpu_name": self.gpu_name,
            "gpu_vram_gb": self.gpu_vram_gb,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "cost_mode": "$0-local",
        }

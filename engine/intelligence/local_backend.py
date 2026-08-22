"""Zero-cost local image backend readiness contracts for PUL7SAR.

These contracts do not install or execute Diffusers/ComfyUI. They provide a
fail-closed boundary for deciding whether an optional local backend is ready.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from engine.intelligence.local_runtime import LocalModelRuntimeGate, RuntimeHardwareSnapshot
from engine.intelligence.zero_cost_models import LocalModelCandidate


class LocalBackendKind(str, Enum):
    DIFFUSERS = "diffusers"
    COMFYUI = "comfyui"


@dataclass(frozen=True)
class LocalBackendSnapshot:
    kind: LocalBackendKind
    available: bool
    version: str | None = None
    endpoint: str | None = None
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class LocalBackendReadiness:
    ready: bool
    backend: LocalBackendKind
    failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class LocalBackendProbe(Protocol):
    def probe(self) -> LocalBackendSnapshot: ...


class LocalBackendReadinessGate:
    """Require both model runtime compatibility and an available local backend."""

    def __init__(self, runtime_gate: LocalModelRuntimeGate | None = None) -> None:
        self._runtime_gate = runtime_gate or LocalModelRuntimeGate()

    def evaluate(
        self,
        *,
        model: LocalModelCandidate,
        runtime: RuntimeHardwareSnapshot,
        backend: LocalBackendSnapshot,
    ) -> LocalBackendReadiness:
        failures: list[str] = []
        warnings: list[str] = []
        runtime_decision = self._runtime_gate.evaluate(model, runtime)
        if not runtime_decision.compatible:
            failures.extend(runtime_decision.reasons)
        if not backend.available:
            failures.append(f"local backend is unavailable: {backend.kind.value}")
        if backend.kind is LocalBackendKind.COMFYUI and not backend.endpoint:
            failures.append("ComfyUI backend requires an explicit local endpoint")
        if backend.kind is LocalBackendKind.DIFFUSERS and not backend.version:
            warnings.append("Diffusers version is unknown")
        return LocalBackendReadiness(not failures, backend.kind, tuple(failures), tuple(warnings))

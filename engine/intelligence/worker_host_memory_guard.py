"""Lease-bound host RAM safety guard for Phase 18 GPU generation workers.

Sequential CPU offload depends on *live* system RAM throughout model execution.
The earlier first-Golden host-memory preflight proves the machine is viable before
model work, but memory pressure can change before a concrete generation job is
leased. This guard re-measures MemAvailable at worker execution boundaries and
never authorizes generation or publication by itself.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.host_memory_qualification import (
    DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB,
    HostMemoryQualificationProbe,
)


@dataclass(frozen=True)
class WorkerHostMemoryGuardReceipt:
    schema: str
    ready: bool
    available_ram_gb: float
    minimum_available_ram_gb: float
    total_ram_gb: float | None
    measurement_source: str | None
    reasons: tuple[str, ...]
    cost_mode: str = "$0-local"
    requalified_immediately_before_queue_or_execution: bool = True
    queue_mutated_by_requalification: bool = False
    generation_authorized_by_requalification: bool = False
    publication_ready: bool = False


class WorkerHostMemoryGuard:
    """Re-prove live host RAM without consuming or mutating generation work."""

    def __init__(
        self,
        *,
        minimum_available_ram_gb: float = DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB,
    ) -> None:
        if minimum_available_ram_gb <= 0:
            raise ValueError("minimum_available_ram_gb must be positive")
        self.minimum_available_ram_gb = float(minimum_available_ram_gb)

    def inspect(self) -> WorkerHostMemoryGuardReceipt:
        report = HostMemoryQualificationProbe(
            minimum_available_ram_gb=self.minimum_available_ram_gb,
        ).inspect()
        if not report.ready:
            raise RuntimeError(
                "GPU worker live host-memory requalification failed: "
                + "; ".join(report.reasons)
            )
        if report.cost_mode != "$0-local":
            raise RuntimeError("GPU worker live host-memory requalification escaped $0-local policy")
        if report.available_ram_gb is None:
            raise RuntimeError("GPU worker live host-memory requalification did not prove MemAvailable")
        if report.available_ram_gb < report.minimum_available_ram_gb:
            raise RuntimeError("GPU worker live host-memory requalification fell below required RAM floor")

        return WorkerHostMemoryGuardReceipt(
            schema="pul7sar-worker-host-memory-guard-v1",
            ready=True,
            available_ram_gb=report.available_ram_gb,
            minimum_available_ram_gb=report.minimum_available_ram_gb,
            total_ram_gb=report.total_ram_gb,
            measurement_source=report.measurement_source,
            reasons=report.reasons,
        )

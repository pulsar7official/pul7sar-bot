"""Fail-closed host-memory qualification for the first Golden GPU run.

Sequential CPU offload moves model state through system RAM. GPU readiness alone
cannot prove that the host has enough *currently available* CPU memory to start
the first Golden Candidate safely. This module measures Linux host memory using
stdlib-only probes before any model download/load, queue mutation, generation,
or publication decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


GIB = 1024 ** 3
DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB = 10.0


@dataclass(frozen=True)
class HostMemoryQualificationReport:
    schema: str
    ready: bool
    total_ram_gb: float | None
    available_ram_gb: float | None
    used_ram_gb: float | None
    swap_total_gb: float | None
    swap_free_gb: float | None
    minimum_available_ram_gb: float
    measurement_source: str | None
    reasons: tuple[str, ...]
    cost_mode: str = "$0-local"
    model_downloads_performed: bool = False
    model_loaded: bool = False
    generation_authorized: bool = False
    queue_mutated: bool = False
    png_created: bool = False
    semantic_approved: bool = False
    golden_quality_approved: bool = False
    publication_ready: bool = False


class HostMemoryQualificationProbe:
    """Measure currently available host RAM without external dependencies."""

    def __init__(
        self,
        *,
        minimum_available_ram_gb: float = DEFAULT_MINIMUM_AVAILABLE_SYSTEM_RAM_GB,
        meminfo_reader: Callable[[], str] | None = None,
    ) -> None:
        if minimum_available_ram_gb <= 0:
            raise ValueError("minimum_available_ram_gb must be positive")
        self._minimum = float(minimum_available_ram_gb)
        self._reader = meminfo_reader or self._read_proc_meminfo

    @staticmethod
    def _read_proc_meminfo() -> str:
        return Path("/proc/meminfo").read_text(encoding="utf-8")

    @staticmethod
    def _parse_kib(meminfo: str, key: str) -> int | None:
        prefix = f"{key}:"
        for line in meminfo.splitlines():
            if not line.startswith(prefix):
                continue
            parts = line.split()
            if len(parts) < 2:
                return None
            try:
                value = int(parts[1])
            except ValueError:
                return None
            if value < 0:
                return None
            return value
        return None

    @staticmethod
    def _kib_to_gib(value: int | None) -> float | None:
        if value is None:
            return None
        return (value * 1024) / GIB

    def inspect(self) -> HostMemoryQualificationReport:
        reasons: list[str] = []
        try:
            meminfo = self._reader()
        except (OSError, RuntimeError):
            meminfo = ""
            reasons.append("host_memory_measurement_unavailable")

        total_kib = self._parse_kib(meminfo, "MemTotal") if meminfo else None
        available_kib = self._parse_kib(meminfo, "MemAvailable") if meminfo else None
        swap_total_kib = self._parse_kib(meminfo, "SwapTotal") if meminfo else None
        swap_free_kib = self._parse_kib(meminfo, "SwapFree") if meminfo else None

        total = self._kib_to_gib(total_kib)
        available = self._kib_to_gib(available_kib)
        swap_total = self._kib_to_gib(swap_total_kib)
        swap_free = self._kib_to_gib(swap_free_kib)
        used = None if total is None or available is None else max(0.0, total - available)

        if total is None or total <= 0:
            reasons.append("total_system_ram_unproven")
        if available is None:
            reasons.append("available_system_ram_unproven")
        elif available < self._minimum:
            reasons.append("available_system_ram_below_first_golden_floor")

        ready = not reasons
        return HostMemoryQualificationReport(
            schema="pul7sar-host-memory-qualification-v1",
            ready=ready,
            total_ram_gb=total,
            available_ram_gb=available,
            used_ram_gb=used,
            swap_total_gb=swap_total,
            swap_free_gb=swap_free,
            minimum_available_ram_gb=self._minimum,
            measurement_source="/proc/meminfo" if meminfo else None,
            reasons=tuple(dict.fromkeys(reasons)),
        )

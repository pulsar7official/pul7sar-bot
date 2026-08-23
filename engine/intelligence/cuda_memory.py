"""Optional CUDA peak-memory instrumentation for real Phase 18 generation.

The module is intentionally tiny and dependency-tolerant. CPU/CI environments
can import it without CUDA. A real GPU process may reset PyTorch peak-memory
counters immediately before model execution and capture high-water marks after
execution. Missing/unsupported telemetry never pretends that a measurement
exists.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

_GIB = float(1024 ** 3)


@dataclass(frozen=True)
class CudaMemorySnapshot:
    available: bool
    peak_allocated_gb: float | None
    peak_reserved_gb: float | None
    current_allocated_gb: float | None
    current_reserved_gb: float | None
    device_index: int | None
    blocker: str | None = None


class CudaPeakMemoryTracker:
    """Best-effort PyTorch CUDA telemetry with truthful unavailable states."""

    def __init__(self, torch_module: Any | None = None) -> None:
        self._torch = torch_module

    def _torch_module(self) -> Any | None:
        if self._torch is not None:
            return self._torch
        try:
            import torch  # type: ignore
        except Exception:
            return None
        return torch

    def reset(self) -> bool:
        torch = self._torch_module()
        if torch is None:
            return False
        try:
            if not bool(torch.cuda.is_available()):
                return False
            device = int(torch.cuda.current_device())
            torch.cuda.reset_peak_memory_stats(device)
            return True
        except Exception:
            return False

    def capture(self) -> CudaMemorySnapshot:
        torch = self._torch_module()
        if torch is None:
            return self._unavailable("torch is unavailable")
        try:
            if not bool(torch.cuda.is_available()):
                return self._unavailable("CUDA is unavailable")
            device = int(torch.cuda.current_device())
            peak_allocated = self._gb(torch.cuda.max_memory_allocated(device))
            peak_reserved = self._gb(torch.cuda.max_memory_reserved(device))
            current_allocated = self._gb(torch.cuda.memory_allocated(device))
            current_reserved = self._gb(torch.cuda.memory_reserved(device))
            return CudaMemorySnapshot(
                available=True,
                peak_allocated_gb=peak_allocated,
                peak_reserved_gb=peak_reserved,
                current_allocated_gb=current_allocated,
                current_reserved_gb=current_reserved,
                device_index=device,
                blocker=None,
            )
        except Exception as exc:
            return self._unavailable(f"CUDA memory telemetry failed: {exc}")

    @staticmethod
    def _gb(value: Any) -> float:
        number = float(value) / _GIB
        if not math.isfinite(number) or number < 0:
            raise ValueError("CUDA memory counter must be finite and non-negative")
        return number

    @staticmethod
    def _unavailable(blocker: str) -> CudaMemorySnapshot:
        return CudaMemorySnapshot(
            available=False,
            peak_allocated_gb=None,
            peak_reserved_gb=None,
            current_allocated_gb=None,
            current_reserved_gb=None,
            device_index=None,
            blocker=blocker,
        )

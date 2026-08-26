"""Fail-closed FLUX.2 CPU-offload capability preflight.

The first Golden Candidate may run on constrained NVIDIA hosts where Diffusers'
sequential CPU offload is required for safe execution. This module proves the
installed Diffusers class exposes the required offload API *before* any model
weights are loaded or downloaded.

No network access, model instantiation, queue mutation, generation, or
publication authority is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version as package_version
from typing import Any

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID


DEFAULT_MODEL_OFFLOAD_MINIMUM_TOTAL_VRAM_GB = 16.0


@dataclass(frozen=True)
class Flux2OffloadCapabilityReport:
    schema: str
    ready: bool
    model_id: str
    diffusers_version: str | None
    pipeline_available: bool
    sequential_cpu_offload_available: bool
    model_cpu_offload_available: bool
    total_vram_gb: float | None
    model_offload_minimum_total_vram_gb: float
    low_vram_host: bool | None
    selected_safe_mode: str | None
    reasons: tuple[str, ...]
    cost_mode: str = "$0-local"
    model_loaded: bool = False
    downloads_performed: bool = False
    generation_authorized: bool = False
    queue_mutated: bool = False
    png_created: bool = False
    publication_ready: bool = False


class Flux2OffloadCapabilityProbe:
    """Inspect the installed Flux2KleinPipeline class without loading weights."""

    def __init__(
        self,
        *,
        model_offload_minimum_total_vram_gb: float = DEFAULT_MODEL_OFFLOAD_MINIMUM_TOTAL_VRAM_GB,
        diffusers_module: Any | None = None,
    ) -> None:
        if model_offload_minimum_total_vram_gb <= 0:
            raise ValueError("model_offload_minimum_total_vram_gb must be positive")
        self._minimum_vram = float(model_offload_minimum_total_vram_gb)
        self._diffusers_module = diffusers_module

    def inspect(self, *, total_vram_gb: float | None) -> Flux2OffloadCapabilityReport:
        reasons: list[str] = []
        if total_vram_gb is not None and total_vram_gb <= 0:
            raise ValueError("total_vram_gb must be positive when provided")

        diffusers = self._diffusers_module
        if diffusers is None:
            try:
                diffusers = import_module("diffusers")
            except (ImportError, ModuleNotFoundError):
                return Flux2OffloadCapabilityReport(
                    schema="pul7sar-flux2-offload-capability-v1",
                    ready=False,
                    model_id=FLUX2_KLEIN_4B_MODEL_ID,
                    diffusers_version=None,
                    pipeline_available=False,
                    sequential_cpu_offload_available=False,
                    model_cpu_offload_available=False,
                    total_vram_gb=total_vram_gb,
                    model_offload_minimum_total_vram_gb=self._minimum_vram,
                    low_vram_host=(total_vram_gb <= self._minimum_vram) if total_vram_gb is not None else None,
                    selected_safe_mode=None,
                    reasons=("diffusers_missing",),
                )

        pipeline_cls = getattr(diffusers, "Flux2KleinPipeline", None)
        pipeline_available = pipeline_cls is not None
        sequential_available = bool(
            pipeline_available and callable(getattr(pipeline_cls, "enable_sequential_cpu_offload", None))
        )
        model_available = bool(
            pipeline_available and callable(getattr(pipeline_cls, "enable_model_cpu_offload", None))
        )
        try:
            diffusers_version = package_version("diffusers")
        except PackageNotFoundError:
            diffusers_version = getattr(diffusers, "__version__", None)

        if not pipeline_available:
            reasons.append("flux2_klein_pipeline_missing")
        if total_vram_gb is None:
            reasons.append("total_vram_unproven")
            low_vram_host = None
        else:
            low_vram_host = total_vram_gb <= self._minimum_vram

        selected_safe_mode: str | None = None
        if pipeline_available and total_vram_gb is not None:
            if sequential_available:
                selected_safe_mode = "sequential_cpu"
            elif low_vram_host:
                reasons.append("sequential_cpu_offload_required_on_low_vram_host")
            elif model_available:
                selected_safe_mode = "model_cpu"
            else:
                reasons.append("no_supported_cpu_offload_mode")

        ready = not reasons and selected_safe_mode is not None
        return Flux2OffloadCapabilityReport(
            schema="pul7sar-flux2-offload-capability-v1",
            ready=ready,
            model_id=FLUX2_KLEIN_4B_MODEL_ID,
            diffusers_version=diffusers_version,
            pipeline_available=pipeline_available,
            sequential_cpu_offload_available=sequential_available,
            model_cpu_offload_available=model_available,
            total_vram_gb=total_vram_gb,
            model_offload_minimum_total_vram_gb=self._minimum_vram,
            low_vram_host=low_vram_host,
            selected_safe_mode=selected_safe_mode,
            reasons=tuple(dict.fromkeys(reasons)),
        )

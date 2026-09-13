"""CUDA-aware dtype policy for Phase 18 visual execution.

PUL7SAR's approved FLUX.2 Klein 4B Golden reference path remains quality-locked
to the model's documented bfloat16 Diffusers configuration. A separate explicit
``float16-preview`` mode exists only to obtain a zero-cost engineering image on
legacy Colab GPUs such as T4 when native BF16 is unavailable. The preview mode
must never be treated as Golden-reference, semantic-quality, or publication
approval and is never selected silently by ``auto``.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


_ALLOWED = {"auto", "bfloat16", "float16-preview"}


@dataclass(frozen=True)
class LocalDTypeDecision:
    requested: str
    resolved: str
    reason: str
    quality_tier: str = "golden_reference"


class LocalDTypeSelector:
    """Resolve reference BF16 or an explicitly requested engineering preview."""

    def select(self, runtime: RuntimeHardwareSnapshot, requested: str = "auto") -> LocalDTypeDecision:
        if not isinstance(runtime, RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")
        if requested not in _ALLOWED:
            raise ValueError(
                "unsupported visual dtype request; use auto/bfloat16 or explicit float16-preview"
            )
        if runtime.kind is not RuntimeKind.LOCAL_CUDA or not runtime.cuda_available:
            raise ValueError("CUDA runtime is required for FLUX dtype selection")

        bf16_supported = runtime.metadata.get("bf16_supported")
        if bf16_supported not in {True, False, None}:
            raise ValueError("runtime bf16 capability must be true, false or unknown")

        if requested == "float16-preview":
            return LocalDTypeDecision(
                requested="float16-preview",
                resolved="float16",
                reason=(
                    "explicit zero-cost engineering preview selected; float16 is not the "
                    "PUL7SAR Golden-reference precision and cannot become publication-ready"
                ),
                quality_tier="t4_engineering_preview",
            )

        if bf16_supported is not True:
            detail = (
                "runtime explicitly reports no native bfloat16 support"
                if bf16_supported is False
                else "runtime bfloat16 support could not be proven"
            )
            raise ValueError(
                detail
                + "; Golden-reference execution will not silently fall back to float16. "
                + "Use float16-preview only for a non-Golden engineering image."
            )

        if requested == "auto":
            return LocalDTypeDecision(
                requested="auto",
                resolved="bfloat16",
                reason="official Golden reference dtype selected after native bfloat16 support was proven",
                quality_tier="golden_reference",
            )
        return LocalDTypeDecision(
            requested="bfloat16",
            resolved="bfloat16",
            reason="explicit bfloat16 request is supported by the CUDA runtime",
            quality_tier="golden_reference",
        )

"""CUDA-aware dtype policy for Phase 18 Golden Visual execution.

PUL7SAR's approved FLUX.2 Klein 4B reference path is quality-locked to the
model's documented bfloat16 Diffusers configuration. Free notebook GPUs are not
homogeneous, so hardware capability is probed instead of assumed. The Golden
Visual path fails closed when native BF16 support cannot be proven rather than
silently changing numerical precision before the first benchmark is established.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


_ALLOWED = {"auto", "bfloat16"}


@dataclass(frozen=True)
class LocalDTypeDecision:
    requested: str
    resolved: str
    reason: str


class LocalDTypeSelector:
    """Resolve only quality-verified dtype modes for the Golden Visual path."""

    def select(self, runtime: RuntimeHardwareSnapshot, requested: str = "auto") -> LocalDTypeDecision:
        if not isinstance(runtime, RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")
        if requested not in _ALLOWED:
            raise ValueError(
                "unsupported Golden Visual dtype request; only auto/bfloat16 are quality-verified"
            )
        if runtime.kind is not RuntimeKind.LOCAL_CUDA or not runtime.cuda_available:
            raise ValueError("CUDA runtime is required for FLUX dtype selection")

        bf16_supported = runtime.metadata.get("bf16_supported")
        if bf16_supported not in {True, False, None}:
            raise ValueError("runtime bf16 capability must be true, false or unknown")
        if bf16_supported is not True:
            detail = (
                "runtime explicitly reports no native bfloat16 support"
                if bf16_supported is False
                else "runtime bfloat16 support could not be proven"
            )
            raise ValueError(
                detail
                + "; PUL7SAR Golden Visual execution will not silently fall back to an unverified precision"
            )

        if requested == "auto":
            return LocalDTypeDecision(
                requested="auto",
                resolved="bfloat16",
                reason="official Golden Visual dtype selected after native bfloat16 support was proven",
            )
        return LocalDTypeDecision(
            requested="bfloat16",
            resolved="bfloat16",
            reason="explicit bfloat16 request is supported by the CUDA runtime",
        )

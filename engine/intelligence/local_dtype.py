"""CUDA-aware dtype selection for Phase 18 local/free GPU execution.

Free notebook GPUs are not homogeneous. Some expose sufficient VRAM for the
approved FLUX.2 Klein 4B profile but do not provide native bfloat16 support.
PUL7SAR therefore resolves `auto` deterministically from the probed CUDA runtime
instead of assuming every >=13 GB GPU behaves like a newer RTX/Ampere device.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


_ALLOWED = {"auto", "float16", "bfloat16", "float32"}


@dataclass(frozen=True)
class LocalDTypeDecision:
    requested: str
    resolved: str
    reason: str


class LocalDTypeSelector:
    """Resolve a concrete torch dtype without silently choosing unsupported BF16."""

    def select(self, runtime: RuntimeHardwareSnapshot, requested: str = "auto") -> LocalDTypeDecision:
        if not isinstance(runtime, RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")
        if requested not in _ALLOWED:
            raise ValueError("unsupported dtype request")
        if runtime.kind is not RuntimeKind.LOCAL_CUDA or not runtime.cuda_available:
            raise ValueError("CUDA runtime is required for FLUX dtype selection")

        bf16_supported = runtime.metadata.get("bf16_supported")
        if bf16_supported not in {True, False, None}:
            raise ValueError("runtime bf16 capability must be true, false or unknown")

        if requested == "auto":
            if bf16_supported is True:
                return LocalDTypeDecision(
                    requested="auto",
                    resolved="bfloat16",
                    reason="CUDA runtime explicitly reports native bfloat16 support",
                )
            return LocalDTypeDecision(
                requested="auto",
                resolved="float16",
                reason=(
                    "CUDA runtime reports no native bfloat16 support"
                    if bf16_supported is False
                    else "CUDA bfloat16 support is unknown; using conservative float16 fallback"
                ),
            )

        if requested == "bfloat16":
            if bf16_supported is not True:
                raise ValueError("bfloat16 was explicitly requested but runtime support is not proven")
            return LocalDTypeDecision(requested, requested, "explicit bfloat16 request is supported")

        if requested == "float16":
            return LocalDTypeDecision(requested, requested, "explicit float16 request")

        return LocalDTypeDecision(
            requested,
            requested,
            "explicit float32 request; caller accepts increased memory pressure",
        )

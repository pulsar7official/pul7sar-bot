"""Combined cache-budget policy for the first strict Golden GPU session.

Qwen and FLUX are prefetched by separate tools, but they normally share the same
Hugging Face cache filesystem. Independent free-space checks can therefore pass
one at a time while still leaving too little room for the second download. This
module evaluates the combined conservative headroom before either model download
is allowed to start.
"""
from __future__ import annotations

from dataclasses import dataclass

GIB = 1024 ** 3
DEFAULT_QWEN_MINIMUM_FREE_GIB = 12.0
DEFAULT_FLUX_MINIMUM_FREE_GIB = 30.0


@dataclass(frozen=True)
class FirstGoldenCacheBudgetDecision:
    qwen_cached: bool
    flux_cached: bool
    free_gib: float | None
    qwen_minimum_free_gib: float
    flux_minimum_free_gib: float
    combined_minimum_free_gib: float
    eligible: bool
    reasons: tuple[str, ...]


class FirstGoldenCacheBudgetPolicy:
    """Require enough shared-cache headroom for every missing approved model."""

    def __init__(
        self,
        *,
        qwen_minimum_free_gib: float = DEFAULT_QWEN_MINIMUM_FREE_GIB,
        flux_minimum_free_gib: float = DEFAULT_FLUX_MINIMUM_FREE_GIB,
    ) -> None:
        if qwen_minimum_free_gib <= 0 or flux_minimum_free_gib <= 0:
            raise ValueError("minimum free-space thresholds must be positive")
        self.qwen_minimum_free_gib = float(qwen_minimum_free_gib)
        self.flux_minimum_free_gib = float(flux_minimum_free_gib)

    def evaluate(
        self,
        *,
        qwen_cached: bool,
        flux_cached: bool,
        free_bytes: int | None,
    ) -> FirstGoldenCacheBudgetDecision:
        if not isinstance(qwen_cached, bool) or not isinstance(flux_cached, bool):
            raise TypeError("qwen_cached and flux_cached must be bool")
        if free_bytes is not None and free_bytes < 0:
            raise ValueError("free_bytes cannot be negative")

        required = 0.0
        if not qwen_cached:
            required += self.qwen_minimum_free_gib
        if not flux_cached:
            required += self.flux_minimum_free_gib

        free_gib = None if free_bytes is None else float(free_bytes) / GIB
        reasons: list[str] = []
        if required > 0:
            if free_gib is None:
                reasons.append("shared Hugging Face cache free space could not be proven")
            elif free_gib < required:
                reasons.append(
                    f"shared Hugging Face cache has {free_gib:.3f} GiB free; "
                    f"at least {required:.3f} GiB is required before downloading all missing approved models"
                )

        return FirstGoldenCacheBudgetDecision(
            qwen_cached=qwen_cached,
            flux_cached=flux_cached,
            free_gib=None if free_gib is None else round(free_gib, 3),
            qwen_minimum_free_gib=self.qwen_minimum_free_gib,
            flux_minimum_free_gib=self.flux_minimum_free_gib,
            combined_minimum_free_gib=round(required, 3),
            eligible=not reasons,
            reasons=tuple(reasons),
        )

    @staticmethod
    def assert_eligible(decision: FirstGoldenCacheBudgetDecision) -> None:
        if not isinstance(decision, FirstGoldenCacheBudgetDecision):
            raise TypeError("decision must be FirstGoldenCacheBudgetDecision")
        if not decision.eligible:
            raise RuntimeError("first Golden cache budget is not eligible: " + "; ".join(decision.reasons))

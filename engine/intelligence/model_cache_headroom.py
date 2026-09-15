"""Fail-closed post-cache disk headroom policy for Phase 18 model execution.

The first-Golden cache-budget preflight proves enough space exists *before*
missing model snapshots are downloaded. This module covers the complementary
post-cache condition: after the exact approved snapshots exist locally, enough
filesystem headroom must still remain for runtime scratch files, receipts and
artifacts before Candidate 1 is allowed to proceed.

This policy is deliberately provider-neutral and performs no I/O by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

_GIB = 1024 ** 3


@dataclass(frozen=True)
class ModelCacheHeadroomDecision:
    minimum_working_free_gib: float
    free_bytes: int
    free_gib: float
    eligible: bool
    reason: str


class ModelCacheHeadroomPolicy:
    """Require a conservative live free-space floor after model caching."""

    def __init__(self, *, minimum_working_free_gib: float = 8.0) -> None:
        if isinstance(minimum_working_free_gib, bool) or not isinstance(minimum_working_free_gib, (int, float)):
            raise ValueError("minimum_working_free_gib must be numeric")
        minimum = float(minimum_working_free_gib)
        if not math.isfinite(minimum) or minimum <= 0:
            raise ValueError("minimum_working_free_gib must be finite and greater than zero")
        self.minimum_working_free_gib = minimum

    def evaluate(self, *, free_bytes: int) -> ModelCacheHeadroomDecision:
        if isinstance(free_bytes, bool) or not isinstance(free_bytes, int):
            raise ValueError("free_bytes must be an integer byte count")
        if free_bytes < 0:
            raise ValueError("free_bytes cannot be negative")

        free_gib = free_bytes / _GIB
        eligible = free_gib >= self.minimum_working_free_gib
        reason = "post_cache_working_headroom_ready" if eligible else "post_cache_working_headroom_below_floor"
        return ModelCacheHeadroomDecision(
            minimum_working_free_gib=self.minimum_working_free_gib,
            free_bytes=free_bytes,
            free_gib=round(free_gib, 3),
            eligible=eligible,
            reason=reason,
        )

    @staticmethod
    def assert_eligible(decision: ModelCacheHeadroomDecision) -> None:
        if not decision.eligible:
            raise RuntimeError(
                "PHASE18_MODEL_CACHE_POST_HEADROOM_INSUFFICIENT:"
                f"free_gib={decision.free_gib}:"
                f"required_gib={decision.minimum_working_free_gib}"
            )

"""Fail-closed model-cache qualification for Phase 18 GPU execution.

This module deliberately separates *model availability* from GPU readiness. A host
can have a valid CUDA/BF16 runtime and still fail the first generation because the
approved model snapshot is unavailable or the Hugging Face cache filesystem lacks
space. The policy here lets the orchestration prove those conditions before
spending GPU time.
"""

from __future__ import annotations

from dataclasses import dataclass


GIB = 1024 ** 3
DEFAULT_MINIMUM_FREE_GIB = 30.0


@dataclass(frozen=True)
class ModelCacheQualification:
    model_id: str
    cache_ready: bool
    cache_path: str | None
    free_gib: float | None
    minimum_free_gib: float
    download_required: bool
    eligible: bool
    reasons: tuple[str, ...]


class ModelCachePolicy:
    """Evaluate whether model acquisition can proceed without guessing.

    If a complete approved snapshot is already cached, free-space gating is not
    required for re-downloading it. If a download is required, the cache
    filesystem must prove a conservative amount of free disk before transfer.
    """

    def __init__(self, minimum_free_gib: float = DEFAULT_MINIMUM_FREE_GIB) -> None:
        if minimum_free_gib <= 0:
            raise ValueError("minimum_free_gib must be positive")
        self.minimum_free_gib = float(minimum_free_gib)

    def evaluate(
        self,
        *,
        model_id: str,
        cached_snapshot_path: str | None,
        free_bytes: int | None,
    ) -> ModelCacheQualification:
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("model_id must be non-empty")
        if free_bytes is not None and free_bytes < 0:
            raise ValueError("free_bytes cannot be negative")

        cache_ready = bool(cached_snapshot_path)
        free_gib = None if free_bytes is None else float(free_bytes) / GIB
        reasons: list[str] = []

        if cache_ready:
            return ModelCacheQualification(
                model_id=model_id,
                cache_ready=True,
                cache_path=cached_snapshot_path,
                free_gib=None if free_gib is None else round(free_gib, 3),
                minimum_free_gib=self.minimum_free_gib,
                download_required=False,
                eligible=True,
                reasons=(),
            )

        if free_gib is None:
            reasons.append("cache filesystem free space could not be proven")
        elif free_gib < self.minimum_free_gib:
            reasons.append(
                f"cache filesystem has {free_gib:.3f} GiB free; "
                f"at least {self.minimum_free_gib:.3f} GiB is required before model download"
            )

        return ModelCacheQualification(
            model_id=model_id,
            cache_ready=False,
            cache_path=None,
            free_gib=None if free_gib is None else round(free_gib, 3),
            minimum_free_gib=self.minimum_free_gib,
            download_required=True,
            eligible=not reasons,
            reasons=tuple(reasons),
        )

    def assert_eligible(self, qualification: ModelCacheQualification) -> None:
        if not isinstance(qualification, ModelCacheQualification):
            raise TypeError("qualification must be ModelCacheQualification")
        if not qualification.eligible:
            raise RuntimeError("model cache is not eligible: " + "; ".join(qualification.reasons))

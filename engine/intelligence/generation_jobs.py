"""Durable, provider-neutral job contracts for Phase 18 GPU generation.

The contracts in this module deliberately do not depend on Redis, SQS, Celery,
GitHub Actions, or a particular GPU vendor.  They define the state machine that
any queue/worker implementation must preserve so PUL7SAR can scale image
production without weakening its existing generation and publication gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class GenerationJobState(str, Enum):
    QUEUED = "queued"
    LEASED = "leased"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    RETRYABLE_FAILED = "retryable_failed"
    TERMINAL_FAILED = "terminal_failed"


_TERMINAL = {GenerationJobState.SUCCEEDED, GenerationJobState.TERMINAL_FAILED}
_ALLOWED_TRANSITIONS = {
    GenerationJobState.QUEUED: {GenerationJobState.LEASED},
    GenerationJobState.LEASED: {
        GenerationJobState.RUNNING,
        GenerationJobState.RETRYABLE_FAILED,
        GenerationJobState.TERMINAL_FAILED,
    },
    GenerationJobState.RUNNING: {
        GenerationJobState.SUCCEEDED,
        GenerationJobState.RETRYABLE_FAILED,
        GenerationJobState.TERMINAL_FAILED,
    },
    GenerationJobState.RETRYABLE_FAILED: {GenerationJobState.QUEUED},
    GenerationJobState.SUCCEEDED: set(),
    GenerationJobState.TERMINAL_FAILED: set(),
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class GenerationJob:
    """Queue-safe description of one locked PUL7SAR generation request."""

    job_id: str
    request_id: str
    handoff_path: str
    payload_sha256: str
    provider_id: str
    model_id: str
    state: GenerationJobState = GenerationJobState.QUEUED
    attempt: int = 0
    max_attempts: int = 3
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    lease_owner: str | None = None
    lease_expires_at: datetime | None = None
    result_path: str | None = None
    failure_code: str | None = None
    failure_detail: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("job_id", "request_id", "handoff_path", "payload_sha256", "provider_id", "model_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if len(self.payload_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in self.payload_sha256.lower()):
            raise ValueError("payload_sha256 must be a 64-character hexadecimal SHA-256")
        if self.attempt < 0:
            raise ValueError("attempt must be non-negative")
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.attempt > self.max_attempts:
            raise ValueError("attempt cannot exceed max_attempts")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")
        if self.lease_expires_at is not None:
            _require_aware(self.lease_expires_at, "lease_expires_at")
        if self.state in {GenerationJobState.LEASED, GenerationJobState.RUNNING}:
            if not self.lease_owner or self.lease_expires_at is None:
                raise ValueError("leased/running jobs require lease_owner and lease_expires_at")
        if self.state is GenerationJobState.SUCCEEDED and not self.result_path:
            raise ValueError("succeeded jobs require result_path")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def terminal(self) -> bool:
        return self.state in _TERMINAL

    @property
    def attempts_remaining(self) -> int:
        return max(0, self.max_attempts - self.attempt)

    def transition(self, state: GenerationJobState, *, now: datetime | None = None, **changes: Any) -> "GenerationJob":
        if not isinstance(state, GenerationJobState):
            raise TypeError("state must be GenerationJobState")
        if state not in _ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"invalid generation job transition: {self.state.value} -> {state.value}")
        timestamp = now or _utcnow()
        _require_aware(timestamp, "now")
        return replace(self, state=state, updated_at=timestamp, **changes)


@dataclass(frozen=True)
class GenerationWorkerCapabilities:
    worker_id: str
    provider_ids: frozenset[str]
    model_ids: frozenset[str]
    cuda_available: bool
    bf16_supported: bool
    vram_gb: float | None = None
    max_concurrency: int = 1
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.worker_id, str) or not self.worker_id.strip():
            raise ValueError("worker_id must be non-empty")
        if self.max_concurrency <= 0:
            raise ValueError("max_concurrency must be positive")
        if self.vram_gb is not None and self.vram_gb < 0:
            raise ValueError("vram_gb must be non-negative")
        object.__setattr__(self, "provider_ids", frozenset(self.provider_ids))
        object.__setattr__(self, "model_ids", frozenset(self.model_ids))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def supports(self, job: GenerationJob, *, require_bf16: bool = True) -> bool:
        if not self.cuda_available:
            return False
        if require_bf16 and not self.bf16_supported:
            return False
        return job.provider_id in self.provider_ids and job.model_id in self.model_ids

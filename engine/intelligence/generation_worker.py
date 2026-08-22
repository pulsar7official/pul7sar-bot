"""Fail-closed worker orchestration for automated Phase 18 generation.

This module turns the existing portable handoff/executor into a scalable worker
contract.  It intentionally owns no queue backend and no GPU implementation.
Instead, it validates capability, lease ownership, bounded retry behaviour and
result identity around an injected executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Protocol

from engine.intelligence.generation_jobs import (
    GenerationJob,
    GenerationJobState,
    GenerationWorkerCapabilities,
)


class GenerationJobStore(Protocol):
    def lease_next(
        self,
        *,
        worker: GenerationWorkerCapabilities,
        lease_until: datetime,
    ) -> GenerationJob | None: ...

    def save(self, job: GenerationJob) -> None: ...


@dataclass(frozen=True)
class WorkerExecutionResult:
    request_id: str
    payload_sha256: str
    provider_id: str
    model_id: str
    result_path: str | None
    retryable: bool = False
    failure_code: str | None = None
    failure_detail: str | None = None

    @property
    def succeeded(self) -> bool:
        return bool(self.result_path) and not self.failure_code


class LockedGenerationExecutor(Protocol):
    def execute(self, job: GenerationJob) -> WorkerExecutionResult: ...


@dataclass(frozen=True)
class WorkerCycleResult:
    worker_id: str
    status: str
    job_id: str | None = None
    state: GenerationJobState | None = None
    detail: str | None = None


class GenerationWorkerService:
    """Lease and execute at most one job per cycle.

    A production runner can call this service continuously or from a process
    supervisor.  Single-cycle semantics keep concurrency explicit: horizontal
    scaling is achieved by more workers, while each GPU worker can independently
    control its safe local concurrency.
    """

    def __init__(
        self,
        *,
        store: GenerationJobStore,
        executor: LockedGenerationExecutor,
        capabilities: GenerationWorkerCapabilities,
        lease_seconds: int = 900,
        require_bf16: bool = True,
    ) -> None:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        self.store = store
        self.executor = executor
        self.capabilities = capabilities
        self.lease_seconds = lease_seconds
        self.require_bf16 = require_bf16

    def run_once(self, *, now: datetime | None = None) -> WorkerCycleResult:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        lease_until = current + timedelta(seconds=self.lease_seconds)
        job = self.store.lease_next(worker=self.capabilities, lease_until=lease_until)
        if job is None:
            return WorkerCycleResult(self.capabilities.worker_id, "idle")

        self._validate_lease(job, current)
        if not self.capabilities.supports(job, require_bf16=self.require_bf16):
            failed = job.transition(
                GenerationJobState.TERMINAL_FAILED,
                now=current,
                failure_code="worker_capability_mismatch",
                failure_detail="leased worker cannot satisfy provider/model/CUDA/BF16 requirements",
            )
            self.store.save(failed)
            return WorkerCycleResult(
                self.capabilities.worker_id,
                "terminal_failed",
                failed.job_id,
                failed.state,
                failed.failure_detail,
            )

        running = job.transition(
            GenerationJobState.RUNNING,
            now=current,
            attempt=job.attempt + 1,
            failure_code=None,
            failure_detail=None,
        )
        self.store.save(running)

        try:
            result = self.executor.execute(running)
        except Exception as exc:  # boundary: executor/runtime errors become explicit job state
            return self._fail(running, "executor_exception", str(exc), retryable=True, now=current)

        identity_error = self._result_identity_error(running, result)
        if identity_error:
            return self._fail(running, "result_identity_mismatch", identity_error, retryable=False, now=current)

        if result.succeeded:
            path = Path(result.result_path or "")
            if not path.is_absolute() and ".." in path.parts:
                return self._fail(
                    running,
                    "unsafe_result_path",
                    "executor result path may not traverse parent directories",
                    retryable=False,
                    now=current,
                )
            succeeded = running.transition(
                GenerationJobState.SUCCEEDED,
                now=current,
                result_path=result.result_path,
                failure_code=None,
                failure_detail=None,
            )
            self.store.save(succeeded)
            return WorkerCycleResult(
                self.capabilities.worker_id,
                "succeeded",
                succeeded.job_id,
                succeeded.state,
                succeeded.result_path,
            )

        return self._fail(
            running,
            result.failure_code or "generation_failed",
            result.failure_detail or "executor returned no result",
            retryable=result.retryable,
            now=current,
        )

    def _fail(
        self,
        running: GenerationJob,
        code: str,
        detail: str,
        *,
        retryable: bool,
        now: datetime,
    ) -> WorkerCycleResult:
        can_retry = retryable and running.attempt < running.max_attempts
        state = GenerationJobState.RETRYABLE_FAILED if can_retry else GenerationJobState.TERMINAL_FAILED
        failed = running.transition(
            state,
            now=now,
            failure_code=code,
            failure_detail=detail,
        )
        self.store.save(failed)
        if can_retry:
            requeued = failed.transition(
                GenerationJobState.QUEUED,
                now=now,
                lease_owner=None,
                lease_expires_at=None,
            )
            self.store.save(requeued)
            return WorkerCycleResult(
                self.capabilities.worker_id,
                "requeued",
                requeued.job_id,
                requeued.state,
                detail,
            )
        return WorkerCycleResult(
            self.capabilities.worker_id,
            "terminal_failed",
            failed.job_id,
            failed.state,
            detail,
        )

    def _validate_lease(self, job: GenerationJob, now: datetime) -> None:
        if job.state is not GenerationJobState.LEASED:
            raise ValueError("job store returned a job that is not leased")
        if job.lease_owner != self.capabilities.worker_id:
            raise ValueError("job lease_owner does not match this worker")
        if job.lease_expires_at is None or job.lease_expires_at <= now:
            raise ValueError("job lease is already expired")
        if job.attempt >= job.max_attempts:
            raise ValueError("job has exhausted max_attempts before execution")

    @staticmethod
    def _result_identity_error(job: GenerationJob, result: WorkerExecutionResult) -> str | None:
        expected = {
            "request_id": job.request_id,
            "payload_sha256": job.payload_sha256,
            "provider_id": job.provider_id,
            "model_id": job.model_id,
        }
        actual = {
            "request_id": result.request_id,
            "payload_sha256": result.payload_sha256,
            "provider_id": result.provider_id,
            "model_id": result.model_id,
        }
        mismatches = [name for name in expected if expected[name] != actual[name]]
        if not mismatches:
            return None
        return "executor result does not match locked job fields: " + ", ".join(mismatches)

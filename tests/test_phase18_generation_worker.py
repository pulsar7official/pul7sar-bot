from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from engine.intelligence.generation_jobs import (
    GenerationJob,
    GenerationJobState,
    GenerationWorkerCapabilities,
)
from engine.intelligence.generation_worker import (
    GenerationWorkerService,
    WorkerExecutionResult,
)


NOW = datetime(2026, 8, 23, 0, 0, tzinfo=timezone.utc)
SHA = "a" * 64


def make_job(*, max_attempts: int = 3) -> GenerationJob:
    return GenerationJob(
        job_id="job-001",
        request_id="golden-general-season-opener-001",
        handoff_path="output/phase18_handoffs/golden-batch/candidate-01.json",
        payload_sha256=SHA,
        provider_id="local-flux2-klein-4b",
        model_id="black-forest-labs/FLUX.2-klein-4B",
        max_attempts=max_attempts,
        created_at=NOW,
        updated_at=NOW,
    )


def make_caps(**changes) -> GenerationWorkerCapabilities:
    values = dict(
        worker_id="gpu-worker-01",
        provider_ids=frozenset({"local-flux2-klein-4b"}),
        model_ids=frozenset({"black-forest-labs/FLUX.2-klein-4B"}),
        cuda_available=True,
        bf16_supported=True,
        vram_gb=24.0,
    )
    values.update(changes)
    return GenerationWorkerCapabilities(**values)


class MemoryStore:
    def __init__(self, job: GenerationJob | None):
        self.job = job
        self.history: list[GenerationJob] = []

    def lease_next(self, *, worker, lease_until):
        if self.job is None or self.job.state is not GenerationJobState.QUEUED:
            return None
        leased = self.job.transition(
            GenerationJobState.LEASED,
            now=NOW,
            lease_owner=worker.worker_id,
            lease_expires_at=lease_until,
        )
        self.job = leased
        self.history.append(leased)
        return leased

    def save(self, job):
        self.job = job
        self.history.append(job)


class SuccessExecutor:
    def execute(self, job):
        return WorkerExecutionResult(
            request_id=job.request_id,
            payload_sha256=job.payload_sha256,
            provider_id=job.provider_id,
            model_id=job.model_id,
            result_path="output/phase18_visual_proof/candidate-01.png",
        )


class RetryExecutor:
    def execute(self, job):
        return WorkerExecutionResult(
            request_id=job.request_id,
            payload_sha256=job.payload_sha256,
            provider_id=job.provider_id,
            model_id=job.model_id,
            result_path=None,
            retryable=True,
            failure_code="cuda_oom",
            failure_detail="temporary VRAM pressure",
        )


class DriftExecutor:
    def execute(self, job):
        return WorkerExecutionResult(
            request_id="different-request",
            payload_sha256=job.payload_sha256,
            provider_id=job.provider_id,
            model_id=job.model_id,
            result_path="output/phase18_visual_proof/wrong.png",
        )


def test_job_state_machine_rejects_skipping_lease():
    with pytest.raises(ValueError, match="invalid generation job transition"):
        make_job().transition(GenerationJobState.RUNNING, now=NOW)


def test_worker_succeeds_only_with_matching_locked_result_identity():
    store = MemoryStore(make_job())
    service = GenerationWorkerService(store=store, executor=SuccessExecutor(), capabilities=make_caps())

    cycle = service.run_once(now=NOW)

    assert cycle.status == "succeeded"
    assert store.job is not None
    assert store.job.state is GenerationJobState.SUCCEEDED
    assert store.job.attempt == 1
    assert store.job.result_path == "output/phase18_visual_proof/candidate-01.png"


def test_result_identity_drift_is_terminal_and_never_requeued():
    store = MemoryStore(make_job())
    service = GenerationWorkerService(store=store, executor=DriftExecutor(), capabilities=make_caps())

    cycle = service.run_once(now=NOW)

    assert cycle.status == "terminal_failed"
    assert store.job.state is GenerationJobState.TERMINAL_FAILED
    assert store.job.failure_code == "result_identity_mismatch"


def test_retryable_gpu_failure_requeues_without_lowering_attempt_limit():
    store = MemoryStore(make_job(max_attempts=3))
    service = GenerationWorkerService(store=store, executor=RetryExecutor(), capabilities=make_caps())

    cycle = service.run_once(now=NOW)

    assert cycle.status == "requeued"
    assert store.job.state is GenerationJobState.QUEUED
    assert store.job.attempt == 1
    assert store.job.max_attempts == 3
    assert store.job.lease_owner is None


def test_retryable_failure_becomes_terminal_on_last_allowed_attempt():
    initial = replace(make_job(max_attempts=2), attempt=1)
    store = MemoryStore(initial)
    service = GenerationWorkerService(store=store, executor=RetryExecutor(), capabilities=make_caps())

    cycle = service.run_once(now=NOW)

    assert cycle.status == "terminal_failed"
    assert store.job.state is GenerationJobState.TERMINAL_FAILED
    assert store.job.attempt == 2
    assert store.job.failure_code == "cuda_oom"


def test_worker_fails_closed_when_bf16_is_not_proven():
    store = MemoryStore(make_job())
    service = GenerationWorkerService(
        store=store,
        executor=SuccessExecutor(),
        capabilities=make_caps(bf16_supported=False),
        require_bf16=True,
    )

    cycle = service.run_once(now=NOW)

    assert cycle.status == "terminal_failed"
    assert store.job.failure_code == "worker_capability_mismatch"


def test_expired_lease_is_rejected_before_executor_runs():
    class ExpiredStore(MemoryStore):
        def lease_next(self, *, worker, lease_until):
            job = self.job.transition(
                GenerationJobState.LEASED,
                now=NOW,
                lease_owner=worker.worker_id,
                lease_expires_at=NOW - timedelta(seconds=1),
            )
            self.job = job
            return job

    store = ExpiredStore(make_job())
    service = GenerationWorkerService(store=store, executor=SuccessExecutor(), capabilities=make_caps())

    with pytest.raises(ValueError, match="lease is already expired"):
        service.run_once(now=NOW)


def test_worker_returns_idle_when_queue_has_no_compatible_job():
    store = MemoryStore(None)
    service = GenerationWorkerService(store=store, executor=SuccessExecutor(), capabilities=make_caps())

    cycle = service.run_once(now=NOW)

    assert cycle.status == "idle"
    assert cycle.job_id is None

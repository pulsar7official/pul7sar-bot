from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import unittest

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
    def __init__(self):
        self.calls = 0

    def execute(self, job):
        self.calls += 1
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


class GenerationWorkerTests(unittest.TestCase):
    def test_job_state_machine_rejects_skipping_lease(self):
        with self.assertRaisesRegex(ValueError, "invalid generation job transition"):
            make_job().transition(GenerationJobState.RUNNING, now=NOW)

    def test_worker_succeeds_only_with_matching_locked_result_identity(self):
        store = MemoryStore(make_job())
        service = GenerationWorkerService(store=store, executor=SuccessExecutor(), capabilities=make_caps())

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "succeeded")
        self.assertIsNotNone(store.job)
        self.assertIs(store.job.state, GenerationJobState.SUCCEEDED)
        self.assertEqual(store.job.attempt, 1)
        self.assertEqual(store.job.result_path, "output/phase18_visual_proof/candidate-01.png")

    def test_lease_bound_guard_runs_after_lease_before_running_and_executor(self):
        store = MemoryStore(make_job())
        executor = SuccessExecutor()
        observed: list[tuple[GenerationJobState, int]] = []

        def guard(job):
            observed.append((job.state, job.attempt))
            self.assertIs(job.state, GenerationJobState.LEASED)
            self.assertEqual(executor.calls, 0)

        service = GenerationWorkerService(
            store=store,
            executor=executor,
            capabilities=make_caps(),
            pre_execute_guard=guard,
        )
        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "succeeded")
        self.assertEqual(observed, [(GenerationJobState.LEASED, 0)])
        self.assertEqual(executor.calls, 1)
        states = [item.state for item in store.history]
        self.assertLess(states.index(GenerationJobState.LEASED), states.index(GenerationJobState.RUNNING))

    def test_guard_failure_requeues_without_executor_or_attempt_consumption(self):
        store = MemoryStore(make_job(max_attempts=3))
        executor = SuccessExecutor()

        def blocked(_job):
            raise RuntimeError("live free VRAM fell below required floor")

        service = GenerationWorkerService(
            store=store,
            executor=executor,
            capabilities=make_caps(),
            pre_execute_guard=blocked,
        )
        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "requeued")
        self.assertEqual(executor.calls, 0)
        self.assertIs(store.job.state, GenerationJobState.QUEUED)
        self.assertEqual(store.job.attempt, 0)
        self.assertIsNone(store.job.lease_owner)
        self.assertIsNone(store.job.lease_expires_at)
        failures = [item for item in store.history if item.state is GenerationJobState.RETRYABLE_FAILED]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].failure_code, "pre_execute_guard_blocked")
        self.assertIn("live free VRAM", failures[0].failure_detail)

    def test_result_identity_drift_is_terminal_and_never_requeued(self):
        store = MemoryStore(make_job())
        service = GenerationWorkerService(store=store, executor=DriftExecutor(), capabilities=make_caps())

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "terminal_failed")
        self.assertIs(store.job.state, GenerationJobState.TERMINAL_FAILED)
        self.assertEqual(store.job.failure_code, "result_identity_mismatch")

    def test_retryable_gpu_failure_requeues_without_lowering_attempt_limit(self):
        store = MemoryStore(make_job(max_attempts=3))
        service = GenerationWorkerService(store=store, executor=RetryExecutor(), capabilities=make_caps())

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "requeued")
        self.assertIs(store.job.state, GenerationJobState.QUEUED)
        self.assertEqual(store.job.attempt, 1)
        self.assertEqual(store.job.max_attempts, 3)
        self.assertIsNone(store.job.lease_owner)

    def test_retryable_failure_becomes_terminal_on_last_allowed_attempt(self):
        initial = replace(make_job(max_attempts=2), attempt=1)
        store = MemoryStore(initial)
        service = GenerationWorkerService(store=store, executor=RetryExecutor(), capabilities=make_caps())

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "terminal_failed")
        self.assertIs(store.job.state, GenerationJobState.TERMINAL_FAILED)
        self.assertEqual(store.job.attempt, 2)
        self.assertEqual(store.job.failure_code, "cuda_oom")

    def test_worker_fails_closed_when_bf16_is_not_proven(self):
        store = MemoryStore(make_job())
        service = GenerationWorkerService(
            store=store,
            executor=SuccessExecutor(),
            capabilities=make_caps(bf16_supported=False),
            require_bf16=True,
        )

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "terminal_failed")
        self.assertEqual(store.job.failure_code, "worker_capability_mismatch")

    def test_expired_lease_is_rejected_before_executor_runs(self):
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

        with self.assertRaisesRegex(ValueError, "lease is already expired"):
            service.run_once(now=NOW)

    def test_worker_returns_idle_when_queue_has_no_compatible_job(self):
        store = MemoryStore(None)
        service = GenerationWorkerService(store=store, executor=SuccessExecutor(), capabilities=make_caps())

        cycle = service.run_once(now=NOW)

        self.assertEqual(cycle.status, "idle")
        self.assertIsNone(cycle.job_id)


if __name__ == "__main__":
    unittest.main()

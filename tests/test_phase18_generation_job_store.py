import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState, GenerationWorkerCapabilities


SHA = "a" * 64


def make_job(job_id="job-1", provider="local-flux2-klein-4b", model="black-forest-labs/FLUX.2-klein-4B"):
    return GenerationJob(
        job_id=job_id,
        request_id=f"request-{job_id}",
        handoff_path=f"handoffs/{job_id}.json",
        payload_sha256=SHA,
        provider_id=provider,
        model_id=model,
        metadata={"cost_mode": "$0-local"},
    )


def make_worker(worker_id="gpu-1", *, bf16=True):
    return GenerationWorkerCapabilities(
        worker_id=worker_id,
        provider_ids=frozenset({"local-flux2-klein-4b"}),
        model_ids=frozenset({"black-forest-labs/FLUX.2-klein-4B"}),
        cuda_available=True,
        bf16_supported=bf16,
        vram_gb=24.0,
    )


class FilesystemGenerationJobStoreTests(unittest.TestCase):
    def test_enqueue_and_round_trip_preserves_locked_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            job = make_job()
            store.enqueue(job)
            restored = store.get(job.job_id)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.payload_sha256, SHA)
            self.assertEqual(restored.metadata["cost_mode"], "$0-local")
            self.assertEqual(restored.state, GenerationJobState.QUEUED)

    def test_duplicate_enqueue_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            job = make_job()
            store.enqueue(job)
            with self.assertRaises(FileExistsError):
                store.enqueue(job)

    def test_lease_moves_job_atomically_into_leased_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            job = make_job()
            store.enqueue(job)
            lease_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            leased = store.lease_next(worker=make_worker(), lease_until=lease_until)
            self.assertIsNotNone(leased)
            self.assertEqual(leased.state, GenerationJobState.LEASED)
            self.assertEqual(leased.lease_owner, "gpu-1")
            self.assertFalse((Path(tmp) / "queued" / "job-1.json").exists())
            self.assertTrue((Path(tmp) / "leased" / "job-1.json").exists())

    def test_second_worker_cannot_lease_already_claimed_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            store.enqueue(make_job())
            lease_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            first = store.lease_next(worker=make_worker("gpu-1"), lease_until=lease_until)
            second = store.lease_next(worker=make_worker("gpu-2"), lease_until=lease_until)
            self.assertIsNotNone(first)
            self.assertIsNone(second)

    def test_incompatible_worker_does_not_claim_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            store.enqueue(make_job())
            lease_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            leased = store.lease_next(worker=make_worker(bf16=False), lease_until=lease_until)
            self.assertIsNone(leased)
            self.assertEqual(store.get("job-1").state, GenerationJobState.QUEUED)

    def test_save_moves_state_file_without_duplicate_state_copies(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            store.enqueue(make_job())
            now = datetime.now(timezone.utc)
            leased = store.lease_next(worker=make_worker(), lease_until=now + timedelta(minutes=15))
            running = leased.transition(GenerationJobState.RUNNING, now=now, attempt=1)
            store.save(running)
            self.assertFalse((Path(tmp) / "leased" / "job-1.json").exists())
            self.assertTrue((Path(tmp) / "running" / "job-1.json").exists())
            self.assertEqual(store.get("job-1").attempt, 1)

    def test_unsafe_job_id_is_rejected_for_filesystem_persistence(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemGenerationJobStore(tmp)
            job = make_job("../escape")
            with self.assertRaises(ValueError):
                store.enqueue(job)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.execution_resource_evidence import LeaseBoundExecutionResourceEvidenceStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState


NOW = datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc)
SHA = "a" * 64


def leased_job() -> GenerationJob:
    queued = GenerationJob(
        job_id="golden-candidate-01",
        request_id="golden-general-season-opener-v5-001",
        handoff_path="output/phase18_handoffs/golden-batch/candidate-01.json",
        payload_sha256=SHA,
        provider_id="local-flux2-klein-4b",
        model_id="black-forest-labs/FLUX.2-klein-4B",
        created_at=NOW,
        updated_at=NOW,
    )
    return queued.transition(
        GenerationJobState.LEASED,
        now=NOW,
        lease_owner="gpu-worker-01",
        lease_expires_at=NOW + timedelta(minutes=30),
    )


def succeeded_job() -> GenerationJob:
    leased = leased_job()
    running = leased.transition(GenerationJobState.RUNNING, now=NOW, attempt=1)
    return running.transition(
        GenerationJobState.SUCCEEDED,
        now=NOW,
        result_path="output/phase18_visual_proof/candidate-01.png",
    )


def good_evidence() -> dict[str, object]:
    return {
        "gpu": {
            "eligible": True,
            "gpu_name": "NVIDIA T4",
            "gpu_free_vram_gb": 13.8,
            "required_vram_gb": 13.0,
            "bf16_supported": True,
            "cost_mode": "$0-local",
            "queue_mutated_by_requalification": False,
            "generation_authorized_by_requalification": False,
            "publication_ready": False,
        },
        "host_memory": {
            "ready": True,
            "available_ram_gb": 18.0,
            "minimum_available_ram_gb": 10.0,
            "cost_mode": "$0-local",
            "queue_mutated_by_requalification": False,
            "generation_authorized_by_requalification": False,
            "publication_ready": False,
        },
    }


class LeaseBoundExecutionResourceEvidenceTests(unittest.TestCase):
    def test_writes_attempt_bound_tamper_evident_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            store = LeaseBoundExecutionResourceEvidenceStore(temp)
            result = store.write(
                job=leased_job(),
                worker_id="gpu-worker-01",
                evidence=good_evidence(),
                observed_at=NOW,
            )

            path = Path(result["path"])
            self.assertTrue(path.is_file())
            self.assertEqual(path.name, "golden-candidate-01-attempt-1-execution-resource.json")
            self.assertEqual(len(result["sha256"]), 64)
            self.assertGreater(result["bytes"], 0)
            self.assertFalse(result["generation_authorized"])
            self.assertFalse(result["semantic_approved"])
            self.assertFalse(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], "pul7sar-lease-bound-execution-resource-v1")
            self.assertEqual(payload["attempt"], 1)
            self.assertEqual(payload["payload_sha256"], SHA)
            self.assertTrue(payload["gpu"]["eligible"])
            self.assertTrue(payload["host_memory"]["ready"])

    def test_replays_written_receipt_against_succeeded_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = LeaseBoundExecutionResourceEvidenceStore(root / "output" / "phase18_worker_results")
            written = store.write(
                job=leased_job(),
                worker_id="gpu-worker-01",
                evidence=good_evidence(),
                observed_at=NOW,
            )
            replay = store.verify(
                path=written["path"],
                job=succeeded_job(),
                repository_root=root,
            )
            self.assertEqual(replay["attempt"], 1)
            self.assertEqual(replay["worker_id"], "gpu-worker-01")
            self.assertEqual(replay["sha256"], written["sha256"])
            self.assertEqual(replay["bytes"], written["bytes"])
            self.assertTrue(replay["gpu"]["eligible"])
            self.assertTrue(replay["host_memory"]["ready"])
            self.assertFalse(replay["publication_ready"])

    def test_replay_rejects_identity_or_attempt_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = LeaseBoundExecutionResourceEvidenceStore(root / "evidence")
            written = store.write(
                job=leased_job(), worker_id="gpu-worker-01", evidence=good_evidence(), observed_at=NOW
            )
            payload = json.loads(Path(written["path"]).read_text(encoding="utf-8"))
            payload["attempt"] = 2
            Path(written["path"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "attempt drift"):
                store.verify(path=written["path"], job=succeeded_job(), repository_root=root)

    def test_replay_rejects_resource_values_below_recorded_floor(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = LeaseBoundExecutionResourceEvidenceStore(root / "evidence")
            written = store.write(
                job=leased_job(), worker_id="gpu-worker-01", evidence=good_evidence(), observed_at=NOW
            )
            payload = json.loads(Path(written["path"]).read_text(encoding="utf-8"))
            payload["gpu"]["gpu_free_vram_gb"] = 8.0
            Path(written["path"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "required live free VRAM"):
                store.verify(path=written["path"], job=succeeded_job(), repository_root=root)

    def test_replay_rejects_repository_path_escape(self):
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            outside = Path(outside_dir) / "resource.json"
            outside.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes repository"):
                LeaseBoundExecutionResourceEvidenceStore(outside.parent).verify(
                    path=outside,
                    job=succeeded_job(),
                    repository_root=root_dir,
                )

    def test_rejects_non_leased_job(self):
        job = leased_job().transition(GenerationJobState.RUNNING, now=NOW, attempt=1)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "leased job"):
                LeaseBoundExecutionResourceEvidenceStore(temp).write(
                    job=job,
                    worker_id="gpu-worker-01",
                    evidence=good_evidence(),
                    observed_at=NOW,
                )

    def test_rejects_worker_that_does_not_own_lease(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "does not own"):
                LeaseBoundExecutionResourceEvidenceStore(temp).write(
                    job=leased_job(),
                    worker_id="gpu-worker-02",
                    evidence=good_evidence(),
                    observed_at=NOW,
                )

    def test_rejects_gpu_or_ram_authority_drift(self):
        cases = []
        gpu = good_evidence()
        gpu["gpu"] = dict(gpu["gpu"], generation_authorized_by_requalification=True)
        cases.append(gpu)
        ram = good_evidence()
        ram["host_memory"] = dict(ram["host_memory"], publication_ready=True)
        cases.append(ram)

        for evidence in cases:
            with self.subTest(evidence=evidence), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(ValueError):
                    LeaseBoundExecutionResourceEvidenceStore(temp).write(
                        job=leased_job(),
                        worker_id="gpu-worker-01",
                        evidence=evidence,
                        observed_at=NOW,
                    )

    def test_rejects_unready_resource_evidence(self):
        evidence = good_evidence()
        evidence["host_memory"] = dict(evidence["host_memory"], ready=False)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "host-memory"):
                LeaseBoundExecutionResourceEvidenceStore(temp).write(
                    job=leased_job(),
                    worker_id="gpu-worker-01",
                    evidence=evidence,
                    observed_at=NOW,
                )


if __name__ == "__main__":
    unittest.main()

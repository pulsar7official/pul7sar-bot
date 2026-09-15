from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_REVISION
from engine.intelligence.first_png_provenance_postflight import FirstPngProvenancePostflight
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState
from engine.intelligence.golden_smoke import GoldenSmokeCandidate


class FirstPngProvenancePostflightTests(unittest.TestCase):
    def _fixture(self, root: Path):
        proof = root / "output" / "phase18_visual_proof" / "candidate-01.png"
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_bytes(b"\x89PNG\r\n\x1a\nreal-proof-bytes")

        metadata = root / "output" / "phase18_visual_proof" / "candidate-01.metadata.json"
        metadata.write_text(json.dumps({
            "request_id": "golden-v5-candidate-01",
            "seed": 7007001,
            "model": "black-forest-labs/FLUX.2-klein-4B",
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "cost_mode": "$0-local",
            "output_ref": str(proof),
        }), encoding="utf-8")

        executor = root / "output" / "phase18_worker_results" / "golden-smoke-candidate-01-attempt-1.json"
        executor.parent.mkdir(parents=True, exist_ok=True)
        executor.write_text(json.dumps({
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "request_id": "golden-v5-candidate-01",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "png": str(proof),
            "metadata": str(metadata),
        }), encoding="utf-8")

        candidate = GoldenSmokeCandidate(
            manifest_path=root / "manifest.json",
            handoff_path=root / "candidate.json",
            candidate=1,
            seed=7007001,
            request_id="golden-v5-candidate-01",
            payload_sha256="a" * 64,
            provider_id="local-diffusers",
            model_id="black-forest-labs/FLUX.2-klein-4B",
        )
        job = GenerationJob(
            job_id="golden-smoke-candidate-01",
            request_id=candidate.request_id,
            handoff_path=str(candidate.handoff_path),
            payload_sha256=candidate.payload_sha256,
            provider_id=candidate.provider_id,
            model_id=candidate.model_id,
            state=GenerationJobState.SUCCEEDED,
            attempt=1,
            result_path=str(proof),
            metadata={"candidate": 1, "seed": candidate.seed, "cost_mode": "$0-local"},
        )
        resource = root / "output" / "phase18_worker_results" / "golden-smoke-candidate-01-attempt-1-execution-resource.json"
        resource.write_text(json.dumps({
            "schema": "pul7sar-lease-bound-execution-resource-v1",
            "job_id": job.job_id,
            "request_id": job.request_id,
            "worker_id": "gpu-worker-01",
            "attempt": 1,
            "payload_sha256": job.payload_sha256,
            "provider_id": job.provider_id,
            "model_id": job.model_id,
            "observed_at": datetime(2026, 8, 26, 12, 0, tzinfo=timezone.utc).isoformat(),
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
            "queue_mutated_by_receipt": False,
            "generation_authorized_by_receipt": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }, sort_keys=True), encoding="utf-8")
        return candidate, job, proof, executor, metadata, resource

    def _verify(self, root: Path, candidate, job, executor, resource):
        return FirstPngProvenancePostflight().verify(
            repository_root=root,
            candidate=candidate,
            job=job,
            executor_result=executor,
            execution_resource_receipt=resource,
        )

    def test_succeeded_candidate_requires_and_passes_full_provenance_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, proof, executor, _, resource = self._fixture(root)
            receipt = self._verify(root, candidate, job, executor, resource)
            self.assertEqual(receipt["status"], "FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED")
            self.assertEqual(receipt["png"], str(proof.resolve()))
            self.assertEqual(len(receipt["png_sha256"]), 64)
            self.assertEqual(receipt["resolved_dtype"], "bfloat16")
            self.assertEqual(receipt["execution_resource_attempt"], 1)
            self.assertEqual(receipt["execution_resource_worker_id"], "gpu-worker-01")
            self.assertEqual(len(receipt["execution_resource_receipt_sha256"]), 64)
            self.assertTrue(receipt["execution_resource_gpu"]["eligible"])
            self.assertTrue(receipt["execution_resource_host_memory"]["ready"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["publication_ready"])

    def test_non_succeeded_job_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, _, executor, _, resource = self._fixture(root)
            queued = GenerationJob(
                job_id=job.job_id,
                request_id=job.request_id,
                handoff_path=job.handoff_path,
                payload_sha256=job.payload_sha256,
                provider_id=job.provider_id,
                model_id=job.model_id,
                metadata={"candidate": 1, "seed": candidate.seed, "cost_mode": "$0-local"},
            )
            with self.assertRaisesRegex(RuntimeError, "REQUIRES_SUCCEEDED_JOB"):
                self._verify(root, candidate, queued, executor, resource)

    def test_job_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, _, executor, _, resource = self._fixture(root)
            drifted = GenerationJob(
                job_id=job.job_id,
                request_id="other-request",
                handoff_path=job.handoff_path,
                payload_sha256=job.payload_sha256,
                provider_id=job.provider_id,
                model_id=job.model_id,
                state=GenerationJobState.SUCCEEDED,
                attempt=1,
                result_path=job.result_path,
                metadata={"candidate": 1, "seed": candidate.seed, "cost_mode": "$0-local"},
            )
            with self.assertRaisesRegex(RuntimeError, "REQUEST_ID_DRIFT"):
                self._verify(root, candidate, drifted, executor, resource)

    def test_executor_or_metadata_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, _, executor, metadata, resource = self._fixture(root)
            data = json.loads(metadata.read_text(encoding="utf-8"))
            data["cost_mode"] = "paid-api"
            metadata.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "METADATA_COST_MODE_MISMATCH"):
                self._verify(root, candidate, job, executor, resource)

    def test_execution_resource_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, _, executor, _, resource = self._fixture(root)
            payload = json.loads(resource.read_text(encoding="utf-8"))
            payload["host_memory"]["available_ram_gb"] = 4.0
            resource.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_EVIDENCE_FAILED"):
                self._verify(root, candidate, job, executor, resource)

    def test_execution_resource_attempt_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, job, _, executor, _, resource = self._fixture(root)
            payload = json.loads(resource.read_text(encoding="utf-8"))
            payload["attempt"] = 2
            resource.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_EVIDENCE_FAILED"):
                self._verify(root, candidate, job, executor, resource)

    def test_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            candidate, job, _, _, _, resource = self._fixture(root)
            external = Path(outside) / "executor.json"
            external.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EXECUTOR_ESCAPES_REPOSITORY"):
                self._verify(root, candidate, job, external, resource)

    def test_resource_evidence_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            candidate, job, _, executor, _, _ = self._fixture(root)
            external = Path(outside) / "resource.json"
            external.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_EVIDENCE_ESCAPES_REPOSITORY"):
                self._verify(root, candidate, job, executor, external)


if __name__ == "__main__":
    unittest.main()

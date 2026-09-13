from __future__ import annotations

from dataclasses import replace
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmissionReceipt
from engine.intelligence.dynamic_visual_brain_queue_binding import DynamicVisualBrainQueueBindingGate
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


class DynamicVisualBrainQueueBindingTests(unittest.TestCase):
    @staticmethod
    def admission() -> DynamicVisualBrainLocalAdmissionReceipt:
        return DynamicVisualBrainLocalAdmissionReceipt(
            contract="pul7sar-dynamic-visual-brain-local-admission-v2-renderer-safe",
            status="DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_LOCAL_RUNTIME_ADMITTED",
            story_fingerprint="a" * 64,
            competition_sha256="b" * 64,
            selected_concept_id="dynamic-transfer-arrival-corridor",
            selected_concept_sha256="c" * 64,
            scene_prompt_sha256="d" * 64,
            renderer_prompt_contract="pul7sar-dynamic-renderer-prompt-v2-identity-neutral",
            renderer_prompt_sha256="e" * 64,
            renderer_identity_neutral=True,
            original_scene_request_sha256="f" * 64,
            provider_id="local-diffusers",
            model_id="black-forest-labs/FLUX.2-klein-4B",
            backend="diffusers",
            request_id="dynamic-request-001",
            seed=20260827,
            cost_mode="$0-local",
            semantic_inspection_required=True,
            runtime_qualified=True,
            generation_request_compiled=True,
            generated_branding_allowed=False,
            generated_exact_facts_allowed=False,
            generated_sport_geometry_allowed=False,
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )

    @classmethod
    def request(cls) -> LocalBackendGenerationRequest:
        admission = cls.admission()
        return LocalBackendGenerationRequest(
            provider_id=admission.provider_id,
            model_id=admission.model_id,
            backend=admission.backend,
            prompt="Create one premium identity-neutral sports arrival atmosphere with no readable text or marks.",
            native_negative_constraints=(),
            width=1080,
            height=1352,
            seed=admission.seed,
            request_id=admission.request_id,
            metadata={
                "cost_mode": "$0-local",
                "generated_branding_allowed": False,
                "generated_exact_facts_allowed": False,
                "generated_sport_geometry_allowed": False,
                "semantic_inspection_required": True,
                "publication_ready": False,
                "human_visual_review_required": True,
                "golden_quality_approved": False,
                "dynamic_visual_brain_story_fingerprint": admission.story_fingerprint,
                "dynamic_visual_brain_competition_sha256": admission.competition_sha256,
                "dynamic_visual_brain_selected_concept_id": admission.selected_concept_id,
                "dynamic_visual_brain_selected_concept_sha256": admission.selected_concept_sha256,
                "dynamic_visual_brain_scene_prompt_sha256": admission.scene_prompt_sha256,
                "dynamic_renderer_prompt_contract": admission.renderer_prompt_contract,
                "dynamic_renderer_prompt_sha256": admission.renderer_prompt_sha256,
                "dynamic_renderer_identity_neutral": True,
                "dynamic_visual_brain_original_scene_request_sha256": admission.original_scene_request_sha256,
            },
        )

    def bind(self, root: Path, *, request=None, admission=None, handoff="output/dvb/request.json"):
        return DynamicVisualBrainQueueBindingGate.bind_and_enqueue(
            branch="phase18/story-intelligence",
            request=request or self.request(),
            admission=admission or self.admission(),
            handoff_path=handoff,
            queue_root="output/queue",
            repository_root=root,
        )

    def test_exact_admission_is_sha_sealed_and_enqueued(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            job, receipt = self.bind(root)
            self.assertEqual(job.state, GenerationJobState.QUEUED)
            self.assertEqual(receipt.status, "DYNAMIC_VISUAL_BRAIN_DURABLE_QUEUE_BOUND")
            self.assertEqual(receipt.selected_concept_sha256, "c" * 64)
            self.assertEqual(receipt.renderer_prompt_sha256, "e" * 64)
            self.assertTrue(receipt.semantic_inspection_required)
            self.assertTrue(receipt.human_visual_review_required)
            self.assertFalse(receipt.golden_quality_approved)
            self.assertFalse(receipt.publication_ready)
            self.assertFalse(receipt.already_enqueued)

            handoff = root / receipt.handoff_path
            replayed = LocalGenerationHandoff.read(str(handoff))
            self.assertEqual(replayed.request_id, self.request().request_id)
            self.assertEqual(replayed.metadata["dynamic_renderer_prompt_sha256"], "e" * 64)
            stored = FilesystemGenerationJobStore(root / "output/queue").get(receipt.job_id)
            self.assertIsNotNone(stored)
            self.assertEqual(stored.payload_sha256, receipt.handoff_payload_sha256)
            self.assertEqual(stored.metadata["dynamic_visual_brain_selected_concept_sha256"], "c" * 64)
            self.assertFalse(stored.metadata["publication_ready"])

    def test_same_exact_request_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_job, first = self.bind(root)
            second_job, second = self.bind(root)
            self.assertEqual(first_job.job_id, second_job.job_id)
            self.assertEqual(first.handoff_payload_sha256, second.handoff_payload_sha256)
            self.assertTrue(second.already_enqueued)

    def test_concept_hash_drift_is_rejected_before_queue_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = self.request()
            metadata = dict(request.metadata)
            metadata["dynamic_visual_brain_selected_concept_sha256"] = "9" * 64
            request = replace(request, metadata=metadata)
            with self.assertRaisesRegex(ValueError, "METADATA_DRIFT"):
                self.bind(root, request=request)
            self.assertEqual(list((root / "output/queue/queued").glob("*.json")) if (root / "output/queue/queued").exists() else [], [])

    def test_renderer_prompt_hash_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            admission = replace(self.admission(), renderer_prompt_sha256="1" * 64)
            with self.assertRaisesRegex(ValueError, "METADATA_DRIFT"):
                self.bind(root, admission=admission)

    def test_cost_or_publication_authority_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(ValueError, "COST_MODE_DRIFT"):
                self.bind(root, admission=replace(self.admission(), cost_mode="$paid"))
            with self.assertRaisesRegex(ValueError, "PUBLICATION_AUTHORITY_DRIFT"):
                self.bind(root, admission=replace(self.admission(), publication_ready=True))

    def test_paths_cannot_escape_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(ValueError, "OUTSIDE_REPOSITORY"):
                self.bind(root, handoff="../escape.json")

    def test_existing_job_with_drift_cannot_be_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            job, receipt = self.bind(root)
            store = FilesystemGenerationJobStore(root / "output/queue")
            stored = store.get(job.job_id)
            self.assertIsNotNone(stored)
            drifted = replace(stored, metadata={**dict(stored.metadata), "publication_ready": True})
            store.save(drifted)
            with self.assertRaisesRegex(ValueError, "EXISTING_QUEUE_JOB_DRIFT"):
                self.bind(root)


if __name__ == "__main__":
    unittest.main()

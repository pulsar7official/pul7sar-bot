from __future__ import annotations

from dataclasses import replace
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.dynamic_visual_brain_critic_binding import DynamicVisualBrainCriticBindingReceipt
from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmissionReceipt
from engine.intelligence.dynamic_visual_brain_queue_binding import DynamicVisualBrainQueueBindingGate
from engine.intelligence.dynamic_visual_brain_queue_critic_binding import DynamicVisualBrainQueueCriticBindingGate
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest


class DynamicVisualBrainQueueCriticBindingTests(unittest.TestCase):
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
            prompt="Create one premium identity-neutral arrival environment without readable text, logos, or exact geometry.",
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

    def fixture(self, root: Path):
        request = self.request()
        admission = self.admission()
        job, queue_receipt = DynamicVisualBrainQueueBindingGate.bind_and_enqueue(
            branch="phase18/story-intelligence",
            request=request,
            admission=admission,
            handoff_path="output/dvb/durable-request.json",
            queue_root="output/queue",
            repository_root=root,
        )
        binding_path = root / "output/dvb/queue-binding.json"
        binding_path.write_text(json.dumps(queue_receipt.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

        png = root / "output/proof/candidate.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\nqueue-bound-test")

        store = FilesystemGenerationJobStore(root / "output/queue")
        stored = store.get(job.job_id)
        self.assertIsNotNone(stored)
        succeeded = replace(stored, state=GenerationJobState.SUCCEEDED, attempt=1, result_path="output/proof/candidate.png")
        store.save(succeeded)

        result = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "png": "output/proof/candidate.png",
            "request_id": admission.request_id,
            "seed": admission.seed,
            "provider_id": admission.provider_id,
            "model_id": admission.model_id,
            "payload_sha256": queue_receipt.handoff_payload_sha256,
            "cost_mode": "$0-local",
            "publication_ready": False,
            "dynamic_visual_brain_story_fingerprint": admission.story_fingerprint,
            "dynamic_visual_brain_competition_sha256": admission.competition_sha256,
            "dynamic_visual_brain_selected_concept_id": admission.selected_concept_id,
            "dynamic_visual_brain_selected_concept_sha256": admission.selected_concept_sha256,
            "dynamic_visual_brain_scene_prompt_sha256": admission.scene_prompt_sha256,
            "dynamic_renderer_prompt_sha256": admission.renderer_prompt_sha256,
            "dynamic_visual_brain_original_scene_request_sha256": admission.original_scene_request_sha256,
            "dynamic_visual_brain_selection_locked_before_rendering": True,
            "concept_id": admission.selected_concept_id,
        }
        result_path = root / "output/worker-result.json"
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return queue_receipt, binding_path, result_path, png

    def critic_receipt(self, queue_receipt, png: Path) -> DynamicVisualBrainCriticBindingReceipt:
        import hashlib
        return DynamicVisualBrainCriticBindingReceipt(
            contract="pul7sar-dynamic-visual-brain-critic-binding-v2-renderer-safe",
            status="DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_CRITIC_PROVENANCE_BOUND",
            story_fingerprint=queue_receipt.story_fingerprint,
            competition_sha256=queue_receipt.competition_sha256,
            selected_concept_id=queue_receipt.selected_concept_id,
            selected_concept_sha256=queue_receipt.selected_concept_sha256,
            scene_prompt_sha256=queue_receipt.scene_prompt_sha256,
            renderer_prompt_contract="pul7sar-dynamic-renderer-prompt-v2-identity-neutral",
            renderer_prompt_sha256=queue_receipt.renderer_prompt_sha256,
            renderer_identity_neutral=True,
            original_scene_request_sha256=queue_receipt.original_scene_request_sha256,
            request_id=queue_receipt.request_id,
            seed=queue_receipt.seed,
            payload_sha256=queue_receipt.handoff_payload_sha256,
            concept_lock_sha256="1" * 64,
            local_admission_sha256="2" * 64,
            generation_result_sha256="3" * 64,
            critic_evidence_sha256="4" * 64,
            png_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),
            critic_approved=True,
            critic_rejections=(),
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )

    def verify(self, root: Path, binding_path: Path, result_path: Path, critic):
        with patch(
            "engine.intelligence.dynamic_visual_brain_queue_critic_binding.DynamicVisualBrainCriticBindingGate.verify",
            return_value=critic,
        ):
            return DynamicVisualBrainQueueCriticBindingGate.verify(
                queue_binding_path=str(binding_path.relative_to(root)),
                concept_lock_path="unused-concept.json",
                local_admission_path="unused-admission.json",
                batch_manifest_path="unused-batch.json",
                generation_result_path=str(result_path.relative_to(root)),
                critic_evidence_path="unused-critic.json",
                repository_root=str(root),
            )

    def test_succeeded_durable_job_is_bound_to_same_critic_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue_receipt, binding_path, result_path, png = self.fixture(root)
            receipt = self.verify(root, binding_path, result_path, self.critic_receipt(queue_receipt, png))
            self.assertEqual(receipt.status, "DYNAMIC_VISUAL_BRAIN_DURABLE_EXECUTION_CRITIC_BOUND")
            self.assertEqual(receipt.job_state, "succeeded")
            self.assertEqual(receipt.job_attempt, 1)
            self.assertTrue(receipt.critic_approved)
            self.assertTrue(receipt.human_visual_review_required)
            self.assertFalse(receipt.golden_quality_approved)
            self.assertFalse(receipt.publication_ready)

    def test_queue_job_concept_metadata_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue_receipt, binding_path, result_path, png = self.fixture(root)
            store = FilesystemGenerationJobStore(root / "output/queue")
            job = store.get(queue_receipt.job_id)
            self.assertIsNotNone(job)
            store.save(replace(job, metadata={**dict(job.metadata), "dynamic_visual_brain_selected_concept_sha256": "9" * 64}))
            with self.assertRaisesRegex(ValueError, "JOB_METADATA_DRIFT"):
                self.verify(root, binding_path, result_path, self.critic_receipt(queue_receipt, png))

    def test_generation_result_or_png_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue_receipt, binding_path, result_path, png = self.fixture(root)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["dynamic_renderer_prompt_sha256"] = "8" * 64
            result_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DURABLE_GENERATION_DRIFT"):
                self.verify(root, binding_path, result_path, self.critic_receipt(queue_receipt, png))

    def test_critic_cannot_belong_to_another_concept_or_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue_receipt, binding_path, result_path, png = self.fixture(root)
            critic = replace(self.critic_receipt(queue_receipt, png), selected_concept_id="other-concept")
            with self.assertRaisesRegex(ValueError, "DURABLE_CRITIC_DRIFT"):
                self.verify(root, binding_path, result_path, critic)

    def test_non_succeeded_job_cannot_be_promoted_to_critic_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            queue_receipt, binding_path, result_path, png = self.fixture(root)
            store = FilesystemGenerationJobStore(root / "output/queue")
            job = store.get(queue_receipt.job_id)
            self.assertIsNotNone(job)
            store.save(replace(job, state=GenerationJobState.TERMINAL_FAILED, result_path=None, failure_code="test", failure_detail="test"))
            with self.assertRaisesRegex(ValueError, "JOB_NOT_SUCCEEDED"):
                self.verify(root, binding_path, result_path, self.critic_receipt(queue_receipt, png))


if __name__ == "__main__":
    unittest.main()

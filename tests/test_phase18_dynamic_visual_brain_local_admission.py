import unittest
from dataclasses import replace

from engine.intelligence.dynamic_renderer_prompt import DynamicRendererPromptCompiler
from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock
from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmission
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class DynamicVisualBrainLocalAdmissionTests(unittest.TestCase):
    def _plan_lock(self):
        plan = DynamicVisualBrain().plan({
            "headline": "Verified League prepares for a new season",
            "summary": "PUL7SAR reports that Verified League is scheduled to begin this weekend.",
            "sport": "football",
            "story_type": "preview",
            "primary_entity": "Verified League",
        })
        return plan, DynamicVisualBrainConceptLock.lock(plan, plan.concepts[0].concept_id)

    @staticmethod
    def _readiness(*, ready=True, runtime_kind="local_cuda", provider_id=None, model_id=None, backend="diffusers"):
        return LocalGenerationReadinessReport(
            ready=ready,
            provider_id=provider_id or FLUX2_KLEIN_4B_LOCAL.provider_id,
            model_id=model_id or FLUX2_KLEIN_4B_LOCAL.model_id,
            backend=backend,
            runtime_kind=runtime_kind,
            gpu_name="Qualified GPU" if runtime_kind == "local_cuda" else None,
            gpu_vram_gb=24.0 if runtime_kind == "local_cuda" else None,
            blockers=() if ready else ("not ready",),
            warnings=(),
        )

    def test_measured_local_cuda_readiness_compiles_renderer_safe_concept_bound_request(self):
        plan, lock = self._plan_lock()
        request, concept_receipt, runtime_receipt, receipt = DynamicVisualBrainLocalAdmission.admit(
            plan=plan,
            lock=lock,
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=self._readiness(),
            backend="diffusers",
            request_id="dynamic-preview-001",
            seed=42,
        )
        self.assertNotIn(plan.concepts[0].scene_prompt, request.prompt)
        self.assertEqual(concept_receipt.renderer_prompt_contract, DynamicRendererPromptCompiler.CONTRACT)
        self.assertEqual(len(concept_receipt.renderer_prompt_sha256), 64)
        self.assertTrue(concept_receipt.renderer_identity_neutral)
        lowered = request.prompt.casefold()
        self.assertNotIn("verified league", lowered)
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)
        self.assertIn("no readable text", lowered)
        self.assertEqual(request.metadata["dynamic_visual_brain_story_fingerprint"], lock.story_fingerprint)
        self.assertEqual(request.metadata["dynamic_visual_brain_competition_sha256"], lock.competition_sha256)
        self.assertEqual(request.metadata["dynamic_visual_brain_selected_concept_sha256"], lock.selected_concept_sha256)
        self.assertEqual(request.metadata["dynamic_visual_brain_scene_prompt_sha256"], lock.scene_prompt_sha256)
        self.assertTrue(request.metadata["dynamic_visual_brain_selection_locked_before_rendering"])
        self.assertFalse(request.metadata["generated_branding_allowed"])
        self.assertFalse(request.metadata["generated_exact_facts_allowed"])
        self.assertFalse(request.metadata["generated_sport_geometry_allowed"])
        self.assertTrue(request.metadata["semantic_inspection_required"])
        self.assertFalse(request.metadata["publication_ready"])
        self.assertFalse(concept_receipt.publication_ready)
        self.assertFalse(runtime_receipt.publication_ready)
        self.assertTrue(receipt.runtime_qualified)
        self.assertTrue(receipt.generation_request_compiled)
        self.assertFalse(receipt.golden_quality_approved)
        self.assertFalse(receipt.publication_ready)

    def test_unready_runtime_is_rejected(self):
        plan, lock = self._plan_lock()
        with self.assertRaisesRegex(ValueError, "readiness|NOT_ADMITTED|not ready"):
            DynamicVisualBrainLocalAdmission.admit(
                plan=plan,
                lock=lock,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=self._readiness(ready=False),
                backend="diffusers",
                request_id="dynamic-preview-002",
                seed=1,
            )

    def test_cpu_runtime_is_not_admitted_for_generation(self):
        plan, lock = self._plan_lock()
        with self.assertRaisesRegex(ValueError, "NOT_ADMITTED"):
            DynamicVisualBrainLocalAdmission.admit(
                plan=plan,
                lock=lock,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=self._readiness(runtime_kind="local_cpu"),
                backend="diffusers",
                request_id="dynamic-preview-003",
                seed=1,
            )

    def test_model_or_backend_readiness_drift_is_rejected(self):
        plan, lock = self._plan_lock()
        with self.assertRaisesRegex(ValueError, "not match|mismatch|NOT_ADMITTED"):
            DynamicVisualBrainLocalAdmission.admit(
                plan=plan,
                lock=lock,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=self._readiness(model_id="wrong/model"),
                backend="diffusers",
                request_id="dynamic-preview-004",
                seed=1,
            )
        with self.assertRaisesRegex(ValueError, "BACKEND_READINESS_MISMATCH"):
            DynamicVisualBrainLocalAdmission.admit(
                plan=plan,
                lock=lock,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=self._readiness(backend="other-backend"),
                backend="diffusers",
                request_id="dynamic-preview-005",
                seed=1,
            )

    def test_concept_lock_tampering_cannot_reach_local_request(self):
        plan, lock = self._plan_lock()
        tampered = replace(lock, competition_sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "COMPETITION_DRIFT"):
            DynamicVisualBrainLocalAdmission.admit(
                plan=plan,
                lock=tampered,
                model=FLUX2_KLEIN_4B_LOCAL,
                readiness=self._readiness(),
                backend="diffusers",
                request_id="dynamic-preview-006",
                seed=1,
            )

    def test_platform_name_never_enters_local_prompt(self):
        plan, lock = self._plan_lock()
        request, *_ = DynamicVisualBrainLocalAdmission.admit(
            plan=plan,
            lock=lock,
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=self._readiness(),
            backend="diffusers",
            request_id="dynamic-preview-007",
            seed=7,
        )
        lowered = request.prompt.casefold()
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)
        self.assertNotIn("verified league", lowered)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.dynamic_renderer_prompt import DynamicRendererPromptCompiler
from tools.phase18_build_dynamic_transfer_handoff import build_dynamic_transfer_request
from tools.phase18_flux2_execute import _dynamic_visual_brain_result_metadata


class DynamicTransferHandoffTests(unittest.TestCase):
    def test_handoff_is_identity_neutral_and_executor_complete(self):
        request, concept, renderer, lock, original = build_dynamic_transfer_request(
            seed=9102001,
            request_id="dynamic-transfer-safe-test",
        )
        folded = request.prompt.casefold()
        self.assertNotIn("test midfielder", folded)
        self.assertNotIn("destination club", folded)
        self.assertNotIn("pul7sar", folded)
        self.assertNotIn("pulsar", folded)
        self.assertIn("no readable text", folded)
        self.assertIn("no football pitch", folded)

        metadata = request.metadata
        self.assertEqual(metadata["dynamic_visual_brain_selected_concept_id"], concept.concept_id)
        self.assertEqual(metadata["dynamic_visual_brain_selected_concept_sha256"], lock.selected_concept_sha256)
        self.assertEqual(metadata["dynamic_visual_brain_competition_sha256"], lock.competition_sha256)
        self.assertEqual(metadata["dynamic_renderer_prompt_contract"], DynamicRendererPromptCompiler.CONTRACT)
        self.assertEqual(metadata["dynamic_renderer_prompt_sha256"], original.renderer_prompt_sha256)
        self.assertTrue(metadata["dynamic_renderer_identity_neutral"])
        self.assertEqual(
            metadata["dynamic_visual_brain_original_scene_request_sha256"],
            original.original_scene_request_sha256,
        )
        self.assertEqual(metadata["cost_mode"], "$0-local")
        self.assertFalse(metadata["generated_branding_allowed"])
        self.assertFalse(metadata["generated_exact_facts_allowed"])
        self.assertFalse(metadata["generated_sport_geometry_allowed"])
        self.assertTrue(metadata["semantic_inspection_required"])
        self.assertTrue(metadata["human_visual_review_required"])
        self.assertFalse(metadata["golden_quality_approved"])
        self.assertFalse(metadata["publication_ready"])
        self.assertTrue(metadata["engineering_handoff_only"])
        self.assertFalse(renderer.publication_ready)

        durable = _dynamic_visual_brain_result_metadata(request)
        self.assertEqual(durable["dynamic_renderer_prompt_sha256"], original.renderer_prompt_sha256)
        self.assertTrue(durable["dynamic_renderer_identity_neutral"])
        self.assertEqual(durable["concept_id"], concept.concept_id)

    def test_seed_changes_execution_identity_without_changing_concept_selection(self):
        first = build_dynamic_transfer_request(seed=9102001, request_id="dynamic-transfer-safe-a")
        second = build_dynamic_transfer_request(seed=9102002, request_id="dynamic-transfer-safe-b")
        first_request, first_concept, _, first_lock, _ = first
        second_request, second_concept, _, second_lock, _ = second
        self.assertEqual(first_concept.concept_id, second_concept.concept_id)
        self.assertEqual(first_lock.selected_concept_sha256, second_lock.selected_concept_sha256)
        self.assertNotEqual(first_request.seed, second_request.seed)
        self.assertNotEqual(first_request.request_id, second_request.request_id)


if __name__ == "__main__":
    unittest.main()

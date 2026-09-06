import unittest
from types import SimpleNamespace

from engine.intelligence.dynamic_renderer_prompt import DynamicRendererPromptCompiler
from tools.phase18_flux2_execute import _dynamic_visual_brain_result_metadata


class DynamicVisualBrainExecutorProvenanceTests(unittest.TestCase):
    def _request(self, **overrides):
        metadata = {
            "dynamic_visual_brain_contract": "pul7sar-dynamic-visual-brain-v1",
            "dynamic_visual_brain_story_fingerprint": "1" * 64,
            "dynamic_visual_brain_competition_sha256": "2" * 64,
            "dynamic_visual_brain_selected_concept_id": "preview-atmosphere-01",
            "dynamic_visual_brain_selected_concept_sha256": "3" * 64,
            "dynamic_visual_brain_scene_prompt_sha256": "4" * 64,
            "dynamic_renderer_prompt_contract": DynamicRendererPromptCompiler.CONTRACT,
            "dynamic_renderer_prompt_sha256": "6" * 64,
            "dynamic_renderer_identity_neutral": True,
            "dynamic_visual_brain_original_scene_request_sha256": "5" * 64,
            "dynamic_visual_brain_selection_locked_before_rendering": True,
            "cost_mode": "$0-local",
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "semantic_inspection_required": True,
            "human_visual_review_required": True,
            "publication_ready": False,
        }
        metadata.update(overrides)
        return SimpleNamespace(metadata=metadata)

    def test_locked_dynamic_identity_and_renderer_prompt_are_copied_without_authority(self):
        result = _dynamic_visual_brain_result_metadata(self._request())
        self.assertEqual(result["concept_id"], "preview-atmosphere-01")
        self.assertEqual(result["dynamic_visual_brain_story_fingerprint"], "1" * 64)
        self.assertEqual(result["dynamic_visual_brain_original_scene_request_sha256"], "5" * 64)
        self.assertEqual(result["dynamic_renderer_prompt_contract"], DynamicRendererPromptCompiler.CONTRACT)
        self.assertEqual(result["dynamic_renderer_prompt_sha256"], "6" * 64)
        self.assertTrue(result["dynamic_renderer_identity_neutral"])
        self.assertTrue(result["dynamic_visual_brain_selection_locked_before_rendering"])
        self.assertNotIn("publication_ready", result)
        self.assertNotIn("generation_authorized", result)

    def test_non_dynamic_request_remains_backward_compatible(self):
        self.assertEqual(_dynamic_visual_brain_result_metadata(SimpleNamespace(metadata={"cost_mode": "$0-local"})), {})

    def test_authority_drift_is_rejected_before_generation(self):
        with self.assertRaisesRegex(RuntimeError, "authority drifted"):
            _dynamic_visual_brain_result_metadata(self._request(generated_sport_geometry_allowed=True))
        with self.assertRaisesRegex(RuntimeError, "authority drifted"):
            _dynamic_visual_brain_result_metadata(self._request(publication_ready=True))

    def test_renderer_prompt_identity_drift_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "prompt contract drifted"):
            _dynamic_visual_brain_result_metadata(self._request(dynamic_renderer_prompt_contract="old-contract"))
        with self.assertRaisesRegex(RuntimeError, "identity neutrality"):
            _dynamic_visual_brain_result_metadata(self._request(dynamic_renderer_identity_neutral=False))
        with self.assertRaisesRegex(RuntimeError, "invalid dynamic_renderer_prompt_sha256"):
            _dynamic_visual_brain_result_metadata(self._request(dynamic_renderer_prompt_sha256="short"))

    def test_missing_or_invalid_hash_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            request = self._request()
            metadata = dict(request.metadata)
            metadata.pop("dynamic_visual_brain_scene_prompt_sha256")
            _dynamic_visual_brain_result_metadata(SimpleNamespace(metadata=metadata))
        with self.assertRaisesRegex(RuntimeError, "invalid"):
            _dynamic_visual_brain_result_metadata(self._request(dynamic_visual_brain_selected_concept_sha256="short"))


if __name__ == "__main__":
    unittest.main()

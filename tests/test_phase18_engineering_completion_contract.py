import unittest
from pathlib import Path


class Phase18EngineeringCompletionContractTests(unittest.TestCase):
    def _text(self, path: str) -> str:
        file = Path(path)
        self.assertTrue(file.is_file(), path)
        return file.read_text(encoding="utf-8")

    def test_partial_geometry_hard_failure_propagates_end_to_end(self):
        expected = "exact_verified_or_visually_indeterminate"
        handoff = self._text("tools/phase18_build_golden_handoff.py")
        budget = self._text("engine/intelligence/golden_prompt_budget.py")
        provider = self._text("engine/intelligence/provider_prompting.py")
        local_backend = self._text("engine/intelligence/local_backend_execution.py")
        batch = self._text("tools/phase18_build_golden_batch.py")
        verifier = self._text("tools/phase18_verify_golden_batch.py")
        colab = self._text("tools/phase18_colab_runner.py")
        qwen = self._text("engine/intelligence/qwen25_vl_inspector.py")
        review = self._text("tools/phase18_build_golden_review_template.py")
        for text in (handoff, budget, verifier, colab):
            self.assertIn(expected, text)
        self.assertIn("GOLDEN_SPORT_GEOMETRY_INTEGRITY_POLICY", batch)
        self.assertIn('"sport_geometry_integrity_policy": geometry_integrity_policy', local_backend)
        self.assertIn('"partial_sport_geometry_allowed": partial_geometry_allowed', local_backend)
        self.assertIn('"partial_sport_geometry_hallucination_is_hard_failure": partial_geometry_hard_failure', local_backend)
        self.assertIn("_NO_PARTIAL_UNVERIFIED_GEOMETRY", provider)
        self.assertIn("show no goal frame or goal net", budget)
        self.assertIn("partial_sport_geometry_hallucination_is_hard_failure", handoff)
        self.assertIn("hard-reject any candidate with invented partial regulation sport geometry", batch)
        self.assertIn("partial_sport_geometry_allowed", verifier)
        self.assertIn("EXPECTED_GEOMETRY_INTEGRITY", colab)
        self.assertIn("physically impossible relationship to a touchline/endline", qwen)
        self.assertIn("broken_sport_surface_geometry as a hard blocker", review)

    def test_colab_persists_image_before_optional_semantic_qa(self):
        notebook = self._text("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.assertIn("Generate, save and display Candidate 1", notebook)
        self.assertIn("Semantic QA", notebook)
        self.assertLess(notebook.index("Generate, save and display Candidate 1"), notebook.index("Semantic QA"))
        self.assertIn("publication_ready", notebook)

    def test_completion_audit_never_claims_publication_readiness(self):
        audit = self._text("tools/phase18_completion_audit.py")
        self.assertIn('"engineering_complete": engineering_complete', audit)
        self.assertIn('"ready_for_publication_claim": False', audit)
        self.assertIn("multi_family_real_png_visual_quality_validation_not_yet_owner_accepted", audit)
        self.assertIn("final_publication_gate_not_yet_owner_approved", audit)


if __name__ == "__main__":
    unittest.main()

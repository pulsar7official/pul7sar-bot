import unittest

from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionPolicy
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport


class HybridVisualInspectionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = HybridVisualInspectionPolicy()

    def report(self, **changes):
        values = dict(
            png_observation=True,
            protected_region_clutter=True,
            semantic_subject_framing=True,
            identity_similarity=True,
            semantic_defect_detection=True,
            forbidden_visual_detection=True,
        )
        values.update(changes)
        return LocalVisionCapabilityReport(**values)

    def test_full_non_identity_capability_is_auto_qa_ready(self):
        decision = self.policy.evaluate(self.report(identity_similarity=False), identity_required=False)
        self.assertTrue(decision.automatic_visual_qa_ready)
        self.assertTrue(decision.publication_visual_gate_ready)
        self.assertEqual(decision.missing_capabilities, ())

    def test_identity_story_requires_similarity(self):
        decision = self.policy.evaluate(self.report(identity_similarity=False), identity_required=True)
        self.assertFalse(decision.automatic_visual_qa_ready)
        self.assertIn("identity_similarity", decision.missing_capabilities)

    def test_semantic_detection_gap_blocks_automatic_qa_but_not_engineering_proof(self):
        decision = self.policy.evaluate(
            self.report(semantic_defect_detection=False, forbidden_visual_detection=False),
            identity_required=False,
        )
        self.assertTrue(decision.engineering_proof_allowed)
        self.assertFalse(decision.automatic_visual_qa_ready)
        self.assertIn("semantic_defect_detection", decision.missing_capabilities)
        self.assertIn("forbidden_visual_detection", decision.missing_capabilities)

    def test_missing_png_observation_blocks_even_engineering_proof(self):
        decision = self.policy.evaluate(self.report(png_observation=False), identity_required=False)
        self.assertFalse(decision.engineering_proof_allowed)


if __name__ == "__main__":
    unittest.main()

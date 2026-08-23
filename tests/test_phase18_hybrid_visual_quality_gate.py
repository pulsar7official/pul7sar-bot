import unittest

from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.hybrid_visual_quality_gate import HybridVisualEvidence, HybridVisualQualityGate
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine


class HybridVisualQualityGateTests(unittest.TestCase):
    def setUp(self):
        editorial = StoryVisualEditorialEngine().plan(
            event=EditorialEvent.RESULT,
            sport="football",
            story_core="verified result",
            editorial_angle="result",
            headline_short="Result",
            primary_subject="Team",
            confidence=0.95,
        )
        self.plan = HybridVisualLayerPlanner().plan(editorial, SportVisualRuleRegistry().get("football"))
        self.gate = HybridVisualQualityGate()

    def valid_evidence(self):
        return HybridVisualEvidence(
            deterministic_geometry_applied=True,
            exact_brand_asset_applied=True,
            exact_typography_applied=True,
            verified_identity_asset_applied=True,
        )

    def test_complete_exact_layers_can_pass(self):
        result = self.gate.evaluate(self.plan, self.valid_evidence())
        self.assertTrue(result.approved)
        self.assertEqual(result.blockers, ())

    def test_generated_pul7sar_wordmark_is_hard_blocked(self):
        evidence = HybridVisualEvidence(
            generated_brand_detected=True,
            deterministic_geometry_applied=True,
            exact_brand_asset_applied=True,
            exact_typography_applied=True,
            verified_identity_asset_applied=True,
        )
        result = self.gate.evaluate(self.plan, evidence)
        self.assertFalse(result.approved)
        self.assertIn("generated_pul7sar_brand_leakage", result.blockers)

    def test_missing_deterministic_pitch_is_hard_blocked(self):
        evidence = HybridVisualEvidence(
            exact_brand_asset_applied=True,
            exact_typography_applied=True,
            verified_identity_asset_applied=True,
        )
        result = self.gate.evaluate(self.plan, evidence)
        self.assertIn("required_deterministic_sport_geometry_missing", result.blockers)

    def test_generated_text_is_hard_blocked(self):
        evidence = self.valid_evidence()
        evidence = HybridVisualEvidence(**{**evidence.__dict__, "generated_text_detected": True})
        result = self.gate.evaluate(self.plan, evidence)
        self.assertIn("generated_text_leakage", result.blockers)


if __name__ == "__main__":
    unittest.main()

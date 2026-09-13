import unittest

from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.hybrid_visual_quality_gate import (
    DeterministicGeometryReceipt,
    HybridVisualEvidence,
    HybridVisualQualityGate,
)
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

    def valid_geometry_receipt(self):
        return DeterministicGeometryReceipt(
            renderer_id="football_pitch_projective_v1",
            integrity_status="REGULATION_FOOTBALL_GEOMETRY_READY",
            output_ref="output/phase18_hybrid/football-pitch-overlay.png",
            details={
                "length_m": 105.0,
                "width_m": 68.0,
                "symmetric_penalty_areas": True,
            },
        )

    def valid_evidence(self):
        return HybridVisualEvidence(
            deterministic_geometry_applied=True,
            deterministic_geometry_receipt=self.valid_geometry_receipt(),
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
            deterministic_geometry_receipt=self.valid_geometry_receipt(),
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
        self.assertIn("deterministic_geometry_receipt_missing", result.blockers)

    def test_boolean_geometry_claim_without_receipt_is_hard_blocked(self):
        evidence = HybridVisualEvidence(
            deterministic_geometry_applied=True,
            exact_brand_asset_applied=True,
            exact_typography_applied=True,
            verified_identity_asset_applied=True,
        )
        result = self.gate.evaluate(self.plan, evidence)
        self.assertFalse(result.approved)
        self.assertIn("deterministic_geometry_receipt_missing", result.blockers)

    def test_invalid_geometry_receipt_is_hard_blocked(self):
        evidence = HybridVisualEvidence(
            deterministic_geometry_applied=True,
            deterministic_geometry_receipt=DeterministicGeometryReceipt(
                renderer_id="",
                integrity_status="REGULATION_FOOTBALL_GEOMETRY_READY",
                output_ref="output/pitch.png",
            ),
            exact_brand_asset_applied=True,
            exact_typography_applied=True,
            verified_identity_asset_applied=True,
        )
        result = self.gate.evaluate(self.plan, evidence)
        self.assertFalse(result.approved)
        self.assertIn("deterministic_geometry_receipt_invalid", result.blockers)

    def test_generated_text_is_hard_blocked(self):
        evidence = self.valid_evidence()
        evidence = HybridVisualEvidence(**{**evidence.__dict__, "generated_text_detected": True})
        result = self.gate.evaluate(self.plan, evidence)
        self.assertIn("generated_text_leakage", result.blockers)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine
from engine.intelligence.visual_layer_qa import HybridLayerQualityGate, LayerLeakageEvidence


class HybridLayerQualityGateTests(unittest.TestCase):
    def setUp(self):
        editorial = StoryVisualEditorialEngine().plan(
            event=EditorialEvent.RESULT,
            sport="football",
            story_core="verified final result",
            editorial_angle="decisive result",
            headline_short="Decisive result",
            primary_subject="Team A",
            confidence=0.95,
        )
        rule = SportVisualRuleRegistry().get("football")
        self.plan = HybridVisualLayerPlanner().plan(editorial, rule)
        self.gate = HybridLayerQualityGate()

    def test_clean_base_scene_passes(self):
        decision = self.gate.evaluate(self.plan, LayerLeakageEvidence())
        self.assertTrue(decision.passed)
        self.assertEqual(decision.blockers, ())

    def test_generated_text_is_always_blocked(self):
        decision = self.gate.evaluate(self.plan, LayerLeakageEvidence(generated_text_detected=True))
        self.assertFalse(decision.passed)
        self.assertIn("generated_text_leaked_into_deterministic_typography", decision.blockers)

    def test_generated_platform_brand_is_blocked(self):
        decision = self.gate.evaluate(self.plan, LayerLeakageEvidence(generated_platform_brand_detected=True))
        self.assertIn("generated_platform_brand_leaked_into_verified_brand_layer", decision.blockers)

    def test_generated_football_geometry_is_blocked_when_geometry_is_deterministic(self):
        decision = self.gate.evaluate(self.plan, LayerLeakageEvidence(generated_sport_geometry_detected=True))
        self.assertIn("generated_sport_geometry_leaked_into_deterministic_geometry_layer", decision.blockers)

    def test_unverified_generated_identity_is_blocked_for_verified_hero_layer(self):
        decision = self.gate.evaluate(self.plan, LayerLeakageEvidence(generated_unverified_identity_detected=True))
        self.assertIn("generated_identity_leaked_into_verified_identity_layer", decision.blockers)

    def test_exact_numbers_and_entity_marks_are_blocked(self):
        evidence = LayerLeakageEvidence(
            generated_exact_numbers_detected=True,
            generated_entity_mark_detected=True,
        )
        decision = self.gate.evaluate(self.plan, evidence)
        self.assertIn("generated_exact_data_leaked_into_deterministic_data_layer", decision.blockers)
        self.assertIn("generated_entity_mark_leaked_into_verified_asset_layer", decision.blockers)

    def test_assert_allowed_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "HYBRID_LAYER_QA_BLOCKED"):
            self.gate.assert_allowed(self.plan, LayerLeakageEvidence(generated_text_detected=True))


if __name__ == "__main__":
    unittest.main()

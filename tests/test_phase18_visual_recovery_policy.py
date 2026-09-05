import unittest

from engine.intelligence.visual_recovery_policy import RecoveryAction, VisualRecoveryPolicy


class VisualRecoveryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = VisualRecoveryPolicy()

    def test_generated_text_regenerates_base_only(self):
        decision = self.policy.decide("generated_text_leakage", generation_attempt=1)
        self.assertEqual(decision.action, RecoveryAction.REGENERATE_BASE)
        self.assertTrue(decision.consumes_generation_retry)
        self.assertEqual(decision.next_attempt, 2)

    def test_geometry_failure_does_not_waste_diffusion_retry(self):
        decision = self.policy.decide("semantic:sport_geometry_alignment_valid:failed", generation_attempt=2)
        self.assertEqual(decision.action, RecoveryAction.RECOMPOSE_GEOMETRY)
        self.assertFalse(decision.consumes_generation_retry)
        self.assertEqual(decision.next_attempt, 2)

    def test_missing_brand_is_post_composition_problem(self):
        decision = self.policy.decide("exact_pul7sar_brand_missing", generation_attempt=1)
        self.assertEqual(decision.action, RecoveryAction.COMPOSE_EXACT_BRAND)
        self.assertFalse(decision.consumes_generation_retry)

    def test_missing_palette_falls_back_to_red(self):
        decision = self.policy.decide("dominant_palette_missing", generation_attempt=0)
        self.assertEqual(decision.action, RecoveryAction.USE_DEFAULT_BRAND_RED)

    def test_identity_failure_switches_to_verified_assets(self):
        decision = self.policy.decide("identity_unverified", generation_attempt=0)
        self.assertEqual(decision.action, RecoveryAction.SWITCH_TO_VERIFIED_ASSETS)

    def test_fact_integrity_failure_returns_upstream(self):
        decision = self.policy.decide("story_integrity:draw_cannot_have_winner_entity", generation_attempt=0)
        self.assertEqual(decision.action, RecoveryAction.REFRESH_FACTS)

    def test_repeated_generative_failure_changes_angle_instead_of_looping_forever(self):
        decision = self.policy.decide("collage_or_split_scene", generation_attempt=3, max_generation_attempts=3)
        self.assertEqual(decision.action, RecoveryAction.REPLAN_EDITORIAL_ANGLE)
        self.assertTrue(decision.exhausted)
        self.assertFalse(decision.consumes_generation_retry)

    def test_unknown_failure_is_not_auto_repaired(self):
        decision = self.policy.decide("mysterious_new_failure", generation_attempt=0)
        self.assertEqual(decision.action, RecoveryAction.BLOCK)


if __name__ == "__main__":
    unittest.main()

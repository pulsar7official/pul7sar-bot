import unittest

from engine.intelligence.scene_complexity_policy import SceneComplexityPolicy, SurfaceVisibility
from engine.intelligence.story_visual_editorial import EditorialEvent


class SceneComplexityPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = SceneComplexityPolicy()

    def test_transfer_does_not_require_generated_pitch_or_stadium(self):
        decision = self.policy.decide(EditorialEvent.TRANSFER_CONFIRMED)
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.NONE)
        self.assertTrue(decision.avoid_full_venue_generation)

    def test_preview_is_context_only_not_deterministic_pitch(self):
        decision = self.policy.decide(EditorialEvent.PREVIEW)
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.CONTEXT_ONLY)
        self.assertTrue(decision.avoid_full_venue_generation)
        self.assertIn("optional surface texture", decision.background_strategy)
        self.assertIn("not mandatory playing-surface geometry", decision.rationale)

    def test_result_uses_only_partial_deterministic_surface(self):
        decision = self.policy.decide(EditorialEvent.RESULT)
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.PARTIAL_DETERMINISTIC)
        self.assertEqual(decision.max_hero_subjects, 2)

    def test_tactics_uses_full_deterministic_surface(self):
        decision = self.policy.decide(EditorialEvent.TACTICS)
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.FULL_DETERMINISTIC)
        self.assertEqual(decision.max_hero_subjects, 0)

    def test_preview_result_tactics_form_strict_surface_hierarchy(self):
        preview = self.policy.decide(EditorialEvent.PREVIEW)
        result = self.policy.decide(EditorialEvent.RESULT)
        tactics = self.policy.decide(EditorialEvent.TACTICS)
        self.assertEqual(
            (preview.surface_visibility, result.surface_visibility, tactics.surface_visibility),
            (
                SurfaceVisibility.CONTEXT_ONLY,
                SurfaceVisibility.PARTIAL_DETERMINISTIC,
                SurfaceVisibility.FULL_DETERMINISTIC,
            ),
        )

    def test_general_story_avoids_exact_venue_dependency(self):
        decision = self.policy.decide(EditorialEvent.GENERAL)
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.CONTEXT_ONLY)
        self.assertTrue(decision.avoid_full_venue_generation)


if __name__ == "__main__":
    unittest.main()

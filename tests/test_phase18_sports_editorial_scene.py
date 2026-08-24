import unittest

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily, SportsEditorialSceneDirector
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class SportsEditorialSceneDirectorTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.director = SportsEditorialSceneDirector()

    def scene(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        decision = self.orchestrator.decide(story)
        return self.director.direct(event, decision.visual_grammar)

    def test_transfer_is_not_forced_into_full_pitch_or_data_card(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        self.assertEqual(scene.family, EditorialSceneFamily.TRANSFER_SIGNATURE)
        self.assertLessEqual(scene.headline_max_words, 8)
        self.assertIn("no mandatory pitch", scene.environment)
        self.assertTrue(scene.metadata["premium_editorial_not_data_card"])
        self.assertIn("forced full football pitch when story does not require it", scene.forbidden)

    def test_result_is_neutral_to_loser_and_copy_is_sparse(self):
        scene = self.scene(EditorialEvent.RESULT)
        self.assertEqual(scene.family, EditorialSceneFamily.RESULT_STATEMENT)
        self.assertFalse(scene.allow_supporting_copy)
        self.assertEqual(scene.supporting_copy_max_words, 0)
        self.assertIn("neutral and respected", scene.hero_priority)

    def test_injury_is_verified_subject_led(self):
        scene = self.scene(EditorialEvent.INJURY)
        self.assertEqual(scene.family, EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
        self.assertIn("verified subject asset", scene.hero_priority)
        self.assertIn("expression and posture must not be fabricated as fact", scene.hero_priority)

    def test_tactics_owns_geometry_deterministically(self):
        scene = self.scene(EditorialEvent.TACTICS)
        self.assertEqual(scene.family, EditorialSceneFamily.TACTICAL_BOARD)
        self.assertIn("deterministic sport geometry", scene.environment)

    def test_table_is_data_monument_without_unnecessary_stadium(self):
        scene = self.scene(EditorialEvent.TABLE)
        self.assertEqual(scene.family, EditorialSceneFamily.DATA_MONUMENT)
        self.assertIn("no unnecessary stadium generation", scene.environment)

    def test_brand_master_is_hybrid_adaptive_and_legacy_logo_forbidden(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        self.assertEqual(scene.brand_identity_id, "pul7sar-hybrid-adaptive-v1")
        self.assertIn("PUL7SAR metallic wordmark geometry", scene.deterministic_ownership)
        self.assertIn("PUL7SAR dynamic pulse/7 geometry", scene.deterministic_ownership)
        self.assertIn("legacy repository logo as canonical identity", scene.forbidden)


if __name__ == "__main__":
    unittest.main()

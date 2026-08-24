import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.platform_editorial_composition import PlatformEditorialCompositionResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent


class PlatformEditorialCompositionTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.resolver = PlatformEditorialCompositionResolver()
        self.profiles = PlatformProfileRegistry()

    def decision(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            secondary_subjects=("Verified Opponent",),
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        return self.orchestrator.decide(story)

    def test_result_gets_result_geometry_not_transfer_layout(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        composition = self.resolver.resolve(self.decision(EditorialEvent.RESULT), profile)
        self.assertEqual(composition.family, EditorialSceneFamily.RESULT_STATEMENT)
        self.assertIsNotNone(composition.result_statement)
        self.assertIsNone(composition.verified_subject_news)
        self.assertIsNone(composition.tactical_intelligence)
        self.assertFalse(composition.inherits_transfer_layout)
        self.assertTrue(composition.result_statement.score_is_primary)
        self.assertLessEqual(composition.brand.max_width_ratio, 0.25)

    def test_transfer_has_no_dedicated_result_subject_or_tactical_contract(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        composition = self.resolver.resolve(self.decision(EditorialEvent.TRANSFER_CONFIRMED), profile)
        self.assertEqual(composition.family, EditorialSceneFamily.TRANSFER_SIGNATURE)
        self.assertIsNone(composition.result_statement)
        self.assertIsNone(composition.verified_subject_news)
        self.assertIsNone(composition.tactical_intelligence)
        self.assertFalse(composition.inherits_transfer_layout)
        self.assertLessEqual(composition.brand.max_width_ratio, 0.30)

    def test_injury_gets_verified_subject_contract(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        injury = self.resolver.resolve(self.decision(EditorialEvent.INJURY), profile)
        self.assertEqual(injury.family, EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
        self.assertIsNotNone(injury.verified_subject_news)
        self.assertTrue(injury.verified_subject_news.verified_subject_required)
        self.assertFalse(injury.verified_subject_news.fabricated_pose_allowed)
        self.assertFalse(injury.verified_subject_news.fabricated_expression_allowed)
        self.assertIsNone(injury.result_statement)
        self.assertIsNone(injury.tactical_intelligence)

    def test_tactics_gets_exact_geometry_contract(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        tactics = self.resolver.resolve(self.decision(EditorialEvent.TACTICS), profile)
        self.assertEqual(tactics.family, EditorialSceneFamily.TACTICAL_BOARD)
        self.assertIsNotNone(tactics.tactical_intelligence)
        self.assertTrue(tactics.tactical_intelligence.exact_sport_geometry_required)
        self.assertTrue(tactics.tactical_intelligence.exact_formation_data_required)
        self.assertFalse(tactics.tactical_intelligence.generated_pitch_markings_allowed)
        self.assertFalse(tactics.tactical_intelligence.generated_player_positions_allowed)
        self.assertIsNone(tactics.result_statement)
        self.assertIsNone(tactics.verified_subject_news)

    def test_injury_and_tactics_receive_distinct_brand_behavior(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        injury = self.resolver.resolve(self.decision(EditorialEvent.INJURY), profile)
        tactics = self.resolver.resolve(self.decision(EditorialEvent.TACTICS), profile)
        self.assertNotEqual(injury.brand.zone, tactics.brand.zone)
        self.assertGreater(injury.brand.max_width_ratio, tactics.brand.max_width_ratio)

    def test_same_result_art_directs_differently_for_portrait_and_landscape(self):
        decision = self.decision(EditorialEvent.RESULT)
        portrait = self.resolver.resolve(decision, self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = self.resolver.resolve(decision, self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.result_statement.score_box, landscape.result_statement.score_box)
        self.assertNotEqual(portrait.result_statement.headline_box, landscape.result_statement.headline_box)

    def test_same_subject_news_art_directs_differently_for_portrait_and_landscape(self):
        decision = self.decision(EditorialEvent.INJURY)
        portrait = self.resolver.resolve(decision, self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = self.resolver.resolve(decision, self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.verified_subject_news.subject_box, landscape.verified_subject_news.subject_box)
        self.assertNotEqual(portrait.verified_subject_news.headline_box, landscape.verified_subject_news.headline_box)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.tactical_intelligence_composition import TacticalIntelligenceComposer
from engine.intelligence.verified_subject_news_composition import VerifiedSubjectNewsComposer
from engine.intelligence.adaptive_brand_placement import BrandZone


class SubjectAndTacticalCompositionTests(unittest.TestCase):
    def setUp(self):
        self.profiles = PlatformProfileRegistry()

    def test_verified_subject_news_is_portrait_led_and_fact_safe(self):
        plan = VerifiedSubjectNewsComposer().plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_RIGHT)
        self.assertTrue(plan.verified_subject_required)
        self.assertTrue(plan.identity_reference_is_not_publishable_subject)
        self.assertFalse(plan.fabricated_pose_allowed)
        self.assertFalse(plan.fabricated_expression_allowed)
        self.assertFalse(plan.fantasy_medical_scene_allowed)
        self.assertTrue(plan.brand_must_not_overlap_face)
        self.assertFalse(plan.publication_ready)

    def test_tactical_intelligence_is_exact_geometry_owned(self):
        plan = TacticalIntelligenceComposer().plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_LEFT)
        self.assertTrue(plan.exact_sport_geometry_required)
        self.assertTrue(plan.exact_formation_data_required)
        self.assertFalse(plan.generated_pitch_markings_allowed)
        self.assertFalse(plan.generated_player_positions_allowed)
        self.assertFalse(plan.decorative_stadium_is_primary)
        self.assertFalse(plan.publication_ready)

    def test_tactical_brand_is_quieter_than_verified_subject_brand(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        subject = VerifiedSubjectNewsComposer().plan(profile)
        tactical = TacticalIntelligenceComposer().plan(profile)
        self.assertLess(tactical.brand.max_width_ratio, subject.brand.max_width_ratio)
        self.assertLess(tactical.brand.max_height_ratio, subject.brand.max_height_ratio)

    def test_portrait_and_landscape_subject_geometry_differ(self):
        composer = VerifiedSubjectNewsComposer()
        portrait = composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = composer.plan(self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.subject_box, landscape.subject_box)
        self.assertNotEqual(portrait.headline_box, landscape.headline_box)

    def test_portrait_and_landscape_tactical_geometry_differ(self):
        composer = TacticalIntelligenceComposer()
        portrait = composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = composer.plan(self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.tactical_surface_box, landscape.tactical_surface_box)
        self.assertNotEqual(portrait.headline_box, landscape.headline_box)


if __name__ == "__main__":
    unittest.main()

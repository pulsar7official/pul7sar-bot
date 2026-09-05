import unittest

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.adaptive_brand_placement import BrandZone


class ResultStatementCompositionTests(unittest.TestCase):
    def setUp(self):
        self.composer = ResultStatementComposer()
        self.profiles = PlatformProfileRegistry()

    def test_instagram_result_is_not_transfer_template(self):
        plan = self.composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertTrue(plan.score_is_primary)
        self.assertTrue(plan.club_identity_scale_equal)
        self.assertEqual(plan.winner_emphasis_mode, "accent_and_hierarchy_only")
        self.assertEqual(plan.loser_treatment, "neutral_respectful_no_degradation")
        self.assertFalse(plan.supporting_paragraph_allowed)
        self.assertFalse(plan.generated_score_allowed)
        self.assertFalse(plan.generated_crest_allowed)
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_CENTER)
        self.assertLessEqual(plan.brand.max_width_ratio, 0.25)
        self.assertFalse(plan.publication_ready)

    def test_score_owns_center_and_club_identities_remain_balanced(self):
        plan = self.composer.plan(self.profiles.get(SocialPlatform.FACEBOOK_FEED))
        self.assertAlmostEqual(plan.home_identity_box.width, plan.away_identity_box.width)
        self.assertAlmostEqual(plan.home_identity_box.height, plan.away_identity_box.height)
        self.assertGreater(plan.score_box.x, plan.home_identity_box.x)
        self.assertLess(plan.score_box.x + plan.score_box.width, plan.away_identity_box.x + plan.away_identity_box.width)

    def test_landscape_result_has_distinct_geometry(self):
        portrait = self.composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = self.composer.plan(self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.score_box, landscape.score_box)
        self.assertNotEqual(portrait.headline_box, landscape.headline_box)
        self.assertEqual(landscape.contract, "pul7sar-result-statement-composition-v1")

    def test_every_platform_produces_normalized_safe_contract(self):
        for platform in SocialPlatform:
            plan = self.composer.plan(self.profiles.get(platform))
            for box in (plan.score_box, plan.home_identity_box, plan.away_identity_box, plan.headline_box):
                self.assertGreaterEqual(box.x, 0)
                self.assertGreaterEqual(box.y, 0)
                self.assertLessEqual(box.x + box.width, 1)
                self.assertLessEqual(box.y + box.height, 1)


if __name__ == "__main__":
    unittest.main()

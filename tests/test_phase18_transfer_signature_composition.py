import unittest

from engine.intelligence.adaptive_brand_placement import BrandZone
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.transfer_signature_composition import TransferSignatureComposer


class TransferSignatureCompositionTests(unittest.TestCase):
    def setUp(self):
        self.composer = TransferSignatureComposer()
        self.profiles = PlatformProfileRegistry()

    def test_transfer_is_verified_hero_led_not_pitch_template(self):
        plan = self.composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        self.assertTrue(plan.verified_hero_required)
        self.assertTrue(plan.destination_context_is_secondary)
        self.assertFalse(plan.full_pitch_required)
        self.assertFalse(plan.dense_stats_allowed)
        self.assertFalse(plan.generated_crest_allowed)
        self.assertFalse(plan.generated_brand_allowed)
        self.assertFalse(plan.protected_person_copy_overlap_allowed)
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_CENTER)
        self.assertLessEqual(plan.brand.max_width_ratio, 0.30)
        self.assertFalse(plan.publication_ready)

    def test_portrait_and_landscape_transfer_geometry_differ(self):
        portrait = self.composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = self.composer.plan(self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.hero_box, landscape.hero_box)
        self.assertNotEqual(portrait.headline_box, landscape.headline_box)
        self.assertNotEqual(portrait.club_context_box, landscape.club_context_box)

    def test_verified_hero_never_intersects_copy_or_adaptive_brand_lane(self):
        for platform in SocialPlatform:
            plan = self.composer.plan(self.profiles.get(platform))
            self.assertFalse(self.composer._intersects(plan.hero_box, plan.headline_box))
            self.assertFalse(self.composer._intersects(plan.hero_box, plan.club_context_box))
            brand = plan.brand
            brand_box = NormalizedBox(
                brand.center_x_ratio - brand.max_width_ratio / 2,
                brand.center_y_ratio - brand.max_height_ratio / 2,
                brand.max_width_ratio,
                brand.max_height_ratio,
            )
            self.assertFalse(self.composer._intersects(plan.hero_box, brand_box), platform.value)

    def test_transfer_contract_is_distinct_and_non_authorizing(self):
        plan = self.composer.plan(self.profiles.get(SocialPlatform.FACEBOOK_FEED))
        self.assertEqual(plan.contract, "pul7sar-transfer-signature-composition-v3-adaptive-brand-lane")
        self.assertFalse(plan.publication_ready)


if __name__ == "__main__":
    unittest.main()

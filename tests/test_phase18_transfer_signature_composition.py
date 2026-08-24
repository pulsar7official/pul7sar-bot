import unittest

from engine.intelligence.adaptive_brand_placement import BrandZone
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
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
        self.assertEqual(plan.brand.zone, BrandZone.LOWER_CENTER)
        self.assertLessEqual(plan.brand.max_width_ratio, 0.30)
        self.assertFalse(plan.publication_ready)

    def test_portrait_and_landscape_transfer_geometry_differ(self):
        portrait = self.composer.plan(self.profiles.get(SocialPlatform.INSTAGRAM_FEED))
        landscape = self.composer.plan(self.profiles.get(SocialPlatform.X_FEED))
        self.assertNotEqual(portrait.hero_box, landscape.hero_box)
        self.assertNotEqual(portrait.headline_box, landscape.headline_box)
        self.assertNotEqual(portrait.club_context_box, landscape.club_context_box)

    def test_transfer_contract_is_distinct_and_non_authorizing(self):
        plan = self.composer.plan(self.profiles.get(SocialPlatform.FACEBOOK_FEED))
        self.assertEqual(plan.contract, "pul7sar-transfer-signature-composition-v1")
        self.assertFalse(plan.publication_ready)


if __name__ == "__main__":
    unittest.main()

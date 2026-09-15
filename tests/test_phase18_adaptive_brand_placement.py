import unittest

from engine.intelligence.adaptive_brand_placement import (
    AdaptiveBrandPlacementResolver,
    BrandZone,
)
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class AdaptiveBrandPlacementTests(unittest.TestCase):
    def setUp(self):
        self.resolver = AdaptiveBrandPlacementResolver()
        self.profiles = PlatformProfileRegistry()

    def test_transfer_signature_is_subordinate_not_footer_dominant(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        plan = self.resolver.resolve(family=EditorialSceneFamily.TRANSFER_SIGNATURE, profile=profile)
        self.assertEqual(plan.zone, BrandZone.LOWER_CENTER)
        self.assertLessEqual(plan.max_width_ratio, 0.30)
        self.assertLessEqual(plan.max_height_ratio, 0.105)
        self.assertIn("subordinate", plan.reason)

    def test_result_signature_is_smaller_than_transfer_and_score_safe(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        transfer = self.resolver.resolve(family=EditorialSceneFamily.TRANSFER_SIGNATURE, profile=profile)
        result = self.resolver.resolve(family=EditorialSceneFamily.RESULT_STATEMENT, profile=profile)
        self.assertLess(result.max_width_ratio, transfer.max_width_ratio)
        self.assertLess(result.max_height_ratio, transfer.max_height_ratio)
        self.assertIn("deterministic score", result.reason)

    def test_verified_subject_prefers_side_signature_to_protect_portrait(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        plan = self.resolver.resolve(family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, profile=profile)
        self.assertEqual(plan.zone, BrandZone.LOWER_RIGHT)
        self.assertIn("portrait-led", plan.reason)

    def test_tactical_board_uses_smallest_structural_signature(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        plan = self.resolver.resolve(family=EditorialSceneFamily.TACTICAL_BOARD, profile=profile)
        self.assertEqual(plan.zone, BrandZone.LOWER_LEFT)
        self.assertLessEqual(plan.max_width_ratio, 0.21)
        self.assertIn("tactical geometry", plan.reason)

    def test_collision_moves_brand_without_changing_geometry_contract(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_STORY)
        plan = self.resolver.resolve(
            family=EditorialSceneFamily.TRANSFER_SIGNATURE,
            profile=profile,
            occupied_zones=(BrandZone.LOWER_CENTER,),
        )
        self.assertEqual(plan.zone, BrandZone.LOWER_RIGHT)
        self.assertEqual(plan.contract, "pul7sar-adaptive-brand-placement-v1")

    def test_no_clear_zone_fails_closed(self):
        profile = self.profiles.get(SocialPlatform.FACEBOOK_FEED)
        with self.assertRaisesRegex(ValueError, "NO_CLEAR_BRAND_ZONE_AVAILABLE"):
            self.resolver.resolve(
                family=EditorialSceneFamily.RESULT_STATEMENT,
                profile=profile,
                occupied_zones=(BrandZone.LOWER_CENTER, BrandZone.UPPER_RIGHT, BrandZone.UPPER_LEFT),
            )

    def test_all_platforms_keep_brand_inside_safe_area_center(self):
        for platform in SocialPlatform:
            profile = self.profiles.get(platform)
            plan = self.resolver.resolve(family=EditorialSceneFamily.EVENT_EDITORIAL, profile=profile)
            left = profile.safe_area.left / profile.width
            right = 1 - profile.safe_area.right / profile.width
            top = profile.safe_area.top / profile.height
            bottom = 1 - profile.safe_area.bottom / profile.height
            self.assertGreater(plan.center_x_ratio, left)
            self.assertLess(plan.center_x_ratio, right)
            self.assertGreater(plan.center_y_ratio, top)
            self.assertLess(plan.center_y_ratio, bottom)


if __name__ == "__main__":
    unittest.main()

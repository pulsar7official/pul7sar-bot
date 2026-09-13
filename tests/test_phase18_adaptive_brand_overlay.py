import unittest

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class AdaptiveBrandOverlayTests(unittest.TestCase):
    def setUp(self):
        self.resolver = AdaptiveBrandPlacementResolver()
        self.profiles = PlatformProfileRegistry()
        self.reference_size = (1000, 300)

    def test_all_42_family_platform_pairs_resolve_to_safe_pixel_boxes(self):
        checked = 0
        for family in EditorialSceneFamily:
            for platform in SocialPlatform:
                profile = self.profiles.get(platform)
                adaptive = self.resolver.resolve(family=family, profile=profile)
                placement, height = AdaptiveBrandOverlayRenderer.resolve_placement(
                    adaptive=adaptive,
                    profile=profile,
                    reference_size=self.reference_size,
                )

                clearance = round(min(profile.width, profile.height) * adaptive.minimum_clearance_ratio)
                safe_left = profile.safe_area.left + clearance
                safe_right = profile.width - profile.safe_area.right - clearance
                safe_top = profile.safe_area.top + clearance
                safe_bottom = profile.height - profile.safe_area.bottom - clearance

                self.assertGreaterEqual(placement.x, safe_left, (family, platform))
                self.assertLessEqual(placement.x + placement.width, safe_right, (family, platform))
                self.assertGreaterEqual(placement.y, safe_top, (family, platform))
                self.assertLessEqual(placement.y + height, safe_bottom, (family, platform))
                self.assertLessEqual(
                    placement.width,
                    round(profile.width * adaptive.max_width_ratio),
                    (family, platform),
                )
                self.assertLessEqual(
                    height,
                    round(profile.height * adaptive.max_height_ratio),
                    (family, platform),
                )
                self.assertNotEqual(placement.width, 870, (family, platform))
                checked += 1

        self.assertEqual(checked, len(EditorialSceneFamily) * len(SocialPlatform))
        self.assertEqual(checked, 42)

    def test_family_scale_hierarchy_survives_pixel_conversion(self):
        profile = self.profiles.get(SocialPlatform.INSTAGRAM_FEED)
        widths = {}
        for family in EditorialSceneFamily:
            adaptive = self.resolver.resolve(family=family, profile=profile)
            placement, _ = AdaptiveBrandOverlayRenderer.resolve_placement(
                adaptive=adaptive,
                profile=profile,
                reference_size=self.reference_size,
            )
            widths[family] = placement.width

        self.assertGreater(
            widths[EditorialSceneFamily.TRANSFER_SIGNATURE],
            widths[EditorialSceneFamily.RESULT_STATEMENT],
        )
        self.assertGreater(
            widths[EditorialSceneFamily.RESULT_STATEMENT],
            widths[EditorialSceneFamily.TACTICAL_BOARD],
        )

    def test_canvas_profile_mismatch_fails_closed(self):
        profile = self.profiles.get(SocialPlatform.X_FEED)
        adaptive = self.resolver.resolve(family=EditorialSceneFamily.EVENT_EDITORIAL, profile=profile)
        with self.assertRaisesRegex(ValueError, "ADAPTIVE_BRAND_PROFILE_CANVAS_MISMATCH"):
            AdaptiveBrandOverlayRenderer.resolve_placement(
                adaptive=adaptive,
                profile=profile,
                reference_size=self.reference_size,
                canvas_size=(1080, 1350),
            )


if __name__ == "__main__":
    unittest.main()

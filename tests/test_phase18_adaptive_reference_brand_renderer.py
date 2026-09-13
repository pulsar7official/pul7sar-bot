import unittest

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver
from engine.intelligence.editorial_reference_scene_study_renderer import EditorialReferenceSceneStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class AdaptiveReferenceBrandRendererTests(unittest.TestCase):
    def setUp(self):
        self.resolver = AdaptiveBrandPlacementResolver()
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)

    def _placement_for(self, family: EditorialSceneFamily):
        adaptive = self.resolver.resolve(family=family, profile=self.profile)
        placement, height = EditorialReferenceSceneStudyRenderer._absolute_brand_placement(
            adaptive=adaptive,
            profile=self.profile,
            reference_size=(1000, 300),
        )
        return adaptive, placement, height

    def test_fixed_870px_brand_regression_is_removed(self):
        self.assertFalse(hasattr(EditorialReferenceSceneStudyRenderer, "BRAND_PLACEMENT"))
        adaptive, placement, height = self._placement_for(EditorialSceneFamily.TRANSFER_SIGNATURE)
        self.assertLess(placement.width, 870)
        self.assertLessEqual(placement.width, round(self.profile.width * adaptive.max_width_ratio))
        self.assertLessEqual(height, round(self.profile.height * adaptive.max_height_ratio))

    def test_transfer_signature_resolves_to_30_percent_width_ceiling(self):
        adaptive, placement, _ = self._placement_for(EditorialSceneFamily.TRANSFER_SIGNATURE)
        self.assertEqual(adaptive.max_width_ratio, 0.30)
        self.assertEqual(placement.width, 324)

    def test_result_signature_is_physically_smaller_than_transfer(self):
        _, transfer, transfer_height = self._placement_for(EditorialSceneFamily.TRANSFER_SIGNATURE)
        _, result, result_height = self._placement_for(EditorialSceneFamily.RESULT_STATEMENT)
        self.assertLess(result.width, transfer.width)
        self.assertLess(result_height, transfer_height)

    def test_placement_box_stays_inside_platform_safe_area_plus_clearance(self):
        adaptive, placement, height = self._placement_for(EditorialSceneFamily.TRANSFER_SIGNATURE)
        clearance = round(min(self.profile.width, self.profile.height) * adaptive.minimum_clearance_ratio)
        safe_left = self.profile.safe_area.left + clearance
        safe_right = self.profile.width - self.profile.safe_area.right - clearance
        safe_top = self.profile.safe_area.top + clearance
        safe_bottom = self.profile.height - self.profile.safe_area.bottom - clearance

        self.assertGreaterEqual(placement.x, safe_left)
        self.assertLessEqual(placement.x + placement.width, safe_right)
        self.assertGreaterEqual(placement.y, safe_top)
        self.assertLessEqual(placement.y + height, safe_bottom)

    def test_mismatched_platform_canvas_fails_closed(self):
        story_profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_STORY)
        adaptive = self.resolver.resolve(
            family=EditorialSceneFamily.TRANSFER_SIGNATURE,
            profile=story_profile,
        )
        with self.assertRaisesRegex(ValueError, "EDITORIAL_STUDY_PROFILE_CANVAS_MISMATCH"):
            EditorialReferenceSceneStudyRenderer._absolute_brand_placement(
                adaptive=adaptive,
                profile=story_profile,
                reference_size=(1000, 300),
            )


if __name__ == "__main__":
    unittest.main()

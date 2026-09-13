import unittest

from engine.intelligence.canvas_normalization import CanvasNormalizationPlanner
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class CanvasNormalizationTests(unittest.TestCase):
    def request(self, width, height, target_width, target_height):
        return LocalBackendGenerationRequest(
            provider_id=FLUX2_KLEIN_4B_LOCAL.provider_id,
            model_id=FLUX2_KLEIN_4B_LOCAL.model_id,
            backend="diffusers",
            prompt="scene",
            native_negative_constraints=(),
            width=width,
            height=height,
            seed=1,
            request_id="canvas-test",
            metadata={
                "cost_mode": "$0-local",
                "target_width": target_width,
                "target_height": target_height,
            },
        )

    def test_flux_instagram_feed_aligns_to_16_pixels(self):
        self.assertEqual(FLUX2_KLEIN_4B_LOCAL.align_canvas(1080, 1350), (1088, 1360))

    def test_flux_story_aligns_native_width_without_changing_target(self):
        self.assertEqual(FLUX2_KLEIN_4B_LOCAL.align_canvas(1080, 1920), (1088, 1920))

    def test_feed_native_canvas_normalizes_back_to_exact_4_5(self):
        plan = CanvasNormalizationPlanner().plan(self.request(1088, 1360, 1080, 1350))
        self.assertEqual((plan.target_width, plan.target_height), (1080, 1350))
        self.assertEqual(plan.crop_width / plan.crop_height, 4 / 5)
        self.assertTrue(plan.requires_resize)

    def test_story_small_native_ratio_difference_is_safely_center_cropped(self):
        plan = CanvasNormalizationPlanner().plan(self.request(1088, 1920, 1080, 1920))
        self.assertLess(plan.crop_width, 1088)
        self.assertEqual(plan.crop_height, 1920)
        self.assertAlmostEqual(plan.crop_width / plan.crop_height, 9 / 16, places=3)

    def test_large_aspect_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "differs too much"):
            CanvasNormalizationPlanner().plan(self.request(1200, 1200, 1080, 1920))


if __name__ == "__main__":
    unittest.main()

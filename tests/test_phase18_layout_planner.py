import unittest

from engine.intelligence.layout_planner import (
    DeterministicLayoutPlanner, LayoutOrientation, LayoutRequirements,
)
from engine.intelligence.layout_safety import LayoutRole, PlatformLayoutSafetyGate
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class DeterministicLayoutPlannerTests(unittest.TestCase):
    def setUp(self):
        self.registry = PlatformProfileRegistry()
        self.planner = DeterministicLayoutPlanner()
        self.gate = PlatformLayoutSafetyGate()

    def test_story_uses_vertical_layout(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_STORY)
        layout = self.planner.plan(profile)
        self.assertEqual(layout.orientation, LayoutOrientation.VERTICAL)
        self.assertEqual(layout.box_for(LayoutRole.SOCIAL_FOOTER).bottom, profile.height - profile.safe_area.bottom)
        self.assertTrue(self.gate.evaluate(profile, layout.boxes).allowed)

    def test_x_uses_landscape_layout(self):
        profile = self.registry.get(SocialPlatform.X_FEED)
        layout = self.planner.plan(profile)
        self.assertEqual(layout.orientation, LayoutOrientation.LANDSCAPE)
        self.assertGreater(layout.box_for(LayoutRole.HERO).width, layout.box_for(LayoutRole.HEADLINE).width)

    def test_instagram_feed_uses_portrait_layout(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        layout = self.planner.plan(profile)
        self.assertEqual(layout.orientation, LayoutOrientation.PORTRAIT)

    def test_result_layout_can_add_crest_and_score(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        layout = self.planner.plan(
            profile,
            LayoutRequirements(include_crest=True, include_score=True),
        )
        self.assertIsNotNone(layout.box_for(LayoutRole.CREST))
        self.assertIsNotNone(layout.box_for(LayoutRole.SCORE))
        self.assertTrue(self.gate.evaluate(profile, layout.boxes).allowed)

    def test_entity_accent_is_normalized(self):
        profile = self.registry.get(SocialPlatform.FACEBOOK_FEED)
        layout = self.planner.plan(profile, entity_accent_hex="e30613")
        self.assertEqual(layout.accent_hex, "#E30613")

    def test_general_story_defaults_to_pul7sar_red(self):
        profile = self.registry.get(SocialPlatform.THREADS_FEED)
        layout = self.planner.plan(profile)
        self.assertEqual(layout.accent_hex, "#E10600")

    def test_invalid_accent_is_rejected(self):
        profile = self.registry.get(SocialPlatform.TELEGRAM_POST)
        with self.assertRaises(ValueError):
            self.planner.plan(profile, entity_accent_hex="red")

    def test_same_story_is_art_directed_differently_by_surface(self):
        vertical = self.planner.plan(self.registry.get(SocialPlatform.INSTAGRAM_STORY))
        landscape = self.planner.plan(self.registry.get(SocialPlatform.X_FEED))
        self.assertNotEqual(vertical.box_for(LayoutRole.HERO), landscape.box_for(LayoutRole.HERO))
        self.assertNotEqual(vertical.orientation, landscape.orientation)


if __name__ == "__main__":
    unittest.main()

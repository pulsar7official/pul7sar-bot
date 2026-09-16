import unittest

from engine.intelligence.direct_visual_layout import DirectDataLayoutPlanner
from engine.intelligence.layout_safety import LayoutRole
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class DirectDataLayoutPlannerTests(unittest.TestCase):
    def test_instagram_feed_separates_headline_and_data_panel(self):
        profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        layout = DirectDataLayoutPlanner().plan(profile)
        headline = layout.box_for(LayoutRole.HEADLINE)
        hero = layout.box_for(LayoutRole.HERO)
        logo = layout.box_for(LayoutRole.LOGO)
        self.assertIsNotNone(headline)
        self.assertIsNotNone(hero)
        self.assertIsNotNone(logo)
        self.assertLess(headline.y + headline.height, hero.y)
        self.assertEqual(layout.strategy, "pul7sar-direct-data-v1")

    def test_x_landscape_keeps_headline_and_data_panel_separate(self):
        profile = PlatformProfileRegistry().get(SocialPlatform.X_FEED)
        layout = DirectDataLayoutPlanner().plan(profile)
        headline = layout.box_for(LayoutRole.HEADLINE)
        hero = layout.box_for(LayoutRole.HERO)
        self.assertLess(headline.x + headline.width, hero.x)


if __name__ == "__main__":
    unittest.main()

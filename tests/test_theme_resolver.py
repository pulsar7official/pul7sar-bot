import unittest

from engine.branding.defaults import get_default_brand_palette
from engine.entities.model import EntityContext
from engine.themes.contrast import choose_text_color, contrast_ratio, luminance
from engine.themes.model import ResolvedTheme
from engine.themes.registry import ThemeRegistry
from engine.themes.resolver import ThemeResolver


class TestThemeResolver(unittest.TestCase):
    def setUp(self):
        self.registry = ThemeRegistry()
        self.club = ResolvedTheme(
            primary_color=(3, 70, 148),
            secondary_color=(255, 255, 255),
            text_color=(255, 255, 255),
            overlay_color=(0, 20, 60),
            overlay_opacity=0.72,
            accent_color=(3, 70, 148),
            entity_key="chelsea",
            source="club",
            logo_treatment="contextual",
        )
        self.registry.register("chelsea", self.club)
        self.resolver = ThemeResolver(self.registry, get_default_brand_palette())

    def test_known(self):
        self.assertIs(
            self.resolver.resolve(EntityContext(key="chelsea")),
            self.club,
        )

    def test_unknown_and_none_fallback(self):
        first = self.resolver.resolve(EntityContext(key="unknown"))
        second = self.resolver.resolve(None)
        self.assertEqual(first, second)
        self.assertIsNone(first.entity_key)

    def test_contrast_module_is_source_of_truth(self):
        background = (245, 245, 245)
        selected = choose_text_color(background)
        self.assertGreaterEqual(
            contrast_ratio(background, selected),
            contrast_ratio(background, (255, 255, 255)),
        )
        self.assertGreater(luminance(background), 0.5)


if __name__ == "__main__":
    unittest.main()

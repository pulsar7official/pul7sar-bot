import unittest

from engine.themes.model import ResolvedTheme
from engine.themes.registry import ThemeRegistry


def make_theme():
    return ResolvedTheme(
        primary_color=(1, 2, 3),
        secondary_color=None,
        text_color=(255, 255, 255),
        overlay_color=(0, 0, 0),
        overlay_opacity=0.7,
        accent_color=(4, 5, 6),
        entity_key="test",
        source="club",
    )


class TestThemeRegistry(unittest.TestCase):
    def test_register_get_has(self):
        registry = ThemeRegistry()
        theme = make_theme()
        registry.register("test", theme)
        self.assertTrue(registry.has("test"))
        self.assertIs(registry.get("test"), theme)
        self.assertIsNone(registry.get("missing"))


if __name__ == "__main__":
    unittest.main()

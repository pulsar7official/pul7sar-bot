import unittest
from dataclasses import FrozenInstanceError

from engine.themes.model import ResolvedTheme


class TestResolvedTheme(unittest.TestCase):
    def test_theme_is_frozen_and_has_no_brand_default(self):
        theme = ResolvedTheme(
            primary_color=(1, 2, 3),
            secondary_color=None,
            text_color=(255, 255, 255),
            overlay_color=(0, 0, 0),
            overlay_opacity=0.7,
            accent_color=(10, 20, 30),
        )
        with self.assertRaises(FrozenInstanceError):
            theme.accent_color = (225, 6, 0)  # type: ignore[misc]

    def test_invalid_opacity_rejected(self):
        with self.assertRaises(ValueError):
            ResolvedTheme(
                primary_color=(1, 2, 3),
                secondary_color=None,
                text_color=(255, 255, 255),
                overlay_color=(0, 0, 0),
                overlay_opacity=1.5,
                accent_color=(10, 20, 30),
            )


if __name__ == "__main__":
    unittest.main()

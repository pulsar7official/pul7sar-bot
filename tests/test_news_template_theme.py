import ast
import unittest
from pathlib import Path

from engine.themes.model import ResolvedTheme


class TestNewsTemplateThemeArchitecture(unittest.TestCase):
    def test_no_club_specific_conditions_in_template_source(self):
        path = Path("engine/templates/implementations/news.py")
        source = path.read_text(encoding="utf-8")
        lowered = source.lower()
        for club in ("chelsea", "liverpool", "real_madrid", "barcelona"):
            self.assertNotIn(club, lowered)

    def test_theme_model_requires_explicit_accent(self):
        with self.assertRaises(TypeError):
            ResolvedTheme(  # type: ignore[call-arg]
                primary_color=(1, 2, 3),
                secondary_color=None,
                text_color=(255, 255, 255),
                overlay_color=(0, 0, 0),
                overlay_opacity=0.7,
            )


if __name__ == "__main__":
    unittest.main()

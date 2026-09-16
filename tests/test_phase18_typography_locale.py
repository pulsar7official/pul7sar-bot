import unittest

from engine.intelligence.typography import TextAlign, TextRole
from engine.intelligence.typography_locale import TypographyLocaleResolver


class TypographyLocaleResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = TypographyLocaleResolver()

    def test_arabic_headline_is_rtl_and_right_aligned(self):
        result = self.resolver.resolve("ريال مدريد يحسم الصفقة", role=TextRole.HEADLINE)
        self.assertEqual(result.direction, "rtl")
        self.assertEqual(result.align, TextAlign.RIGHT)

    def test_english_headline_is_ltr_and_left_aligned(self):
        result = self.resolver.resolve("Real Madrid completes the deal", role=TextRole.HEADLINE)
        self.assertEqual(result.direction, "ltr")
        self.assertEqual(result.align, TextAlign.LEFT)

    def test_score_is_centered_even_with_team_names(self):
        result = self.resolver.resolve("ARS 2-1 CHE", role=TextRole.SCORE)
        self.assertEqual(result.align, TextAlign.CENTER)

    def test_mixed_headline_uses_dominant_script(self):
        result = self.resolver.resolve("ريال مدريد Real Madrid يحسمها", role=TextRole.HEADLINE)
        self.assertTrue(result.mixed)
        self.assertEqual(result.direction, "rtl")
        self.assertEqual(result.align, TextAlign.RIGHT)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.dynamic_brand_contrast import DynamicBrandContrastResolver, contrast_ratio


class DynamicBrandContrastTests(unittest.TestCase):
    def test_high_contrast_keeps_accent_without_keyline(self):
        plan = DynamicBrandContrastResolver().resolve(accent_hex="#E10600", background_hex="#101010")
        self.assertFalse(plan.keyline_required)
        self.assertIsNone(plan.keyline_hex)
        self.assertTrue(plan.preserve_accent)

    def test_low_contrast_adds_keyline_without_recoloring_accent(self):
        plan = DynamicBrandContrastResolver().resolve(accent_hex="#202020", background_hex="#242424")
        self.assertTrue(plan.keyline_required)
        self.assertIn(plan.keyline_hex, {"#FFFFFF", "#000000"})
        self.assertEqual(plan.accent_hex, "#202020")
        self.assertTrue(plan.preserve_accent)

    def test_contrast_ratio_is_symmetric(self):
        self.assertAlmostEqual(contrast_ratio("#FFFFFF", "#000000"), contrast_ratio("#000000", "#FFFFFF"))
        self.assertGreater(contrast_ratio("#FFFFFF", "#000000"), 20.0)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.sport_visual_rules import SportSurface, SportVisualRuleRegistry


class SportVisualRuleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = SportVisualRuleRegistry()

    def test_explicit_major_sports_have_rules(self):
        sports = (
            "football", "basketball", "tennis", "padel", "badminton", "volleyball", "handball",
            "baseball", "american_football", "rugby", "cricket", "golf", "boxing", "mma",
            "wrestling", "judo", "taekwondo", "athletics", "formula_1", "motorsport", "swimming",
            "cycling", "rowing", "sailing", "ice_hockey", "winter_sport", "table_tennis", "snooker",
            "darts", "gymnastics", "weightlifting", "equestrian", "esports",
        )
        for sport in sports:
            with self.subTest(sport=sport):
                rule = self.registry.get(sport)
                self.assertEqual(rule.sport, sport)
                self.assertTrue(rule.safe_generated_context)

    def test_arabic_aliases_preserve_correct_sport(self):
        self.assertEqual(self.registry.get("كرة القدم").sport, "football")
        self.assertEqual(self.registry.get("رفع الأثقال").sport, "weightlifting")
        self.assertEqual(self.registry.get("الرياضات الإلكترونية").sport, "esports")
        self.assertEqual(self.registry.get("تنس الطاولة").surface, SportSurface.TABLE)

    def test_unknown_sport_stays_conservative(self):
        rule = self.registry.get("sepaktakraw")
        self.assertEqual(rule.surface, SportSurface.OPEN_ENVIRONMENT)
        self.assertFalse(rule.exact_geometry_preferred)
        self.assertIn("generated text", rule.high_risk_generated_elements)
        self.assertIn("exact diagrams", rule.high_risk_generated_elements)


if __name__ == "__main__":
    unittest.main()

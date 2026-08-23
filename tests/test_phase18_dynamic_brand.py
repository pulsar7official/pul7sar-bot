import unittest

from engine.intelligence.dynamic_brand import BrandAccentReason, DynamicBrandResolver, StoryHeroEvidence
from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver


class DynamicBrandResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = DynamicBrandResolver()

    def palette(self, entity="Club A", color="#123ABC", confidence=0.95):
        return EntityPaletteEvidence(entity, color, confidence, "verified_registry")

    def test_general_story_uses_default_red(self):
        result = self.resolver.resolve(None)
        self.assertEqual(result.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.reason, BrandAccentReason.DEFAULT_GENERAL)
        self.assertFalse(result.contextual)

    def test_verified_unambiguous_hero_can_drive_accent(self):
        hero = StoryHeroEvidence("Club A", 0.96, True, self.palette())
        result = self.resolver.resolve(hero)
        self.assertEqual(result.accent_hex, "#123ABC")
        self.assertEqual(result.reason, BrandAccentReason.VERIFIED_HERO)
        self.assertTrue(result.contextual)
        self.assertEqual(result.tint_scope, ("seven", "pulse"))

    def test_ambiguous_multi_entity_story_falls_back_to_red(self):
        hero = StoryHeroEvidence("Club A", 0.98, False, self.palette())
        result = self.resolver.resolve(hero)
        self.assertEqual(result.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.reason, BrandAccentReason.AMBIGUOUS_HERO)

    def test_low_hero_confidence_falls_back_to_red(self):
        hero = StoryHeroEvidence("Club A", 0.60, True, self.palette())
        result = self.resolver.resolve(hero)
        self.assertEqual(result.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.reason, BrandAccentReason.LOW_CONFIDENCE)

    def test_missing_palette_does_not_guess_from_name(self):
        hero = StoryHeroEvidence("Club A", 0.99, True, None)
        result = self.resolver.resolve(hero)
        self.assertEqual(result.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.reason, BrandAccentReason.PALETTE_UNAVAILABLE)

    def test_diffusion_never_owns_brand(self):
        hero = StoryHeroEvidence("Club A", 0.99, True, self.palette())
        result = self.resolver.resolve(hero)
        self.assertTrue(result.structure_locked)
        self.assertFalse(result.generator_may_draw_brand)


if __name__ == "__main__":
    unittest.main()

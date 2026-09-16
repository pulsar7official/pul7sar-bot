import unittest

from engine.intelligence.dynamic_brand import BrandAccentReason
from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver
from engine.intelligence.story_visual_editorial import EditorialEvent


class EditorialDynamicBrandIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.service = EditorialPlanningService()

    def candidate(self, *, secondary=()):
        return EditorialAngleCandidate(
            angle_id="hero",
            event=EditorialEvent.RECORD,
            story_core="verified record",
            fact_phrase="يحطم الرقم القياسي",
            primary_subject="Hero Club",
            secondary_subjects=secondary,
            editorial_importance=0.95,
            fact_confidence=0.98,
            identity_confidence=0.97,
        )

    def test_verified_unambiguous_hero_palette_drives_seven_and_pulse(self):
        palette = EntityPaletteEvidence("Hero Club", "#0057B8", 0.97, "verified_registry")
        result = self.service.plan(
            sport="football",
            candidates=(self.candidate(),),
            hero_palette=palette,
            hero_is_unambiguous=True,
        )
        self.assertEqual(result.brand.accent_hex, "#0057B8")
        self.assertEqual(result.brand.reason, BrandAccentReason.VERIFIED_HERO)
        self.assertEqual(result.brand.tint_scope, ("seven", "pulse"))
        self.assertFalse(result.brand.generator_may_draw_brand)

    def test_ambiguous_matchup_falls_back_to_pul7sar_red(self):
        palette = EntityPaletteEvidence("Hero Club", "#0057B8", 0.97, "verified_registry")
        result = self.service.plan(
            sport="football",
            candidates=(self.candidate(secondary=("Opponent",)),),
            hero_palette=palette,
        )
        self.assertEqual(result.brand.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.brand.reason, BrandAccentReason.AMBIGUOUS_HERO)

    def test_missing_palette_never_guesses_color_from_entity_name(self):
        result = self.service.plan(sport="football", candidates=(self.candidate(),))
        self.assertEqual(result.brand.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertEqual(result.brand.reason, BrandAccentReason.PALETTE_UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()

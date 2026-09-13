import tempfile
import unittest
from pathlib import Path

from engine.intelligence.dynamic_brand import DynamicBrandDecision, BrandAccentReason
from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe
from engine.intelligence.dynamic_brand_renderer import DynamicBrandPlacement, PillowDynamicBrandRenderer
from engine.intelligence.typography import FontReference


class DynamicBrandRendererTests(unittest.TestCase):
    def recipe(self, approved=True):
        return DynamicBrandGeometryRecipe(
            recipe_id="test-brand-v1",
            wordmark_text="PUL7SAR",
            seven_index=3,
            wordmark_font_id="brand-font",
            pulse_path=((0.08, 0.6), (0.30, 0.6), (0.40, 0.15), (0.50, 0.9), (0.62, 0.45), (0.90, 0.45)),
            approved=approved,
            approval_reference="test-approval" if approved else None,
        )

    def decision(self):
        return DynamicBrandDecision(
            accent_hex="#E10600",
            reason=BrandAccentReason.DEFAULT_GENERAL,
            hero_entity=None,
            contextual=False,
        )

    def test_unapproved_recipe_is_rejected_before_file_rendering(self):
        recipe = DynamicBrandGeometryRecipe(
            recipe_id="draft",
            wordmark_text="PUL7SAR",
            seven_index=3,
            wordmark_font_id="brand-font",
            pulse_path=((0.1, 0.5), (0.3, 0.5), (0.5, 0.1), (0.8, 0.5)),
            approved=False,
        )
        with self.assertRaisesRegex(ValueError, "explicitly approved"):
            PillowDynamicBrandRenderer().render_on_file(
                base_path="missing.png",
                output_path="out.png",
                recipe=recipe,
                decision=self.decision(),
                font=FontReference("brand-font", "Brand"),
                font_path="missing.ttf",
                placement=DynamicBrandPlacement(10, 10, 300, 80),
            )

    def test_recipe_font_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "font id"):
            PillowDynamicBrandRenderer().render_on_file(
                base_path="missing.png",
                output_path="out.png",
                recipe=self.recipe(),
                decision=self.decision(),
                font=FontReference("wrong-font", "Wrong"),
                font_path="missing.ttf",
                placement=DynamicBrandPlacement(10, 10, 300, 80),
            )

    def test_generator_owned_brand_decision_is_rejected(self):
        bad = DynamicBrandDecision(
            accent_hex="#E10600",
            reason=BrandAccentReason.DEFAULT_GENERAL,
            hero_entity=None,
            contextual=False,
            generator_may_draw_brand=True,
        )
        with self.assertRaisesRegex(ValueError, "generator"):
            PillowDynamicBrandRenderer().render_on_file(
                base_path="missing.png",
                output_path="out.png",
                recipe=self.recipe(),
                decision=bad,
                font=FontReference("brand-font", "Brand"),
                font_path="missing.ttf",
                placement=DynamicBrandPlacement(10, 10, 300, 80),
            )

    def test_invalid_placement_fails_immediately(self):
        with self.assertRaises(ValueError):
            DynamicBrandPlacement(-1, 0, 100, 50)


if __name__ == "__main__":
    unittest.main()

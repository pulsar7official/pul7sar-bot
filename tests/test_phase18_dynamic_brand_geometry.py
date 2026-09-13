import unittest

from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe, DynamicBrandGeometryRegistry


class DynamicBrandGeometryTests(unittest.TestCase):
    def test_unapproved_placeholder_is_allowed_but_cannot_render(self):
        recipe = DynamicBrandGeometryRecipe(
            recipe_id="draft",
            wordmark_text="PUL7SAR",
            seven_index=3,
            wordmark_font_id=None,
            pulse_path=(),
            approved=False,
        )
        registry = DynamicBrandGeometryRegistry((recipe,))
        with self.assertRaisesRegex(ValueError, "not approved"):
            registry.require_approved("draft")

    def test_approved_recipe_requires_font_pulse_and_approval_reference(self):
        with self.assertRaises(ValueError):
            DynamicBrandGeometryRecipe(
                recipe_id="bad",
                wordmark_text="PUL7SAR",
                seven_index=3,
                wordmark_font_id=None,
                pulse_path=((0.1, 0.5), (0.3, 0.5), (0.5, 0.2), (0.7, 0.5)),
                approved=True,
                approval_reference="user-approved",
            )

    def test_approved_recipe_can_be_resolved(self):
        recipe = DynamicBrandGeometryRecipe(
            recipe_id="v1",
            wordmark_text="PUL7SAR",
            seven_index=3,
            wordmark_font_id="pul7sar-wordmark-font-v1",
            pulse_path=((0.05, 0.55), (0.30, 0.55), (0.42, 0.20), (0.55, 0.78), (0.67, 0.55), (0.95, 0.55)),
            approved=True,
            approval_reference="explicit-visual-approval",
        )
        registry = DynamicBrandGeometryRegistry((recipe,))
        self.assertEqual(registry.require_approved("v1"), recipe)

    def test_wordmark_and_seven_position_are_locked(self):
        with self.assertRaises(ValueError):
            DynamicBrandGeometryRecipe("bad", "PULSAR", 3, None, (), False)
        with self.assertRaises(ValueError):
            DynamicBrandGeometryRecipe("bad", "PUL7SAR", 2, None, (), False)


if __name__ == "__main__":
    unittest.main()

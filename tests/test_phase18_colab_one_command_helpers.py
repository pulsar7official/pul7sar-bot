import unittest

from engine.intelligence.hybrid_layer_planner import LayerSource
from tools.phase18_colab_one_command import _golden_layer_plan


class ColabOneCommandHelperTests(unittest.TestCase):
    def test_golden_preview_keeps_surface_optional_but_brand_and_typography_exact(self):
        plan = _golden_layer_plan()
        surface = plan.by_name("sport_surface_geometry")
        self.assertEqual(surface.source, LayerSource.OPTIONAL)
        self.assertFalse(surface.required)
        self.assertTrue(plan.by_name("pul7sar_brand").required)
        self.assertTrue(plan.by_name("editorial_typography").required)

    def test_golden_preview_does_not_hide_a_deterministic_pitch_dependency(self):
        plan = _golden_layer_plan()
        deterministic_required = {
            layer.name for layer in plan.layers
            if layer.required and layer.source is LayerSource.DETERMINISTIC
        }
        self.assertNotIn("sport_surface_geometry", deterministic_required)
        self.assertIn("editorial_typography", deterministic_required)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.hybrid_evidence_builder import VisualInspectionFlags
from engine.intelligence.hybrid_layer_planner import LayerSource
from tools.phase18_colab_one_command import _golden_layer_plan, _merge_flags


class ColabOneCommandHelperTests(unittest.TestCase):
    def test_golden_layer_plan_requires_exact_geometry_brand_and_typography(self):
        plan = _golden_layer_plan()
        self.assertEqual(plan.by_name("sport_surface_geometry").source, LayerSource.DETERMINISTIC)
        self.assertTrue(plan.by_name("pul7sar_brand").required)
        self.assertTrue(plan.by_name("editorial_typography").required)

    def test_stage_specific_semantic_failures_merge_without_false_pass(self):
        base = VisualInspectionFlags(generated_text_detected=True)
        hybrid = VisualInspectionFlags(severe_anatomy_or_object_defect=True)
        merged = _merge_flags(base, hybrid)
        self.assertTrue(merged.generated_text_detected)
        self.assertTrue(merged.severe_anatomy_or_object_defect)
        self.assertFalse(merged.generated_brand_detected)


if __name__ == "__main__":
    unittest.main()

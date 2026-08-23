import tempfile
import unittest
from pathlib import Path

from engine.intelligence.hybrid_layer_planner import LayerSource
from tools.phase18_colab_one_command import _golden_layer_plan, _semantic_payload


class ColabOneCommandHelperTests(unittest.TestCase):
    def test_golden_layer_plan_requires_exact_geometry_brand_and_typography(self):
        plan = _golden_layer_plan()
        self.assertEqual(plan.by_name("sport_surface_geometry").source, LayerSource.DETERMINISTIC)
        self.assertTrue(plan.by_name("pul7sar_brand").required)
        self.assertTrue(plan.by_name("editorial_typography").required)

    def test_semantic_none_mode_never_claims_automatic_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            image = Path(temp) / "unused.png"
            payload, caps, verdict = _semantic_payload(image, "none")
            self.assertEqual(payload["status"], "SEMANTIC_INSPECTION_NOT_REQUESTED")
            self.assertFalse(payload["approved"])
            self.assertIsNone(verdict)
            self.assertFalse(caps.semantic_defect_detection)
            self.assertFalse(caps.forbidden_visual_detection)


if __name__ == "__main__":
    unittest.main()

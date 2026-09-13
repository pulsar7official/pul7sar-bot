import unittest

from engine.intelligence.qwen25_vl_inspector import Qwen25VLSemanticInspector
from engine.intelligence.semantic_visual_verdict import InspectionState


class Qwen25VLSemanticInspectorTests(unittest.TestCase):
    def test_json_parser_accepts_fenced_json(self):
        data = Qwen25VLSemanticInspector._json_object('```json\n{"single_scene":{"pass":true,"confidence":0.95,"detail":"ok"}}\n```')
        self.assertIn("single_scene", data)

    def test_missing_field_becomes_not_inspected_not_false_pass(self):
        check = Qwen25VLSemanticInspector._check({}, "single_scene")
        self.assertEqual(check.state, InspectionState.NOT_INSPECTED)
        self.assertEqual(check.confidence, 0.0)

    def test_valid_field_is_normalized(self):
        check = Qwen25VLSemanticInspector._check(
            {"single_scene": {"pass": True, "confidence": 0.93, "detail": "one frame"}},
            "single_scene",
        )
        self.assertEqual(check.state, InspectionState.PASS)
        self.assertAlmostEqual(check.confidence, 0.93)

    def test_generated_text_list_can_be_extracted(self):
        output = [{"generated_text": [{"role": "assistant", "content": "{\"single_scene\":{}}"}]}]
        self.assertIn("single_scene", Qwen25VLSemanticInspector._extract_text(output))


if __name__ == "__main__":
    unittest.main()

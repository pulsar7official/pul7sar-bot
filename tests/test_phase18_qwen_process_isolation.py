import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen25_vl_inspector import (
    Qwen25VLConfig,
    Qwen25VLSemanticInspector,
    SemanticInspectionStage,
    _verdict_from_payload,
    _verdict_to_payload,
)
from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict


class QwenProcessIsolationTests(unittest.TestCase):
    def _verdict(self):
        passed = SemanticCheck(InspectionState.PASS, 0.95, "ok")
        return SemanticVisualVerdict(
            verifier_id="test-verifier",
            readable_text_absent=passed,
            platform_brand_absent=passed,
            fake_entity_marks_absent=passed,
            single_scene=passed,
            severe_defects_absent=passed,
            subject_framing_valid=passed,
            sport_geometry_alignment_valid=passed,
            exact_numbers_absent=passed,
            generated_sport_geometry_absent=passed,
            identity_valid=None,
        )

    def test_verdict_round_trip_survives_process_boundary(self):
        original = self._verdict()
        replayed = _verdict_from_payload(_verdict_to_payload(original))
        self.assertEqual(replayed, original)

    def test_default_config_enables_process_isolation(self):
        self.assertTrue(Qwen25VLConfig().process_isolation)
        self.assertGreaterEqual(Qwen25VLConfig().process_timeout_seconds, 30)

    def test_inspect_file_routes_to_isolated_path_by_default(self):
        inspector = Qwen25VLSemanticInspector()
        expected = self._verdict()
        fake = Path(__file__)
        with patch.object(inspector, "_inspect_file_isolated", return_value=expected) as isolated:
            result = inspector.inspect_file(str(fake), stage=SemanticInspectionStage.BASE_SCENE)
        self.assertEqual(result, expected)
        isolated.assert_called_once()

    def test_process_isolation_can_be_disabled_only_explicitly(self):
        inspector = Qwen25VLSemanticInspector(Qwen25VLConfig(process_isolation=False))
        expected = self._verdict()
        fake = Path(__file__)
        with patch.object(inspector, "_inspect_file_inprocess", return_value=expected) as direct:
            result = inspector.inspect_file(str(fake), stage=SemanticInspectionStage.HYBRID_SURFACE)
        self.assertEqual(result, expected)
        direct.assert_called_once()


if __name__ == "__main__":
    unittest.main()

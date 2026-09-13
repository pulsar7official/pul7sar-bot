import unittest

from engine.intelligence.semantic_layer_evidence import SemanticLayerEvidenceAdapter
from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict


def check(state=InspectionState.PASS, confidence=0.95):
    return SemanticCheck(state, confidence, "test")


def verdict(**overrides):
    data = dict(
        verifier_id="test-vlm",
        readable_text_absent=check(),
        platform_brand_absent=check(),
        fake_entity_marks_absent=check(),
        single_scene=check(),
        severe_defects_absent=check(),
        subject_framing_valid=check(),
        exact_numbers_absent=check(),
        generated_sport_geometry_absent=check(),
    )
    data.update(overrides)
    return SemanticVisualVerdict(**data)


class SemanticLayerEvidenceTests(unittest.TestCase):
    def test_complete_clean_verdict_produces_clean_layer_evidence(self):
        result = SemanticLayerEvidenceAdapter().adapt(
            verdict(), require_exact_number_check=True, require_sport_geometry_check=True
        )
        self.assertTrue(result.complete)
        self.assertFalse(result.evidence.generated_text_detected)
        self.assertFalse(result.evidence.generated_sport_geometry_detected)

    def test_detected_leakage_maps_to_exact_layer_flags(self):
        result = SemanticLayerEvidenceAdapter().adapt(
            verdict(
                readable_text_absent=check(InspectionState.FAIL),
                platform_brand_absent=check(InspectionState.FAIL),
                exact_numbers_absent=check(InspectionState.FAIL),
                generated_sport_geometry_absent=check(InspectionState.FAIL),
            ),
            require_exact_number_check=True,
            require_sport_geometry_check=True,
        )
        self.assertTrue(result.complete)
        self.assertTrue(result.evidence.generated_text_detected)
        self.assertTrue(result.evidence.generated_platform_brand_detected)
        self.assertTrue(result.evidence.generated_exact_numbers_detected)
        self.assertTrue(result.evidence.generated_sport_geometry_detected)

    def test_missing_required_geometry_check_fails_closed(self):
        result = SemanticLayerEvidenceAdapter().adapt(
            verdict(generated_sport_geometry_absent=None),
            require_exact_number_check=False,
            require_sport_geometry_check=True,
        )
        self.assertFalse(result.complete)
        self.assertIn("generated_sport_geometry_absent:not_inspected", result.blockers)

    def test_low_confidence_core_check_fails_closed(self):
        result = SemanticLayerEvidenceAdapter(minimum_confidence=0.90).adapt(
            verdict(platform_brand_absent=check(confidence=0.60)),
            require_exact_number_check=False,
            require_sport_geometry_check=False,
        )
        self.assertFalse(result.complete)
        self.assertIn("platform_brand_absent:confidence_below_threshold", result.blockers)


if __name__ == "__main__":
    unittest.main()

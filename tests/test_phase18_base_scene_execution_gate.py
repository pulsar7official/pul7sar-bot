import unittest

from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionGate
from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, LayerSource, VisualLayer
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


def plan():
    return HybridLayerPlan((
        VisualLayer("atmosphere_base", LayerSource.GENERATIVE, "base"),
        VisualLayer("sport_surface_geometry", LayerSource.DETERMINISTIC, "pitch"),
        VisualLayer("exact_entity_marks", LayerSource.VERIFIED_ASSET, "marks", required=False),
        VisualLayer("data_and_score", LayerSource.DETERMINISTIC, "numbers", required=False),
        VisualLayer("editorial_typography", LayerSource.DETERMINISTIC, "copy"),
        VisualLayer("pul7sar_brand", LayerSource.VERIFIED_ASSET, "brand"),
    ))


class BaseSceneExecutionGateTests(unittest.TestCase):
    def test_clean_complete_semantic_evidence_allows_composition(self):
        decision = BaseSceneExecutionGate().evaluate(
            plan(), verdict(), require_exact_number_check=True, require_sport_geometry_check=True
        )
        self.assertTrue(decision.inspection_complete)
        self.assertTrue(decision.allowed)
        self.assertEqual((), decision.blockers)

    def test_missing_required_semantic_check_blocks_before_composition(self):
        decision = BaseSceneExecutionGate().evaluate(
            plan(),
            verdict(generated_sport_geometry_absent=None),
            require_exact_number_check=True,
            require_sport_geometry_check=True,
        )
        self.assertFalse(decision.inspection_complete)
        self.assertFalse(decision.allowed)
        self.assertIn("generated_sport_geometry_absent:not_inspected", decision.blockers)

    def test_detected_generated_geometry_blocks_layer_ownership(self):
        decision = BaseSceneExecutionGate().evaluate(
            plan(),
            verdict(generated_sport_geometry_absent=check(InspectionState.FAIL)),
            require_exact_number_check=True,
            require_sport_geometry_check=True,
        )
        self.assertTrue(decision.inspection_complete)
        self.assertFalse(decision.allowed)
        self.assertIn("generated_sport_geometry_leaked_into_deterministic_geometry_layer", decision.blockers)

    def test_generated_platform_brand_blocks_even_with_complete_inspection(self):
        decision = BaseSceneExecutionGate().evaluate(
            plan(),
            verdict(platform_brand_absent=check(InspectionState.FAIL)),
            require_exact_number_check=True,
            require_sport_geometry_check=True,
        )
        self.assertTrue(decision.inspection_complete)
        self.assertFalse(decision.allowed)
        self.assertIn("generated_platform_brand_leaked_into_verified_brand_layer", decision.blockers)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.semantic_visual_verdict import (
    InspectionState,
    SemanticCheck,
    SemanticVisualVerdict,
    SemanticVisualVerdictGate,
)


class SemanticVisualVerdictTests(unittest.TestCase):
    def check(self, state=InspectionState.PASS, confidence=0.95):
        return SemanticCheck(state, confidence)

    def verdict(self, **kwargs):
        data = dict(
            verifier_id="local-vlm-test",
            readable_text_absent=self.check(),
            platform_brand_absent=self.check(),
            fake_entity_marks_absent=self.check(),
            single_scene=self.check(),
            severe_defects_absent=self.check(),
            subject_framing_valid=self.check(),
            identity_valid=None,
        )
        data.update(kwargs)
        return SemanticVisualVerdict(**data)

    def test_complete_clean_verdict_passes(self):
        approved, failures = SemanticVisualVerdictGate().evaluate(self.verdict(), identity_required=False)
        self.assertTrue(approved)
        self.assertEqual(failures, ())

    def test_not_inspected_is_not_the_same_as_pass(self):
        verdict = self.verdict(readable_text_absent=self.check(InspectionState.NOT_INSPECTED, 0.0))
        approved, failures = SemanticVisualVerdictGate().evaluate(verdict, identity_required=False)
        self.assertFalse(approved)
        self.assertIn("readable_text_absent:not_inspected", failures)

    def test_detected_generated_text_becomes_hybrid_flag(self):
        verdict = self.verdict(readable_text_absent=self.check(InspectionState.FAIL, 0.99))
        flags = verdict.to_flags()
        self.assertTrue(flags.generated_text_detected)

    def test_low_confidence_pass_is_rejected(self):
        verdict = self.verdict(single_scene=self.check(InspectionState.PASS, 0.50))
        approved, failures = SemanticVisualVerdictGate().evaluate(verdict, identity_required=False)
        self.assertFalse(approved)
        self.assertIn("single_scene:confidence_below_threshold", failures)

    def test_identity_required_needs_separate_identity_check(self):
        approved, failures = SemanticVisualVerdictGate().evaluate(self.verdict(), identity_required=True)
        self.assertFalse(approved)
        self.assertEqual(failures, ("identity_not_inspected",))


if __name__ == "__main__":
    unittest.main()

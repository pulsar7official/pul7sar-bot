import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate, VisualAwareEditorialAngleSelector
from engine.intelligence.story_visual_editorial import EditorialEvent


class EditorialAngleSelectorTests(unittest.TestCase):
    def setUp(self):
        self.selector = VisualAwareEditorialAngleSelector()

    def candidate(self, angle_id, **kwargs):
        data = dict(
            angle_id=angle_id,
            event=EditorialEvent.RESULT,
            story_core="verified core",
            fact_phrase="fact",
            primary_subject="Subject",
            editorial_importance=0.9,
            fact_confidence=0.98,
        )
        data.update(kwargs)
        return EditorialAngleCandidate(**data)

    def test_visually_reliable_angle_can_beat_slightly_more_important_complex_angle(self):
        complex_angle = self.candidate(
            "complex",
            editorial_importance=1.0,
            secondary_subjects=("A", "B", "C", "D"),
            requires_exact_text=True,
            requires_exact_geometry=True,
        )
        simple_angle = self.candidate("simple", editorial_importance=0.92)
        result = self.selector.select((complex_angle, simple_angle))
        self.assertEqual(result.selected.candidate.angle_id, "simple")

    def test_unverified_identity_is_hard_blocked(self):
        unsafe = self.candidate("unsafe", requires_unverified_identity=True)
        score = self.selector.evaluate(unsafe)
        self.assertFalse(score.eligible)
        self.assertIn("unverified_identity_required", score.hard_blockers)

    def test_low_fact_confidence_is_hard_blocked(self):
        unsafe = self.candidate("weak", fact_confidence=0.60)
        self.assertFalse(self.selector.evaluate(unsafe).eligible)

    def test_identity_below_threshold_is_hard_blocked(self):
        unsafe = self.candidate("identity", identity_confidence=0.89)
        self.assertIn("identity_confidence_below_0_90", self.selector.evaluate(unsafe).hard_blockers)

    def test_exact_text_and_geometry_are_penalties_not_inventions(self):
        score = self.selector.evaluate(self.candidate(
            "data",
            requires_exact_text=True,
            requires_exact_geometry=True,
        ))
        self.assertTrue(score.eligible)
        self.assertIn("exact_text_requires_deterministic_layer", score.penalties)
        self.assertIn("exact_geometry_requires_deterministic_layer", score.penalties)

    def test_all_blocked_returns_none(self):
        result = self.selector.select((
            self.candidate("a", fact_confidence=0.4),
            self.candidate("b", requires_invented_scene=True),
        ))
        self.assertIsNone(result.selected)


if __name__ == "__main__":
    unittest.main()

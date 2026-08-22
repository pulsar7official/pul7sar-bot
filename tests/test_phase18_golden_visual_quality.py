import unittest

from engine.intelligence.golden_visual_quality import (
    GoldenVisualBlockers,
    GoldenVisualEvaluation,
    GoldenVisualQualitySelector,
    GoldenVisualScores,
)


class GoldenVisualQualityTests(unittest.TestCase):
    def scores(self, value=8.0):
        return GoldenVisualScores(value, value, value, value, value, value)

    def test_strong_candidate_is_approved(self):
        item = GoldenVisualEvaluation("candidate-1", 1, self.scores(8.2))
        self.assertTrue(item.approved)
        self.assertGreaterEqual(item.scores.weighted_score, 8.0)

    def test_hard_visual_blocker_rejects_even_high_score(self):
        item = GoldenVisualEvaluation(
            "candidate-1", 1, self.scores(9.5),
            GoldenVisualBlockers(pseudo_text_or_gibberish=True),
        )
        self.assertFalse(item.approved)

    def test_core_dimension_below_floor_rejects(self):
        scores = GoldenVisualScores(6.9, 9.0, 9.0, 9.0, 9.0, 9.0)
        item = GoldenVisualEvaluation("candidate-1", 1, scores)
        self.assertFalse(item.approved)

    def test_selector_chooses_best_approved_not_best_blocked(self):
        blocked = GoldenVisualEvaluation(
            "blocked", 1, self.scores(9.8),
            GoldenVisualBlockers(fake_logo_or_crest=True),
        )
        good = GoldenVisualEvaluation("good", 2, self.scores(8.4))
        weaker = GoldenVisualEvaluation("weaker", 3, self.scores(7.8))
        selection = GoldenVisualQualitySelector().select((blocked, weaker, good))
        self.assertIsNotNone(selection.selected)
        self.assertEqual(selection.selected.request_id, "good")
        self.assertIn("blocked", selection.rejected_request_ids)

    def test_selector_returns_none_when_all_candidates_fail(self):
        low = GoldenVisualEvaluation("low", 1, self.scores(6.0))
        blocked = GoldenVisualEvaluation(
            "blocked", 2, self.scores(9.0), GoldenVisualBlockers(cluttered_collage=True)
        )
        selection = GoldenVisualQualitySelector().select((low, blocked))
        self.assertIsNone(selection.selected)


if __name__ == "__main__":
    unittest.main()

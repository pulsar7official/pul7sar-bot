import unittest

from engine.intelligence.golden_visual_quality import (
    ELITE_TARGET,
    GOLDEN_CORE_FLOOR,
    GOLDEN_WEIGHTED_FLOOR,
    GoldenVisualBlockers,
    GoldenVisualEvaluation,
    GoldenVisualQualitySelector,
    GoldenVisualScores,
)


class GoldenVisualQualityTests(unittest.TestCase):
    def scores(self, value=8.6):
        return GoldenVisualScores(value, value, value, value, value, value)

    def test_premium_candidate_is_approved_at_strict_floor(self):
        item = GoldenVisualEvaluation("candidate-1", 1, self.scores(8.6))
        self.assertTrue(item.approved)
        self.assertGreaterEqual(item.scores.weighted_score, GOLDEN_WEIGHTED_FLOOR)
        self.assertEqual(item.quality_tier, "golden")

    def test_old_acceptable_floor_is_now_rejected(self):
        item = GoldenVisualEvaluation("candidate-1", 1, self.scores(8.2))
        self.assertFalse(item.approved)
        self.assertEqual(item.quality_tier, "below_golden")

    def test_elite_candidate_is_explicitly_classified(self):
        item = GoldenVisualEvaluation("candidate-1", 1, self.scores(ELITE_TARGET))
        self.assertTrue(item.approved)
        self.assertEqual(item.quality_tier, "elite")

    def test_hard_visual_blocker_rejects_even_high_score(self):
        item = GoldenVisualEvaluation(
            "candidate-1", 1, self.scores(9.5),
            GoldenVisualBlockers(pseudo_text_or_gibberish=True),
        )
        self.assertFalse(item.approved)
        self.assertEqual(item.quality_tier, "below_golden")

    def test_core_dimension_below_premium_floor_rejects(self):
        scores = GoldenVisualScores(GOLDEN_CORE_FLOOR - 0.1, 9.5, 9.5, 9.5, 9.5, 9.5)
        item = GoldenVisualEvaluation("candidate-1", 1, scores)
        self.assertFalse(item.approved)

    def test_selector_chooses_best_approved_not_best_blocked(self):
        blocked = GoldenVisualEvaluation(
            "blocked", 1, self.scores(9.8),
            GoldenVisualBlockers(fake_logo_or_crest=True),
        )
        good = GoldenVisualEvaluation("good", 2, self.scores(9.1))
        weaker = GoldenVisualEvaluation("weaker", 3, self.scores(8.6))
        selection = GoldenVisualQualitySelector().select((blocked, weaker, good))
        self.assertIsNotNone(selection.selected)
        self.assertEqual(selection.selected.request_id, "good")
        self.assertIn("blocked", selection.rejected_request_ids)

    def test_selector_returns_none_when_all_candidates_fail(self):
        low = GoldenVisualEvaluation("low", 1, self.scores(8.4))
        blocked = GoldenVisualEvaluation(
            "blocked", 2, self.scores(9.0), GoldenVisualBlockers(cluttered_collage=True)
        )
        selection = GoldenVisualQualitySelector().select((low, blocked))
        self.assertIsNone(selection.selected)


if __name__ == "__main__":
    unittest.main()

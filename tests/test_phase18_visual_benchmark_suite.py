import unittest

from engine.intelligence.visual_benchmark_suite import (
    BenchmarkReviewKind,
    PHASE18_VISUAL_BENCHMARKS,
    benchmark_for,
)
from engine.intelligence.story_visual_editorial import EditorialEvent


class VisualBenchmarkSuiteTests(unittest.TestCase):
    def test_four_story_families_are_registered(self):
        self.assertEqual(len(PHASE18_VISUAL_BENCHMARKS), 4)
        self.assertEqual(
            {case.event for case in PHASE18_VISUAL_BENCHMARKS},
            {
                EditorialEvent.TRANSFER_CONFIRMED,
                EditorialEvent.RESULT,
                EditorialEvent.INJURY,
                EditorialEvent.TACTICS,
            },
        )

    def test_transfer_benchmark_rejects_legacy_logo_and_dense_stats(self):
        case = benchmark_for(EditorialEvent.TRANSFER_CONFIRMED)
        self.assertIn("legacy repository logo", case.must_avoid)
        self.assertIn("dense infographic statistics", case.must_avoid)

    def test_result_benchmark_contains_loser_respect_rule(self):
        case = benchmark_for(EditorialEvent.RESULT)
        self.assertIn("respectful treatment of losing side", case.must_show)
        self.assertIn("humiliation imagery", case.must_avoid)

    def test_injury_benchmark_requires_verified_asset(self):
        case = benchmark_for(EditorialEvent.INJURY)
        self.assertIn("verified source subject asset", case.must_show)
        self.assertIn("unverified identity", case.must_avoid)

    def test_tactics_benchmark_is_structural(self):
        case = benchmark_for(EditorialEvent.TACTICS)
        self.assertEqual(case.review_kind, BenchmarkReviewKind.STRUCTURAL)
        self.assertIn("deterministic sport geometry", case.must_show)


if __name__ == "__main__":
    unittest.main()

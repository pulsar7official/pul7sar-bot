import unittest

from engine.intelligence.visual_benchmark_suite import BenchmarkReviewKind, PHASE18_VISUAL_BENCHMARKS, benchmark_for
from engine.intelligence.story_visual_editorial import EditorialEvent


class VisualBenchmarkSuiteTests(unittest.TestCase):
    def test_seven_canonical_validation_cases_are_registered(self):
        self.assertEqual(len(PHASE18_VISUAL_BENCHMARKS), 7)
        self.assertEqual(
            {case.event for case in PHASE18_VISUAL_BENCHMARKS},
            {
                EditorialEvent.TRANSFER_CONFIRMED,
                EditorialEvent.RESULT,
                EditorialEvent.INJURY,
                EditorialEvent.TACTICS,
                EditorialEvent.RECORD,
                EditorialEvent.PREVIEW,
                EditorialEvent.GENERAL,
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

    def test_record_benchmark_keeps_exact_numbers_deterministic(self):
        case = benchmark_for(EditorialEvent.RECORD)
        self.assertEqual(case.review_kind, BenchmarkReviewKind.STRUCTURAL)
        self.assertIn("exact deterministic record value", case.must_show)
        self.assertIn("AI-generated exact numbers", case.must_avoid)
        self.assertIn("invented statistics", case.must_avoid)

    def test_preview_benchmark_enforces_exact_or_indeterminate_geometry(self):
        case = benchmark_for(EditorialEvent.PREVIEW)
        self.assertIn("sport geometry either exact verified or visually indeterminate", case.must_show)
        self.assertIn("isolated or partial unverifiable goal geometry", case.must_avoid)
        self.assertIn("mandatory full-pitch master shot", case.must_avoid)

    def test_general_editorial_benchmark_uses_optional_not_mandatory_football_motifs(self):
        case = benchmark_for(EditorialEvent.GENERAL)
        self.assertIn("optional stadium light or tactical texture only when supportive", case.must_show)
        self.assertIn("mandatory full football pitch", case.must_avoid)
        self.assertIn("visual clutter competing with the headline", case.must_avoid)


if __name__ == "__main__":
    unittest.main()

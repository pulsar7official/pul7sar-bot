import unittest

from engine.intelligence.source_consensus import (
    SourceConsensusGuard,
    SourceConsensusStatus,
    SourceFactObservation,
)


class SourceConsensusGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = SourceConsensusGuard()

    def obs(self, source, value, *, authoritative=False, confidence=0.95):
        return SourceFactObservation(source, "score", value, confidence, authoritative)

    def test_matching_independent_sources_pass(self):
        result = self.guard.evaluate(
            (self.obs("a", "2-1"), self.obs("b", "2-1")),
            slot="score",
            minimum_independent_sources=2,
        )
        self.assertEqual(result.status, SourceConsensusStatus.CONSISTENT)
        self.assertEqual(result.accepted_value, "2-1")

    def test_conflicting_non_authoritative_sources_block(self):
        result = self.guard.evaluate(
            (self.obs("a", "2-1"), self.obs("b", "3-1")),
            slot="score",
        )
        self.assertEqual(result.status, SourceConsensusStatus.CONFLICT)
        self.assertIn("independent_sources_disagree", result.failures)

    def test_single_authoritative_source_can_resolve_non_authoritative_disagreement(self):
        result = self.guard.evaluate(
            (self.obs("official", "2-1", authoritative=True), self.obs("reporter", "3-1")),
            slot="score",
        )
        self.assertEqual(result.status, SourceConsensusStatus.CONSISTENT)
        self.assertEqual(result.accepted_value, "2-1")
        self.assertTrue(result.conflicting_values)

    def test_two_authoritative_sources_in_conflict_fail_closed(self):
        result = self.guard.evaluate(
            (self.obs("official-a", "2-1", authoritative=True), self.obs("official-b", "3-1", authoritative=True)),
            slot="score",
        )
        self.assertEqual(result.status, SourceConsensusStatus.CONFLICT)
        self.assertIn("authoritative_sources_conflict", result.failures)

    def test_insufficient_source_count_is_not_consensus(self):
        result = self.guard.evaluate(
            (self.obs("only", "2-1"),),
            slot="score",
            minimum_independent_sources=2,
        )
        self.assertEqual(result.status, SourceConsensusStatus.INSUFFICIENT)


if __name__ == "__main__":
    unittest.main()

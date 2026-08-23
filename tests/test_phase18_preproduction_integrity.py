import unittest
from datetime import datetime, timezone

from engine.intelligence.preproduction_integrity import ExactSlotConsensusRequirement, PreproductionIntegrityGate
from engine.intelligence.source_consensus import SourceFactObservation
from engine.intelligence.story_visual_editorial import EditorialEvent


class PreproductionIntegrityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = PreproductionIntegrityGate()
        self.now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)

    def test_clean_result_can_proceed(self):
        decision = self.gate.evaluate(
            event=EditorialEvent.RESULT,
            facts={
                "subject": "A", "opponent": "B", "result_status": "final",
                "score": "2-1", "winner_entity": "A", "verified_at": self.now.isoformat(),
            },
            source_requirements=(ExactSlotConsensusRequirement(
                "score",
                (
                    SourceFactObservation("official", "score", "2-1", 0.99, True),
                    SourceFactObservation("wire", "score", "2-1", 0.95, False),
                ),
            ),),
            now=self.now,
        )
        self.assertTrue(decision.approved)
        self.assertEqual(decision.action, "PROCEED_TO_EDITORIAL_PLANNING")

    def test_source_conflict_blocks_before_visual_planning(self):
        decision = self.gate.evaluate(
            event=EditorialEvent.RESULT,
            facts={"subject": "A", "opponent": "B", "result_status": "final", "score": "2-1"},
            source_requirements=(ExactSlotConsensusRequirement(
                "score",
                (
                    SourceFactObservation("a", "score", "2-1", 0.95),
                    SourceFactObservation("b", "score", "3-1", 0.95),
                ),
            ),),
            now=self.now,
        )
        self.assertFalse(decision.approved)
        self.assertTrue(any(item.startswith("source_consensus:score:") for item in decision.failures))

    def test_missing_required_fact_blocks(self):
        decision = self.gate.evaluate(
            event=EditorialEvent.RESULT,
            facts={"subject": "A", "result_status": "final", "score": "1-0"},
            now=self.now,
        )
        self.assertFalse(decision.approved)
        self.assertIn("missing_required:opponent", decision.failures)

    def test_retracted_story_withdraws(self):
        decision = self.gate.evaluate(
            event=EditorialEvent.GENERAL,
            facts={"subject": "A", "verified_fact": "fact", "revision_status": "retracted"},
            now=self.now,
        )
        self.assertFalse(decision.approved)
        self.assertEqual(decision.action, "WITHDRAW_STORY")

    def test_rumour_superseded_by_official_is_reclassified(self):
        decision = self.gate.evaluate(
            event=EditorialEvent.TRANSFER_RUMOUR,
            facts={
                "subject": "Player", "interested_entity": "Club", "rumour_status": "reported",
                "confirmation_status": "official",
            },
            now=self.now,
        )
        self.assertFalse(decision.approved)
        self.assertEqual(decision.action, "REFRESH_OR_RECLASSIFY_STORY")


if __name__ == "__main__":
    unittest.main()

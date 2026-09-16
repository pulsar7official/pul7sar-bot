import unittest
from datetime import datetime, timedelta, timezone

from engine.intelligence.story_state_integrity import StoryRevisionAction, StoryStateIntegrityGuard
from engine.intelligence.story_visual_editorial import EditorialEvent


class StoryStateIntegrityGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = StoryStateIntegrityGuard()
        self.now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)

    def test_live_result_cannot_have_final_winner(self):
        result = self.guard.validate(
            event=EditorialEvent.RESULT,
            facts={"result_status": "live", "winner_entity": "Club A", "score": "1-0"},
            now=self.now,
        )
        self.assertFalse(result.valid)
        self.assertIn("winner_present_while_result_is_live", result.failures)

    def test_final_result_requires_score(self):
        result = self.guard.validate(
            event=EditorialEvent.RESULT,
            facts={"result_status": "final"},
            now=self.now,
        )
        self.assertFalse(result.valid)
        self.assertIn("final_result_missing_score", result.failures)

    def test_rumour_that_became_official_is_reclassified(self):
        result = self.guard.validate(
            event=EditorialEvent.TRANSFER_RUMOUR,
            facts={"confirmation_status": "official"},
            now=self.now,
        )
        self.assertEqual(result.action, StoryRevisionAction.RECLASSIFY)
        self.assertIn("rumour_superseded_by_confirmed_transfer", result.failures)

    def test_postponed_preview_is_reclassified(self):
        result = self.guard.validate(
            event=EditorialEvent.PREVIEW,
            facts={"schedule_status": "postponed"},
            now=self.now,
        )
        self.assertEqual(result.action, StoryRevisionAction.RECLASSIFY)

    def test_stale_fast_moving_fact_requires_refresh(self):
        result = self.guard.validate(
            event=EditorialEvent.RESULT,
            facts={
                "result_status": "final",
                "score": "2-1",
                "verified_at": (self.now - timedelta(minutes=50)).isoformat(),
            },
            now=self.now,
            max_fact_age_minutes=30,
        )
        self.assertEqual(result.action, StoryRevisionAction.REFRESH)
        self.assertIn("fact_state_is_stale", result.failures)

    def test_retracted_story_is_withdrawn(self):
        result = self.guard.validate(
            event=EditorialEvent.GENERAL,
            facts={"revision_status": "retracted"},
            now=self.now,
        )
        self.assertEqual(result.action, StoryRevisionAction.WITHDRAW)

    def test_clean_final_result_passes(self):
        result = self.guard.validate(
            event=EditorialEvent.RESULT,
            facts={"result_status": "final", "score": "2-1", "verified_at": self.now.isoformat()},
            now=self.now,
        )
        self.assertTrue(result.valid)
        self.assertEqual(result.action, StoryRevisionAction.KEEP)


if __name__ == "__main__":
    unittest.main()

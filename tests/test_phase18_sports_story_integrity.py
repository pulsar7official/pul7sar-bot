import unittest

from engine.intelligence.sports_story_integrity import SportsStoryIntegrityGuard
from engine.intelligence.story_visual_editorial import EditorialEvent


class SportsStoryIntegrityGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = SportsStoryIntegrityGuard()

    def test_result_winner_must_be_participant(self):
        result = self.guard.validate(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club C"
        })
        self.assertFalse(result.valid)
        self.assertIn("winner_is_not_a_match_participant", result.violations)

    def test_draw_cannot_have_winner(self):
        result = self.guard.validate(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "draw", "winner_entity": "Club A"
        })
        self.assertFalse(result.valid)
        self.assertIn("draw_cannot_have_winner_entity", result.violations)

    def test_subject_win_status_cannot_conflict_with_explicit_winner(self):
        result = self.guard.validate(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "subject_win", "winner_entity": "Club B"
        })
        self.assertIn("winner_conflicts_with_subject_win_status", result.violations)

    def test_transfer_origin_and_destination_cannot_match(self):
        result = self.guard.validate(EditorialEvent.TRANSFER_CONFIRMED, {
            "subject": "Player X", "origin": "Club A", "destination": "Club A", "confirmation_status": "confirmed"
        })
        self.assertFalse(result.valid)
        self.assertIn("transfer_origin_equals_destination", result.violations)

    def test_confirmed_transfer_cannot_have_pending_status(self):
        result = self.guard.validate(EditorialEvent.TRANSFER_CONFIRMED, {
            "subject": "Player X", "origin": "Club A", "destination": "Club B", "confirmation_status": "pending"
        })
        self.assertIn("confirmed_transfer_has_nonfinal_status", result.violations)

    def test_transfer_rumour_cannot_carry_final_status(self):
        result = self.guard.validate(EditorialEvent.TRANSFER_RUMOUR, {
            "subject": "Player X", "interested_entity": "Club B", "rumour_status": "official"
        })
        self.assertIn("transfer_rumour_contains_final_transfer_status", result.violations)

    def test_eliminated_side_cannot_eliminate_itself(self):
        result = self.guard.validate(EditorialEvent.ELIMINATION, {
            "subject": "Club A", "elimination_status": "eliminated", "eliminating_entity": "Club A"
        })
        self.assertIn("eliminated_entity_cannot_eliminate_itself", result.violations)

    def test_valid_completed_result_passes(self):
        result = self.guard.validate(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A", "score": "2-0"
        })
        self.assertTrue(result.valid)
        self.assertEqual(result.violations, ())


if __name__ == "__main__":
    unittest.main()

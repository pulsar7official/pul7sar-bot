import unittest

from engine.intelligence.story_dominant_entity import DominantEntityReason, StoryDominantEntityResolver
from engine.intelligence.story_visual_editorial import EditorialEvent


class StoryDominantEntityResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = StoryDominantEntityResolver()

    def resolve(self, event, facts):
        return self.resolver.resolve(event=event, facts=facts, confidence=0.97)

    def test_confirmed_transfer_destination_owns_story_dominance(self):
        result = self.resolve(EditorialEvent.TRANSFER_CONFIRMED, {
            "subject": "Player X",
            "origin": "Club A",
            "destination": "Club B",
            "confirmation_status": "confirmed",
        })
        self.assertEqual(result.entity_name, "Club B")
        self.assertEqual(result.reason, DominantEntityReason.TRANSFER_DESTINATION)

    def test_unresolved_transfer_does_not_get_destination_color(self):
        result = self.resolve(EditorialEvent.TRANSFER_CONFIRMED, {
            "subject": "Player X",
            "origin": "Club A",
            "destination": "Club B",
            "confirmation_status": "pending",
        })
        self.assertIsNone(result)

    def test_match_winner_entity_wins_even_with_two_clubs(self):
        result = self.resolve(EditorialEvent.RESULT, {
            "subject": "Club A",
            "opponent": "Club B",
            "result_status": "completed",
            "winner_entity": "Club B",
            "score": "1-3",
        })
        self.assertEqual(result.entity_name, "Club B")
        self.assertEqual(result.reason, DominantEntityReason.RESULT_WINNER)

    def test_normalized_subject_win_can_resolve_without_free_text_parsing(self):
        result = self.resolve(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "subject_win"
        })
        self.assertEqual(result.entity_name, "Club A")

    def test_draw_has_no_dominant_entity(self):
        result = self.resolve(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "draw"
        })
        self.assertIsNone(result)

    def test_non_final_result_does_not_use_declared_winner(self):
        result = self.resolve(EditorialEvent.RESULT, {
            "subject": "Club A", "opponent": "Club B", "result_status": "live", "winner_entity": "Club A"
        })
        self.assertIsNone(result)

    def test_preview_has_no_brand_winner(self):
        result = self.resolve(EditorialEvent.PREVIEW, {
            "subject": "Club A", "opponent": "Club B", "event_status": "scheduled"
        })
        self.assertIsNone(result)

    def test_transfer_rumour_does_not_color_interested_club_as_winner(self):
        result = self.resolve(EditorialEvent.TRANSFER_RUMOUR, {
            "subject": "Player X", "interested_entity": "Club B", "rumour_status": "reported"
        })
        self.assertIsNone(result)

    def test_eliminated_subject_never_becomes_brand_owner(self):
        result = self.resolve(EditorialEvent.ELIMINATION, {
            "subject": "Club A", "elimination_status": "eliminated"
        })
        self.assertIsNone(result)

    def test_explicit_eliminating_entity_owns_story(self):
        result = self.resolve(EditorialEvent.ELIMINATION, {
            "subject": "Club A", "elimination_status": "eliminated", "eliminating_entity": "Club B"
        })
        self.assertEqual(result.entity_name, "Club B")
        self.assertEqual(result.reason, DominantEntityReason.ELIMINATING_ENTITY)

    def test_trophy_champion_can_be_explicit(self):
        result = self.resolve(EditorialEvent.TROPHY, {
            "subject": "Club A", "competition": "Cup", "title_status": "confirmed_champion", "champion_entity": "Club A"
        })
        self.assertEqual(result.entity_name, "Club A")


if __name__ == "__main__":
    unittest.main()

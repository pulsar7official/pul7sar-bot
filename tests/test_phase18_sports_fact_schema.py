import unittest

from engine.intelligence.sports_fact_schema import EventFactSchemaRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent


class SportsFactSchemaTests(unittest.TestCase):
    def setUp(self):
        self.registry = EventFactSchemaRegistry()

    def test_every_editorial_event_has_schema(self):
        for event in EditorialEvent:
            with self.subTest(event=event.value):
                schema = self.registry.get(event)
                self.assertEqual(schema.event, event)
                self.assertTrue(schema.required_slots)

    def test_result_requires_subject_opponent_and_status(self):
        invalid = self.registry.validate(EditorialEvent.RESULT, {"subject": "A"})
        self.assertFalse(invalid.valid)
        self.assertEqual(set(invalid.missing_required), {"opponent", "result_status"})
        valid = self.registry.validate(EditorialEvent.RESULT, {
            "subject": "A", "opponent": "B", "result_status": "final", "score": "2-1"
        })
        self.assertTrue(valid.valid)
        self.assertEqual(valid.exact_render_values["score"], "2-1")

    def test_transfer_rumour_does_not_require_completed_signing(self):
        schema = self.registry.get(EditorialEvent.TRANSFER_RUMOUR)
        self.assertIn("completed signing", schema.forbidden_implications)
        valid = self.registry.validate(EditorialEvent.TRANSFER_RUMOUR, {
            "subject": "Player", "interested_entity": "Club", "rumour_status": "interest"
        })
        self.assertTrue(valid.valid)

    def test_injury_exact_absence_is_deterministic_if_known(self):
        valid = self.registry.validate(EditorialEvent.INJURY, {
            "subject": "Player", "injury_status": "confirmed", "expected_absence": "3 weeks"
        })
        self.assertTrue(valid.valid)
        self.assertEqual(valid.exact_render_values["expected_absence"], "3 weeks")

    def test_tactics_keeps_formation_and_roles_exact(self):
        valid = self.registry.validate(EditorialEvent.TACTICS, {
            "subject": "Team", "tactical_claim": "changed buildup", "formation": "4-3-3", "roles": "verified roles"
        })
        self.assertTrue(valid.valid)
        self.assertEqual(valid.exact_render_values["formation"], "4-3-3")
        self.assertEqual(valid.exact_render_values["roles"], "verified roles")


if __name__ == "__main__":
    unittest.main()

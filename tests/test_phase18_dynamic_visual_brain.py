import unittest

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.story_visual_editorial import EditorialEvent


class DynamicVisualBrainTests(unittest.TestCase):
    def setUp(self):
        self.brain = DynamicVisualBrain()

    def test_transfer_story_generates_diverse_story_specific_concepts(self):
        plan = self.brain.plan({
            "headline": "Player completes move to new club",
            "summary": "The verified player has completed a permanent transfer after an agreement between the clubs.",
            "sport": "football",
            "story_type": "transfer_confirmed",
            "primary_entity": "Verified Player",
            "secondary_entities": ["Destination Club"],
        })
        self.assertEqual(plan.event, EditorialEvent.TRANSFER_CONFIRMED)
        self.assertEqual(len(plan.concepts), 3)
        self.assertTrue(all(c.metadata["dynamic"] for c in plan.concepts))
        self.assertTrue(all("football pitch" in " ".join(c.forbidden_elements).casefold() for c in plan.concepts))
        self.assertEqual(len({c.concept_id for c in plan.concepts}), 3)
        self.assertFalse(plan.publication_ready)

    def test_result_story_preserves_loser_respect_and_exact_score_ownership(self):
        plan = self.brain.plan({
            "headline": "Club A defeats Club B",
            "summary": "Club A won the verified final result against Club B.",
            "sport": "football",
            "story_type": "result",
            "primary_entity": "Club A",
            "secondary_entities": ["Club B"],
        })
        self.assertEqual(plan.event, EditorialEvent.RESULT)
        joined = " ".join(c.scene_prompt for c in plan.concepts).casefold()
        self.assertIn("respect the losing side", joined)
        self.assertIn("exact score", joined)
        self.assertNotIn("crushing loser", joined)

    def test_injury_story_does_not_fabricate_person_or_injury(self):
        plan = self.brain.plan({
            "headline": "Player ruled out after injury",
            "summary": "The club confirmed the player will miss the next match.",
            "sport": "football",
            "story_type": "injury",
            "primary_entity": "Verified Player",
        })
        self.assertEqual(plan.event, EditorialEvent.INJURY)
        joined = " ".join(c.scene_prompt for c in plan.concepts).casefold()
        self.assertIn("do not invent facial expression", joined)
        self.assertIn("real-person likeness", joined)

    def test_unknown_story_type_fails_safe_to_general(self):
        plan = self.brain.plan({
            "headline": "League announces new initiative",
            "summary": "A verified organizational initiative was announced.",
            "sport": "football",
            "story_type": "new_unrecognized_type",
        })
        self.assertEqual(plan.event, EditorialEvent.GENERAL)
        self.assertEqual(len(plan.concepts), 3)

    def test_story_changes_change_fingerprint(self):
        a = self.brain.plan({"headline": "A", "summary": "One verified event", "story_type": "general"})
        b = self.brain.plan({"headline": "B", "summary": "Another verified event", "story_type": "general"})
        self.assertNotEqual(a.story_fingerprint, b.story_fingerprint)

    def test_tactics_reserves_exact_geometry_for_deterministic_layer(self):
        plan = self.brain.plan({
            "headline": "Coach changes pressing structure",
            "summary": "The analysis describes a verified tactical structure.",
            "sport": "football",
            "story_type": "tactics",
            "primary_entity": "Team",
        })
        self.assertEqual(plan.event, EditorialEvent.TACTICS)
        joined = " ".join(c.scene_prompt for c in plan.concepts).casefold()
        self.assertIn("exact pitch geometry", joined)
        self.assertIn("deterministic", joined)


if __name__ == "__main__":
    unittest.main()

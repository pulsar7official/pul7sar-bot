import unittest

from engine.intelligence.editorial_scene_copy_gate import EditorialSceneCopyGate
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.editorial_headline_grammar import HeadlineTone


class EditorialSceneCopyGateTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.gate = EditorialSceneCopyGate()

    def scene(self, event):
        story = VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        )
        return self.orchestrator.decide(story).sports_editorial_scene

    def test_transfer_accepts_short_headline_and_restrained_support(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        decision = self.gate.evaluate(scene, headline="PLAYER JOINS REAL MADRID", supporting_copy="Five-year deal after verified agreement")
        self.assertTrue(decision.allowed, decision.failures)

    def test_transfer_rejects_dense_infographic_headline(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        decision = self.gate.evaluate(scene, headline="ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE")
        self.assertFalse(decision.allowed)
        self.assertIn("headline exceeds scene word budget", decision.failures)

    def test_result_forbids_supporting_paragraph(self):
        scene = self.scene(EditorialEvent.RESULT)
        decision = self.gate.evaluate(scene, headline="ARSENAL WIN 2-1", supporting_copy="A long explanatory paragraph is not allowed here")
        self.assertFalse(decision.allowed)
        self.assertIn("supporting copy is forbidden for this scene family", decision.failures)

    def test_empty_headline_fails_closed(self):
        scene = self.scene(EditorialEvent.STATEMENT)
        decision = self.gate.evaluate(scene, headline="")
        self.assertFalse(decision.allowed)
        self.assertIn("headline is empty", decision.failures)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode


class StoryVisualScenarioMatrixTests(unittest.TestCase):
    def test_cross_sport_scenario_matrix(self):
        engine = StoryToVisualOrchestrator()
        cases = (
            (EditorialEvent.RESULT, "football", ProductionMode.HYBRID),
            (EditorialEvent.RESULT, "basketball", ProductionMode.HYBRID),
            (EditorialEvent.QUALIFICATION, "tennis", ProductionMode.HYBRID),
            (EditorialEvent.RECORD, "golf", ProductionMode.HYBRID),
            (EditorialEvent.INJURY, "boxing", ProductionMode.VERIFIED_ASSET_EDITORIAL),
            (EditorialEvent.COMEBACK, "mma", ProductionMode.HYBRID),
            (EditorialEvent.RECORD, "athletics", ProductionMode.HYBRID),
            (EditorialEvent.RESULT, "formula_1", ProductionMode.HYBRID),
            (EditorialEvent.SCHEDULE, "motorsport", ProductionMode.DETERMINISTIC_COMPOSITION),
            (EditorialEvent.RESULT, "swimming", ProductionMode.HYBRID),
            (EditorialEvent.RESULT, "cycling", ProductionMode.HYBRID),
            (EditorialEvent.PREVIEW, "volleyball", ProductionMode.HYBRID),
            (EditorialEvent.TACTICS, "handball", ProductionMode.DETERMINISTIC_COMPOSITION),
            (EditorialEvent.RESULT, "ice_hockey", ProductionMode.HYBRID),
            (EditorialEvent.GENERAL, "winter_sport", ProductionMode.HYBRID),
            (EditorialEvent.DRAW, "football", ProductionMode.DETERMINISTIC_COMPOSITION),
            (EditorialEvent.TABLE, "football", ProductionMode.DETERMINISTIC_COMPOSITION),
            (EditorialEvent.FINANCIAL, "football", ProductionMode.DETERMINISTIC_COMPOSITION),
            (EditorialEvent.TRANSFER_RUMOUR, "football", ProductionMode.VERIFIED_ASSET_EDITORIAL),
            (EditorialEvent.STATEMENT, "football", ProductionMode.VERIFIED_ASSET_EDITORIAL),
            (EditorialEvent.CONTROVERSY, "tennis", ProductionMode.VERIFIED_ASSET_EDITORIAL),
            (EditorialEvent.OFFICIATING, "basketball", ProductionMode.VERIFIED_ASSET_EDITORIAL),
            (EditorialEvent.RETIREMENT, "boxing", ProductionMode.HYBRID),
            (EditorialEvent.APPOINTMENT, "football", ProductionMode.HYBRID),
            (EditorialEvent.DISMISSAL, "football", ProductionMode.HYBRID),
            (EditorialEvent.TROPHY, "football", ProductionMode.HYBRID),
            (EditorialEvent.AWARD, "tennis", ProductionMode.HYBRID),
            (EditorialEvent.ELIMINATION, "football", ProductionMode.HYBRID),
            (EditorialEvent.TRANSFER_CONFIRMED, "football", ProductionMode.HYBRID),
            (EditorialEvent.CONTRACT, "basketball", ProductionMode.HYBRID),
        )
        for event, sport, expected_mode in cases:
            with self.subTest(event=event.value, sport=sport):
                story = VerifiedEditorialStory(
                    event=event,
                    sport=sport,
                    subject="Verified Subject",
                    fact_phrase="حدث مثبت من المصدر",
                    story_core="verified factual core",
                    tone=HeadlineTone.NEUTRAL,
                    confidence=0.95,
                )
                decision = engine.decide(story)
                self.assertEqual(decision.plan.production_mode, expected_mode)
                self.assertTrue(decision.headline.strip())
                self.assertFalse(decision.plan.metadata.get("publication_ready", False))


if __name__ == "__main__":
    unittest.main()

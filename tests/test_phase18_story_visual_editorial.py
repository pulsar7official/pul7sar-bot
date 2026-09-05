import unittest

from engine.intelligence.story_visual_editorial import (
    EditorialEvent,
    ProductionMode,
    StoryVisualEditorialEngine,
    VisualFamily,
)


class StoryVisualEditorialEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = StoryVisualEditorialEngine()

    def plan(self, event, **kwargs):
        defaults = dict(
            sport="football",
            story_core="verified event",
            editorial_angle="focus on the decisive meaning of the event",
            headline_short="Decisive moment",
            confidence=0.95,
        )
        defaults.update(kwargs)
        return self.engine.plan(event=event, **defaults)

    def test_result_is_hybrid_score_monument(self):
        plan = self.plan(EditorialEvent.RESULT)
        self.assertEqual(plan.visual_family, VisualFamily.SCORE_MONUMENT)
        self.assertEqual(plan.production_mode, ProductionMode.HYBRID)

    def test_tactics_is_deterministic(self):
        plan = self.plan(EditorialEvent.TACTICS, geometry_requirements=("verified formation geometry",))
        self.assertEqual(plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)

    def test_draw_is_deterministic(self):
        plan = self.plan(EditorialEvent.DRAW)
        self.assertEqual(plan.visual_family, VisualFamily.BRACKET)
        self.assertEqual(plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)

    def test_injury_uses_verified_asset_editorial(self):
        plan = self.plan(EditorialEvent.INJURY)
        self.assertEqual(plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)

    def test_low_confidence_disables_imaginative_generation(self):
        plan = self.plan(EditorialEvent.TRANSFER_CONFIRMED, confidence=0.55)
        self.assertEqual(plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)

    def test_brand_and_exact_text_are_forbidden_inside_generation(self):
        plan = self.plan(EditorialEvent.RECORD)
        forbidden = set(plan.forbidden_generated_elements)
        self.assertIn("PUL7SAR logo", forbidden)
        self.assertIn("headline text", forbidden)
        self.assertIn("scores", forbidden)
        self.assertIn("statistics", forbidden)

    def test_all_event_types_have_a_policy(self):
        for event in EditorialEvent:
            with self.subTest(event=event):
                plan = self.plan(event)
                self.assertIsInstance(plan.visual_family, VisualFamily)
                self.assertIsInstance(plan.production_mode, ProductionMode)


if __name__ == "__main__":
    unittest.main()

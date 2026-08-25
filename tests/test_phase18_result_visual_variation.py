import unittest

from engine.intelligence.result_visual_variation import (
    ResultStorySignals,
    ResultVisualFamily,
    ResultVisualVariationEngine,
)


class ResultVisualVariationTests(unittest.TestCase):
    def setUp(self):
        self.engine = ResultVisualVariationEngine()

    def test_same_story_and_seed_are_reproducible(self):
        signals = ResultStorySignals(3, 1, "home")
        a = self.engine.choose(story_key="arsenal-liverpool-2026-08-25", signals=signals, seed=18)
        b = self.engine.choose(story_key="arsenal-liverpool-2026-08-25", signals=signals, seed=18)
        self.assertEqual(a, b)

    def test_recent_family_is_avoided_when_alternative_exists(self):
        signals = ResultStorySignals(
            3, 1, "home",
            recent_visual_families=(
                ResultVisualFamily.CENTRAL_MONUMENT,
                ResultVisualFamily.OFFSET_DUEL,
                ResultVisualFamily.VERTICAL_TENSION,
            ),
        )
        result = self.engine.choose(story_key="same-club-next-match", signals=signals, seed=7)
        self.assertNotIn(result.family, signals.recent_visual_families)
        self.assertTrue(result.anti_repetition_applied)

    def test_derby_prefers_duel_or_vertical_language(self):
        result = self.engine.choose(
            story_key="derby-001",
            signals=ResultStorySignals(2, 1, "home", derby=True),
            seed=2,
        )
        self.assertIn(result.family, {ResultVisualFamily.OFFSET_DUEL, ResultVisualFamily.VERTICAL_TENSION})

    def test_draw_prefers_quieter_or_wider_family(self):
        result = self.engine.choose(
            story_key="draw-001",
            signals=ResultStorySignals(1, 1, None),
            seed=3,
        )
        self.assertIn(result.family, {ResultVisualFamily.QUIET_EDITORIAL, ResultVisualFamily.WIDE_ARENA})

    def test_big_margin_prefers_monument_or_wide_arena(self):
        result = self.engine.choose(
            story_key="big-win-001",
            signals=ResultStorySignals(5, 0, "home"),
            seed=4,
        )
        self.assertIn(result.family, {ResultVisualFamily.CENTRAL_MONUMENT, ResultVisualFamily.WIDE_ARENA})


if __name__ == "__main__":
    unittest.main()

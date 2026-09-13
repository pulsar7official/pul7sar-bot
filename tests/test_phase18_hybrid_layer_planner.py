import unittest

from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner, LayerSource
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine


class HybridLayerPlannerTests(unittest.TestCase):
    def setUp(self):
        self.editorial = StoryVisualEditorialEngine()
        self.layers = HybridVisualLayerPlanner()
        self.sports = SportVisualRuleRegistry()

    def test_football_pitch_geometry_is_owned_by_code(self):
        plan = self.editorial.plan(
            event=EditorialEvent.RESULT,
            sport="football",
            story_core="verified result",
            editorial_angle="result",
            headline_short="Result",
            primary_subject="Team",
            confidence=0.95,
        )
        layers = self.layers.plan(plan, self.sports.get("football"))
        self.assertEqual(layers.by_name("sport_surface_geometry").source, LayerSource.DETERMINISTIC)

    def test_brand_and_typography_are_never_generative(self):
        plan = self.editorial.plan(
            event=EditorialEvent.GENERAL,
            sport="football",
            story_core="verified story",
            editorial_angle="atmosphere",
            headline_short="Headline",
            confidence=0.95,
        )
        layers = self.layers.plan(plan, self.sports.get("football"))
        self.assertEqual(layers.by_name("pul7sar_brand").source, LayerSource.VERIFIED_ASSET)
        self.assertEqual(layers.by_name("editorial_typography").source, LayerSource.DETERMINISTIC)
        self.assertEqual(layers.by_name("data_and_score").source, LayerSource.DETERMINISTIC)

    def test_verified_subject_is_not_unconstrained_generation(self):
        plan = self.editorial.plan(
            event=EditorialEvent.RECORD,
            sport="tennis",
            story_core="record",
            editorial_angle="achievement",
            headline_short="Record",
            primary_subject="Player",
            confidence=0.95,
        )
        layers = self.layers.plan(plan, self.sports.get("tennis"))
        self.assertEqual(layers.by_name("hero_identity").source, LayerSource.VERIFIED_ASSET)


if __name__ == "__main__":
    unittest.main()

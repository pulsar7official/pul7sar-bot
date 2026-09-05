import unittest

from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContractCompiler
from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine


class HybridBaseSceneContractTests(unittest.TestCase):
    def setUp(self):
        editorial = StoryVisualEditorialEngine().plan(
            event=EditorialEvent.RESULT,
            sport="football",
            story_core="verified result",
            editorial_angle="decisive result",
            headline_short="Decisive result",
            primary_subject="Club A",
            confidence=0.96,
        )
        layers = HybridVisualLayerPlanner().plan(editorial, SportVisualRuleRegistry().get("football"))
        self.contract = HybridBaseSceneContractCompiler().compile(layers)

    def test_exact_pitch_geometry_is_reserved(self):
        joined = " ".join(self.contract.reserved_content)
        self.assertIn("playing-surface geometry", joined)
        self.assertIn("plain and unmarked", self.contract.prompt_suffix)
        self.assertIn("centre circle", self.contract.prompt_suffix)

    def test_brand_text_score_and_identity_are_not_generator_owned(self):
        prompt = self.contract.prompt_suffix
        lowered = prompt.casefold()
        self.assertIn("platform branding", lowered)
        self.assertIn("scoreboards", lowered)
        self.assertIn("do not invent a recognizable real-person face", lowered)
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)

    def test_one_continuous_scene_is_explicit(self):
        self.assertIn("single coherent camera", self.contract.prompt_suffix)
        self.assertIn("one continuous editorial scene", " ".join(self.contract.allowed_content))


if __name__ == "__main__":
    unittest.main()

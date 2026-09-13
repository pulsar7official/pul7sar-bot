import unittest

from engine.intelligence.scene_complexity_policy import SurfaceVisibility
from engine.intelligence.story_visual_editorial import ProductionMode, VisualFamily
from engine.intelligence.visual_execution_route import PixelExecutionRoute, VisualExecutionRouter
from engine.intelligence.visual_grammar import CameraLanguage, FantasyLevel, VisualGrammarDecision


class VisualExecutionRouterTests(unittest.TestCase):
    def setUp(self):
        self.router = VisualExecutionRouter()

    def grammar(self, mode, generated=("atmosphere",), deterministic=("headline typography",)):
        return VisualGrammarDecision(
            family=VisualFamily.DATA_EDITORIAL,
            production_mode=mode,
            surface_visibility=SurfaceVisibility.NONE,
            camera_language=CameraLanguage.GRAPHIC_FRONT,
            fantasy_level=FantasyLevel.NONE,
            hero_subject_limit=1,
            environment_direction="restrained",
            lighting_direction="editorial",
            composition_direction="single scene",
            generated_elements=generated,
            deterministic_elements=deterministic,
            forbidden_generated_elements=("PUL7SAR logo", "headline text"),
            rationale="test",
            metadata={"contract": "pul7sar-visual-grammar-v1"},
        )

    def test_deterministic_composition_never_selects_provider(self):
        decision = self.router.route(self.grammar(
            ProductionMode.DETERMINISTIC_COMPOSITION,
            generated=(),
            deterministic=("exact data", "headline typography"),
        ))
        self.assertEqual(decision.route, PixelExecutionRoute.DETERMINISTIC_ONLY)
        self.assertFalse(decision.generator_required)
        self.assertFalse(decision.provider_selection_allowed)
        self.assertTrue(decision.metadata["provider_bypass"])
        self.assertEqual(decision.generated_elements, ())

    def test_verified_asset_editorial_never_selects_provider(self):
        decision = self.router.route(self.grammar(
            ProductionMode.VERIFIED_ASSET_EDITORIAL,
            generated=(),
            deterministic=("verified player image", "headline typography"),
        ))
        self.assertEqual(decision.route, PixelExecutionRoute.VERIFIED_ASSET_ONLY)
        self.assertFalse(decision.generator_required)
        self.assertFalse(decision.provider_selection_allowed)

    def test_hybrid_generation_is_limited_to_declared_elements(self):
        decision = self.router.route(self.grammar(
            ProductionMode.HYBRID,
            generated=("atmosphere", "lighting", "depth"),
            deterministic=("score", "club identity", "headline typography"),
        ))
        self.assertEqual(decision.route, PixelExecutionRoute.HYBRID_GENERATIVE)
        self.assertTrue(decision.generator_required)
        self.assertTrue(decision.provider_selection_allowed)
        self.assertEqual(decision.generated_elements, ("atmosphere", "lighting", "depth"))
        self.assertIn("score", decision.deterministic_elements)

    def test_empty_hybrid_fails_closed_to_no_generator(self):
        decision = self.router.route(self.grammar(ProductionMode.HYBRID, generated=()))
        self.assertEqual(decision.route, PixelExecutionRoute.DETERMINISTIC_ONLY)
        self.assertFalse(decision.generator_required)
        self.assertTrue(decision.metadata["provider_bypass"])

    def test_generative_scene_requires_generator_owned_content(self):
        with self.assertRaises(ValueError):
            self.router.route(self.grammar(ProductionMode.GENERATIVE_SCENE, generated=()))

    def test_generative_scene_allows_provider_only_when_content_declared(self):
        decision = self.router.route(self.grammar(
            ProductionMode.GENERATIVE_SCENE,
            generated=("environment", "atmosphere"),
        ))
        self.assertEqual(decision.route, PixelExecutionRoute.GENERATIVE_SCENE)
        self.assertTrue(decision.generator_required)
        self.assertEqual(decision.metadata["visual_grammar_contract"], "pul7sar-visual-grammar-v1")

    def test_wrong_input_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.router.route(object())


if __name__ == "__main__":
    unittest.main()

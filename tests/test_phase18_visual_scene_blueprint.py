import unittest

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_scene_blueprint import VisualSceneBlueprintCompiler


class VisualSceneBlueprintTests(unittest.TestCase):
    def setUp(self):
        self.compiler = VisualSceneBlueprintCompiler()

    def test_every_family_compiles_to_renderer_agnostic_blueprint(self):
        for family in EditorialSceneFamily:
            decision = CrossFamilyVisualSystem.choose(family=family, story_key=f"benchmark-{family.value}", seed=18)
            blueprint = self.compiler.compile(decision)
            self.assertEqual(blueprint.family, family.value)
            self.assertTrue(blueprint.hero_layer)
            self.assertTrue(blueprint.environment_layer)
            self.assertTrue(blueprint.metadata["provider_agnostic"])
            self.assertTrue(blueprint.metadata["renderer_agnostic"])

    def test_placeholder_artifacts_are_forbidden_everywhere(self):
        for family in EditorialSceneFamily:
            decision = CrossFamilyVisualSystem.choose(family=family, story_key=f"placeholder-{family.value}")
            forbidden = self.compiler.compile(decision).forbidden
            self.assertIn("empty crest placeholder", forbidden)
            self.assertIn("unexplained dot or badge placeholder", forbidden)

    def test_exact_crest_stays_out_of_generated_layer(self):
        family = EditorialSceneFamily.RESULT_STATEMENT
        for index, archetype in enumerate(CrossFamilyVisualSystem.archetypes(family)):
            decision = CrossFamilyVisualSystem.choose(
                family=family,
                story_key=f"result-{index}",
                recent_archetypes=tuple(a.id for a in CrossFamilyVisualSystem.archetypes(family) if a.id != archetype.id),
                seed=index,
            )
            blueprint = self.compiler.compile(decision)
            for item in blueprint.generated_layers:
                self.assertNotIn("exact crest", item.casefold())


if __name__ == "__main__":
    unittest.main()

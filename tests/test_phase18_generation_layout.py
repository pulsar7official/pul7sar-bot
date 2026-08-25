import unittest

from engine.intelligence.generation_layout import GenerationLayoutCompiler
from engine.intelligence.layout_planner import DeterministicLayoutPlanner
from engine.intelligence.platform_scene_spec import PlatformSceneSpecBuilder
from engine.intelligence.post_composition import AssetBundle, AssetRef
from engine.intelligence.scene_complexity_policy import SceneComplexityPolicy
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDirector, VisualConceptSignals
from engine.intelligence.visual_grammar import VisualGrammarCompiler
from engine.models import SocialPlatform


class GenerationLayoutPackageTests(unittest.TestCase):
    def setUp(self):
        self.compiler = GenerationLayoutCompiler()
        self.layout = DeterministicLayoutPlanner()
        self.specs = PlatformSceneSpecBuilder()
        self.grammar = VisualGrammarCompiler(SceneComplexityPolicy())
        self.concepts = VisualConceptDirector()
        self.assets = AssetBundle(
            platform_logo=AssetRef("platform-logo", "logo.png", "a" * 64),
            platform_wordmark=AssetRef("platform-wordmark", "wordmark.png", "b" * 64),
            team_crests=(),
            social_icons=(),
        )

    def _spec(self, platform):
        layout = self.layout.plan(platform, EditorialSceneFamily.EVENT_EDITORIAL, entity_accent="#e10600")
        return self.specs.build(layout=layout, family=EditorialSceneFamily.EVENT_EDITORIAL, story_summary="global sports season opener")

    def _visual_grammar(self, event):
        return self.grammar.compile(event=event, sport="football")

    def test_ai_base_scene_excludes_brand_and_editorial_overlays(self):
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets)
        prompt = package.scene_prompt.casefold()
        self.assertIn("clean photographic/editorial base scene", prompt)
        self.assertIn("exact branding and typography are added only by deterministic post-composition", prompt)

    def test_entity_accent_reaches_package(self):
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets)
        self.assertEqual(package.metadata["entity_accent"], "#e10600")

    def test_layout_geometry_reaches_generation_package(self):
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets)
        self.assertTrue(package.layout_geometry)

    def test_mismatched_platform_layout_is_rejected(self):
        spec = self._spec(SocialPlatform.INSTAGRAM_FEED)
        with self.assertRaises(ValueError):
            self.compiler.compile(spec, self.assets, platform=SocialPlatform.X_FEED)

    def test_result_geometry_can_include_score_and_crest(self):
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets)
        self.assertIsInstance(package.layout_geometry, tuple)

    def test_result_visual_grammar_reserves_only_partial_deterministic_surface(self):
        grammar = self._visual_grammar(EditorialEvent.RESULT)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_grammar=grammar)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "partial_deterministic")

    def test_transfer_visual_grammar_explicitly_avoids_pitch_dependency(self):
        grammar = self._visual_grammar(EditorialEvent.TRANSFER_CONFIRMED)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_grammar=grammar)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "none")

    def test_tactics_visual_grammar_reserves_full_surface_without_generating_markings(self):
        grammar = self._visual_grammar(EditorialEvent.TACTICS)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_grammar=grammar)
        prompt = package.scene_prompt.casefold()
        self.assertIn("full sport-surface layer", prompt)
        self.assertIn("must not draw its exact markings", prompt)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "full_deterministic")
        self.assertEqual(package.metadata["visual_grammar_generated_elements"], ())

    def test_visual_concept_reaches_generation_prompt_without_brand_leakage(self):
        concept = self.concepts.direct(EditorialSceneFamily.EVENT_EDITORIAL, VisualConceptSignals(safe_generated_context=True))
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_concept=concept)
        prompt = package.scene_prompt.casefold()
        self.assertIn("story-specific visual concept archetype: generative_event_atmosphere", prompt)
        self.assertIn("story-specific non-identifying sports atmosphere", prompt)
        self.assertIn("specific real venue identity without verified reference", prompt)
        self.assertEqual(package.metadata["visual_concept_contract"], "pul7sar-visual-concept-director-v1")
        self.assertEqual(package.metadata["visual_concept_archetype"], VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE.value)
        self.assertTrue(package.metadata["visual_concept_selected_before_renderer"])
        self.assertFalse(package.metadata["visual_concept_publication_ready"])
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)

    def test_visual_concept_type_is_enforced(self):
        with self.assertRaises(TypeError):
            self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_concept="not-a-concept")

    def test_visual_grammar_type_is_enforced(self):
        with self.assertRaises(TypeError):
            self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, visual_grammar="not-grammar")


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.layout_planner import DeterministicLayoutPlanner, LayoutRequirements
from engine.intelligence.models import Sentiment
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDirector, VisualConceptSignals
from engine.intelligence.visual_grammar import VisualGrammar


class GenerationLayoutPackageTests(unittest.TestCase):
    def setUp(self):
        self.registry = PlatformProfileRegistry()
        self.layout_planner = DeterministicLayoutPlanner()
        self.compiler = GenerationPackageCompiler()
        self.editorial = StoryVisualEditorialEngine()
        self.grammar = VisualGrammar()
        self.concepts = VisualConceptDirector()
        self.assets = AssetBundle((
            AssetReference("pul7sar-wordmark", AssetRole.PUL7SAR_LOGO, AssetTreatment.EXACT),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, AssetTreatment.TINTABLE_ACCENT),
        ))

    def _spec(self, platform):
        profile = self.registry.get(platform)
        return OriginalSceneSpecification(
            platform=platform, width=profile.width, height=profile.height, aspect_ratio=profile.aspect_ratio,
            safe_area={"top": profile.safe_area.top, "right": profile.safe_area.right, "bottom": profile.safe_area.bottom, "left": profile.safe_area.left},
            family="general_world", concept="global sports season opener", subject=None, identity_reference=None,
            environment="global sports editorial world", composition="platform-specific editorial composition",
            camera_direction="wide premium framing", emotional_mood=Sentiment.ANTICIPATORY.value, palette_strategy="brand_red",
        )

    def _visual_grammar(self, event):
        plan = self.editorial.plan(
            event=event,
            sport="football",
            story_core="verified story",
            editorial_angle="premium editorial concept",
            headline_short="SHORT HEADLINE",
        )
        return self.grammar.direct(plan)

    def test_layout_geometry_reaches_generation_package(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_STORY)
        layout = self.layout_planner.plan(profile)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_STORY), self.assets, planned_layout=layout)
        self.assertEqual(package.canvas, "1080x1920")
        self.assertIn("hero", package.layout_boxes); self.assertIn("logo", package.layout_boxes)
        self.assertIn("headline", package.layout_boxes); self.assertIn("social_footer", package.layout_boxes)
        self.assertEqual(package.accent_hex, "#E10600")
        self.assertEqual(package.metadata["layout_strategy"], "pul7sar-deterministic-v1")

    def test_entity_accent_reaches_package(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        layout = self.layout_planner.plan(profile, entity_accent_hex="#DB0007")
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, planned_layout=layout)
        self.assertEqual(package.accent_hex, "#DB0007")
        self.assertIn("#DB0007", package.scene_prompt)

    def test_ai_base_scene_excludes_brand_and_editorial_overlays(self):
        profile = self.registry.get(SocialPlatform.INSTAGRAM_FEED)
        layout = self.layout_planner.plan(profile)
        package = self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, planned_layout=layout)
        prompt = package.scene_prompt.casefold()
        self.assertEqual(package.metadata["base_scene_overlay_policy"], "no_brand_or_editorial_overlays_in_ai_scene")
        self.assertTrue(package.metadata["brand_name_redacted_from_generation_prompt"])
        self.assertIn("do not draw or imitate any platform logo", prompt)
        self.assertIn("deterministic post-composition", prompt)
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)

    def test_result_geometry_can_include_score_and_crest(self):
        profile = self.registry.get(SocialPlatform.FACEBOOK_FEED)
        layout = self.layout_planner.plan(profile, LayoutRequirements(include_crest=True, include_score=True))
        package = self.compiler.compile(self._spec(SocialPlatform.FACEBOOK_FEED), self.assets, planned_layout=layout)
        self.assertIn("score", package.layout_boxes); self.assertIn("crest", package.layout_boxes)

    def test_transfer_visual_grammar_explicitly_avoids_pitch_dependency(self):
        grammar = self._visual_grammar(EditorialEvent.TRANSFER_CONFIRMED)
        package = self.compiler.compile(
            self._spec(SocialPlatform.INSTAGRAM_FEED),
            self.assets,
            visual_grammar=grammar,
        )
        prompt = package.scene_prompt.casefold()
        self.assertIn("do not make a full pitch", prompt)
        self.assertIn("prioritize the editorial subject", prompt)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "none")
        self.assertTrue(package.metadata["visual_grammar_provider_agnostic"])
        self.assertNotIn("pul7sar", prompt)

    def test_result_visual_grammar_reserves_only_partial_deterministic_surface(self):
        grammar = self._visual_grammar(EditorialEvent.RESULT)
        package = self.compiler.compile(
            self._spec(SocialPlatform.INSTAGRAM_FEED),
            self.assets,
            visual_grammar=grammar,
        )
        prompt = package.scene_prompt.casefold()
        self.assertIn("restrained partial sport-surface context", prompt)
        self.assertIn("exact sport geometry is added later", prompt)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "partial_deterministic")

    def test_tactics_visual_grammar_reserves_full_surface_without_generating_markings(self):
        grammar = self._visual_grammar(EditorialEvent.TACTICS)
        package = self.compiler.compile(
            self._spec(SocialPlatform.INSTAGRAM_FEED),
            self.assets,
            visual_grammar=grammar,
        )
        prompt = package.scene_prompt.casefold()
        self.assertIn("full sport-surface layer", prompt)
        self.assertIn("must not draw its exact markings", prompt)
        self.assertEqual(package.metadata["visual_grammar_surface_visibility"], "full_deterministic")
        self.assertEqual(package.metadata["visual_grammar_generated_elements"], ())

    def test_visual_concept_reaches_generation_prompt_without_brand_leakage(self):
        concept = self.concepts.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(safe_generated_context=True),
        )
        package = self.compiler.compile(
            self._spec(SocialPlatform.INSTAGRAM_FEED),
            self.assets,
            visual_concept=concept,
        )
        prompt = package.scene_prompt.casefold()
        self.assertIn("story-specific visual concept archetype: generative_event_atmosphere", prompt)
        self.assertIn("story-specific non-identifying sports atmosphere", prompt)
        self.assertIn("specific real venue identity without verified context", prompt)
        self.assertEqual(package.metadata["visual_concept_contract"], "pul7sar-visual-concept-director-v1")
        self.assertEqual(package.metadata["visual_concept_archetype"], VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE.value)
        self.assertTrue(package.metadata["visual_concept_selected_before_renderer"])
        self.assertFalse(package.metadata["visual_concept_publication_ready"])
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)

    def test_visual_concept_type_is_enforced(self):
        with self.assertRaises(TypeError):
            self.compiler.compile(
                self._spec(SocialPlatform.INSTAGRAM_FEED),
                self.assets,
                visual_concept="not-a-concept",
            )

    def test_visual_grammar_type_is_enforced(self):
        with self.assertRaises(TypeError):
            self.compiler.compile(
                self._spec(SocialPlatform.INSTAGRAM_FEED),
                self.assets,
                visual_grammar="not-a-grammar",
            )

    def test_mismatched_platform_layout_is_rejected(self):
        x_layout = self.layout_planner.plan(self.registry.get(SocialPlatform.X_FEED))
        with self.assertRaises(ValueError):
            self.compiler.compile(self._spec(SocialPlatform.INSTAGRAM_FEED), self.assets, planned_layout=x_layout)


if __name__ == "__main__":
    unittest.main()

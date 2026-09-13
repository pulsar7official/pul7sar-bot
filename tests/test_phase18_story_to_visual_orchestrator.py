import unittest

from engine.intelligence.concept_renderer_registry import ConceptRendererStatus
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.scene_complexity_policy import SurfaceVisibility
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode, VisualFamily
from engine.intelligence.visual_concept_director import VisualConceptArchetype
from engine.intelligence.visual_execution_route import PixelExecutionRoute
from engine.intelligence.visual_grammar import CameraLanguage


class StoryToVisualOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.engine = StoryToVisualOrchestrator()

    def story(self, event=EditorialEvent.RESULT, **kwargs):
        data = dict(event=event, sport="football", subject="Arsenal", fact_phrase="يفوز في المباراة", story_core="Arsenal won the verified match", tone=HeadlineTone.POSITIVE, confidence=0.96)
        data.update(kwargs)
        return VerifiedEditorialStory(**data)

    def test_result_copy_and_visual_plan_share_one_decision(self):
        decision = self.engine.decide(self.story())
        self.assertIn("Arsenal", decision.headline)
        self.assertEqual(decision.plan.visual_family, VisualFamily.SCORE_MONUMENT)
        self.assertEqual(decision.plan.production_mode, ProductionMode.HYBRID)
        self.assertEqual(decision.visual_anchor, "result")
        self.assertEqual(decision.visual_grammar.surface_visibility, SurfaceVisibility.PARTIAL_DETERMINISTIC)
        self.assertEqual(decision.visual_grammar.camera_language, CameraLanguage.GRAPHIC_FRONT)
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(decision.concept_renderer.status, ConceptRendererStatus.IMPLEMENTED)
        self.assertEqual(decision.concept_renderer.renderer_class, 'ResultStatementStudyRenderer')
        # Family grammar may still expose historical hybrid capability; concept
        # execution is the final authority and keeps this fallback deterministic.
        self.assertEqual(decision.execution_route.route, PixelExecutionRoute.HYBRID_GENERATIVE)

    def test_verified_decisive_moment_is_reference_only_not_final_pixels(self):
        decision = self.engine.decide(self.story(metadata={"verified_action_photo": True, "decisive_moment_known": True, "exact_club_assets": True}))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertEqual(decision.concept_renderer.status, ConceptRendererStatus.IMPLEMENTED)
        self.assertEqual(decision.concept_renderer.renderer_class, 'ResultStatementStudyRenderer')

    def test_explicit_original_result_scene_waits_for_qualified_runtime(self):
        decision = self.engine.decide(self.story(metadata={"allow_original_scene_generation": True, "verified_action_photo": True, "decisive_moment_known": True, "exact_club_assets": True}))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertEqual(decision.concept_renderer.status, ConceptRendererStatus.CONTRACT_ONLY)
        self.assertTrue(decision.concept_renderer.generator_required)

    def test_football_geometry_is_explicit_and_not_left_to_diffusion(self):
        decision = self.engine.decide(self.story())
        joined = " ".join(decision.sport_geometry_requirements)
        self.assertIn("regulation rectangular pitch proportions", joined)
        self.assertIn("centre circle", joined)
        self.assertIn("penalty", joined)
        self.assertIn("sport surface geometry", decision.visual_grammar.deterministic_elements)
        self.assertIn("sport surface geometry", decision.execution_route.deterministic_elements)

    def test_tactics_routes_to_deterministic_composition(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.TACTICS, fact_phrase="يعتمد شكلاً جديداً", story_core="verified tactical change"))
        self.assertEqual(decision.plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)
        self.assertEqual(decision.plan.visual_family, VisualFamily.TACTICAL_INTELLIGENCE)
        self.assertEqual(decision.visual_grammar.surface_visibility, SurfaceVisibility.FULL_DETERMINISTIC)
        self.assertEqual(decision.visual_grammar.camera_language, CameraLanguage.TACTICAL_TOP)
        self.assertEqual(decision.visual_grammar.generated_elements, ())
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.TACTICAL_SPATIAL_MAP)
        self.assertEqual(decision.execution_route.route, PixelExecutionRoute.DETERMINISTIC_ONLY)

    def test_transfer_does_not_inherit_football_pitch_dependency(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.TRANSFER_CONFIRMED, fact_phrase="ينتقل رسمياً", story_core="verified completed transfer"))
        self.assertEqual(decision.visual_grammar.surface_visibility, SurfaceVisibility.NONE)
        self.assertNotIn("sport surface geometry", decision.visual_grammar.deterministic_elements)
        self.assertTrue(decision.visual_grammar.metadata["provider_agnostic"])

    def test_general_event_can_use_safe_non_identifying_generated_atmosphere(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.PREVIEW, subject="Domestic season", fact_phrase="يقترب من الانطلاق", story_core="verified season-opening anticipation", tone=HeadlineTone.NEUTRAL))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertIn("non-identifying", decision.visual_concept.hero)
        self.assertIn("specific real venue identity without verified reference", decision.visual_concept.forbidden_motifs)
        self.assertFalse(decision.visual_concept.metadata["publication_ready"])
        self.assertEqual(decision.concept_renderer.status, ConceptRendererStatus.CONTRACT_ONLY)
        self.assertTrue(decision.concept_renderer.generator_required)
        self.assertFalse(decision.concept_renderer.network_required)

    def test_general_event_can_explicitly_disable_generated_context(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.PREVIEW, subject="Domestic season", fact_phrase="يقترب من الانطلاق", story_core="verified season-opening anticipation", tone=HeadlineTone.NEUTRAL, metadata={"allow_generated_context": False}))
        self.assertEqual(decision.visual_concept.archetype, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL)
        self.assertEqual(decision.concept_renderer.status, ConceptRendererStatus.IMPLEMENTED)

    def test_low_confidence_falls_back_to_verified_assets(self):
        decision = self.engine.decide(self.story(confidence=0.60))
        self.assertEqual(decision.plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)
        self.assertEqual(decision.fallback_reason, "low_story_confidence")
        self.assertEqual(decision.visual_grammar.generated_elements, ())
        self.assertEqual(decision.execution_route.route, PixelExecutionRoute.VERIFIED_ASSET_ONLY)

    def test_injury_bypasses_generator_and_uses_verified_asset_editorial(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.INJURY, fact_phrase="يتعرض لإصابة", story_core="verified injury update"))
        self.assertEqual(decision.plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)
        self.assertEqual(decision.execution_route.route, PixelExecutionRoute.VERIFIED_ASSET_ONLY)

    def test_table_bypasses_generator_for_exact_data_composition(self):
        decision = self.engine.decide(self.story(event=EditorialEvent.TABLE, fact_phrase="يتصدر الجدول", story_core="verified league table update"))
        self.assertEqual(decision.plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)
        self.assertEqual(decision.execution_route.route, PixelExecutionRoute.DETERMINISTIC_ONLY)
        self.assertIn("exact data", decision.execution_route.deterministic_elements)

    def test_tennis_uses_tennis_specific_geometry(self):
        decision = self.engine.decide(self.story(sport="tennis", subject="Player", fact_phrase="يتأهل إلى النهائي", story_core="player qualified for final", event=EditorialEvent.QUALIFICATION))
        joined = " ".join(decision.sport_geometry_requirements)
        self.assertIn("service boxes", joined)
        self.assertNotIn("penalty areas", joined)

    def test_padel_now_has_explicit_sport_geometry_policy(self):
        decision = self.engine.decide(self.story(sport="padel"))
        joined = " ".join(decision.sport_geometry_requirements)
        self.assertIn("glass", joined)
        self.assertIn("net", joined)

    def test_generated_branding_and_exact_data_remain_forbidden(self):
        decision = self.engine.decide(self.story())
        forbidden = set(decision.plan.forbidden_generated_elements)
        self.assertIn("PUL7SAR logo", forbidden)
        self.assertIn("scores", forbidden)
        self.assertIn("statistics", forbidden)
        self.assertIn("club crests", forbidden)
        self.assertEqual(set(decision.visual_grammar.forbidden_generated_elements), forbidden)

    def test_unknown_sport_fails_safe_to_generic_exact_overlay_risks(self):
        decision = self.engine.decide(self.story(sport="sepaktakraw"))
        self.assertIn("generated text", decision.high_risk_generated_elements)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.scene_complexity_policy import SurfaceVisibility
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode, VisualFamily
from engine.intelligence.visual_grammar import CameraLanguage


class StoryToVisualOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.engine = StoryToVisualOrchestrator()

    def story(self, event=EditorialEvent.RESULT, **kwargs):
        data = dict(
            event=event,
            sport="football",
            subject="Arsenal",
            fact_phrase="يفوز في المباراة",
            story_core="Arsenal won the verified match",
            tone=HeadlineTone.POSITIVE,
            confidence=0.96,
        )
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

    def test_football_geometry_is_explicit_and_not_left_to_diffusion(self):
        decision = self.engine.decide(self.story())
        joined = " ".join(decision.sport_geometry_requirements)
        self.assertIn("regulation rectangular pitch proportions", joined)
        self.assertIn("centre circle", joined)
        self.assertIn("penalty", joined)
        self.assertIn("sport surface geometry", decision.visual_grammar.deterministic_elements)

    def test_tactics_routes_to_deterministic_composition(self):
        decision = self.engine.decide(self.story(
            event=EditorialEvent.TACTICS,
            fact_phrase="يعتمد شكلاً جديداً",
            story_core="verified tactical change",
        ))
        self.assertEqual(decision.plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)
        self.assertEqual(decision.plan.visual_family, VisualFamily.TACTICAL_INTELLIGENCE)
        self.assertEqual(decision.visual_grammar.surface_visibility, SurfaceVisibility.FULL_DETERMINISTIC)
        self.assertEqual(decision.visual_grammar.camera_language, CameraLanguage.TACTICAL_TOP)
        self.assertEqual(decision.visual_grammar.generated_elements, ())

    def test_transfer_does_not_inherit_football_pitch_dependency(self):
        decision = self.engine.decide(self.story(
            event=EditorialEvent.TRANSFER_CONFIRMED,
            fact_phrase="ينتقل رسمياً",
            story_core="verified completed transfer",
        ))
        self.assertEqual(decision.visual_grammar.surface_visibility, SurfaceVisibility.NONE)
        self.assertNotIn("sport surface geometry", decision.visual_grammar.deterministic_elements)
        self.assertTrue(decision.visual_grammar.metadata["provider_agnostic"])

    def test_low_confidence_falls_back_to_verified_assets(self):
        decision = self.engine.decide(self.story(confidence=0.60))
        self.assertEqual(decision.plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)
        self.assertEqual(decision.fallback_reason, "low_story_confidence")
        self.assertEqual(decision.visual_grammar.generated_elements, ())

    def test_tennis_uses_tennis_specific_geometry(self):
        decision = self.engine.decide(self.story(
            sport="tennis",
            subject="Player",
            fact_phrase="يتأهل إلى النهائي",
            story_core="player qualified for final",
            event=EditorialEvent.QUALIFICATION,
        ))
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
        self.assertIn("generated logos", decision.high_risk_generated_elements)


if __name__ == "__main__":
    unittest.main()

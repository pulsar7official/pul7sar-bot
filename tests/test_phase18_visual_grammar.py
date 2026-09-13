import unittest

from engine.intelligence.scene_complexity_policy import SurfaceVisibility
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine
from engine.intelligence.visual_grammar import CameraLanguage, FantasyLevel, VisualGrammar


class VisualGrammarTests(unittest.TestCase):
    def setUp(self):
        self.editorial = StoryVisualEditorialEngine()
        self.grammar = VisualGrammar()

    def _plan(self, event, *, secondary=(), geometry=(), exact_assets=()):
        return self.editorial.plan(
            event=event,
            sport="football",
            story_core="fact-locked story",
            editorial_angle="premium editorial concept",
            headline_short="SHORT HEADLINE",
            primary_subject="Primary",
            secondary_subjects=secondary,
            geometry_requirements=geometry,
            exact_assets=exact_assets,
        )

    def test_transfer_does_not_request_pitch(self):
        decision = self.grammar.direct(self._plan(EditorialEvent.TRANSFER_CONFIRMED))
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.NONE)
        self.assertNotIn("sport surface geometry", decision.deterministic_elements)
        self.assertTrue(decision.metadata["provider_agnostic"])
        self.assertTrue(decision.metadata["zero_cost_compatible"])

    def test_injury_is_no_fantasy_verified_editorial(self):
        decision = self.grammar.direct(self._plan(EditorialEvent.INJURY))
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.NONE)
        self.assertEqual(decision.fantasy_level, FantasyLevel.NONE)
        self.assertEqual(decision.generated_elements, ())
        self.assertEqual(decision.camera_language, CameraLanguage.HERO_CLOSE)

    def test_result_uses_only_partial_deterministic_surface(self):
        decision = self.grammar.direct(self._plan(EditorialEvent.RESULT, secondary=("Opponent",)))
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.PARTIAL_DETERMINISTIC)
        self.assertIn("sport surface geometry", decision.deterministic_elements)
        self.assertIn("score", decision.deterministic_elements)
        self.assertIn("club identity", decision.deterministic_elements)
        self.assertEqual(decision.fantasy_level, FantasyLevel.RESTRAINED)

    def test_tactics_is_the_full_surface_case(self):
        decision = self.grammar.direct(self._plan(EditorialEvent.TACTICS, geometry=("formation geometry",)))
        self.assertEqual(decision.surface_visibility, SurfaceVisibility.FULL_DETERMINISTIC)
        self.assertIn("sport surface geometry", decision.deterministic_elements)
        self.assertIn("formation geometry", decision.deterministic_elements)
        self.assertEqual(decision.camera_language, CameraLanguage.TACTICAL_TOP)
        self.assertEqual(decision.generated_elements, ())

    def test_exact_assets_never_become_generated_elements(self):
        decision = self.grammar.direct(
            self._plan(EditorialEvent.CONTRACT, exact_assets=("verified player cutout", "club crest"))
        )
        self.assertIn("verified player cutout", decision.deterministic_elements)
        self.assertIn("club crest", decision.deterministic_elements)
        self.assertNotIn("club crest", decision.generated_elements)

    def test_forbidden_exact_content_remains_forbidden_for_generator(self):
        decision = self.grammar.direct(self._plan(EditorialEvent.RESULT))
        self.assertIn("PUL7SAR logo", decision.forbidden_generated_elements)
        self.assertIn("headline text", decision.forbidden_generated_elements)
        self.assertIn("scores", decision.forbidden_generated_elements)
        self.assertIn("club crests", decision.forbidden_generated_elements)


if __name__ == "__main__":
    unittest.main()

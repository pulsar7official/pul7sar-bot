import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.editorial_visual_authorization import EditorialVisualAuthorizationGate, VisualProductionAction
from engine.intelligence.story_visual_editorial import EditorialEvent


class EditorialVisualAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.planning = EditorialPlanningService()
        self.gate = EditorialVisualAuthorizationGate()

    def candidate(self, event=EditorialEvent.RESULT):
        return EditorialAngleCandidate(
            angle_id="main",
            event=event,
            story_core="verified story",
            fact_phrase="حدث موثق",
            primary_subject="Verified Subject",
            fact_confidence=0.97,
            identity_confidence=0.96,
        )

    def test_football_result_authorizes_hybrid_actions(self):
        result = self.planning.plan(sport="football", candidates=(self.candidate(),))
        auth = self.gate.evaluate(result)
        self.assertTrue(auth.allowed)
        self.assertIn(VisualProductionAction.GENERATE_ATMOSPHERE, auth.actions)
        self.assertIn(VisualProductionAction.BUILD_DETERMINISTIC, auth.actions)
        self.assertIn(VisualProductionAction.COMPOSE_VERIFIED_ASSETS, auth.actions)
        self.assertFalse(auth.publication_ready)

    def test_geometry_blocked_story_cannot_reach_visual_production(self):
        result = self.planning.plan(sport="basketball", candidates=(self.candidate(EditorialEvent.TACTICS),))
        auth = self.gate.evaluate(result)
        self.assertFalse(auth.allowed)
        self.assertEqual(auth.actions, (VisualProductionAction.BLOCK,))
        self.assertIn("editorial_visual_plan_not_ready", auth.blockers)

    def test_low_confidence_or_unsafe_plan_fails_before_gpu(self):
        unsafe = EditorialAngleCandidate(
            angle_id="unsafe",
            event=EditorialEvent.RESULT,
            story_core="weak",
            fact_phrase="غير كاف",
            primary_subject="Subject",
            fact_confidence=0.40,
        )
        result = self.planning.plan(sport="football", candidates=(unsafe,))
        with self.assertRaisesRegex(ValueError, "EDITORIAL_VISUAL_AUTHORIZATION_BLOCKED"):
            self.gate.assert_allowed(result)


if __name__ == "__main__":
    unittest.main()

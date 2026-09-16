import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.editorial_visual_authorization import EditorialVisualAuthorizationGate
from engine.intelligence.hybrid_layer_planner import LayerSource
from engine.intelligence.story_visual_editorial import EditorialEvent


SPORTS = (
    "football", "basketball", "tennis", "padel", "badminton", "volleyball", "handball",
    "baseball", "american_football", "rugby", "cricket", "golf", "boxing", "mma",
    "wrestling", "judo", "taekwondo", "athletics", "formula_1", "motorsport", "swimming",
    "cycling", "rowing", "sailing", "ice_hockey", "winter_sport", "table_tennis", "snooker",
    "darts", "gymnastics", "weightlifting", "equestrian", "esports",
)


class FullEventSportPlanningMatrixTests(unittest.TestCase):
    def test_every_event_across_major_sports_fails_safe_or_authorizes_explicit_actions(self):
        planning = EditorialPlanningService()
        auth_gate = EditorialVisualAuthorizationGate()
        exercised = 0

        for sport in SPORTS:
            for event in EditorialEvent:
                with self.subTest(sport=sport, event=event.value):
                    candidate = EditorialAngleCandidate(
                        angle_id=f"{sport}-{event.value}",
                        event=event,
                        story_core="verified factual core",
                        fact_phrase="حدث موثق",
                        primary_subject="Verified Subject",
                        fact_confidence=0.97,
                        identity_confidence=0.96,
                    )
                    result = planning.plan(sport=sport, candidates=(candidate,))
                    exercised += 1

                    self.assertIn(result.status, {"EDITORIAL_VISUAL_PLAN_READY", "GEOMETRY_CAPABILITY_BLOCKED"})
                    authorization = auth_gate.evaluate(result)
                    if result.status == "GEOMETRY_CAPABILITY_BLOCKED":
                        self.assertFalse(authorization.allowed)
                        self.assertIsNone(result.layers)
                        continue

                    self.assertTrue(authorization.allowed)
                    self.assertIsNotNone(result.layers)
                    self.assertIsNotNone(result.complexity)
                    self.assertFalse(authorization.publication_ready)

                    # No plan may assign exact PUL7SAR branding or typography to generation.
                    self.assertEqual(result.layers.by_name("pul7sar_brand").source, LayerSource.VERIFIED_ASSET)
                    self.assertEqual(result.layers.by_name("editorial_typography").source, LayerSource.DETERMINISTIC)
                    self.assertEqual(result.layers.by_name("data_and_score").source, LayerSource.DETERMINISTIC)

                    # If the geometry capability is unavailable, a surviving plan
                    # must have removed any required deterministic surface rather
                    # than handing it back to diffusion.
                    if result.geometry_capability is not None and not result.geometry_capability.ready:
                        surface = result.layers.by_name("sport_surface_geometry")
                        self.assertFalse(surface.required)
                        self.assertNotEqual(surface.source, LayerSource.GENERATIVE)

        self.assertEqual(exercised, len(SPORTS) * len(EditorialEvent))
        self.assertGreater(exercised, 800)


if __name__ == "__main__":
    unittest.main()

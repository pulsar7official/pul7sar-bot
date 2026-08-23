import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.geometry_capabilities import DeterministicGeometryCapabilityRegistry, GeometryCapabilityStatus
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode


class GeometryCapabilitiesTests(unittest.TestCase):
    def setUp(self):
        self.rules = SportVisualRuleRegistry()
        self.capabilities = DeterministicGeometryCapabilityRegistry()
        self.service = EditorialPlanningService()

    def candidate(self, event, subject="Team"):
        return EditorialAngleCandidate(
            angle_id=f"{event.value}-1",
            event=event,
            story_core="verified story",
            fact_phrase="حدث موثق",
            primary_subject=subject,
            fact_confidence=0.97,
            identity_confidence=0.96,
        )

    def test_football_geometry_renderer_is_ready(self):
        capability = self.capabilities.evaluate(self.rules.get("football"))
        self.assertEqual(capability.status, GeometryCapabilityStatus.READY)
        self.assertEqual(capability.renderer_id, "football_pitch_projective_v1")

    def test_basketball_exact_geometry_is_not_falsely_claimed_ready(self):
        capability = self.capabilities.evaluate(self.rules.get("basketball"))
        self.assertEqual(capability.status, GeometryCapabilityStatus.UNAVAILABLE)
        self.assertFalse(capability.ready)

    def test_basketball_result_removes_surface_and_falls_back_safely(self):
        result = self.service.plan(sport="basketball", candidates=(self.candidate(EditorialEvent.RESULT),))
        self.assertEqual(result.status, "EDITORIAL_VISUAL_PLAN_READY")
        self.assertEqual(result.decision.plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL)
        self.assertEqual(result.decision.fallback_reason, "deterministic_geometry_unavailable")
        self.assertEqual(result.complexity.surface_visibility.value, "none")

    def test_basketball_tactics_blocks_until_geometry_renderer_exists(self):
        result = self.service.plan(sport="basketball", candidates=(self.candidate(EditorialEvent.TACTICS),))
        self.assertEqual(result.status, "GEOMETRY_CAPABILITY_BLOCKED")
        self.assertIsNone(result.layers)
        self.assertEqual(result.geometry_capability.status, GeometryCapabilityStatus.UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()

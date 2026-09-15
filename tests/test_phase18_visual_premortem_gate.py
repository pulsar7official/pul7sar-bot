import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.entity_theme import EntityPaletteEvidence
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_premortem_gate import PremortemAction, VisualPremortemGate


class VisualPremortemGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = VisualPremortemGate()
        self.service = EditorialPlanningService()

    def caps(self, semantic=True):
        return LocalVisionCapabilityReport(
            png_observation=True,
            protected_region_clutter=True,
            semantic_subject_framing=semantic,
            identity_similarity=semantic,
            semantic_defect_detection=semantic,
            forbidden_visual_detection=semantic,
        )

    def candidate(self, event=EditorialEvent.RESULT, **kwargs):
        data = dict(
            angle_id="main",
            event=event,
            story_core="verified core",
            fact_phrase="يحسم الحدث",
            primary_subject="Club A",
            secondary_subjects=("Club B",) if event is EditorialEvent.RESULT else (),
            editorial_importance=0.95,
            fact_confidence=0.98,
            identity_confidence=0.97,
        )
        data.update(kwargs)
        return EditorialAngleCandidate(**data)

    def plan_result(self):
        return self.service.plan(
            sport="football",
            candidates=(self.candidate(),),
            verified_facts={
                "subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A"
            },
            entity_palettes={"Club A": EntityPaletteEvidence("Club A", "#E30613", 0.98, "registry")},
        )

    def test_missing_semantic_vision_allows_engineering_only_not_publication(self):
        decision = self.gate.evaluate(
            planning=self.plan_result(),
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A"},
            vision_capabilities=self.caps(semantic=False),
            identity_required=False,
            identity_verified=True,
            dominant_palette_verified=True,
            brand_geometry_approved=True,
        )
        self.assertEqual(decision.action, PremortemAction.ENGINEERING_PROOF_ONLY)
        self.assertTrue(decision.gpu_execution_allowed)
        self.assertFalse(decision.publication_allowed)
        self.assertIn("semantic_visual_inspection_missing", decision.blockers)

    def test_unapproved_brand_geometry_allows_proof_but_blocks_publication(self):
        decision = self.gate.evaluate(
            planning=self.plan_result(),
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A"},
            vision_capabilities=self.caps(),
            identity_required=False,
            identity_verified=True,
            dominant_palette_verified=True,
            brand_geometry_approved=False,
        )
        self.assertEqual(decision.action, PremortemAction.ENGINEERING_PROOF_ONLY)
        self.assertTrue(decision.gpu_execution_allowed)
        self.assertFalse(decision.publication_allowed)
        self.assertIn("brand_geometry_unapproved", decision.blockers)

    def test_live_result_is_blocked_before_gpu(self):
        planning = self.service.plan(
            sport="football",
            candidates=(self.candidate(),),
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "live"},
        )
        decision = self.gate.evaluate(
            planning=planning,
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "live"},
            vision_capabilities=self.caps(),
            identity_required=False,
            identity_verified=True,
            dominant_palette_verified=False,
            brand_geometry_approved=True,
        )
        self.assertEqual(decision.action, PremortemAction.BLOCK)
        self.assertFalse(decision.gpu_execution_allowed)
        self.assertIn("winner_brand_before_final", decision.blockers)

    def test_missing_palette_uses_safe_fallback_not_block(self):
        decision = self.gate.evaluate(
            planning=self.plan_result(),
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A"},
            vision_capabilities=self.caps(),
            identity_required=False,
            identity_verified=True,
            dominant_palette_verified=False,
            brand_geometry_approved=True,
        )
        self.assertEqual(decision.action, PremortemAction.REPLAN_TO_SAFE_FALLBACK)
        self.assertTrue(decision.gpu_execution_allowed)
        self.assertIn("dominant_palette_missing", decision.fallback_reasons)

    def test_verified_identity_requirement_blocks_when_identity_not_verified(self):
        decision = self.gate.evaluate(
            planning=self.plan_result(),
            verified_facts={"subject": "Club A", "opponent": "Club B", "result_status": "completed", "winner_entity": "Club A"},
            vision_capabilities=self.caps(),
            identity_required=True,
            identity_verified=False,
            dominant_palette_verified=True,
            brand_geometry_approved=True,
        )
        self.assertEqual(decision.action, PremortemAction.BLOCK)
        self.assertIn("identity_unverified", decision.blockers)


if __name__ == "__main__":
    unittest.main()

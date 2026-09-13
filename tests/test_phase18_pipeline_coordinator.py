import unittest
from datetime import datetime, timezone

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.entity_theme import EntityPaletteEvidence
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.phase18_pipeline_coordinator import Phase18PipelineCoordinator
from engine.intelligence.story_visual_editorial import EditorialEvent


class Phase18PipelineCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.coordinator = Phase18PipelineCoordinator()
        self.now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)

    def candidate(self, **kwargs):
        data = dict(
            angle_id="result-main",
            event=EditorialEvent.RESULT,
            story_core="verified final result",
            fact_phrase="يحسم المباراة",
            primary_subject="Club A",
            secondary_subjects=("Club B",),
            editorial_importance=0.95,
            fact_confidence=0.98,
            identity_confidence=0.98,
        )
        data.update(kwargs)
        return EditorialAngleCandidate(**data)

    def full_vision(self):
        return LocalVisionCapabilityReport(True, True, True, True, True, True)

    def limited_vision(self):
        return LocalVisionCapabilityReport(True, True, False, False, False, False)

    def facts(self):
        return {
            "subject": "Club A",
            "opponent": "Club B",
            "result_status": "final",
            "score": "2-1",
            "winner_entity": "Club A",
            "verified_at": self.now.isoformat(),
        }

    def test_clean_plan_reaches_execution_ready(self):
        decision = self.coordinator.prepare(
            event=EditorialEvent.RESULT,
            sport="football",
            facts=self.facts(),
            candidates=(self.candidate(),),
            vision_capabilities=self.full_vision(),
            identity_required=False,
            identity_verified=True,
            brand_geometry_approved=True,
            entity_palettes={"Club A": EntityPaletteEvidence("Club A", "#AA0000", 0.99, "registry")},
            now=self.now,
        )
        self.assertTrue(decision.gpu_execution_allowed)
        self.assertEqual(decision.status, "PHASE18_EXECUTION_READY")
        self.assertIsNotNone(decision.execution_plan)
        self.assertEqual(decision.execution_plan.dominant_entity, "Club A")

    def test_invalid_story_never_reaches_planning(self):
        facts = self.facts()
        facts["winner_entity"] = "Club C"
        decision = self.coordinator.prepare(
            event=EditorialEvent.RESULT,
            sport="football",
            facts=facts,
            candidates=(self.candidate(),),
            vision_capabilities=self.full_vision(),
            identity_required=False,
            identity_verified=True,
            brand_geometry_approved=True,
            now=self.now,
        )
        self.assertFalse(decision.gpu_execution_allowed)
        self.assertEqual(decision.status, "PREPRODUCTION_INTEGRITY_BLOCKED")
        self.assertIsNone(decision.planning)

    def test_missing_semantic_vision_allows_only_engineering_proof(self):
        decision = self.coordinator.prepare(
            event=EditorialEvent.RESULT,
            sport="football",
            facts=self.facts(),
            candidates=(self.candidate(),),
            vision_capabilities=self.limited_vision(),
            identity_required=False,
            identity_verified=True,
            brand_geometry_approved=True,
            entity_palettes={"Club A": EntityPaletteEvidence("Club A", "#AA0000", 0.99, "registry")},
            now=self.now,
        )
        self.assertTrue(decision.gpu_execution_allowed)
        self.assertFalse(decision.publication_allowed_at_this_stage)
        self.assertEqual(decision.status, "PHASE18_ENGINEERING_PROOF_READY")

    def test_unverified_identity_blocks_before_gpu(self):
        decision = self.coordinator.prepare(
            event=EditorialEvent.RESULT,
            sport="football",
            facts=self.facts(),
            candidates=(self.candidate(),),
            vision_capabilities=self.full_vision(),
            identity_required=True,
            identity_verified=False,
            brand_geometry_approved=True,
            now=self.now,
        )
        self.assertFalse(decision.gpu_execution_allowed)
        self.assertEqual(decision.status, "VISUAL_PREMORTEM_BLOCKED")
        self.assertIn("identity_unverified", decision.blockers)


if __name__ == "__main__":
    unittest.main()

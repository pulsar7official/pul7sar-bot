import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.entity_theme import EntityPaletteEvidence
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_execution_plan import VisualExecutionPlanCompiler


class VisualExecutionPlanTests(unittest.TestCase):
    def planning(self, event=EditorialEvent.RESULT):
        candidate = EditorialAngleCandidate(
            angle_id="main",
            event=event,
            story_core="verified story core",
            fact_phrase="يحسم الحدث",
            primary_subject="Club A",
            editorial_importance=0.95,
            fact_confidence=0.98,
            identity_confidence=0.97,
        )
        palette = EntityPaletteEvidence("Club A", "#0047AB", 0.95, "verified_registry")
        return EditorialPlanningService().plan(
            sport="football",
            candidates=(candidate,),
            hero_palette=palette,
            hero_is_unambiguous=True,
        )

    def test_result_plan_owns_football_geometry_and_dynamic_brand(self):
        plan = VisualExecutionPlanCompiler().compile(self.planning())
        self.assertEqual(plan.status, "VISUAL_EXECUTION_PLAN_READY")
        self.assertEqual(plan.geometry_executor, "football_pitch_projective_v1")
        self.assertIsNotNone(plan.football_camera_preset)
        self.assertEqual(plan.dynamic_brand_accent_hex, "#0047AB")
        self.assertEqual(plan.dominant_entity, "Club A")
        self.assertIsNone(plan.story_dominance_reason)
        self.assertIn("deterministic_sport_geometry_applied", plan.hard_verification_requirements)
        self.assertIn("no_generated_pul7sar_brand", plan.hard_verification_requirements)
        self.assertIn("plain and unmarked", plan.base_scene_contract.prompt_suffix)

    def test_verified_match_winner_is_auditable_in_execution_plan(self):
        candidate = EditorialAngleCandidate(
            angle_id="result",
            event=EditorialEvent.RESULT,
            story_core="verified completed match",
            fact_phrase="يفوز في المباراة",
            primary_subject="Club A",
            secondary_subjects=("Club B",),
            editorial_importance=0.98,
            fact_confidence=0.99,
            identity_confidence=0.99,
        )
        palettes = {
            "Club A": EntityPaletteEvidence("Club A", "#AA0000", 0.98, "registry"),
            "Club B": EntityPaletteEvidence("Club B", "#0033AA", 0.98, "registry"),
        }
        planning = EditorialPlanningService().plan(
            sport="football",
            candidates=(candidate,),
            verified_facts={
                "subject": "Club A",
                "opponent": "Club B",
                "result_status": "completed",
                "winner_entity": "Club B",
            },
            entity_palettes=palettes,
        )
        plan = VisualExecutionPlanCompiler().compile(planning)
        self.assertEqual(plan.dominant_entity, "Club B")
        self.assertEqual(plan.story_dominance_reason, "result_winner")
        self.assertEqual(plan.dynamic_brand_accent_hex, "#0033AA")
        self.assertEqual(plan.dynamic_brand_reason, "verified_dominant_entity")

    def test_non_executable_planning_is_rejected(self):
        bad = EditorialPlanningService().plan(
            sport="football",
            candidates=(EditorialAngleCandidate(
                angle_id="unsafe",
                event=EditorialEvent.RESULT,
                story_core="uncertain",
                fact_phrase="قد يفوز",
                primary_subject="Club A",
                editorial_importance=0.9,
                fact_confidence=0.3,
                identity_confidence=0.9,
            ),),
        )
        with self.assertRaises(ValueError):
            VisualExecutionPlanCompiler().compile(bad)


if __name__ == "__main__":
    unittest.main()

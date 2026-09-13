import unittest

from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode
from engine.intelligence.visual_failure_scenarios import FailureSeverity, VisualFailureScenarioEngine


class VisualFailureScenarioEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = VisualFailureScenarioEngine()

    def evaluate(self, **kwargs):
        defaults = dict(
            event=EditorialEvent.RESULT,
            production_mode=ProductionMode.HYBRID,
            verified_facts={"result_status": "final"},
            has_verified_palette_for_dominant_entity=True,
            identity_required=False,
            identity_verified=True,
            deterministic_geometry_required=False,
            deterministic_geometry_ready=True,
            readable_text_required=False,
            brand_geometry_approved=True,
            semantic_visual_inspection_ready=True,
            subject_count=1,
        )
        defaults.update(kwargs)
        return self.engine.evaluate(**defaults)

    def test_missing_geometry_renderer_hard_blocks(self):
        result = self.evaluate(deterministic_geometry_required=True, deterministic_geometry_ready=False)
        self.assertTrue(result.hard_blocked)
        self.assertIn("geometry_renderer_missing", {x.scenario_id for x in result.scenarios})

    def test_unverified_identity_hard_blocks(self):
        result = self.evaluate(identity_required=True, identity_verified=False)
        self.assertTrue(result.hard_blocked)
        self.assertIn("identity_unverified", {x.scenario_id for x in result.scenarios})

    def test_semantic_visual_inspection_missing_blocks_publication(self):
        result = self.evaluate(semantic_visual_inspection_ready=False)
        item = next(x for x in result.scenarios if x.scenario_id == "semantic_visual_inspection_missing")
        self.assertEqual(item.severity, FailureSeverity.HARD_BLOCK)

    def test_non_final_result_cannot_receive_final_winner_treatment(self):
        result = self.evaluate(verified_facts={"result_status": "live"})
        self.assertIn("winner_brand_before_final", {x.scenario_id for x in result.scenarios})

    def test_non_final_transfer_is_blocked(self):
        result = self.evaluate(
            event=EditorialEvent.TRANSFER_CONFIRMED,
            verified_facts={"confirmation_status": "pending"},
        )
        self.assertIn("transfer_not_final", {x.scenario_id for x in result.scenarios})

    def test_missing_dominant_palette_warns_and_falls_back(self):
        result = self.evaluate(has_verified_palette_for_dominant_entity=False)
        item = next(x for x in result.scenarios if x.scenario_id == "dominant_palette_missing")
        self.assertEqual(item.severity, FailureSeverity.WARNING)

    def test_exact_data_story_must_not_use_generative_scene(self):
        result = self.evaluate(
            event=EditorialEvent.TABLE,
            production_mode=ProductionMode.GENERATIVE_SCENE,
            verified_facts={},
        )
        self.assertIn("wrong_production_mode_for_exact_data", {x.scenario_id for x in result.scenarios})

    def test_excessive_subjects_warns(self):
        result = self.evaluate(subject_count=4)
        self.assertIn("excessive_subject_complexity", {x.scenario_id for x in result.scenarios})


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.qwen25_vl_inspector import Qwen25VLSemanticInspector, SemanticInspectionStage


class QwenInspectionStageTests(unittest.TestCase):
    def test_base_stage_forbids_model_owned_sport_geometry(self):
        text = Qwen25VLSemanticInspector._instruction(None, SemanticInspectionStage.BASE_SCENE)
        self.assertIn("BEFORE DETERMINISTIC COMPOSITION", text)
        self.assertIn("generated_sport_geometry_absent", text)
        self.assertIn("exact or partial regulation sport geometry", text)
        self.assertIn("goal frames/nets", text)
        self.assertIn("penalty-area or goal-area lines", text)
        self.assertIn("corner arcs/flags", text)
        self.assertIn("centre circles", text)
        self.assertIn("halfway lines", text)
        self.assertIn("physically implausible", text)
        self.assertIn("Vague unmarked turf/floor may pass", text)

    def test_severe_defect_rule_names_impossible_goal_relationship(self):
        text = Qwen25VLSemanticInspector._instruction(None, SemanticInspectionStage.BASE_SCENE)
        self.assertIn("goal frame/net appearing in a physically impossible relationship to a touchline/endline", text)

    def test_hybrid_stage_expects_deterministic_pitch_and_checks_alignment(self):
        text = Qwen25VLSemanticInspector._instruction(None, SemanticInspectionStage.HYBRID_SURFACE)
        self.assertIn("AFTER DETERMINISTIC SPORT GEOMETRY COMPOSITION", text)
        self.assertIn("Deterministic pitch markings are expected", text)
        self.assertIn("sport_geometry_alignment_valid", text)
        self.assertIn("implausibly wide/short/long", text)
        self.assertIn("goal positioned inconsistently with goal-line/touchline geometry", text)

    def test_stage_must_be_enum(self):
        inspector = Qwen25VLSemanticInspector()
        with self.assertRaises(TypeError):
            inspector.inspect_file("missing.png", stage="base_scene")


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_planning_service import EditorialPlanningService
from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver
from engine.intelligence.hybrid_layer_planner import LayerSource
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode


class EditorialPlanningServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = EditorialPlanningService()

    def candidate(self, angle_id, **kwargs):
        data = dict(
            angle_id=angle_id,
            event=EditorialEvent.RESULT,
            story_core="verified result core",
            fact_phrase="يحسم المباراة",
            primary_subject="Arsenal",
            editorial_importance=0.9,
            fact_confidence=0.98,
            identity_confidence=0.96,
        )
        data.update(kwargs)
        return EditorialAngleCandidate(**data)

    def palette(self, name, color):
        return EntityPaletteEvidence(name, color, 0.98, "verified_registry")

    def test_selects_angle_and_builds_copy_visual_and_layers_together(self):
        result = self.service.plan(
            sport="football",
            candidates=(self.candidate("main"),),
            tone=HeadlineTone.POSITIVE,
        )
        self.assertEqual(result.status, "EDITORIAL_VISUAL_PLAN_READY")
        self.assertEqual(result.selected_angle.candidate.angle_id, "main")
        self.assertIn("Arsenal", result.decision.headline)
        self.assertEqual(result.decision.plan.production_mode, ProductionMode.HYBRID)
        self.assertEqual(result.layers.by_name("sport_surface_geometry").source, LayerSource.DETERMINISTIC)
        self.assertEqual(result.layers.by_name("pul7sar_brand").source, LayerSource.VERIFIED_ASSET)

    def test_match_winner_controls_7_and_pulse_even_with_two_teams(self):
        candidate = self.candidate("result", secondary_subjects=("Chelsea",))
        result = self.service.plan(
            sport="football",
            candidates=(candidate,),
            verified_facts={
                "subject": "Arsenal",
                "opponent": "Chelsea",
                "result_status": "completed",
                "winner_entity": "Chelsea",
                "score": "1-2",
            },
            entity_palettes={
                "Arsenal": self.palette("Arsenal", "#E30613"),
                "Chelsea": self.palette("Chelsea", "#034694"),
            },
        )
        self.assertEqual(result.brand.hero_entity, "Chelsea")
        self.assertEqual(result.brand.accent_hex, "#034694")
        self.assertTrue(result.brand.contextual)

    def test_confirmed_transfer_destination_controls_brand_not_origin(self):
        candidate = self.candidate(
            "transfer",
            event=EditorialEvent.TRANSFER_CONFIRMED,
            primary_subject="Player X",
            secondary_subjects=("Origin FC", "Destination FC"),
            story_core="confirmed transfer",
            fact_phrase="ينضم رسميا",
        )
        result = self.service.plan(
            sport="football",
            candidates=(candidate,),
            verified_facts={
                "subject": "Player X",
                "origin": "Origin FC",
                "destination": "Destination FC",
                "confirmation_status": "confirmed",
            },
            entity_palettes={
                "Origin FC": self.palette("Origin FC", "#FFAA00"),
                "Destination FC": self.palette("Destination FC", "#1122CC"),
            },
        )
        self.assertEqual(result.brand.hero_entity, "Destination FC")
        self.assertEqual(result.brand.accent_hex, "#1122CC")

    def test_draw_between_two_teams_falls_back_to_default_red(self):
        candidate = self.candidate("draw", secondary_subjects=("Chelsea",))
        result = self.service.plan(
            sport="football",
            candidates=(candidate,),
            verified_facts={"subject": "Arsenal", "opponent": "Chelsea", "result_status": "draw"},
            entity_palettes={
                "Arsenal": self.palette("Arsenal", "#E30613"),
                "Chelsea": self.palette("Chelsea", "#034694"),
            },
        )
        self.assertEqual(result.brand.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertFalse(result.brand.contextual)

    def test_visually_safer_angle_can_be_selected(self):
        complex_angle = self.candidate(
            "complex",
            editorial_importance=1.0,
            secondary_subjects=("A", "B", "C", "D"),
            requires_exact_text=True,
            requires_exact_geometry=True,
        )
        safe_angle = self.candidate("safe", editorial_importance=0.92)
        result = self.service.plan(sport="football", candidates=(complex_angle, safe_angle))
        self.assertEqual(result.selected_angle.candidate.angle_id, "safe")

    def test_all_unsafe_angles_stop_before_visual_production(self):
        result = self.service.plan(
            sport="football",
            candidates=(
                self.candidate("weak", fact_confidence=0.5),
                self.candidate("invented", requires_invented_scene=True),
            ),
        )
        self.assertEqual(result.status, "NO_SAFE_EDITORIAL_ANGLE")
        self.assertIsNone(result.decision)
        self.assertIsNone(result.layers)
        self.assertEqual(set(result.rejected_angle_ids), {"weak", "invented"})

    def test_tactics_owns_geometry_and_data_deterministically(self):
        result = self.service.plan(
            sport="football",
            candidates=(self.candidate(
                "tactics",
                event=EditorialEvent.TACTICS,
                story_core="verified tactical setup",
                fact_phrase="يغير شكل الوسط",
                requires_exact_geometry=True,
            ),),
        )
        self.assertEqual(result.decision.plan.production_mode, ProductionMode.DETERMINISTIC_COMPOSITION)
        self.assertEqual(result.layers.by_name("sport_surface_geometry").source, LayerSource.DETERMINISTIC)
        self.assertEqual(result.layers.by_name("data_and_score").source, LayerSource.DETERMINISTIC)


if __name__ == "__main__":
    unittest.main()

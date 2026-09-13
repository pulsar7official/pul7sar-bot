import unittest
from datetime import datetime, timezone

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.phase18_pipeline_coordinator import Phase18PipelineCoordinator
from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode


class GoldenStoryMatrixTests(unittest.TestCase):
    def setUp(self):
        self.coordinator = Phase18PipelineCoordinator()
        self.now = datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc)
        self.vision = LocalVisionCapabilityReport(True, True, True, True, True, True)

    def candidate(self, event, subject, phrase, *, secondary=(), importance=0.95, geometry=False):
        return EditorialAngleCandidate(
            angle_id=f"{event.value}-golden",
            event=event,
            story_core="verified golden matrix story",
            fact_phrase=phrase,
            primary_subject=subject,
            secondary_subjects=secondary,
            editorial_importance=importance,
            fact_confidence=0.99,
            identity_confidence=0.99,
            requires_exact_geometry=geometry,
        )

    def prepare(self, event, sport, facts, candidate, *, palettes=None, identity_required=False):
        facts = {**facts, "verified_at": self.now.isoformat()}
        return self.coordinator.prepare(
            event=event,
            sport=sport,
            facts=facts,
            candidates=(candidate,),
            vision_capabilities=self.vision,
            identity_required=identity_required,
            identity_verified=True,
            brand_geometry_approved=True,
            entity_palettes=palettes,
            now=self.now,
        )

    def test_result_story_uses_winner_color_and_hybrid_geometry(self):
        palette_a = EntityPaletteEvidence("Club A", "#AA0000", 0.99, "registry")
        palette_b = EntityPaletteEvidence("Club B", "#0000AA", 0.99, "registry")
        result = self.prepare(
            EditorialEvent.RESULT,
            "football",
            {"subject": "Club A", "opponent": "Club B", "result_status": "final", "score": "1-2", "winner_entity": "Club B"},
            self.candidate(EditorialEvent.RESULT, "Club A", "يخسر أمام منافسه", secondary=("Club B",)),
            palettes={"Club A": palette_a, "Club B": palette_b},
        )
        self.assertTrue(result.gpu_execution_allowed)
        self.assertEqual(result.planning.brand.hero_entity, "Club B")
        self.assertEqual(result.planning.brand.accent_hex, "#0000AA")
        self.assertEqual(result.execution_plan.production_mode, ProductionMode.HYBRID.value)
        self.assertEqual(result.execution_plan.geometry_executor, "football_pitch_projective_v1")

    def test_confirmed_transfer_uses_destination_color_without_needing_pitch(self):
        destination = EntityPaletteEvidence("Destination FC", "#1166CC", 0.99, "registry")
        result = self.prepare(
            EditorialEvent.TRANSFER_CONFIRMED,
            "football",
            {"subject": "Player X", "origin": "Origin FC", "destination": "Destination FC", "confirmation_status": "official"},
            self.candidate(EditorialEvent.TRANSFER_CONFIRMED, "Player X", "ينضم رسميا", secondary=("Origin FC", "Destination FC")),
            palettes={"Destination FC": destination},
            identity_required=True,
        )
        self.assertEqual(result.planning.brand.hero_entity, "Destination FC")
        self.assertEqual(result.planning.brand.accent_hex, "#1166CC")
        self.assertIsNone(result.execution_plan.geometry_executor)

    def test_injury_uses_verified_asset_editorial_not_imagined_medical_scene(self):
        result = self.prepare(
            EditorialEvent.INJURY,
            "football",
            {"subject": "Player Y", "injury_status": "confirmed", "injury_type": "hamstring"},
            self.candidate(EditorialEvent.INJURY, "Player Y", "يتعرض لإصابة"),
            identity_required=True,
        )
        self.assertEqual(result.execution_plan.production_mode, ProductionMode.VERIFIED_ASSET_EDITORIAL.value)
        self.assertIsNone(result.execution_plan.geometry_executor)

    def test_record_story_keeps_exact_record_value_out_of_generation(self):
        result = self.prepare(
            EditorialEvent.RECORD,
            "tennis",
            {"subject": "Player Z", "record_metric": "wins", "record_value": "100"},
            self.candidate(EditorialEvent.RECORD, "Player Z", "يحقق رقما قياسيا"),
            identity_required=True,
        )
        self.assertTrue(result.gpu_execution_allowed)
        self.assertIn("data_and_score", dict(result.execution_plan.layer_sources))

    def test_tactics_is_deterministic_and_blocks_when_sport_renderer_missing(self):
        result = self.prepare(
            EditorialEvent.TACTICS,
            "basketball",
            {"subject": "Team Q", "tactical_claim": "zone defense", "formation": "2-3"},
            self.candidate(EditorialEvent.TACTICS, "Team Q", "يعتمد دفاع المنطقة", geometry=True),
        )
        self.assertFalse(result.gpu_execution_allowed)
        self.assertEqual(result.status, "GEOMETRY_CAPABILITY_BLOCKED")

    def test_ambiguous_preview_returns_default_red(self):
        result = self.prepare(
            EditorialEvent.PREVIEW,
            "football",
            {"subject": "Club A", "opponent": "Club B", "event_status": "scheduled"},
            self.candidate(EditorialEvent.PREVIEW, "Club A", "يواجه منافسه", secondary=("Club B",)),
            palettes={
                "Club A": EntityPaletteEvidence("Club A", "#AA0000", 0.99, "registry"),
                "Club B": EntityPaletteEvidence("Club B", "#0000AA", 0.99, "registry"),
            },
        )
        self.assertEqual(result.planning.brand.accent_hex, EntityThemeResolver.PUL7SAR_RED)
        self.assertFalse(result.planning.brand.contextual)


if __name__ == "__main__":
    unittest.main()

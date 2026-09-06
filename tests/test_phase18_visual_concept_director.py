import unittest

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_concept_director import (
    VisualConceptArchetype,
    VisualConceptDirector,
    VisualConceptSignals,
)


class VisualConceptDirectorTests(unittest.TestCase):
    def setUp(self):
        self.director = VisualConceptDirector()

    def test_result_uses_original_generation_even_when_match_photo_exists(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(
                verified_subject_asset=True,
                verified_action_photo=True,
                verified_match_photo=True,
                decisive_moment_known=True,
                exact_club_assets=True,
                safe_generated_context=True,
            ),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertIn("third-party match photograph as final publication canvas", decision.forbidden_motifs)
        self.assertTrue(decision.metadata["original_publication_pixels_required"])
        self.assertTrue(decision.metadata["third_party_photos_reference_only_by_default"])

    def test_score_monument_is_original_result_fallback_not_mandatory_stadium(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(exact_club_assets=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertIn("mandatory stadium background", decision.forbidden_motifs)
        self.assertIn("third-party match photograph as final publication canvas", decision.forbidden_motifs)

    def test_event_context_photo_is_reference_not_default_canvas(self):
        decision = self.director.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(verified_context_photo=True, safe_generated_context=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertIn("third-party context photograph as final publication canvas", decision.forbidden_motifs)
        self.assertIn("abstract portal as default hero", decision.forbidden_motifs)
        self.assertIn("duplicate PUL7SAR pulse motif", decision.forbidden_motifs)

    def test_event_can_use_safe_non_identifying_generated_atmosphere(self):
        decision = self.director.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(safe_generated_context=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertIn("original", decision.hero)
        self.assertIn("specific real venue identity without verified reference", decision.forbidden_motifs)
        self.assertIn("specific real-person depiction", decision.forbidden_motifs)
        self.assertFalse(decision.metadata["publication_ready"])

    def test_event_without_generation_remains_original_minimal(self):
        decision = self.director.direct(EditorialSceneFamily.EVENT_EDITORIAL, VisualConceptSignals())
        self.assertEqual(decision.archetype, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL)
        self.assertIn("generic stadium", decision.forbidden_motifs)

    def test_verified_subject_reference_does_not_authorize_press_photo_pixels(self):
        decision = self.director.direct(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            VisualConceptSignals(verified_subject_asset=True, story_requires_person=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.HERO_ARRIVAL)
        self.assertIn("third-party portrait as final publication pixels", decision.forbidden_motifs)
        self.assertIn("verified_subject_reference", decision.asset_priority)

    def test_tactics_requires_exact_spatial_data(self):
        with self.assertRaisesRegex(ValueError, "TACTICAL_CONCEPT_REQUIRES_EXACT_TACTICAL_DATA"):
            self.director.direct(EditorialSceneFamily.TACTICAL_BOARD, VisualConceptSignals())
        decision = self.director.direct(
            EditorialSceneFamily.TACTICAL_BOARD,
            VisualConceptSignals(exact_tactical_data=True, story_requires_pitch=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.TACTICAL_SPATIAL_MAP)

    def test_every_concept_forbids_generic_template_and_source_photo_default(self):
        samples = (
            (EditorialSceneFamily.TRANSFER_SIGNATURE, VisualConceptSignals()),
            (EditorialSceneFamily.RESULT_STATEMENT, VisualConceptSignals()),
            (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, VisualConceptSignals()),
            (EditorialSceneFamily.TACTICAL_BOARD, VisualConceptSignals(exact_tactical_data=True, story_requires_pitch=True)),
            (EditorialSceneFamily.DATA_MONUMENT, VisualConceptSignals(exact_data_anchor=True)),
            (EditorialSceneFamily.EVENT_EDITORIAL, VisualConceptSignals()),
            (EditorialSceneFamily.EVENT_EDITORIAL, VisualConceptSignals(safe_generated_context=True)),
        )
        for family, signals in samples:
            decision = self.director.direct(family, signals)
            self.assertIn("generic one-template layout", decision.forbidden_motifs)
            self.assertIn("unexplained decorative pulse outside PUL7SAR brand", decision.forbidden_motifs)
            self.assertIn("source-news photograph as default publication canvas", decision.forbidden_motifs)
            self.assertTrue(decision.metadata["concept_selected_before_renderer"])
            self.assertTrue(decision.metadata["original_publication_pixels_required"])


if __name__ == "__main__":
    unittest.main()

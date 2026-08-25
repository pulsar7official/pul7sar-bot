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

    def test_result_prefers_verified_decisive_moment_over_scoreboard_template(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(
                verified_subject_asset=True,
                verified_action_photo=True,
                decisive_moment_known=True,
                exact_club_assets=True,
            ),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.DECISIVE_MOMENT)
        self.assertIn("scoreboard-first composition when decisive verified moment exists", decision.forbidden_motifs)

    def test_result_prefers_verified_celebration_before_generic_stadium(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(
                verified_subject_asset=True,
                verified_celebration_photo=True,
                exact_club_assets=True,
            ),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.CELEBRATION_MOMENT)
        self.assertIn("humiliation or collapse imagery for losing side", decision.forbidden_motifs)

    def test_score_monument_is_result_fallback_not_mandatory_stadium(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(exact_club_assets=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        self.assertIn("mandatory stadium background", decision.forbidden_motifs)

    def test_event_uses_verified_context_instead_of_abstract_portal(self):
        decision = self.director.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(verified_context_photo=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.PHOTOGRAPHIC_EVENT)
        self.assertIn("abstract portal as default hero", decision.forbidden_motifs)
        self.assertIn("duplicate PUL7SAR pulse motif", decision.forbidden_motifs)

    def test_event_can_use_safe_non_identifying_generated_atmosphere(self):
        decision = self.director.direct(
            EditorialSceneFamily.EVENT_EDITORIAL,
            VisualConceptSignals(safe_generated_context=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE)
        self.assertIn("non-identifying", decision.hero)
        self.assertIn("specific real venue identity without verified context", decision.forbidden_motifs)
        self.assertIn("specific real-person depiction", decision.forbidden_motifs)
        self.assertFalse(decision.metadata["publication_ready"])

    def test_event_without_verified_or_safe_generated_context_remains_minimal(self):
        decision = self.director.direct(EditorialSceneFamily.EVENT_EDITORIAL, VisualConceptSignals())
        self.assertEqual(decision.archetype, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL)
        self.assertIn("generic stadium", decision.forbidden_motifs)

    def test_tactics_requires_exact_spatial_data(self):
        with self.assertRaisesRegex(ValueError, "TACTICAL_CONCEPT_REQUIRES_EXACT_TACTICAL_DATA"):
            self.director.direct(EditorialSceneFamily.TACTICAL_BOARD, VisualConceptSignals())
        decision = self.director.direct(
            EditorialSceneFamily.TACTICAL_BOARD,
            VisualConceptSignals(exact_tactical_data=True, story_requires_pitch=True),
        )
        self.assertEqual(decision.archetype, VisualConceptArchetype.TACTICAL_SPATIAL_MAP)

    def test_every_concept_forbids_generic_template_fallback_and_duplicate_pulse(self):
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
            self.assertTrue(decision.metadata["concept_selected_before_renderer"])


if __name__ == "__main__":
    unittest.main()

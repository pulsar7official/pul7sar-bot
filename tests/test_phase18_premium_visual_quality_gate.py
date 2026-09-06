import unittest

from engine.intelligence.premium_visual_quality_gate import PremiumVisualEvidence, PremiumVisualQualityGate, VisualQualityDisposition
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDirector, VisualConceptSignals


class PremiumVisualQualityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = PremiumVisualQualityGate()
        self.director = VisualConceptDirector()

    def evidence(self, **kwargs):
        data = dict(
            family=EditorialSceneFamily.RESULT_STATEMENT,
            concept=VisualConceptArchetype.SCORE_MONUMENT,
            primary_visual_anchor_count=1,
            unexplained_graphic_panel_count=0,
            decorative_pulse_count_outside_brand=0,
            full_pitch_visible=False,
            pitch_is_information=False,
            verified_stronger_moment_available=False,
            score_monument_used=True,
            brand_width_ratio=0.22,
            brand_height_ratio=0.07,
            dense_copy_used=False,
            readable_text_over_protected_face=False,
            exact_identity_placeholder_used=False,
            photographic_context_used=False,
            context_is_story_evidence=False,
        )
        data.update(kwargs)
        return PremiumVisualEvidence(**data)

    def concept(self):
        return self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(verified_subject_asset=True, verified_action_photo=True, decisive_moment_known=True, exact_club_assets=True),
        )

    def test_verified_match_photo_does_not_change_original_result_quality_concept(self):
        concept = self.concept()
        self.assertEqual(concept.archetype, VisualConceptArchetype.SCORE_MONUMENT)
        decision = self.gate.evaluate(self.evidence(), concept_decision=concept)
        self.assertEqual(decision.disposition, VisualQualityDisposition.HUMAN_REVIEW_READY)
        self.assertEqual(decision.blockers, ())
        self.assertTrue(decision.human_visual_review_required)
        self.assertFalse(decision.publication_ready)

    def test_duplicate_pulse_and_unexplained_portal_are_hard_blockers(self):
        decision = self.gate.evaluate(self.evidence(unexplained_graphic_panel_count=1, decorative_pulse_count_outside_brand=1))
        self.assertEqual(decision.disposition, VisualQualityDisposition.BLOCKED)
        joined = ' '.join(decision.blockers)
        self.assertIn('panel/card/portal', joined)
        self.assertIn('pulse geometry', joined)

    def test_score_monument_is_blocked_only_if_external_quality_evidence_proves_stronger_moment(self):
        decision = self.gate.evaluate(self.evidence(verified_stronger_moment_available=True))
        self.assertEqual(decision.disposition, VisualQualityDisposition.BLOCKED)
        self.assertTrue(any('stronger verified' in item for item in decision.blockers))

    def test_unnecessary_full_pitch_and_oversized_brand_are_blocked(self):
        decision = self.gate.evaluate(self.evidence(full_pitch_visible=True, pitch_is_information=False, brand_width_ratio=0.42, brand_height_ratio=0.15))
        self.assertEqual(decision.disposition, VisualQualityDisposition.BLOCKED)
        joined = ' '.join(decision.blockers)
        self.assertIn('full pitch', joined)
        self.assertIn('too wide', joined)
        self.assertIn('too tall', joined)

    def test_dense_copy_face_overlap_and_identity_placeholder_are_blocked(self):
        decision = self.gate.evaluate(self.evidence(dense_copy_used=True, readable_text_over_protected_face=True, exact_identity_placeholder_used=True))
        self.assertEqual(decision.disposition, VisualQualityDisposition.BLOCKED)
        self.assertGreaterEqual(len(decision.blockers), 3)

    def test_atmosphere_only_photo_is_warning_not_fake_event_evidence(self):
        decision = self.gate.evaluate(self.evidence(photographic_context_used=True, context_is_story_evidence=False))
        self.assertEqual(decision.disposition, VisualQualityDisposition.HUMAN_REVIEW_READY)
        self.assertTrue(any('atmosphere only' in item for item in decision.warnings))


if __name__ == '__main__':
    unittest.main()

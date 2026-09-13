import unittest

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_candidate_readiness import CandidateReadiness, VisualCandidateReadinessGate
from engine.intelligence.verified_subject_compositor import VerifiedSubjectCompositionReceipt


class VisualCandidateReadinessGateTests(unittest.TestCase):
    def scene(self, event):
        decision = StoryToVisualOrchestrator().decide(VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Player",
            fact_phrase="verified update",
            story_core="verified candidate readiness story",
            tone=HeadlineTone.NEUTRAL,
            confidence=1.0,
        ))
        return decision.sports_editorial_scene

    @staticmethod
    def receipt(**overrides):
        values = dict(
            output_path="candidate.png",
            output_sha256="a" * 64,
            base_sha256="b" * 64,
            subject_asset_id="verified-player-visual",
            subject_sha256="c" * 64,
            source_reference="trusted:source:image",
            entity_name="Verified Player",
            identity_confidence=0.98,
            mode="transparent_cutout",
            identity_verified=True,
            generator_used=False,
            subject_placeholder_used=False,
            publication_ready=False,
        )
        values.update(overrides)
        return VerifiedSubjectCompositionReceipt(**values)

    def test_transfer_placeholder_is_allowed_only_as_composition_study(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        decision = VisualCandidateReadinessGate().evaluate(scene, composition_study=True, subject_placeholder_used=True)
        self.assertEqual(decision.status, CandidateReadiness.COMPOSITION_STUDY_ONLY)
        self.assertFalse(decision.real_candidate_allowed)
        self.assertTrue(decision.identity_subject_required)

    def test_transfer_real_candidate_requires_verified_subject_receipt(self):
        scene = self.scene(EditorialEvent.TRANSFER_CONFIRMED)
        missing = VisualCandidateReadinessGate().evaluate(scene, composition_study=False)
        self.assertFalse(missing.real_candidate_allowed)
        self.assertIn("requires verified subject", " ".join(missing.blockers))
        ready = VisualCandidateReadinessGate().evaluate(scene, composition_study=False, verified_subject=self.receipt())
        self.assertEqual(ready.status, CandidateReadiness.REAL_CANDIDATE_READY)
        self.assertTrue(ready.real_candidate_allowed)
        self.assertTrue(ready.verified_subject_provenance_accepted)

    def test_placeholder_can_never_enter_real_candidate(self):
        scene = self.scene(EditorialEvent.INJURY)
        decision = VisualCandidateReadinessGate().evaluate(scene, composition_study=False, subject_placeholder_used=True, verified_subject=self.receipt())
        self.assertFalse(decision.real_candidate_allowed)
        self.assertIn("subject placeholder is forbidden in a real news candidate", decision.blockers)

    def test_generator_owned_subject_receipt_is_rejected(self):
        scene = self.scene(EditorialEvent.STATEMENT)
        decision = VisualCandidateReadinessGate().evaluate(scene, composition_study=False, verified_subject=self.receipt(generator_used=True))
        self.assertFalse(decision.real_candidate_allowed)
        self.assertIn("verified subject pixels may not be generator-owned", decision.blockers)

    def test_result_does_not_require_person_subject(self):
        scene = self.scene(EditorialEvent.RESULT)
        decision = VisualCandidateReadinessGate().evaluate(scene, composition_study=False)
        self.assertTrue(decision.real_candidate_allowed)
        self.assertFalse(decision.identity_subject_required)


if __name__ == "__main__":
    unittest.main()

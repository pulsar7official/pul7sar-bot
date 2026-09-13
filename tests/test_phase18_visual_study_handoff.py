import unittest
from dataclasses import replace

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_study_handoff import VisualStudyHandoffCompiler


class VisualStudyHandoffCompilerTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.compiler = VisualStudyHandoffCompiler()

    def decision(self, event):
        return self.orchestrator.decide(VerifiedEditorialStory(
            event=event,
            sport="football",
            subject="Verified Subject",
            fact_phrase="verified fact",
            story_core="verified story core",
            tone=HeadlineTone.NEUTRAL,
            confidence=0.99,
        ))

    def test_transfer_handoff_binds_benchmark_brand_guide_and_reference(self):
        handoff = self.compiler.compile(
            self.decision(EditorialEvent.TRANSFER_CONFIRMED),
            headline="PLAYER JOINS CLUB",
        )
        self.assertEqual(handoff.scene_family, "transfer_signature")
        self.assertEqual(handoff.benchmark_id, "transfer-signature-v1")
        self.assertEqual(handoff.brand_identity_id, "pul7sar-hybrid-adaptive-v1")
        self.assertEqual(handoff.visual_reference_id, "pul7sar-chelsea-reference-7of10-v1")
        self.assertEqual(handoff.brand_guide_evidence_id, "pul7sar-brand-guide-approved-phase18-v1")
        self.assertFalse(handoff.exact_brand_geometry_ready)
        self.assertFalse(handoff.publication_ready)
        self.assertTrue(handoff.human_review_allowed)
        self.assertIn("dense infographic statistics", handoff.benchmark_must_avoid)
        self.assertIn("headline copy that is too long or visually crowded", handoff.visual_reference_improve_or_avoid)
        self.assertFalse(handoff.metadata["legacy_repo_logo_allowed"])
        self.compiler.verify(handoff)

    def test_dense_copy_cannot_produce_human_review_handoff(self):
        with self.assertRaisesRegex(ValueError, "VISUAL_STUDY_NOT_READY"):
            self.compiler.compile(
                self.decision(EditorialEvent.TRANSFER_CONFIRMED),
                headline="ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE",
            )

    def test_tactical_structural_benchmark_does_not_create_human_art_handoff(self):
        with self.assertRaisesRegex(ValueError, "VISUAL_STUDY_NOT_READY"):
            self.compiler.compile(
                self.decision(EditorialEvent.TACTICS),
                headline="4-3-3 BUILD-UP",
            )

    def test_checksum_tampering_is_rejected(self):
        handoff = self.compiler.compile(
            self.decision(EditorialEvent.TRANSFER_CONFIRMED),
            headline="PLAYER JOINS CLUB",
        )
        forged = replace(handoff, headline="FORGED COPY")
        with self.assertRaisesRegex(ValueError, "CHECKSUM_MISMATCH"):
            self.compiler.verify(forged)

    def test_visual_study_may_never_claim_publication_ready(self):
        handoff = self.compiler.compile(
            self.decision(EditorialEvent.RESULT),
            headline="TEAM WINS 2-1",
        )
        forged = replace(handoff, publication_ready=True)
        with self.assertRaises(ValueError):
            self.compiler.verify(forged)


if __name__ == "__main__":
    unittest.main()

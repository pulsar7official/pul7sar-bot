import unittest

from engine.intelligence.brand_master_geometry import BrandMasterGeometryState, ExactBrandGeometryAsset
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_review_readiness import VisualReviewReadiness, VisualReviewReadinessGate


class VisualReviewReadinessGateTests(unittest.TestCase):
    def setUp(self):
        self.orchestrator = StoryToVisualOrchestrator()
        self.gate = VisualReviewReadinessGate()

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

    @staticmethod
    def geometry():
        return BrandMasterGeometryState(
            ExactBrandGeometryAsset("wordmark", "assets/brand/wordmark.png", "a" * 64, "approved"),
            ExactBrandGeometryAsset("pulse-seven", "assets/brand/pulse-seven.png", "b" * 64, "approved"),
        )

    def test_transfer_can_reach_human_review_before_publication_geometry_is_registered(self):
        result = self.gate.evaluate(
            self.decision(EditorialEvent.TRANSFER_CONFIRMED),
            headline="PLAYER JOINS CLUB",
        )
        self.assertEqual(result.status, VisualReviewReadiness.PUBLICATION_GEOMETRY_BLOCKED)
        self.assertTrue(result.human_review_allowed)
        self.assertFalse(result.publication_geometry_ready)
        self.assertEqual(result.benchmark_id, "transfer-signature-v1")

    def test_registered_two_part_geometry_reaches_human_visual_ready(self):
        result = self.gate.evaluate(
            self.decision(EditorialEvent.TRANSFER_CONFIRMED),
            headline="PLAYER JOINS CLUB",
            brand_geometry=self.geometry(),
        )
        self.assertEqual(result.status, VisualReviewReadiness.HUMAN_VISUAL_READY)
        self.assertTrue(result.human_review_allowed)
        self.assertTrue(result.publication_geometry_ready)

    def test_dense_transfer_copy_is_blocked_before_human_review(self):
        result = self.gate.evaluate(
            self.decision(EditorialEvent.TRANSFER_CONFIRMED),
            headline="ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE",
        )
        self.assertEqual(result.status, VisualReviewReadiness.BLOCKED)
        self.assertFalse(result.human_review_allowed)
        self.assertIn("headline exceeds scene word budget", result.failures)

    def test_result_supporting_paragraph_is_blocked_before_review(self):
        result = self.gate.evaluate(
            self.decision(EditorialEvent.RESULT),
            headline="TEAM WINS 2-1",
            supporting_copy="This explanatory paragraph should not be on a result visual",
        )
        self.assertEqual(result.status, VisualReviewReadiness.BLOCKED)
        self.assertIn("supporting copy is forbidden for this scene family", result.failures)

    def test_tactical_benchmark_is_structural_and_does_not_demand_human_art_review(self):
        result = self.gate.evaluate(
            self.decision(EditorialEvent.TACTICS),
            headline="4-3-3 BUILD-UP",
        )
        self.assertEqual(result.status, VisualReviewReadiness.STRUCTURAL_READY)
        self.assertFalse(result.human_review_allowed)
        self.assertEqual(result.benchmark_id, "tactical-intelligence-v1")


if __name__ == "__main__":
    unittest.main()

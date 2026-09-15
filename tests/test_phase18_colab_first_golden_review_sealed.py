import unittest
from pathlib import Path


class ColabFirstGoldenReviewSealedTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("tools/phase18_colab_first_golden_review_sealed.py")
        self.text = self.path.read_text(encoding="utf-8")

    def test_staging_precedes_integrity_seal(self):
        staging = self.text.index("phase18_colab_first_golden_review.py")
        sealing = self.text.index("phase18_seal_first_golden_review_packet.py")
        self.assertLess(staging, sealing)
        self.assertIn("FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW", self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_PACKET_SEALED_AND_VERIFIED", self.text)

    def test_wrapper_remains_candidate_one_zero_cost_and_fail_closed(self):
        self.assertIn('EXPECTED_BRANCH = "phase18/story-intelligence"', self.text)
        self.assertIn('staged.get("candidate") != 1', self.text)
        self.assertIn('staged.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('seal.get("candidate") != 1', self.text)
        self.assertIn('seal.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('"seeds_2_to_4_authorized": False', self.text)
        self.assertIn('"publication_ready": False', self.text)
        self.assertIn('"golden_quality_approved": False', self.text)
        self.assertIn('"human_visual_review_approved": False', self.text)

    def test_wrapper_does_not_auto_decide_or_apply_golden_review(self):
        self.assertNotIn("phase18_record_hybrid_human_review.py", self.text)
        self.assertNotIn("phase18_apply_human_approved_golden_review.py", self.text)
        self.assertNotIn("phase18_review_locked_golden.py", self.text)
        self.assertIn("explicit human review", self.text)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path


class Phase18ColabFirstGoldenReviewTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("tools/phase18_colab_first_golden_review.py")
        self.text = self.path.read_text(encoding="utf-8")

    def test_tool_is_phase18_candidate1_only(self):
        self.assertIn('EXPECTED_BRANCH = "phase18/story-intelligence"', self.text)
        self.assertIn('if first_png.get("candidate") != 1', self.text)
        self.assertIn('"--candidate",\n            "1"', self.text)
        self.assertIn('"seeds_2_to_4_authorized": False', self.text)
        self.assertNotIn('"--candidate", str(', self.text)

    def test_runs_current_trusted_path_in_strict_order(self):
        first_png = self.text.index("phase18_first_png.py")
        handoff = self.text.index("phase18_build_first_png_hybrid_handoff.py")
        continuation = self.text.index("phase18_continue_hybrid_from_first_png.py")
        review_bundle = self.text.index("phase18_prepare_hybrid_human_review.py")
        review_template = self.text.index("phase18_build_hybrid_human_review_template.py")
        self.assertLess(first_png, handoff)
        self.assertLess(handoff, continuation)
        self.assertLess(continuation, review_bundle)
        self.assertLess(review_bundle, review_template)

    def test_requires_semantic_approval_before_human_review_staging(self):
        self.assertIn('continuation.get("semantic_layer_gate_approved") is not True', self.text)
        self.assertIn('continuation.get("hybrid_semantic_review_approved") is not True', self.text)
        self.assertIn('continuation.get("status") != "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY"', self.text)

    def test_never_records_human_or_golden_approval_automatically(self):
        self.assertIn('template.get("decision") is not None', self.text)
        self.assertIn('"human_visual_review_approved": False', self.text)
        self.assertIn('"golden_quality_approved": False', self.text)
        self.assertIn('"publication_ready": False', self.text)
        self.assertNotIn("phase18_record_hybrid_human_review.py", self.text)
        self.assertNotIn("phase18_apply_human_approved_golden_review.py", self.text)

    def test_review_artifacts_are_sha_bound_and_inside_repository(self):
        self.assertIn('"review_base_png_sha256": _sha256(review_base)', self.text)
        self.assertIn('"review_hybrid_png_sha256": _sha256(review_hybrid)', self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_PATH_ESCAPES_REPOSITORY", self.text)
        self.assertIn('value.read_bytes()[:8] != b"\\x89PNG\\r\\n\\x1a\\n"', self.text)

    def test_preserves_zero_cost_and_publication_gates(self):
        self.assertIn('first_png.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('"cost_mode": "$0-local"', self.text)
        self.assertIn('_require_false(first_png, "publication_ready"', self.text)
        self.assertIn('_require_false(template, "golden_quality_approved", "publication_ready"', self.text)


if __name__ == "__main__":
    unittest.main()

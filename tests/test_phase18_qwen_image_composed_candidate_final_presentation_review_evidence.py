from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    EVIDENCE_SCHEMA,
    _review,
)


class TestPhase18QwenImageComposedCandidateFinalPresentationReviewEvidence(unittest.TestCase):
    def _request(self):
        return {
            "story_snapshot_sha256": "a" * 64,
            "receipt_sha256": "b" * 64,
            "composed_candidate_png": {"sha256": "c" * 64},
        }

    def _evidence(self, checks, *, decision="approve"):
        return {
            "schema": EVIDENCE_SCHEMA,
            "story_snapshot_sha256": "a" * 64,
            "composed_candidate_png_sha256": "c" * 64,
            "review_request_receipt_sha256": "b" * 64,
            "review_method": "independent_manual_final_presentation_review",
            "reviewer_id": "reviewer-1",
            "review_notes": "Checked exact brand geometry, typography, safe areas, and final surface.",
            "checks": {name: True for name in checks},
            "decision": decision,
        }

    def test_approve_requires_all_checks_and_returns_true(self):
        checks = ("brand_master_geometry_matches", "typography_copy_is_exact_legible_and_not_pseudo_text")
        results, approved = _review(self._evidence(checks), self._request(), checks)
        self.assertTrue(approved)
        self.assertEqual(results, {name: True for name in checks})

    def test_approve_with_failed_check_is_rejected(self):
        checks = ("brand_master_geometry_matches", "typography_copy_is_exact_legible_and_not_pseudo_text")
        evidence = self._evidence(checks)
        evidence["checks"][checks[1]] = False
        with self.assertRaisesRegex(ValueError, "APPROVAL_WITH_FAILED_CHECK"):
            _review(evidence, self._request(), checks)

    def test_reject_without_failed_check_is_rejected(self):
        checks = ("brand_master_geometry_matches",)
        with self.assertRaisesRegex(ValueError, "REJECTION_WITHOUT_FAILED_CHECK"):
            _review(self._evidence(checks, decision="reject"), self._request(), checks)

    def test_review_is_bound_to_exact_candidate(self):
        checks = ("brand_master_geometry_matches",)
        evidence = self._evidence(checks)
        evidence["composed_candidate_png_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "CANDIDATE_DRIFT"):
            _review(evidence, self._request(), checks)

    def test_review_is_bound_to_exact_request_receipt(self):
        checks = ("brand_master_geometry_matches",)
        evidence = self._evidence(checks)
        evidence["review_request_receipt_sha256"] = "e" * 64
        with self.assertRaisesRegex(ValueError, "REQUEST_RECEIPT_DRIFT"):
            _review(evidence, self._request(), checks)

    def test_check_set_must_match_request_exactly(self):
        checks = ("brand_master_geometry_matches", "typography_font_policy_is_resolved")
        evidence = self._evidence(checks)
        evidence["checks"].pop("typography_font_policy_is_resolved")
        with self.assertRaisesRegex(ValueError, "CHECK_SET_INVALID"):
            _review(evidence, self._request(), checks)


if __name__ == "__main__":
    unittest.main()

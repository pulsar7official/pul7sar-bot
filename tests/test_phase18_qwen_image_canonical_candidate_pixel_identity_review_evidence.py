from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence import (
    build_pixel_identity_review_evidence,
    verify_pixel_identity_review_evidence,
)

STORY_SHA = "a" * 64


def _write_json(path: Path, payload: dict) -> bytes:
    raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


class CS267PixelIdentityReviewEvidenceTests(unittest.TestCase):
    def _fixture(self, root: Path, *, all_checks: bool = True):
        candidate = root / "candidate.png"
        candidate_raw = b"synthetic-candidate-bytes"
        candidate.write_bytes(candidate_raw)

        identity_path = root / "identity.json"
        identity_raw = _write_json(identity_path, {"identity": "fixture"})

        cs266 = root / "cs266.json"
        cs266.write_text("{}", encoding="utf-8")
        target = {
            "entity_id": "player.test",
            "display_name": "Test Player",
            "kind": "player",
            "identity_source_refs": ["source:official-profile", "source:club-profile"],
        }
        request = {
            "schema": "pul7sar-phase18-qwen-image-canonical-candidate-pixel-identity-review-request-v1",
            "receipt_sha256": "c" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": {
                "repository_relative_path": "candidate.png",
                "sha256": hashlib.sha256(candidate_raw).hexdigest(),
                "byte_size": len(candidate_raw),
            },
            "identity_evidence": {
                "repository_relative_path": "identity.json",
                "sha256": hashlib.sha256(identity_raw).hexdigest(),
                "byte_size": len(identity_raw),
            },
            "review_targets": [target],
            "pixel_identity_review_required": True,
            "pixel_identity_review_request_created": True,
            "pixel_identity_review_executed": False,
            "identity_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        checks = {
            "candidate_subject_matches_canonical_entity": all_checks,
            "no_identity_substitution": True,
            "no_ambiguous_or_conflicting_identity": True,
            "source_backed_reference_evidence_used": True,
        }
        review_path = root / "external-review.json"
        _write_json(review_path, {
            "schema": "pul7sar-phase18-pixel-identity-external-review-v1",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png_sha256": hashlib.sha256(candidate_raw).hexdigest(),
            "review_method": "manual_source_comparison",
            "reviewer_id": "reviewer.fixture",
            "review_targets": [target],
            "checks": checks,
            "review_notes": "Compared the visible subject with both bound source references.",
            "source_refs_compared": ["source:official-profile", "source:club-profile"],
        })
        return cs266, request, review_path, candidate

    def _build(self, root: Path, *, all_checks: bool = True):
        cs266, request, review_path, candidate = self._fixture(root, all_checks=all_checks)
        target = (
            "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence."
            "verify_pixel_identity_review_request"
        )
        with patch(target, return_value=request):
            result = build_pixel_identity_review_evidence(
                cs266, review_path, root / "out", repo_root=root
            )
            receipt = verify_pixel_identity_review_evidence(result.receipt_path, repo_root=root)
        return result, receipt, request, review_path, candidate

    def test_all_required_attestations_can_admit_identity_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, receipt, _, _, _ = self._build(root)
            self.assertTrue(result.identity_approved)
            self.assertTrue(receipt["pixel_identity_review_executed"])
            self.assertTrue(receipt["identity_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["publication_ready"])

    def test_single_failed_check_rejects_identity_and_cannot_advance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, receipt, _, _, _ = self._build(root, all_checks=False)
            self.assertFalse(result.identity_approved)
            self.assertEqual(receipt["status"], "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_REJECTED")
            self.assertFalse(receipt["identity_approved"])
            self.assertFalse(receipt["publication_ready"])

    def test_candidate_digest_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs266, request, review_path, _ = self._fixture(root)
            payload = json.loads(review_path.read_text(encoding="utf-8"))
            payload["candidate_png_sha256"] = "f" * 64
            _write_json(review_path, payload)
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence."
                "verify_pixel_identity_review_request"
            )
            with patch(target, return_value=request):
                with self.assertRaisesRegex(ValueError, "CANDIDATE_DRIFT"):
                    build_pixel_identity_review_evidence(cs266, review_path, root / "out", repo_root=root)

    def test_external_review_byte_drift_invalidates_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, request, review_path, _ = self._build(root)
            review_path.write_text('{"tampered":true}', encoding="utf-8")
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence."
                "verify_pixel_identity_review_request"
            )
            with patch(target, return_value=request):
                with self.assertRaisesRegex(ValueError, "EXTERNAL_INVALID_BYTE_DRIFT"):
                    verify_pixel_identity_review_evidence(result.receipt_path, repo_root=root)

    def test_cs266_byte_drift_invalidates_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, request, _, _ = self._build(root)
            cs266 = root / "cs266.json"
            cs266.write_text('{"tampered":true}', encoding="utf-8")
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence."
                "verify_pixel_identity_review_request"
            )
            with patch(target, return_value=request):
                with self.assertRaisesRegex(ValueError, "CS266_INVALID_BYTE_DRIFT"):
                    verify_pixel_identity_review_evidence(result.receipt_path, repo_root=root)

    def test_missing_reviewer_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs266, request, review_path, _ = self._fixture(root)
            payload = json.loads(review_path.read_text(encoding="utf-8"))
            payload["reviewer_id"] = ""
            _write_json(review_path, payload)
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence."
                "verify_pixel_identity_review_request"
            )
            with patch(target, return_value=request):
                with self.assertRaisesRegex(ValueError, "REVIEWER_MISSING"):
                    build_pixel_identity_review_evidence(cs266, review_path, root / "out", repo_root=root)


if __name__ == "__main__":
    unittest.main()

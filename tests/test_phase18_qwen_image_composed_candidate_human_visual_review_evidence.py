from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import SCHEMA as CS277_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    EVIDENCE_SCHEMA,
    build_composed_candidate_human_visual_review_evidence,
    verify_composed_candidate_human_visual_review_evidence,
)

MODULE = "engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence"
STORY = "1" * 64
CHECKS = (
    "story_and_editorial_fidelity",
    "factual_and_result_integrity",
    "entity_identity_continuity_when_applicable",
    "sentiment_neutrality_and_loser_respect",
    "composition_and_visual_hierarchy",
    "photorealism_and_cinematic_realism",
    "sport_geometry_and_physical_coherence",
    "artifact_and_pseudo_text_absence",
    "exact_brand_logo_and_typography_surface",
    "overall_golden_visual_acceptability",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HumanVisualReviewEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.request_path = self.root / "cs277.json"
        self.request_path.write_text("{}\n", encoding="utf-8")
        runs = self.root / "runs"
        runs.mkdir()
        self.png = runs / "composed_candidate.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-control-plane-fixture")
        self.evidence_path = self.root / "human-review.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _request(self) -> dict:
        return {
            "schema": CS277_SCHEMA,
            "receipt_sha256": "2" * 64,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": {
                "repository_relative_path": "runs/composed_candidate.png",
                "sha256": _sha(self.png),
                "byte_size": self.png.stat().st_size,
                "width": 1024,
                "height": 1024,
            },
            "golden_quality_selector_executed": True,
            "golden_quality_approved": True,
            "required_review_checks": list(CHECKS),
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _write_evidence(self, request: dict, *, decision: str = "approve", failed: str | None = None) -> None:
        results = {name: True for name in CHECKS}
        if failed:
            results[failed] = False
        evidence = {
            "schema": EVIDENCE_SCHEMA,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png_sha256": request["composed_candidate_png"]["sha256"],
            "review_request_receipt_sha256": request["receipt_sha256"],
            "review_method": "independent_manual_human_visual_review",
            "reviewer_id": "human-reviewer-001",
            "review_notes": "Independent review of the exact bound composed PNG.",
            "checks": results,
            "decision": decision,
        }
        self.evidence_path.write_text(json.dumps(evidence, separators=(",", ":")) + "\n", encoding="utf-8")

    def _build(self, request: dict, name: str = "out") -> Path:
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            return build_composed_candidate_human_visual_review_evidence(
                self.request_path, self.evidence_path, self.root / name, repo_root=self.root
            )

    def test_approved_evidence_records_human_approval_without_final_authority(self):
        request = self._request()
        self._write_evidence(request)
        path = self._build(request)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["human_visual_review_executed"])
        self.assertTrue(receipt["human_visual_review_evidence_admitted"])
        self.assertTrue(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            verified = verify_composed_candidate_human_visual_review_evidence(path, repo_root=self.root)
        self.assertEqual(verified["review_decision"], "approve")

    def test_rejected_evidence_is_admitted_but_does_not_approve(self):
        request = self._request()
        self._write_evidence(request, decision="reject", failed="photorealism_and_cinematic_realism")
        path = self._build(request)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["human_visual_review_executed"])
        self.assertTrue(receipt["human_visual_review_evidence_admitted"])
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertEqual(receipt["review_decision"], "reject")

    def test_approval_with_failed_check_is_rejected(self):
        request = self._request()
        self._write_evidence(request, decision="approve", failed="factual_and_result_integrity")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "APPROVAL_WITH_FAILED_CHECK"):
                build_composed_candidate_human_visual_review_evidence(
                    self.request_path, self.evidence_path, self.root / "blocked", repo_root=self.root
                )

    def test_missing_check_is_rejected(self):
        request = self._request()
        self._write_evidence(request)
        evidence = json.loads(self.evidence_path.read_text(encoding="utf-8"))
        evidence["checks"].pop(CHECKS[0])
        self.evidence_path.write_text(json.dumps(evidence) + "\n", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "CHECK_SET_INVALID"):
                build_composed_candidate_human_visual_review_evidence(
                    self.request_path, self.evidence_path, self.root / "blocked", repo_root=self.root
                )

    def test_composed_png_byte_tamper_invalidates_admission(self):
        request = self._request()
        self._write_evidence(request)
        path = self._build(request)
        self.png.write_bytes(self.png.read_bytes() + b"tamper")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_human_visual_review_evidence(path, repo_root=self.root)

    def test_external_review_byte_tamper_invalidates_admission(self):
        request = self._request()
        self._write_evidence(request)
        path = self._build(request)
        self.evidence_path.write_text(self.evidence_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_human_visual_review_evidence(path, repo_root=self.root)

    def test_receipt_cannot_forge_genuine_golden_or_publication_even_when_rehashed(self):
        request = self._request()
        self._write_evidence(request)
        path = self._build(request)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["genuine_golden_png_created"] = True
        receipt["publication_ready"] = True
        receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = sha256_json(receipt)
        path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                verify_composed_candidate_human_visual_review_evidence(path, repo_root=self.root)

    def test_existing_output_is_rejected(self):
        request = self._request()
        self._write_evidence(request)
        output = self.root / "taken"
        output.mkdir()
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=request):
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                build_composed_candidate_human_visual_review_evidence(
                    self.request_path, self.evidence_path, output, repo_root=self.root
                )


if __name__ == "__main__":
    unittest.main()

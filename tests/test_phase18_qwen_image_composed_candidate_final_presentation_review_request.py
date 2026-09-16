from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import SCHEMA as CS278_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    build_composed_candidate_final_presentation_review_request,
    verify_composed_candidate_final_presentation_review_request,
)

MODULE = "engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request"
STORY = "1" * 64
POLICY_SOURCES = (
    "engine/intelligence/brand_approval_evidence.py",
    "engine/intelligence/brand_asset_approval.py",
    "engine/intelligence/brand_master_geometry.py",
    "engine/fonts/resolver.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FinalPresentationReviewRequestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cs278_path = self.root / "cs278.json"
        self.cs278_path.write_text("{}\n", encoding="utf-8")
        runs = self.root / "runs"
        runs.mkdir()
        self.png = runs / "composed_candidate.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-control-plane-fixture")
        for rel in POLICY_SOURCES:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# synthetic policy fixture: {rel}\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _source(self, *, human_approved: bool = True) -> dict:
        return {
            "schema": CS278_SCHEMA,
            "receipt_sha256": "2" * 64,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": {
                "repository_relative_path": "runs/composed_candidate.png",
                "sha256": _sha(self.png),
                "byte_size": self.png.stat().st_size,
                "width": 1024,
                "height": 1024,
            },
            "generation_context": {
                "request_id": "qwen-cs262-" + "3" * 64,
                "request_id_source": "exact_cs262_receipt_sha256",
                "seed": 424242,
                "seed_source": "reverified_cs263_to_cs262_inference_receipt",
                "cs262_receipt_sha256": "3" * 64,
            },
            "weighted_score": 9.0,
            "quality_tier": "elite",
            "golden_quality_selector_executed": True,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": human_approved,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _build(self, source: dict, name: str = "out") -> Path:
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            return build_composed_candidate_final_presentation_review_request(
                self.cs278_path, self.root / name, repo_root=self.root
            )

    def test_human_approved_candidate_creates_request_without_final_approval(self):
        source = self._source()
        path = self._build(source)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["final_presentation_review_requested"])
        self.assertFalse(receipt["final_presentation_review_executed"])
        self.assertFalse(receipt["final_presentation_review_approved"])
        self.assertFalse(receipt["exact_brand_integrity_approved"])
        self.assertFalse(receipt["typography_integrity_approved"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(set(receipt["presentation_policy_sources"]), set(POLICY_SOURCES))
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            verified = verify_composed_candidate_final_presentation_review_request(path, repo_root=self.root)
        self.assertEqual(verified["quality_tier"], "elite")

    def test_human_rejection_cannot_reach_presentation_review(self):
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._source(human_approved=False)):
            with self.assertRaisesRegex(ValueError, "REQUIRED_GATE_MISSING:human_visual_review_approved"):
                build_composed_candidate_final_presentation_review_request(
                    self.cs278_path, self.root / "blocked", repo_root=self.root
                )

    def test_composed_png_byte_tamper_invalidates_request(self):
        source = self._source()
        path = self._build(source)
        self.png.write_bytes(self.png.read_bytes() + b"tamper")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_final_presentation_review_request(path, repo_root=self.root)

    def test_policy_source_byte_tamper_invalidates_request(self):
        source = self._source()
        path = self._build(source)
        policy = self.root / POLICY_SOURCES[0]
        policy.write_text(policy.read_text(encoding="utf-8") + "# tamper\n", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_final_presentation_review_request(path, repo_root=self.root)

    def test_cs278_receipt_byte_tamper_invalidates_request(self):
        source = self._source()
        path = self._build(source)
        self.cs278_path.write_text('{"tampered":true}\n', encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_final_presentation_review_request(path, repo_root=self.root)

    def test_request_cannot_forge_presentation_or_publication_authority(self):
        source = self._source()
        path = self._build(source)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["exact_brand_integrity_approved"] = True
        receipt["typography_integrity_approved"] = True
        receipt["final_presentation_review_approved"] = True
        receipt["genuine_golden_png_created"] = True
        receipt["publication_ready"] = True
        receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = sha256_json(receipt)
        path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=source):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                verify_composed_candidate_final_presentation_review_request(path, repo_root=self.root)

    def test_existing_output_is_rejected(self):
        output = self.root / "taken"
        output.mkdir()
        with patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._source()):
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                build_composed_candidate_final_presentation_review_request(
                    self.cs278_path, output, repo_root=self.root
                )


if __name__ == "__main__":
    unittest.main()

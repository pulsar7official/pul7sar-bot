from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import SCHEMA as CS276_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    build_composed_candidate_human_visual_review_request,
    verify_composed_candidate_human_visual_review_request,
)

MODULE = "engine.intelligence.qwen_image_composed_candidate_human_visual_review_request"
STORY = "1" * 64


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HumanVisualReviewRequestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cs276_path = self.root / "cs276.json"
        self.cs276_path.write_text("{}\n", encoding="utf-8")
        runs = self.root / "runs"
        runs.mkdir()
        self.png = runs / "composed_candidate.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-control-plane-fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def _source(self, *, approved: bool = True, tier: str = "elite") -> dict:
        return {
            "schema": CS276_SCHEMA,
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
            "weighted_score": 9.0 if approved else 7.0,
            "quality_tier": tier,
            "golden_quality_selector_executed": True,
            "golden_quality_approved": approved,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": True,
            "visual_quality_review_executed": True,
            "visual_quality_evidence_admitted": True,
            "human_visual_review_approved": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _build(self, source: dict, name: str = "out") -> Path:
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=source):
            return build_composed_candidate_human_visual_review_request(
                self.cs276_path, self.root / name, repo_root=self.root
            )

    def test_golden_candidate_creates_request_without_human_approval(self):
        source = self._source()
        path = self._build(source)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["human_visual_review_requested"])
        self.assertFalse(receipt["human_visual_review_executed"])
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=source):
            verified = verify_composed_candidate_human_visual_review_request(path, repo_root=self.root)
        self.assertEqual(verified["quality_tier"], "elite")

    def test_below_golden_candidate_is_rejected(self):
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=self._source(approved=False, tier="below_golden")):
            with self.assertRaisesRegex(ValueError, "BELOW_GOLDEN"):
                build_composed_candidate_human_visual_review_request(
                    self.cs276_path, self.root / "blocked", repo_root=self.root
                )

    def test_composed_png_byte_tamper_invalidates_request(self):
        source = self._source()
        path = self._build(source)
        self.png.write_bytes(self.png.read_bytes() + b"tamper")
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=source):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_human_visual_review_request(path, repo_root=self.root)

    def test_cs276_receipt_byte_tamper_invalidates_request(self):
        source = self._source()
        path = self._build(source)
        self.cs276_path.write_text('{"tampered":true}\n', encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=source):
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_human_visual_review_request(path, repo_root=self.root)

    def test_request_cannot_forge_human_approval_even_with_rehashed_digest(self):
        source = self._source()
        path = self._build(source)
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["human_visual_review_executed"] = True
        receipt["human_visual_review_approved"] = True
        receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = sha256_json(receipt)
        path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=source):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                verify_composed_candidate_human_visual_review_request(path, repo_root=self.root)

    def test_existing_output_is_rejected(self):
        output = self.root / "taken"
        output.mkdir()
        with patch(f"{MODULE}.verify_composed_candidate_golden_quality_adjudication", return_value=self._source()):
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                build_composed_candidate_human_visual_review_request(
                    self.cs276_path, output, repo_root=self.root
                )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    build_composed_candidate_visual_quality_review_request,
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json


class VisualQualityReviewRequestTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict]:
        (root / "engine/intelligence").mkdir(parents=True)
        (root / "engine/intelligence/golden_visual_quality.py").write_text(
            "# bound quality contract fixture\n", encoding="utf-8"
        )
        (root / "artifacts").mkdir()
        candidate = root / "artifacts/composed_candidate.png"
        candidate.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        import hashlib
        composed = {
            "repository_relative_path": "artifacts/composed_candidate.png",
            "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "byte_size": len(candidate.read_bytes()),
            "width": 1080,
            "height": 1350,
        }
        cs273 = root / "artifacts/cs273.json"
        cs273.write_text("{}\n", encoding="utf-8")
        source = {
            "schema": CS273_SCHEMA,
            "receipt_sha256": "b" * 64,
            "story_snapshot_sha256": "a" * 64,
            "composed_candidate_png": composed,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        return cs273, source

    def test_builds_byte_bound_request_without_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            out = root / "review"
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                receipt_path = build_composed_candidate_visual_quality_review_request(
                    cs273, out, repo_root=root
                )
                receipt = verify_composed_candidate_visual_quality_review_request(
                    receipt_path, repo_root=root
                )
            self.assertTrue(receipt["visual_quality_review_requested"])
            self.assertFalse(receipt["visual_quality_review_executed"])
            self.assertFalse(receipt["visual_quality_review_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["publication_ready"])
            self.assertIn("score_fields", receipt["golden_visual_quality_contract"])
            self.assertIn("blocker_fields", receipt["golden_visual_quality_contract"])

    def test_rejects_candidate_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                receipt_path = build_composed_candidate_visual_quality_review_request(
                    cs273, root / "review", repo_root=root
                )
                (root / "artifacts/composed_candidate.png").write_bytes(b"changed")
                with self.assertRaisesRegex(ValueError, "COMPOSED_INVALID_BYTE_DRIFT"):
                    verify_composed_candidate_visual_quality_review_request(
                        receipt_path, repo_root=root
                    )

    def test_rejects_quality_contract_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                receipt_path = build_composed_candidate_visual_quality_review_request(
                    cs273, root / "review", repo_root=root
                )
                (root / "engine/intelligence/golden_visual_quality.py").write_text(
                    "# drift\n", encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, "CONTRACT_DRIFT"):
                    verify_composed_candidate_visual_quality_review_request(
                        receipt_path, repo_root=root
                    )

    def test_rejects_premature_golden_authority_even_with_rehashed_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                receipt_path = build_composed_candidate_visual_quality_review_request(
                    cs273, root / "review", repo_root=root
                )
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt["golden_quality_approved"] = True
                unsigned = dict(receipt)
                unsigned.pop("receipt_sha256", None)
                receipt["receipt_sha256"] = sha256_json(unsigned)
                receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                    verify_composed_candidate_visual_quality_review_request(
                        receipt_path, repo_root=root
                    )

    def test_rejects_unapproved_cs273(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            source["hybrid_surface_semantic_qa_approved"] = False
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                with self.assertRaisesRegex(ValueError, "REQUIRED_GATE_MISSING"):
                    build_composed_candidate_visual_quality_review_request(
                        cs273, root / "review", repo_root=root
                    )

    def test_rejects_existing_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs273, source = self._fixture(root)
            out = root / "review"
            out.mkdir()
            with patch(
                "engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request."
                "verify_composed_candidate_hybrid_surface_semantic_qa",
                return_value=source,
            ):
                with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                    build_composed_candidate_visual_quality_review_request(
                        cs273, out, repo_root=root
                    )


if __name__ == "__main__":
    unittest.main()

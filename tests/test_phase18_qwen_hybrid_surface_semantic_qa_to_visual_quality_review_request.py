from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request as cs338


STORY_SHA = "a" * 64


def bind(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    return {
        "repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def downstream_false() -> dict:
    return {
        "visual_quality_review_executed": False,
        "visual_quality_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }


class Phase18HybridSurfaceSemanticQAToVisualQualityReviewRequestTests(unittest.TestCase):
    def _fixture(self, root: Path, *, approved: bool = True):
        source = root / "source"
        source.mkdir()
        candidate_path = source / "candidate.png"
        composed_path = source / "composed.png"
        cs337_path = source / "cs337.json"
        cs273_path = source / "cs273.json"
        candidate_path.write_bytes(b"candidate")
        composed_path.write_bytes(b"composed")
        cs337_path.write_text("337\n", encoding="utf-8")
        cs273_path.write_text("273\n", encoding="utf-8")
        candidate = {**bind(candidate_path, root), "width": 4, "height": 4}
        composed = {**bind(composed_path, root), "width": 4, "height": 4}
        cs273_binding = bind(cs273_path, root)
        cs337 = {
            "schema": cs338.CS337_SCHEMA,
            "status": "HYBRID_SURFACE_SEMANTIC_QA_PASSED" if approved else "HYBRID_SURFACE_SEMANTIC_QA_REJECTED",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs273_receipt": cs273_binding,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": approved,
            "visual_quality_review_requested": False,
            "authoritative": False,
            **downstream_false(),
        }
        cs273 = {
            "schema": cs338.CS273_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "composed_candidate_png": composed,
            "receipt_sha256": "d" * 64,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": approved,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        return cs337_path, cs273_path, cs337, cs273

    def _fake_build(self, root: Path, cs273: dict):
        def build(cs273_path, output_dir, *, repo_root):
            output_dir.mkdir()
            path = output_dir / "composed_candidate_visual_quality_review_request.json"
            path.write_text("274\n", encoding="utf-8")
            return path
        return build

    def _cs274(self, root: Path, cs273_path: Path, cs273: dict, cs337: dict) -> dict:
        return {
            "schema": cs338.CS274_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "source_cs273_receipt": {
                **bind(cs273_path, root),
                "receipt_sha256": cs273["receipt_sha256"],
            },
            "composed_candidate_png": cs337["composed_candidate_png"],
            "visual_quality_review_requested": True,
            **downstream_false(),
        }

    def test_semantic_pass_builds_exact_cs274_request_and_stops_before_cs275(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs337_path, cs273_path, source337, source273 = self._fixture(root)
            source274 = self._cs274(root, cs273_path, source273, source337)
            with (
                patch.object(cs338, "verify_composed_byte_admission_to_hybrid_surface_semantic_qa", return_value=source337),
                patch.object(cs338, "verify_composed_candidate_hybrid_surface_semantic_qa", return_value=source273),
                patch.object(cs338, "build_composed_candidate_visual_quality_review_request", side_effect=self._fake_build(root, source273)) as build274,
                patch.object(cs338, "verify_composed_candidate_visual_quality_review_request", return_value=source274),
            ):
                run = cs338.continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
                    cs337_path, root / "out", repo_root=root
                )
            receipt = cs338._read_json(run.receipt_path, "bad")
            self.assertTrue(receipt["visual_quality_review_requested"])
            self.assertFalse(receipt["visual_quality_review_executed"])
            self.assertFalse(receipt["visual_quality_review_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])
            build274.assert_called_once()

    def test_semantic_rejection_cannot_request_visual_quality(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs337_path, _, source337, _ = self._fixture(root, approved=False)
            with patch.object(
                cs338,
                "verify_composed_byte_admission_to_hybrid_surface_semantic_qa",
                return_value=source337,
            ):
                with self.assertRaisesRegex(ValueError, "CS337_SEMANTIC_PASS_REQUIRED"):
                    cs338.continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
                        cs337_path, root / "out", repo_root=root
                    )

    def test_cross_story_cs273_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs337_path, _, source337, source273 = self._fixture(root)
            source273["story_snapshot_sha256"] = "f" * 64
            with (
                patch.object(cs338, "verify_composed_byte_admission_to_hybrid_surface_semantic_qa", return_value=source337),
                patch.object(cs338, "verify_composed_candidate_hybrid_surface_semantic_qa", return_value=source273),
            ):
                with self.assertRaisesRegex(ValueError, "CS273_LINEAGE_DRIFT"):
                    cs338.continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
                        cs337_path, root / "out", repo_root=root
                    )

    def test_cs274_must_bind_exact_cs273_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs337_path, cs273_path, source337, source273 = self._fixture(root)
            source274 = self._cs274(root, cs273_path, source273, source337)
            source274["source_cs273_receipt"]["sha256"] = "e" * 64
            with (
                patch.object(cs338, "verify_composed_byte_admission_to_hybrid_surface_semantic_qa", return_value=source337),
                patch.object(cs338, "verify_composed_candidate_hybrid_surface_semantic_qa", return_value=source273),
                patch.object(cs338, "build_composed_candidate_visual_quality_review_request", side_effect=self._fake_build(root, source273)),
                patch.object(cs338, "verify_composed_candidate_visual_quality_review_request", return_value=source274),
            ):
                with self.assertRaisesRegex(ValueError, "CS274_CS273_BINDING_DRIFT"):
                    cs338.continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
                        cs337_path, root / "out", repo_root=root
                    )

    def test_premature_visual_approval_is_rejected(self) -> None:
        value = {**downstream_false()}
        value["visual_quality_review_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:visual_quality_review_approved"):
            cs338._assert_downstream_closed(value, "CS338")

    def test_source_has_no_generation_scoring_network_or_publication_shortcut(self) -> None:
        source = Path(cs338.__file__).read_text(encoding="utf-8")
        forbidden = (
            "QwenImagePipeline",
            ".from_pretrained(",
            "GoldenVisualScores(",
            "GoldenVisualBlockers(",
            "requests.",
            "httpx.",
            "urllib.",
            "publish(",
            "upload(",
            '"visual_quality_review_executed": True',
            '"visual_quality_review_approved": True',
            '"composed_visual_approved": True',
            '"semantic_approved": True',
            '"human_visual_review_approved": True',
            '"golden_quality_approved": True',
            '"genuine_golden_png_created": True',
            '"publication_ready": True',
        )
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()

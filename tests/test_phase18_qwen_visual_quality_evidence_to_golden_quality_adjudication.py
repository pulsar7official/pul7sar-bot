from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_visual_quality_evidence_to_golden_quality_adjudication as cs340

STORY_SHA = "a" * 64


def bind(path: Path, root: Path, receipt_sha256: str | None = None) -> dict:
    raw = path.read_bytes()
    value = {"repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}
    if receipt_sha256 is not None:
        value["receipt_sha256"] = receipt_sha256
    return value


def downstream_false() -> dict:
    return {"composed_visual_approved": False, "semantic_approved": False, "human_visual_review_approved": False, "genuine_golden_png_created": False, "publication_ready": False}


class Phase18VisualQualityEvidenceToGoldenQualityAdjudicationTests(unittest.TestCase):
    def test_exact_cs339_to_cs276_path_stops_before_human_and_publication(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); src = root / "src"; src.mkdir()
            candidate_file = src / "candidate.png"; candidate_file.write_bytes(b"candidate")
            composed_file = src / "composed.png"; composed_file.write_bytes(b"composed")
            r339 = src / "cs339.json"; r339.write_text("339\n", encoding="utf-8")
            r275 = src / "cs275.json"; r275.write_text("275\n", encoding="utf-8")
            r272 = src / "cs272.json"; r272.write_text("272\n", encoding="utf-8")
            r263 = src / "cs263.json"; r263.write_text("263\n", encoding="utf-8")
            candidate = {**bind(candidate_file, root), "width": 4, "height": 4}
            composed = {**bind(composed_file, root), "width": 4, "height": 4}
            cs275v = {"receipt_sha256": "5" * 64, "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed}
            b275 = bind(r275, root, cs275v["receipt_sha256"])
            cs339v = {
                "schema": cs340.CS339_SCHEMA, "status": "VISUAL_QUALITY_EVIDENCE_ADMITTED",
                "story_snapshot_sha256": STORY_SHA, "candidate_png": candidate, "composed_candidate_png": composed,
                "cs275_receipt": b275, "composition_executed": True,
                "composed_candidate_bytes_admitted_for_post_composition_qa": True,
                "semantic_inspection_executed": True, "hybrid_surface_semantic_qa_approved": True,
                "visual_quality_review_requested": True, "visual_quality_review_executed": True,
                "visual_quality_evidence_admitted": True, "visual_quality_review_approved": False,
                "golden_quality_approved": False, "authoritative": False, **downstream_false(),
            }
            cs272v = {"receipt_sha256": "2" * 64}
            b272 = bind(r272, root, cs272v["receipt_sha256"])
            cs263v = {"receipt_sha256": "3" * 64}
            b263 = bind(r263, root, cs263v["receipt_sha256"])
            cs276v = {
                "schema": cs340.CS276_SCHEMA, "receipt_sha256": "6" * 64,
                "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed,
                "source_cs263_receipt": b263, "source_cs272_receipt": b272, "source_cs275_receipt": b275,
                "golden_quality_selector_executed": True, "golden_quality_approved": True,
                **downstream_false(),
            }

            def build(_p263, _p272, _p275, out, *, repo_root):
                out.mkdir(); path = out / "composed_candidate_golden_quality_adjudication.json"; path.write_text("276\n", encoding="utf-8"); return path

            with patch.object(cs340, "verify_visual_quality_review_request_to_evidence_admission", return_value=cs339v), patch.object(cs340, "verify_composed_candidate_visual_quality_review_evidence", return_value=cs275v), patch.object(cs340, "_derive_cs272_from_cs275", return_value=(r272, b272, cs272v)), patch.object(cs340, "_derive_cs263_from_cs272", return_value=(r263, b263, cs263v)), patch.object(cs340, "build_composed_candidate_golden_quality_adjudication", side_effect=build), patch.object(cs340, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v):
                run = cs340.continue_visual_quality_evidence_to_golden_quality_adjudication(r339, root / "out", repo_root=root)
            receipt = cs340._json(run.receipt_path, "bad")
            self.assertTrue(receipt["golden_quality_selector_executed"])
            self.assertTrue(receipt["golden_quality_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_cs339_premature_golden_authority_is_rejected(self) -> None:
        value = {
            "schema": cs340.CS339_SCHEMA, "status": "VISUAL_QUALITY_EVIDENCE_ADMITTED",
            "composition_executed": True, "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True, "hybrid_surface_semantic_qa_approved": True,
            "visual_quality_review_requested": True, "visual_quality_review_executed": True,
            "visual_quality_evidence_admitted": True, "visual_quality_review_approved": False,
            "golden_quality_approved": True, "authoritative": False, **downstream_false(),
        }
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
            cs340._assert_cs339(value)

    def test_source_has_no_generation_evidence_fabrication_network_human_or_publication_shortcut(self) -> None:
        source = Path(cs340.__file__).read_text(encoding="utf-8")
        for token in ("QwenImagePipeline", ".from_pretrained(", "GoldenVisualScores(", "GoldenVisualBlockers(", "requests.", "httpx.", "urllib.", '"human_visual_review_approved": True', '"genuine_golden_png_created": True', '"publication_ready": True', "publish(", "upload("):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()

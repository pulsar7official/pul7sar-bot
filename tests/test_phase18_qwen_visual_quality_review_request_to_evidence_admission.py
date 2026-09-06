from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_visual_quality_review_request_to_evidence_admission as cs339

STORY_SHA = "a" * 64


def bind(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    return {"repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def closed() -> dict:
    return {"visual_quality_review_approved": False, "composed_visual_approved": False, "semantic_approved": False, "human_visual_review_approved": False, "golden_quality_approved": False, "genuine_golden_png_created": False, "publication_ready": False}


class Phase18VisualQualityReviewRequestToEvidenceAdmissionTests(unittest.TestCase):
    def test_exact_cs338_to_cs275_path_stops_before_cs276(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); src = root / "src"; src.mkdir()
            c = src / "candidate.png"; c.write_bytes(b"candidate")
            p = src / "composed.png"; p.write_bytes(b"composed")
            r338 = src / "cs338.json"; r338.write_text("338\n", encoding="utf-8")
            r274 = src / "cs274.json"; r274.write_text("274\n", encoding="utf-8")
            ext = src / "review.json"; ext.write_text("{}\n", encoding="utf-8")
            candidate = {**bind(c, root), "width": 4, "height": 4}; composed = {**bind(p, root), "width": 4, "height": 4}
            cs338v = {"schema": cs339.CS338_SCHEMA, "status": "VISUAL_QUALITY_REVIEW_REQUEST_READY", "story_snapshot_sha256": STORY_SHA, "candidate_png": candidate, "composed_candidate_png": composed, "cs274_receipt": bind(r274, root), "hybrid_surface_semantic_qa_approved": True, "visual_quality_review_requested": True, "visual_quality_review_executed": False, "authoritative": False, **closed()}
            cs274v = {"schema": cs339.CS274_SCHEMA, "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed, "receipt_sha256": "d"*64, "visual_quality_review_requested": True, "visual_quality_review_executed": False, **closed()}
            cs275v = {"schema": cs339.CS275_SCHEMA, "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed, "source_cs274_request": {**bind(r274, root), "receipt_sha256": cs274v["receipt_sha256"]}, "external_review_evidence": bind(ext, root), "visual_quality_review_requested": True, "visual_quality_review_executed": True, "visual_quality_evidence_admitted": True, **closed()}
            def build(_req, _ext, out, *, repo_root):
                out.mkdir(); q = out / "composed_candidate_visual_quality_review_evidence.json"; q.write_text("275\n", encoding="utf-8"); return q
            with patch.object(cs339, "verify_hybrid_surface_semantic_qa_to_visual_quality_review_request", return_value=cs338v), patch.object(cs339, "verify_composed_candidate_visual_quality_review_request", return_value=cs274v), patch.object(cs339, "build_composed_candidate_visual_quality_review_evidence", side_effect=build), patch.object(cs339, "verify_composed_candidate_visual_quality_review_evidence", return_value=cs275v):
                run = cs339.continue_visual_quality_review_request_to_evidence_admission(r338, ext, root / "out", repo_root=root)
            receipt = cs339._json(run.receipt_path, "bad")
            self.assertTrue(receipt["visual_quality_review_executed"])
            self.assertTrue(receipt["visual_quality_evidence_admitted"])
            self.assertFalse(receipt["visual_quality_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_premature_visual_approval_is_rejected(self) -> None:
        value = closed(); value["visual_quality_review_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:visual_quality_review_approved"):
            cs339._assert_closed(value, "CS339")

    def test_source_has_no_generation_scoring_network_cs276_or_publication_shortcut(self) -> None:
        source = Path(cs339.__file__).read_text(encoding="utf-8")
        for token in ("QwenImagePipeline", ".from_pretrained(", "GoldenVisualScores(", "GoldenVisualBlockers(", "requests.", "httpx.", "urllib.", "build_composed_candidate_golden", "publish(", "upload(", '"visual_quality_review_approved": True', '"golden_quality_approved": True', '"genuine_golden_png_created": True', '"publication_ready": True'):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()

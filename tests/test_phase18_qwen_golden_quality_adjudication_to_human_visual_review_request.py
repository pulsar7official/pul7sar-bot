from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_golden_quality_adjudication_to_human_visual_review_request as cs341

STORY_SHA = "a" * 64
SNAPSHOT = {
    "snapshot_byte_inventory_verified": True,
    "snapshot_inventory_sha256": "b" * 64,
    "snapshot_file_count": 7,
    "snapshot_total_bytes": 123456,
    "model_revision": "qwen-image-approved-local-revision",
}


def bind(path: Path, root: Path, receipt_sha256: str | None = None) -> dict:
    raw = path.read_bytes()
    value = {"repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}
    if receipt_sha256 is not None:
        value["receipt_sha256"] = receipt_sha256
    return value


def final_false() -> dict:
    return {"human_visual_review_executed": False, "human_visual_review_approved": False, "composed_visual_approved": False, "semantic_approved": False, "genuine_golden_png_created": False, "publication_ready": False}


class Phase18GoldenQualityToHumanVisualReviewRequestTests(unittest.TestCase):
    def _fixture(self, root: Path):
        src = root / "src"; src.mkdir()
        candidate_file = src / "candidate.png"; candidate_file.write_bytes(b"candidate")
        composed_file = src / "composed.png"; composed_file.write_bytes(b"composed")
        r340 = src / "cs340.json"; r340.write_text("340\n", encoding="utf-8")
        r276 = src / "cs276.json"; r276.write_text("276\n", encoding="utf-8")
        candidate = {**bind(candidate_file, root), "width": 4, "height": 4}
        composed = {**bind(composed_file, root), "width": 4, "height": 4}
        cs276v = {"schema": cs341.CS276_SCHEMA, "receipt_sha256": "6" * 64, "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed, "quality_tier": "golden", "golden_quality_selector_executed": True, "golden_quality_approved": True, **final_false()}
        b276 = bind(r276, root, cs276v["receipt_sha256"])
        cs340v = {"schema": cs341.CS340_SCHEMA, "status": "GOLDEN_QUALITY_ADJUDICATED", "story_snapshot_sha256": STORY_SHA, "candidate_png": candidate, "composed_candidate_png": composed, "cs276_receipt": b276, "golden_quality_selector_executed": True, "golden_quality_approved": True, "authoritative": False, **SNAPSHOT, **final_false()}
        cs277v = {"schema": cs341.CS277_SCHEMA, "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_REQUESTED", "receipt_sha256": "7" * 64, "story_snapshot_sha256": STORY_SHA, "composed_candidate_png": composed, "source_cs276_receipt": b276, "golden_quality_approved": True, "human_visual_review_requested": True, **final_false()}
        return r340, r276, cs340v, cs276v, cs277v

    @staticmethod
    def _build277(_p276, out, *, repo_root):
        out.mkdir()
        path = out / "composed_candidate_human_visual_review_request.json"
        path.write_text("277\n", encoding="utf-8")
        return path

    def test_exact_green_cs340_opens_only_cs277_request_and_preserves_snapshot_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r340, _, cs340v, cs276v, cs277v = self._fixture(root)
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v), patch.object(cs341, "build_composed_candidate_human_visual_review_request", side_effect=self._build277) as builder, patch.object(cs341, "verify_composed_candidate_human_visual_review_request", return_value=cs277v):
                run = cs341.continue_golden_quality_to_human_visual_review_request(r340, root / "out", repo_root=root)
            receipt = cs341._json(run.receipt_path, "bad")
            self.assertEqual(builder.call_count, 1)
            for field, expected in SNAPSHOT.items():
                self.assertEqual(receipt[field], expected)
            self.assertTrue(receipt["human_visual_review_requested"])
            self.assertFalse(receipt["human_visual_review_executed"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_unverified_snapshot_stops_before_cs277_creation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r340, _, cs340v, _, _ = self._fixture(root)
            cs340v = {**cs340v, "snapshot_byte_inventory_verified": False}
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "build_composed_candidate_human_visual_review_request") as builder:
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_INVALID"):
                    cs341.continue_golden_quality_to_human_visual_review_request(r340, root / "out", repo_root=root)
            builder.assert_not_called()
            self.assertFalse((root / "out").exists())

    def test_recomputed_outer_digest_cannot_hide_snapshot_inventory_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r340, _, cs340v, cs276v, cs277v = self._fixture(root)
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v), patch.object(cs341, "build_composed_candidate_human_visual_review_request", side_effect=self._build277), patch.object(cs341, "verify_composed_candidate_human_visual_review_request", return_value=cs277v):
                run = cs341.continue_golden_quality_to_human_visual_review_request(r340, root / "out", repo_root=root)
            receipt = cs341._json(run.receipt_path, "bad")
            receipt["snapshot_inventory_sha256"] = "c" * 64
            unsigned = dict(receipt); unsigned.pop("receipt_sha256", None)
            receipt["receipt_sha256"] = cs341.sha256_json(unsigned)
            run.receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v), patch.object(cs341, "verify_composed_candidate_human_visual_review_request", return_value=cs277v):
                with self.assertRaisesRegex(ValueError, "CS340_SNAPSHOT_LINEAGE_DRIFT:snapshot_inventory_sha256"):
                    cs341.verify_golden_quality_to_human_visual_review_request(run.receipt_path, repo_root=root)

    def test_recomputed_outer_digest_cannot_hide_model_revision_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r340, _, cs340v, cs276v, cs277v = self._fixture(root)
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v), patch.object(cs341, "build_composed_candidate_human_visual_review_request", side_effect=self._build277), patch.object(cs341, "verify_composed_candidate_human_visual_review_request", return_value=cs277v):
                run = cs341.continue_golden_quality_to_human_visual_review_request(r340, root / "out", repo_root=root)
            receipt = cs341._json(run.receipt_path, "bad")
            receipt["model_revision"] = "tampered-revision"
            unsigned = dict(receipt); unsigned.pop("receipt_sha256", None)
            receipt["receipt_sha256"] = cs341.sha256_json(unsigned)
            run.receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            with patch.object(cs341, "verify_visual_quality_evidence_to_golden_quality_adjudication", return_value=cs340v), patch.object(cs341, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276v), patch.object(cs341, "verify_composed_candidate_human_visual_review_request", return_value=cs277v):
                with self.assertRaisesRegex(ValueError, "CS340_SNAPSHOT_LINEAGE_DRIFT:model_revision"):
                    cs341.verify_golden_quality_to_human_visual_review_request(run.receipt_path, repo_root=root)

    def test_rejected_cs340_cannot_open_human_review(self) -> None:
        value = {"schema": cs341.CS340_SCHEMA, "status": "GOLDEN_QUALITY_ADJUDICATED", "golden_quality_selector_executed": True, "golden_quality_approved": False, "authoritative": False, **SNAPSHOT, **final_false()}
        with self.assertRaisesRegex(ValueError, "BELOW_GOLDEN"):
            cs341._assert_cs340(value)

    def test_premature_human_authority_is_rejected(self) -> None:
        value = {"schema": cs341.CS340_SCHEMA, "status": "GOLDEN_QUALITY_ADJUDICATED", "golden_quality_selector_executed": True, "golden_quality_approved": True, "authoritative": False, **SNAPSHOT, **{**final_false(), "human_visual_review_approved": True}}
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
            cs341._assert_cs340(value)

    def test_source_has_no_generation_human_verdict_network_or_publication_shortcut(self) -> None:
        source = Path(cs341.__file__).read_text(encoding="utf-8")
        for token in ("QwenImagePipeline", ".from_pretrained(", "GoldenVisualScores(", "GoldenVisualBlockers(", '\"human_visual_review_approved\": True', '\"composed_visual_approved\": True', '\"semantic_approved\": True', '\"genuine_golden_png_created\": True', '\"publication_ready\": True', "requests.", "httpx.", "urllib.", "publish(", "upload("):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()

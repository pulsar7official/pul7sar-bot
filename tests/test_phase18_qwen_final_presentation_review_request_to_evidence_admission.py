from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_final_presentation_review_request_to_evidence_admission as cs344
from engine.intelligence.qwen_image_inference_measurement import sha256_json

STORY_SHA = "a" * 64
SNAPSHOT_SHA = "b" * 64
MODEL_REVISION = "qwen-image-pinned-test-revision"


def bind(path: Path, root: Path, receipt_sha256: str | None = None) -> dict:
    raw = path.read_bytes()
    value = {
        "repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }
    if receipt_sha256 is not None:
        value["receipt_sha256"] = receipt_sha256
    return value


def downstream_false() -> dict:
    return {
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }


def snapshot_lineage() -> dict:
    return {
        "snapshot_byte_inventory_verified": True,
        "snapshot_inventory_sha256": SNAPSHOT_SHA,
        "snapshot_file_count": 9,
        "snapshot_total_bytes": 123456,
        "model_revision": MODEL_REVISION,
    }


class Phase18FinalPresentationReviewRequestToEvidenceAdmissionTests(unittest.TestCase):
    def _fixture(self, root: Path, *, approved: bool = True):
        src = root / "src"
        src.mkdir()
        candidate_file = src / "candidate.png"
        candidate_file.write_bytes(b"candidate")
        composed_file = src / "composed.png"
        composed_file.write_bytes(b"composed")
        r343 = src / "cs343.json"
        r343.write_text("343\n", encoding="utf-8")
        r279 = src / "cs279.json"
        r279.write_text("279\n", encoding="utf-8")
        external = src / "presentation_review.json"
        external.write_text("external presentation review\n", encoding="utf-8")
        candidate = {**bind(candidate_file, root), "width": 4, "height": 4}
        composed = {**bind(composed_file, root), "width": 4, "height": 4}
        b279 = bind(r279, root, "7" * 64)
        cs343v = {
            "schema": cs344.CS343_SCHEMA,
            "status": "FINAL_PRESENTATION_REVIEW_REQUEST_READY",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs279_receipt": b279,
            **snapshot_lineage(),
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": False,
            "final_presentation_review_approved": False,
            "exact_brand_integrity_approved": False,
            "typography_integrity_approved": False,
            "authoritative": False,
            **downstream_false(),
        }
        cs279v = {
            "schema": cs344.CS279_SCHEMA,
            "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED",
            "receipt_sha256": "7" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "composed_candidate_png": composed,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": False,
            "final_presentation_review_approved": False,
            "exact_brand_integrity_approved": False,
            "typography_integrity_approved": False,
            **downstream_false(),
        }
        external_binding = bind(external, root)
        return r343, r279, external, candidate, composed, b279, cs343v, cs279v, external_binding, approved

    def _cs280(self, composed: dict, b279: dict, external_binding: dict, approved: bool) -> dict:
        return {
            "schema": cs344.CS280_SCHEMA,
            "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED",
            "receipt_sha256": "8" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "composed_candidate_png": composed,
            "source_cs279_request": b279,
            "external_final_presentation_review_evidence": external_binding,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": True,
            "final_presentation_review_evidence_admitted": True,
            "final_presentation_review_approved": approved,
            "exact_brand_integrity_approved": approved,
            "typography_integrity_approved": approved,
            **downstream_false(),
        }

    def test_exact_cs343_admits_external_presentation_evidence_through_cs280_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r343, _r279, external, _candidate, composed, b279, cs343v, cs279v, external_binding, approved = self._fixture(root)

            def build(_p279, _external, out, *, repo_root):
                self.assertEqual(_external, external)
                out.mkdir()
                path = out / "composed_candidate_final_presentation_review_evidence.json"
                path.write_text("280\n", encoding="utf-8")
                return path

            cs280v = self._cs280(composed, b279, external_binding, approved)
            with patch.object(cs344, "verify_human_visual_review_evidence_to_final_presentation_review_request", return_value=cs343v), patch.object(cs344, "verify_composed_candidate_final_presentation_review_request", return_value=cs279v), patch.object(cs344, "build_composed_candidate_final_presentation_review_evidence", side_effect=build) as builder, patch.object(cs344, "verify_composed_candidate_final_presentation_review_evidence", return_value=cs280v):
                run = cs344.continue_final_presentation_review_request_to_evidence_admission(r343, external, root / "out", repo_root=root)
            receipt = cs344._json(run.receipt_path, "bad")
            self.assertEqual(builder.call_count, 1)
            for field, expected in snapshot_lineage().items():
                self.assertEqual(receipt[field], expected)
            self.assertTrue(receipt["final_presentation_review_executed"])
            self.assertTrue(receipt["final_presentation_review_evidence_admitted"])
            self.assertTrue(receipt["final_presentation_review_approved"])
            self.assertTrue(receipt["exact_brand_integrity_approved"])
            self.assertTrue(receipt["typography_integrity_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_unverified_snapshot_is_rejected_before_cs280_creation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r343, _r279, external, _candidate, _composed, _b279, cs343v, _cs279v, _external_binding, _approved = self._fixture(root)
            cs343v["snapshot_byte_inventory_verified"] = False
            with patch.object(cs344, "verify_human_visual_review_evidence_to_final_presentation_review_request", return_value=cs343v), patch.object(cs344, "build_composed_candidate_final_presentation_review_evidence") as builder:
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_INVALID"):
                    cs344.continue_final_presentation_review_request_to_evidence_admission(r343, external, root / "out", repo_root=root)
            builder.assert_not_called()
            self.assertFalse((root / "out").exists())

    def test_recomputed_outer_digest_cannot_hide_snapshot_inventory_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r343, _r279, external, _candidate, composed, b279, cs343v, cs279v, external_binding, approved = self._fixture(root)

            def build(_p279, _external, out, *, repo_root):
                out.mkdir()
                path = out / "composed_candidate_final_presentation_review_evidence.json"
                path.write_text("280\n", encoding="utf-8")
                return path

            cs280v = self._cs280(composed, b279, external_binding, approved)
            with patch.object(cs344, "verify_human_visual_review_evidence_to_final_presentation_review_request", return_value=cs343v), patch.object(cs344, "verify_composed_candidate_final_presentation_review_request", return_value=cs279v), patch.object(cs344, "build_composed_candidate_final_presentation_review_evidence", side_effect=build), patch.object(cs344, "verify_composed_candidate_final_presentation_review_evidence", return_value=cs280v):
                run = cs344.continue_final_presentation_review_request_to_evidence_admission(r343, external, root / "out", repo_root=root)
                receipt = cs344._json(run.receipt_path, "bad")
                receipt["snapshot_inventory_sha256"] = "c" * 64
                unsigned = dict(receipt)
                unsigned.pop("receipt_sha256")
                receipt["receipt_sha256"] = sha256_json(unsigned)
                run.receipt_path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT:snapshot_inventory_sha256"):
                    cs344.verify_final_presentation_review_request_to_evidence_admission(run.receipt_path, repo_root=root)

    def test_recomputed_outer_digest_cannot_hide_model_revision_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r343, _r279, external, _candidate, composed, b279, cs343v, cs279v, external_binding, approved = self._fixture(root)

            def build(_p279, _external, out, *, repo_root):
                out.mkdir()
                path = out / "composed_candidate_final_presentation_review_evidence.json"
                path.write_text("280\n", encoding="utf-8")
                return path

            cs280v = self._cs280(composed, b279, external_binding, approved)
            with patch.object(cs344, "verify_human_visual_review_evidence_to_final_presentation_review_request", return_value=cs343v), patch.object(cs344, "verify_composed_candidate_final_presentation_review_request", return_value=cs279v), patch.object(cs344, "build_composed_candidate_final_presentation_review_evidence", side_effect=build), patch.object(cs344, "verify_composed_candidate_final_presentation_review_evidence", return_value=cs280v):
                run = cs344.continue_final_presentation_review_request_to_evidence_admission(r343, external, root / "out", repo_root=root)
                receipt = cs344._json(run.receipt_path, "bad")
                receipt["model_revision"] = "tampered-revision"
                unsigned = dict(receipt)
                unsigned.pop("receipt_sha256")
                receipt["receipt_sha256"] = sha256_json(unsigned)
                run.receipt_path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT:model_revision"):
                    cs344.verify_final_presentation_review_request_to_evidence_admission(run.receipt_path, repo_root=root)

    def test_presentation_rejection_is_preserved_without_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r343, _r279, external, _candidate, composed, b279, cs343v, cs279v, external_binding, _approved = self._fixture(root, approved=False)

            def build(_p279, _external, out, *, repo_root):
                out.mkdir()
                path = out / "composed_candidate_final_presentation_review_evidence.json"
                path.write_text("280\n", encoding="utf-8")
                return path

            cs280v = self._cs280(composed, b279, external_binding, False)
            with patch.object(cs344, "verify_human_visual_review_evidence_to_final_presentation_review_request", return_value=cs343v), patch.object(cs344, "verify_composed_candidate_final_presentation_review_request", return_value=cs279v), patch.object(cs344, "build_composed_candidate_final_presentation_review_evidence", side_effect=build), patch.object(cs344, "verify_composed_candidate_final_presentation_review_evidence", return_value=cs280v):
                run = cs344.continue_final_presentation_review_request_to_evidence_admission(r343, external, root / "out", repo_root=root)
            receipt = cs344._json(run.receipt_path, "bad")
            self.assertFalse(receipt["final_presentation_review_approved"])
            self.assertFalse(receipt["exact_brand_integrity_approved"])
            self.assertFalse(receipt["typography_integrity_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["publication_ready"])

    def test_premature_presentation_authority_in_cs343_is_rejected(self) -> None:
        value = {
            "schema": cs344.CS343_SCHEMA,
            "status": "FINAL_PRESENTATION_REVIEW_REQUEST_READY",
            **snapshot_lineage(),
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": False,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": False,
            "typography_integrity_approved": False,
            "authoritative": False,
            **downstream_false(),
        }
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
            cs344._assert_cs343(value)

    def test_story_or_png_drift_in_cs280_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _r343, _r279, _external, _candidate, composed, b279, cs343v, cs279v, external_binding, _approved = self._fixture(root)
            bad = {
                "schema": cs344.CS280_SCHEMA,
                "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED",
                "story_snapshot_sha256": "b" * 64,
                "composed_candidate_png": composed,
                "source_cs279_request": b279,
                "external_final_presentation_review_evidence": external_binding,
            }
            with self.assertRaisesRegex(ValueError, "STORY_DRIFT"):
                cs344._assert_cs280(bad, cs343v, b279, cs279v, external_binding)

    def test_source_has_no_generation_verdict_fabrication_network_or_publication_shortcut(self) -> None:
        source = Path(cs344.__file__).read_text(encoding="utf-8")
        for token in (
            "QwenImagePipeline",
            ".from_pretrained(",
            "GoldenVisualScores(",
            "GoldenVisualBlockers(",
            '\"composed_visual_approved\": True',
            '\"semantic_approved\": True',
            '\"genuine_golden_png_created\": True',
            '\"publication_ready\": True',
            "requests.",
            "httpx.",
            "urllib.",
            "publish(",
            "upload(",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()

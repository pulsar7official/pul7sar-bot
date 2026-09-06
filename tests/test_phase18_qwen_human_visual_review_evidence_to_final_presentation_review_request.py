from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_human_visual_review_evidence_to_final_presentation_review_request as cs343

STORY_SHA = "a" * 64


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


def final_false() -> dict:
    return {
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }


def presentation_false() -> dict:
    return {
        "final_presentation_review_executed": False,
        "final_presentation_review_approved": False,
        "exact_brand_integrity_approved": False,
        "typography_integrity_approved": False,
        **final_false(),
    }


class Phase18HumanVisualReviewEvidenceToFinalPresentationReviewRequestTests(unittest.TestCase):
    def _fixture(self, root: Path):
        src = root / "src"
        src.mkdir()
        candidate_file = src / "candidate.png"
        candidate_file.write_bytes(b"candidate")
        composed_file = src / "composed.png"
        composed_file.write_bytes(b"composed")
        r342 = src / "cs342.json"
        r342.write_text("342\n", encoding="utf-8")
        r278 = src / "cs278.json"
        r278.write_text("278\n", encoding="utf-8")

        candidate = {**bind(candidate_file, root), "width": 4, "height": 4}
        composed = {**bind(composed_file, root), "width": 4, "height": 4}
        cs278v = {
            "schema": cs343.CS278_SCHEMA,
            "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED",
            "receipt_sha256": "8" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "composed_candidate_png": composed,
            "golden_quality_selector_executed": True,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": True,
            **final_false(),
        }
        b278 = bind(r278, root, cs278v["receipt_sha256"])
        cs342v = {
            "schema": cs343.CS342_SCHEMA,
            "status": "HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs278_receipt": b278,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": True,
            "authoritative": False,
            **final_false(),
        }
        return r342, r278, candidate, composed, b278, cs342v, cs278v

    def test_approved_exact_cs342_opens_existing_cs279_request_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r342, _r278, _candidate, composed, b278, cs342v, cs278v = self._fixture(root)

            def build(_p278, out, *, repo_root):
                out.mkdir()
                path = out / "composed_candidate_final_presentation_review_request.json"
                path.write_text("279\n", encoding="utf-8")
                return path

            cs279v = {
                "schema": cs343.CS279_SCHEMA,
                "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED",
                "receipt_sha256": "9" * 64,
                "story_snapshot_sha256": STORY_SHA,
                "source_cs278_receipt": b278,
                "composed_candidate_png": composed,
                "human_visual_review_approved": True,
                "final_presentation_review_requested": True,
                **presentation_false(),
            }
            with patch.object(cs343, "verify_human_visual_review_request_to_evidence_admission", return_value=cs342v), patch.object(cs343, "verify_composed_candidate_human_visual_review_evidence", return_value=cs278v), patch.object(cs343, "build_composed_candidate_final_presentation_review_request", side_effect=build) as builder, patch.object(cs343, "verify_composed_candidate_final_presentation_review_request", return_value=cs279v):
                run = cs343.continue_human_visual_review_evidence_to_final_presentation_review_request(
                    r342,
                    root / "out",
                    repo_root=root,
                )
            receipt = cs343._json(run.receipt_path, "bad")
            self.assertEqual(builder.call_count, 1)
            self.assertTrue(receipt["human_visual_review_approved"])
            self.assertTrue(receipt["final_presentation_review_requested"])
            self.assertFalse(receipt["final_presentation_review_executed"])
            self.assertFalse(receipt["final_presentation_review_approved"])
            self.assertFalse(receipt["exact_brand_integrity_approved"])
            self.assertFalse(receipt["typography_integrity_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_human_rejection_blocks_cs279_fail_closed(self) -> None:
        value = {
            "schema": cs343.CS342_SCHEMA,
            "status": "HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED",
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": False,
            "authoritative": False,
            **final_false(),
        }
        with self.assertRaisesRegex(ValueError, "REQUIRED_GATE_MISSING:human_visual_review_approved"):
            cs343._assert_cs342(value)

    def test_cs278_story_or_png_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _r342, _r278, _candidate, _composed, _b278, cs342v, cs278v = self._fixture(root)
            drifted_story = dict(cs278v)
            drifted_story["story_snapshot_sha256"] = "b" * 64
            with self.assertRaisesRegex(ValueError, "STORY_DRIFT"):
                cs343._assert_cs278(drifted_story, cs342v)
            drifted_png = dict(cs278v)
            drifted_png["composed_candidate_png"] = {"sha256": "c" * 64}
            with self.assertRaisesRegex(ValueError, "PNG_DRIFT"):
                cs343._assert_cs278(drifted_png, cs342v)

    def test_cs279_cannot_claim_presentation_or_final_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _r342, _r278, _candidate, composed, b278, cs342v, cs278v = self._fixture(root)
            value = {
                "schema": cs343.CS279_SCHEMA,
                "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED",
                "story_snapshot_sha256": STORY_SHA,
                "source_cs278_receipt": b278,
                "composed_candidate_png": composed,
                "human_visual_review_approved": True,
                "final_presentation_review_requested": True,
                **presentation_false(),
            }
            value["final_presentation_review_approved"] = True
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                cs343._assert_cs279(value, cs342v, b278, cs278v)

    def test_source_has_no_generation_verdict_fabrication_network_or_publication_shortcut(self) -> None:
        source = Path(cs343.__file__).read_text(encoding="utf-8")
        for token in (
            "QwenImagePipeline",
            ".from_pretrained(",
            "GoldenVisualScores(",
            "GoldenVisualBlockers(",
            '\"final_presentation_review_approved\": True',
            '\"exact_brand_integrity_approved\": True',
            '\"typography_integrity_approved\": True',
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

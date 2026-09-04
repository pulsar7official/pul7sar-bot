from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_human_visual_review_request_to_evidence_admission as cs342

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


class Phase18HumanVisualReviewRequestToEvidenceAdmissionTests(unittest.TestCase):
    def _fixture(self, root: Path, *, approved: bool = True):
        src = root / "src"
        src.mkdir()
        candidate_file = src / "candidate.png"
        candidate_file.write_bytes(b"candidate")
        composed_file = src / "composed.png"
        composed_file.write_bytes(b"composed")
        r341 = src / "cs341.json"
        r341.write_text("341\n", encoding="utf-8")
        r277 = src / "cs277.json"
        r277.write_text("277\n", encoding="utf-8")
        external = src / "human_review.json"
        external.write_text("external human review\n", encoding="utf-8")
        candidate = {**bind(candidate_file, root), "width": 4, "height": 4}
        composed = {**bind(composed_file, root), "width": 4, "height": 4}
        cs277v = {
            "schema": cs342.CS277_SCHEMA,
            "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_REQUESTED",
            "receipt_sha256": "7" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "composed_candidate_png": composed,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": False,
            **final_false(),
        }
        b277 = bind(r277, root, cs277v["receipt_sha256"])
        cs341v = {
            "schema": cs342.CS341_SCHEMA,
            "status": "HUMAN_VISUAL_REVIEW_REQUEST_READY",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs277_receipt": b277,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": False,
            "authoritative": False,
            **final_false(),
        }
        external_binding = bind(external, root)
        return r341, r277, external, candidate, composed, b277, cs341v, cs277v, external_binding, approved

    def test_exact_cs341_admits_external_human_evidence_through_cs278_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r341, _r277, external, _candidate, composed, b277, cs341v, cs277v, external_binding, approved = self._fixture(root)

            def build(_p277, _external, out, *, repo_root):
                self.assertEqual(_external, external)
                out.mkdir()
                path = out / "composed_candidate_human_visual_review_evidence.json"
                path.write_text("278\n", encoding="utf-8")
                return path

            cs278v = {
                "schema": cs342.CS278_SCHEMA,
                "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED",
                "receipt_sha256": "8" * 64,
                "story_snapshot_sha256": STORY_SHA,
                "composed_candidate_png": composed,
                "source_cs277_request": b277,
                "external_human_review_evidence": external_binding,
                "golden_quality_approved": True,
                "human_visual_review_requested": True,
                "human_visual_review_executed": True,
                "human_visual_review_evidence_admitted": True,
                "human_visual_review_approved": approved,
                **final_false(),
            }
            with patch.object(cs342, "verify_golden_quality_to_human_visual_review_request", return_value=cs341v), patch.object(cs342, "verify_composed_candidate_human_visual_review_request", return_value=cs277v), patch.object(cs342, "build_composed_candidate_human_visual_review_evidence", side_effect=build) as builder, patch.object(cs342, "verify_composed_candidate_human_visual_review_evidence", return_value=cs278v):
                run = cs342.continue_human_visual_review_request_to_evidence_admission(r341, external, root / "out", repo_root=root)
            receipt = cs342._json(run.receipt_path, "bad")
            self.assertEqual(builder.call_count, 1)
            self.assertTrue(receipt["human_visual_review_executed"])
            self.assertTrue(receipt["human_visual_review_evidence_admitted"])
            self.assertTrue(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])

    def test_human_rejection_is_preserved_without_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            r341, _r277, external, _candidate, composed, b277, cs341v, cs277v, external_binding, _approved = self._fixture(root, approved=False)

            def build(_p277, _external, out, *, repo_root):
                out.mkdir()
                path = out / "composed_candidate_human_visual_review_evidence.json"
                path.write_text("278\n", encoding="utf-8")
                return path

            cs278v = {
                "schema": cs342.CS278_SCHEMA,
                "status": "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED",
                "receipt_sha256": "8" * 64,
                "story_snapshot_sha256": STORY_SHA,
                "composed_candidate_png": composed,
                "source_cs277_request": b277,
                "external_human_review_evidence": external_binding,
                "golden_quality_approved": True,
                "human_visual_review_requested": True,
                "human_visual_review_executed": True,
                "human_visual_review_evidence_admitted": True,
                "human_visual_review_approved": False,
                **final_false(),
            }
            with patch.object(cs342, "verify_golden_quality_to_human_visual_review_request", return_value=cs341v), patch.object(cs342, "verify_composed_candidate_human_visual_review_request", return_value=cs277v), patch.object(cs342, "build_composed_candidate_human_visual_review_evidence", side_effect=build), patch.object(cs342, "verify_composed_candidate_human_visual_review_evidence", return_value=cs278v):
                run = cs342.continue_human_visual_review_request_to_evidence_admission(r341, external, root / "out", repo_root=root)
            receipt = cs342._json(run.receipt_path, "bad")
            self.assertTrue(receipt["human_visual_review_executed"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["publication_ready"])

    def test_premature_human_authority_in_cs341_is_rejected(self) -> None:
        value = {
            "schema": cs342.CS341_SCHEMA,
            "status": "HUMAN_VISUAL_REVIEW_REQUEST_READY",
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": True,
            "authoritative": False,
            **final_false(),
        }
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
            cs342._assert_cs341(value)

    def test_source_has_no_generation_human_verdict_fabrication_network_or_publication_shortcut(self) -> None:
        source = Path(cs342.__file__).read_text(encoding="utf-8")
        for token in (
            "QwenImagePipeline",
            ".from_pretrained(",
            "GoldenVisualScores(",
            "GoldenVisualBlockers(",
            '\"human_visual_review_approved\": True',
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

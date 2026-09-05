from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_final_composed_visual_approval_to_final_semantic_approval as subject


def _binding(root: Path, path: Path, receipt_sha: str | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    value: dict[str, object] = {
        "repository_relative_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }
    if receipt_sha is not None:
        value["receipt_sha256"] = receipt_sha
    return value


class FinalComposedVisualApprovalToFinalSemanticApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.story = "a" * 64
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/composed.png").write_bytes(b"PNG")
        self.png = {
            "repository_relative_path": "artifacts/composed.png",
            "sha256": hashlib.sha256(b"PNG").hexdigest(),
            "byte_size": 3,
        }
        self.cs345_path = self.root / "cs345.json"
        self.cs345_path.write_text("{}", encoding="utf-8")
        self.cs281_path = self.root / "cs281.json"
        self.cs281_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs345(self) -> dict[str, object]:
        return {
            "schema": subject.CS345_SCHEMA,
            "status": subject.CS345_STATUS,
            "receipt_sha256": "1" * 64,
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.png,
            "cs281_receipt": _binding(self.root, self.cs281_path, "2" * 64),
            "golden_quality_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
        }

    def _cs281(self) -> dict[str, object]:
        return {
            "schema": subject.CS281_SCHEMA,
            "receipt_sha256": "2" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "hybrid_surface_semantic_qa_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "final_composed_visual_approval_executed": True,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs282(self) -> dict[str, object]:
        return {
            "schema": subject.CS282_SCHEMA,
            "receipt_sha256": "3" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_exact_cs345_continues_once_to_existing_cs282(self) -> None:
        cs345 = self._cs345()
        cs281 = self._cs281()
        cs282 = self._cs282()
        calls = {"cs282": 0}

        def build282(given281: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs282"] += 1
            self.assertEqual(given281, self.cs281_path)
            output.mkdir()
            path = output / "cs282.json"
            path.write_text("{}", encoding="utf-8")
            return path

        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_evidence_to_final_composed_visual_approval",
                return_value=cs345,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_composed_visual_approval",
                return_value=cs281,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_semantic_approval",
                side_effect=build282,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_semantic_approval",
                return_value=cs282,
            ),
        ):
            run = subject.continue_final_composed_visual_approval_to_final_semantic_approval(
                self.cs345_path,
                self.root / "out",
                repo_root=self.root,
            )

        payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(calls["cs282"], 1)
        self.assertEqual(payload["status"], subject.STATUS)
        self.assertIs(payload["composed_visual_approved"], True)
        self.assertIs(payload["semantic_approved"], True)
        self.assertIs(payload["genuine_golden_png_created"], False)
        self.assertIs(payload["publication_ready"], False)
        self.assertIs(payload["authoritative"], False)

    def test_missing_final_composed_approval_never_reaches_cs282(self) -> None:
        cs345 = self._cs345()
        cs345["composed_visual_approved"] = False
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_evidence_to_final_composed_visual_approval",
                return_value=cs345,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_semantic_approval",
                side_effect=AssertionError("CS282 must remain closed"),
            ),
            self.assertRaisesRegex(
                ValueError,
                "CS346_CS345_REQUIRED_GATE_MISSING:composed_visual_approved",
            ),
        ):
            subject.continue_final_composed_visual_approval_to_final_semantic_approval(
                self.cs345_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_premature_semantic_authority_in_cs345_fails_closed(self) -> None:
        cs345 = self._cs345()
        cs345["semantic_approved"] = True
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_evidence_to_final_composed_visual_approval",
                return_value=cs345,
            ),
            self.assertRaisesRegex(
                ValueError,
                "CS346_CS345_PREMATURE_AUTHORITY:semantic_approved",
            ),
        ):
            subject.continue_final_composed_visual_approval_to_final_semantic_approval(
                self.cs345_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_exact_cs281_receipt_binding_is_required(self) -> None:
        cs345 = self._cs345()
        cs281 = self._cs281()
        cs281["receipt_sha256"] = "9" * 64
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_evidence_to_final_composed_visual_approval",
                return_value=cs345,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_composed_visual_approval",
                return_value=cs281,
            ),
            self.assertRaisesRegex(ValueError, "CS346_CS281_RECEIPT_DRIFT"),
        ):
            subject.continue_final_composed_visual_approval_to_final_semantic_approval(
                self.cs345_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_cs282_cannot_grant_golden_or_publication_authority(self) -> None:
        cs345 = self._cs345()
        cs281 = self._cs281()
        cs282 = self._cs282()
        cs282["publication_ready"] = True

        def build282(given281: Path, output: Path, *, repo_root: Path) -> Path:
            output.mkdir()
            path = output / "cs282.json"
            path.write_text("{}", encoding="utf-8")
            return path

        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_evidence_to_final_composed_visual_approval",
                return_value=cs345,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_composed_visual_approval",
                return_value=cs281,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_semantic_approval",
                side_effect=build282,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_semantic_approval",
                return_value=cs282,
            ),
            self.assertRaisesRegex(ValueError, "CS346_CS282_PREMATURE_AUTHORITY:publication_ready"),
        ):
            subject.continue_final_composed_visual_approval_to_final_semantic_approval(
                self.cs345_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_continuation_cannot_generate_pixels_or_bypass_publication_gate(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertIn("build_composed_candidate_final_semantic_approval", source)
        self.assertIn("verify_composed_candidate_final_semantic_approval", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn(".from_pretrained(", source)
        self.assertNotIn("build_composed_candidate_genuine_golden_materialization", source)
        self.assertNotIn("SemanticPublicationGate(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("upload", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertIn('"semantic_approved": True', source)
        self.assertIn('"genuine_golden_png_created": False', source)
        self.assertIn('"publication_ready": False', source)
        self.assertIn('"authoritative": False', source)


if __name__ == "__main__":
    unittest.main()

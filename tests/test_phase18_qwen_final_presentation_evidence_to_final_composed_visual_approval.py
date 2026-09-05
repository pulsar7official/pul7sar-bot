from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_final_presentation_evidence_to_final_composed_visual_approval as subject


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


class FinalPresentationEvidenceToFinalComposedVisualApprovalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.story = "a" * 64
        self.png = {
            "repository_relative_path": "artifacts/composed.png",
            "sha256": "b" * 64,
            "byte_size": 321,
        }
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/composed.png").write_bytes(b"PNG")
        self.cs344_path = self.root / "cs344.json"
        self.cs344_path.write_text("{}", encoding="utf-8")
        self.cs280_path = self.root / "cs280.json"
        self.cs280_path.write_text("{}", encoding="utf-8")
        self.cs273_path = self.root / "cs273.json"
        self.cs273_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs344(self, *, approved: bool = True) -> dict[str, object]:
        r280 = "c" * 64
        return {
            "schema": subject.CS344_SCHEMA,
            "status": "FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED",
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.png,
            "cs280_receipt": _binding(self.root, self.cs280_path, r280),
            "golden_quality_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": True,
            "final_presentation_review_evidence_admitted": True,
            "final_presentation_review_approved": approved,
            "exact_brand_integrity_approved": approved,
            "typography_integrity_approved": approved,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
        }

    def _cs280(self) -> dict[str, object]:
        return {
            "schema": subject.CS280_SCHEMA,
            "receipt_sha256": "c" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": True,
            "final_presentation_review_evidence_admitted": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs273(self) -> dict[str, object]:
        return {
            "schema": subject.CS273_SCHEMA,
            "receipt_sha256": "e" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": True,
        }

    def test_exact_approved_cs344_continues_once_to_existing_cs281(self) -> None:
        cs344 = self._cs344()
        cs280 = self._cs280()
        cs273 = self._cs273()
        calls = {"cs281": 0}

        def build281(given273: Path, given280: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs281"] += 1
            self.assertEqual(given273, self.cs273_path)
            self.assertEqual(given280, self.cs280_path)
            output.mkdir()
            path = output / "cs281.json"
            path.write_text("{}", encoding="utf-8")
            return path

        def verify281(path: Path, *, repo_root: Path) -> dict[str, object]:
            return {
                "schema": subject.CS281_SCHEMA,
                "receipt_sha256": "f" * 64,
                "story_snapshot_sha256": self.story,
                "composed_candidate_png": self.png,
                "composed_visual_approved": True,
                "semantic_approved": False,
                "genuine_golden_png_created": False,
                "publication_ready": False,
            }

        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_review_request_to_evidence_admission",
                return_value=cs344,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_evidence",
                return_value=cs280,
            ),
            mock.patch.object(subject, "_derive_exact_cs273", return_value=(self.cs273_path, cs273)),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_composed_visual_approval",
                side_effect=build281,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_composed_visual_approval",
                side_effect=verify281,
            ),
        ):
            run = subject.continue_final_presentation_evidence_to_final_composed_visual_approval(
                self.cs344_path,
                self.root / "out",
                repo_root=self.root,
            )

        payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(calls["cs281"], 1)
        self.assertEqual(payload["status"], subject.STATUS)
        self.assertIs(payload["final_presentation_review_approved"], True)
        self.assertIs(payload["exact_brand_integrity_approved"], True)
        self.assertIs(payload["typography_integrity_approved"], True)
        self.assertIs(payload["composed_visual_approved"], True)
        self.assertIs(payload["semantic_approved"], False)
        self.assertIs(payload["genuine_golden_png_created"], False)
        self.assertIs(payload["publication_ready"], False)
        self.assertIs(payload["authoritative"], False)

    def test_presentation_rejection_never_reaches_cs281(self) -> None:
        cs344 = self._cs344(approved=False)
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_review_request_to_evidence_admission",
                return_value=cs344,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_composed_visual_approval",
                side_effect=AssertionError("CS281 must remain closed after rejection"),
            ),
            self.assertRaisesRegex(
                ValueError,
                "CS345_CS344_REQUIRED_GATE_MISSING:final_presentation_review_approved",
            ),
        ):
            subject.continue_final_presentation_evidence_to_final_composed_visual_approval(
                self.cs344_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_premature_semantic_authority_fails_closed(self) -> None:
        cs344 = self._cs344()
        cs344["semantic_approved"] = True
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_review_request_to_evidence_admission",
                return_value=cs344,
            ),
            self.assertRaisesRegex(ValueError, "CS345_CS344_PREMATURE_AUTHORITY:semantic_approved"),
        ):
            subject.continue_final_presentation_evidence_to_final_composed_visual_approval(
                self.cs344_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_exact_cs280_binding_receipt_is_required(self) -> None:
        cs344 = self._cs344()
        cs280 = self._cs280()
        cs280["receipt_sha256"] = "9" * 64
        with (
            mock.patch.object(
                subject,
                "verify_final_presentation_review_request_to_evidence_admission",
                return_value=cs344,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_evidence",
                return_value=cs280,
            ),
            self.assertRaisesRegex(ValueError, "CS345_CS280_RECEIPT_DRIFT"),
        ):
            subject.continue_final_presentation_evidence_to_final_composed_visual_approval(
                self.cs344_path,
                self.root / "out",
                repo_root=self.root,
            )

    def test_continuation_cannot_generate_review_pixels_or_final_semantic_publication(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertIn("build_composed_candidate_final_composed_visual_approval", source)
        self.assertIn("verify_composed_candidate_final_presentation_review_evidence", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn(".from_pretrained(", source)
        self.assertNotIn("build_composed_candidate_final_semantic_approval", source)
        self.assertNotIn("build_composed_candidate_genuine_golden_materialization", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("upload", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertIn('"semantic_approved": False', source)
        self.assertIn('"genuine_golden_png_created": False', source)
        self.assertIn('"publication_ready": False', source)


if __name__ == "__main__":
    unittest.main()

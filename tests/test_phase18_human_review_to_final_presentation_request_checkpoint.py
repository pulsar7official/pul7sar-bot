from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import SCHEMA as CS277_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import SCHEMA as CS278_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import SCHEMA as CS279_SCHEMA
from tools.phase18_continue_human_review_to_final_presentation_request import (
    CS324_SCHEMA,
    continue_human_review_to_final_presentation_request,
)

MODULE = "tools.phase18_continue_human_review_to_final_presentation_request"
STORY = "1" * 64


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HumanReviewToFinalPresentationRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        runs = self.root / "runs"
        runs.mkdir()
        self.png = runs / "composed.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        self.cs277_path = self.root / "cs277.json"
        self.cs277_path.write_text('{"cs":277}\n', encoding="utf-8")
        self.cs278_path = self.root / "cs278.json"
        self.cs278_path.write_text('{"cs":278}\n', encoding="utf-8")
        self.cs324_path = self.root / "cs324.json"
        self._write_cs324()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _png_binding(self) -> dict:
        return {
            "repository_relative_path": "runs/composed.png",
            "sha256": _sha(self.png),
            "byte_size": self.png.stat().st_size,
            "width": 1024,
            "height": 1024,
        }

    def _write_cs324(self, **updates) -> dict:
        payload = {
            "schema": CS324_SCHEMA,
            "status": "HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED",
            "authoritative": False,
            "story_snapshot_sha256": STORY,
            "candidate_png": {"sha256": "2" * 64},
            "composed_candidate_png": self._png_binding(),
            "cs277_receipt": "cs277.json",
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        payload.update(updates)
        self.cs324_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return payload

    def _cs277(self) -> dict:
        return {
            "schema": CS277_SCHEMA,
            "receipt_sha256": "7" * 64,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": self._png_binding(),
            "human_visual_review_requested": True,
            "human_visual_review_executed": False,
            "human_visual_review_approved": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs278(self, approved: bool = True) -> dict:
        return {
            "schema": CS278_SCHEMA,
            "receipt_sha256": "8" * 64,
            "story_snapshot_sha256": STORY,
            "source_cs277_request": {
                "repository_relative_path": "cs277.json",
                "sha256": _sha(self.cs277_path),
                "byte_size": self.cs277_path.stat().st_size,
                "receipt_sha256": "7" * 64,
            },
            "composed_candidate_png": self._png_binding(),
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": approved,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs279(self) -> dict:
        return {
            "schema": CS279_SCHEMA,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": self._png_binding(),
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": False,
            "final_presentation_review_approved": False,
            "exact_brand_integrity_approved": False,
            "typography_integrity_approved": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _fake_build(_cs278_path: Path, output_dir: Path, *, repo_root: Path) -> Path:
        output_dir.mkdir()
        path = output_dir / "cs279.json"
        path.write_text("{}\n", encoding="utf-8")
        return path

    def test_approved_external_cs278_opens_request_only(self) -> None:
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=self._cs277()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._cs278()),
            patch(f"{MODULE}.build_composed_candidate_final_presentation_review_request", side_effect=self._fake_build),
            patch(f"{MODULE}.verify_composed_candidate_final_presentation_review_request", return_value=self._cs279()),
        ):
            path = continue_human_review_to_final_presentation_request(
                self.cs324_path,
                self.cs278_path,
                self.root / "out",
                repo_root=self.root,
            )
        checkpoint = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["status"], "FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED")
        self.assertTrue(checkpoint["human_visual_review_approved"])
        self.assertTrue(checkpoint["final_presentation_review_requested"])
        self.assertFalse(checkpoint["final_presentation_review_executed"])
        self.assertFalse(checkpoint["final_presentation_review_approved"])
        self.assertFalse(checkpoint["exact_brand_integrity_approved"])
        self.assertFalse(checkpoint["typography_integrity_approved"])
        self.assertFalse(checkpoint["composed_visual_approved"])
        self.assertFalse(checkpoint["semantic_approved"])
        self.assertFalse(checkpoint["genuine_golden_png_created"])
        self.assertFalse(checkpoint["publication_ready"])
        self.assertFalse(checkpoint["authoritative"])

    def test_rejected_human_review_cannot_open_presentation_request(self) -> None:
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=self._cs277()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._cs278(approved=False)),
            patch(f"{MODULE}.build_composed_candidate_final_presentation_review_request") as build,
        ):
            with self.assertRaisesRegex(ValueError, "HUMAN_REVIEW_NOT_APPROVED"):
                continue_human_review_to_final_presentation_request(
                    self.cs324_path,
                    self.cs278_path,
                    self.root / "blocked",
                    repo_root=self.root,
                )
        build.assert_not_called()

    def test_cs278_must_reference_exact_cs277_from_cs324(self) -> None:
        cs278 = self._cs278()
        cs278["source_cs277_request"] = dict(cs278["source_cs277_request"])
        cs278["source_cs277_request"]["repository_relative_path"] = "other-cs277.json"
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=self._cs277()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=cs278),
        ):
            with self.assertRaisesRegex(ValueError, "CS277_PATH_DRIFT"):
                continue_human_review_to_final_presentation_request(
                    self.cs324_path,
                    self.cs278_path,
                    self.root / "blocked",
                    repo_root=self.root,
                )

    def test_cs279_cannot_arrive_with_premature_final_authority(self) -> None:
        cs279 = self._cs279()
        cs279["publication_ready"] = True
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=self._cs277()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._cs278()),
            patch(f"{MODULE}.build_composed_candidate_final_presentation_review_request", side_effect=self._fake_build),
            patch(f"{MODULE}.verify_composed_candidate_final_presentation_review_request", return_value=cs279),
        ):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:publication_ready"):
                continue_human_review_to_final_presentation_request(
                    self.cs324_path,
                    self.cs278_path,
                    self.root / "blocked",
                    repo_root=self.root,
                )


if __name__ == "__main__":
    unittest.main()

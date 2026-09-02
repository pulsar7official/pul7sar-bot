from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    SCHEMA as CS278_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    SCHEMA as CS277_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    build_composed_candidate_final_presentation_review_request,
    verify_composed_candidate_final_presentation_review_request,
)

MODULE = "engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request"
STORY = "1" * 64
POLICY_SOURCES = (
    "engine/intelligence/brand_approval_evidence.py",
    "engine/intelligence/brand_asset_approval.py",
    "engine/intelligence/brand_master_geometry.py",
    "engine/fonts/resolver.py",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FinalPresentationLineageRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cs278_path = self.root / "cs278.json"
        self.cs278_path.write_text("{}\n", encoding="utf-8")
        self.cs277_path = self.root / "cs277.json"
        self.cs277_path.write_text('{"synthetic":"cs277"}\n', encoding="utf-8")
        runs = self.root / "runs"
        runs.mkdir()
        self.png = runs / "composed_candidate.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\nsynthetic-control-plane-fixture")
        for rel in POLICY_SOURCES:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# synthetic policy fixture: {rel}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _png_binding(self) -> dict:
        return {
            "repository_relative_path": "runs/composed_candidate.png",
            "sha256": _sha(self.png),
            "byte_size": self.png.stat().st_size,
            "width": 1024,
            "height": 1024,
        }

    def _cs277(self) -> dict:
        return {
            "schema": CS277_SCHEMA,
            "receipt_sha256": "7" * 64,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": self._png_binding(),
            "generation_context": {
                "request_id": "qwen-cs262-" + "3" * 64,
                "request_id_source": "exact_cs262_receipt_sha256",
                "seed": 424242,
                "seed_source": "reverified_cs263_to_cs262_inference_receipt",
                "cs262_receipt_sha256": "3" * 64,
            },
            "weighted_score": 9.1,
            "quality_tier": "elite",
        }

    def _cs278_without_context(self) -> dict:
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
            "golden_quality_selector_executed": True,
            "golden_quality_approved": True,
            "human_visual_review_requested": True,
            "human_visual_review_executed": True,
            "human_visual_review_evidence_admitted": True,
            "human_visual_review_approved": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_real_cs278_shape_recovers_context_from_exact_cs277(self) -> None:
        cs277 = self._cs277()
        cs278 = self._cs278_without_context()
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=cs278),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=cs277),
        ):
            path = build_composed_candidate_final_presentation_review_request(
                self.cs278_path,
                self.root / "out",
                repo_root=self.root,
            )
            receipt = verify_composed_candidate_final_presentation_review_request(
                path,
                repo_root=self.root,
            )
        self.assertEqual(receipt["generation_context"], cs277["generation_context"])
        self.assertEqual(receipt["weighted_score"], 9.1)
        self.assertEqual(receipt["quality_tier"], "elite")
        self.assertFalse(receipt["final_presentation_review_approved"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_cs277_story_drift_is_rejected(self) -> None:
        cs277 = self._cs277()
        cs277["story_snapshot_sha256"] = "9" * 64
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._cs278_without_context()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=cs277),
        ):
            with self.assertRaisesRegex(ValueError, "CS277_STORY_DRIFT"):
                build_composed_candidate_final_presentation_review_request(
                    self.cs278_path,
                    self.root / "blocked",
                    repo_root=self.root,
                )

    def test_cs277_png_drift_is_rejected(self) -> None:
        cs277 = self._cs277()
        cs277["composed_candidate_png"] = dict(cs277["composed_candidate_png"])
        cs277["composed_candidate_png"]["sha256"] = "a" * 64
        with (
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_evidence", return_value=self._cs278_without_context()),
            patch(f"{MODULE}.verify_composed_candidate_human_visual_review_request", return_value=cs277),
        ):
            with self.assertRaisesRegex(ValueError, "CS277_PNG_DRIFT"):
                build_composed_candidate_final_presentation_review_request(
                    self.cs278_path,
                    self.root / "blocked",
                    repo_root=self.root,
                )


if __name__ == "__main__":
    unittest.main()

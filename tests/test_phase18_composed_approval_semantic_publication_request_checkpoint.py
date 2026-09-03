from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    SCHEMA as CS282_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
)
from tools.phase18_continue_composed_approval_to_semantic_publication_request import (
    SCHEMA,
    STATUS,
    continue_composed_approval_to_semantic_publication_request,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE = "tools.phase18_continue_composed_approval_to_semantic_publication_request"
STORY = "a" * 64


class FinalSemanticPublicationRequestCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        self.png = self.root / "composed.png"
        self.png.write_bytes(b"genuine-composed-test-bytes")
        raw = self.png.read_bytes()
        self.png_binding = {
            "repository_relative_path": self.png.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
        }
        self.cs281_path = self.root / "cs281.json"
        self.cs281_path.write_text("{}\n", encoding="utf-8")
        self.cs326_path = self.root / "cs326.json"
        self.output = self.root / "out"
        self.cs326 = {
            "schema": "pul7sar-phase18-final-presentation-evidence-composed-approval-checkpoint-v1",
            "status": "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL",
            "authoritative": False,
            "story_snapshot_sha256": STORY,
            "candidate_png": {"sha256": "b" * 64},
            "composed_candidate_png": dict(self.png_binding),
            "cs281_receipt": self.cs281_path.relative_to(ROOT).as_posix(),
            "golden_quality_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        self._write_checkpoint()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_checkpoint(self) -> None:
        self.cs326_path.write_text(json.dumps(self.cs326) + "\n", encoding="utf-8")

    def _cs281(self, **updates):
        value = {
            "schema": CS281_SCHEMA,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": dict(self.png_binding),
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    def _cs282(self, **updates):
        value = {
            "schema": CS282_SCHEMA,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": dict(self.png_binding),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    def _cs283(self, **updates):
        value = {
            "schema": CS283_SCHEMA,
            "story_snapshot_sha256": STORY,
            "composed_candidate_png": dict(self.png_binding),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": False,
            "semantic_publication_allowed": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    @staticmethod
    def _fake_builder(name: str):
        def build(source: Path, output_dir: Path, *, repo_root: Path) -> Path:
            del source, repo_root
            output_dir.mkdir()
            path = output_dir / name
            path.write_text("{}\n", encoding="utf-8")
            return path
        return build

    def test_happy_path_stops_before_semantic_publication_execution(self) -> None:
        with (
            patch(f"{MODULE}.verify_composed_candidate_final_composed_visual_approval", return_value=self._cs281()),
            patch(f"{MODULE}.build_composed_candidate_final_semantic_approval", side_effect=self._fake_builder("cs282.json")) as build282,
            patch(f"{MODULE}.verify_composed_candidate_final_semantic_approval", return_value=self._cs282()),
            patch(f"{MODULE}.build_semantic_publication_execution_request", side_effect=self._fake_builder("cs283.json")) as build283,
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
        ):
            path = continue_composed_approval_to_semantic_publication_request(
                self.cs326_path, self.output, repo_root=ROOT
            )
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["status"], STATUS)
        self.assertFalse(payload["authoritative"])
        self.assertTrue(payload["composed_visual_approved"])
        self.assertTrue(payload["semantic_approved"])
        self.assertTrue(payload["semantic_publication_execution_requested"])
        self.assertFalse(payload["semantic_publication_gate_executed"])
        self.assertFalse(payload["semantic_publication_allowed"])
        self.assertFalse(payload["genuine_golden_png_created"])
        self.assertFalse(payload["publication_ready"])
        self.assertTrue(payload["policy"]["cs284_requires_real_external_execution_evidence"])
        build282.assert_called_once()
        build283.assert_called_once()

    def test_rejects_premature_semantic_authority_in_cs326(self) -> None:
        self.cs326["semantic_approved"] = True
        self._write_checkpoint()
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            continue_composed_approval_to_semantic_publication_request(
                self.cs326_path, self.output, repo_root=ROOT
            )

    def test_rejects_checkpoint_png_byte_drift_before_downstream_build(self) -> None:
        self.cs326["composed_candidate_png"]["sha256"] = "0" * 64
        self._write_checkpoint()
        with self.assertRaisesRegex(ValueError, "COMPOSED_PNG_INVALID_BYTE_DRIFT"):
            continue_composed_approval_to_semantic_publication_request(
                self.cs326_path, self.output, repo_root=ROOT
            )

    def test_rejects_cs281_cross_story_before_cs282(self) -> None:
        with (
            patch(
                f"{MODULE}.verify_composed_candidate_final_composed_visual_approval",
                return_value=self._cs281(story_snapshot_sha256="c" * 64),
            ),
            patch(f"{MODULE}.build_composed_candidate_final_semantic_approval") as build282,
        ):
            with self.assertRaisesRegex(ValueError, "CS281_CROSS_STORY"):
                continue_composed_approval_to_semantic_publication_request(
                    self.cs326_path, self.output, repo_root=ROOT
                )
        build282.assert_not_called()

    def test_rejects_attempted_publication_allowance_from_cs283(self) -> None:
        with (
            patch(f"{MODULE}.verify_composed_candidate_final_composed_visual_approval", return_value=self._cs281()),
            patch(f"{MODULE}.build_composed_candidate_final_semantic_approval", side_effect=self._fake_builder("cs282.json")),
            patch(f"{MODULE}.verify_composed_candidate_final_semantic_approval", return_value=self._cs282()),
            patch(f"{MODULE}.build_semantic_publication_execution_request", side_effect=self._fake_builder("cs283.json")),
            patch(
                f"{MODULE}.verify_semantic_publication_execution_request",
                return_value=self._cs283(semantic_publication_allowed=True),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "CS283_STATE_DRIFT:semantic_publication_allowed"):
                continue_composed_approval_to_semantic_publication_request(
                    self.cs326_path, self.output, repo_root=ROOT
                )

    def test_orchestrator_contains_no_generation_or_cs284_execution_shortcut(self) -> None:
        source = (ROOT / "tools/phase18_continue_composed_approval_to_semantic_publication_request.py").read_text(encoding="utf-8")
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("build_semantic_publication_execution(", source)
        self.assertNotIn("semantic_publication_allowed\": True", source)
        self.assertNotIn("publication_ready\": True", source)
        self.assertNotIn("genuine_golden_png_created\": True", source)


if __name__ == "__main__":
    unittest.main()

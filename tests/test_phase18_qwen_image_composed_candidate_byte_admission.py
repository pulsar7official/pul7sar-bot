from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import SCHEMA as CS271_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    admit_composed_candidate_bytes,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json


def _png(width: int, height: int, tail: bytes = b"") -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x06\x00\x00\x00" + tail


class ComposedCandidateByteAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.cs271 = self.repo / "cs271.json"
        self.cs271.write_text("{}\n", encoding="utf-8")
        self.candidate = self.repo / "candidate.png"
        self.candidate.write_bytes(_png(1024, 1024, b"candidate"))
        self.composed = self.repo / "composed.png"
        self.composed.write_bytes(_png(1024, 1024, b"composed"))
        self.story_sha = "2" * 64

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _binding(self, path: Path, **extra: object) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            **extra,
        }

    def _source(self) -> dict[str, object]:
        return {
            "schema": CS271_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "runner_id": "test-project-native-runner-v1",
            "candidate_png": self._binding(self.candidate, width=1024, height=1024),
            "composed_candidate_png": self._binding(self.composed, width=1024, height=1024),
            "composition_executed": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _patch_source(self):
        return patch(
            "engine.intelligence.qwen_image_composed_candidate_byte_admission.verify_one_shot_composition_execution",
            return_value=self._source(),
        )

    def test_admits_exact_composed_bytes_without_quality_authority(self) -> None:
        with self._patch_source():
            run = admit_composed_candidate_bytes(
                self.cs271, self.repo / "out", repo_root=self.repo
            )
            receipt = verify_composed_candidate_byte_admission(
                run.receipt_path, repo_root=self.repo
            )
        self.assertTrue(receipt["composition_executed"])
        self.assertTrue(receipt["composed_candidate_bytes_admitted_for_post_composition_qa"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_composed_byte_drift_invalidates_admission(self) -> None:
        with self._patch_source():
            run = admit_composed_candidate_bytes(
                self.cs271, self.repo / "out", repo_root=self.repo
            )
            self.composed.write_bytes(self.composed.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_byte_admission(
                    run.receipt_path, repo_root=self.repo
                )

    def test_cs271_byte_drift_invalidates_admission(self) -> None:
        with self._patch_source():
            run = admit_composed_candidate_bytes(
                self.cs271, self.repo / "out", repo_root=self.repo
            )
            self.cs271.write_text('{"changed":true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composed_candidate_byte_admission(
                    run.receipt_path, repo_root=self.repo
                )

    def test_dimension_drift_is_rejected(self) -> None:
        source = self._source()
        source["composed_candidate_png"] = self._binding(
            self.composed, width=512, height=512
        )
        with patch(
            "engine.intelligence.qwen_image_composed_candidate_byte_admission.verify_one_shot_composition_execution",
            return_value=source,
        ):
            with self.assertRaisesRegex(ValueError, "PNG_DIMENSION_DRIFT"):
                admit_composed_candidate_bytes(
                    self.cs271, self.repo / "out", repo_root=self.repo
                )

    def test_premature_golden_authority_is_rejected(self) -> None:
        source = self._source()
        source["genuine_golden_png_created"] = True
        with patch(
            "engine.intelligence.qwen_image_composed_candidate_byte_admission.verify_one_shot_composition_execution",
            return_value=source,
        ):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                admit_composed_candidate_bytes(
                    self.cs271, self.repo / "out", repo_root=self.repo
                )

    def test_existing_output_directory_blocks_reuse(self) -> None:
        out = self.repo / "out"
        out.mkdir()
        with self._patch_source():
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                admit_composed_candidate_bytes(
                    self.cs271, out, repo_root=self.repo
                )


if __name__ == "__main__":
    unittest.main()

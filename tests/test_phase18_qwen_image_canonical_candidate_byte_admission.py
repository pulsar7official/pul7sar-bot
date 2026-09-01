from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

import engine.intelligence.qwen_image_canonical_candidate_byte_admission as admission
from engine.intelligence.qwen_image_canonical_candidate_handoff import (
    SCHEMA as HANDOFF_SCHEMA,
)
from engine.intelligence.qwen_image_one_shot_canonical_inference import (
    ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
)


def _png(width: int = 32, height: int = 24) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height)


def _binding(repo: Path, path: Path) -> dict:
    raw = path.read_bytes()
    return {
        "repository_relative_path": path.relative_to(repo).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _source(candidate: bytes) -> dict:
    return {
        "schema": ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
        "receipt_sha256": "a" * 64,
        "story_snapshot_sha256": "b" * 64,
        "model_id": "Qwen/Qwen-Image-2512",
        "model_revision": "c" * 40,
        "cost_mode": "$0-local",
        "width": 32,
        "height": 24,
        "seed": 7,
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "png": {
            "filename": "canonical_candidate.png",
            "sha256": hashlib.sha256(candidate).hexdigest(),
            "byte_size": len(candidate),
            "width": 32,
            "height": 24,
        },
        "genuine_canonical_inference_executed": True,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }


class CanonicalCandidateByteAdmissionTests(unittest.TestCase):
    def _fixture(self, root: Path):
        repo = root / "repo"
        run = repo / "artifacts" / "sealed"
        run.mkdir(parents=True)
        raw = _png()
        candidate = run / "canonical_candidate.png"
        candidate.write_bytes(raw)
        source_path = run / "canonical_inference_receipt.json"
        source_path.write_text("{}\n", encoding="utf-8")
        handoff_path = run / "canonical_candidate_handoff.json"
        handoff_path.write_text("{}\n", encoding="utf-8")
        source = _source(raw)
        handoff = {
            "schema": HANDOFF_SCHEMA,
            "handoff_sha256": "d" * 64,
            "story_snapshot_sha256": "b" * 64,
            "model_id": "Qwen/Qwen-Image-2512",
            "model_revision": "c" * 40,
            "cost_mode": "$0-local",
            "network_allowed": False,
            "local_files_only": True,
            "source_bindings": {
                "canonical_inference_receipt.json": _binding(repo, source_path),
            },
            "canonical_candidate_png": {
                **_binding(repo, candidate),
                "width": 32,
                "height": 24,
            },
            "inference_settings": {
                "width": 32,
                "height": 24,
                "seed": 7,
                "num_inference_steps": 8,
                "guidance_scale": 1.0,
            },
            "genuine_canonical_inference_executed": True,
            "handoff_sealed": True,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

        def verify_handoff(path, **_kwargs):
            if Path(path).name != "canonical_candidate_handoff.json":
                raise ValueError("QWEN_CANDIDATE_HANDOFF_SCHEMA_STATUS_DRIFT")
            return handoff

        patchers = (
            mock.patch.object(admission, "verify_canonical_candidate_handoff", side_effect=verify_handoff),
            mock.patch.object(
                admission,
                "verify_one_shot_canonical_inference",
                side_effect=lambda *_args, **_kwargs: source,
            ),
        )
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)
        return repo, handoff_path, source_path, candidate, source, handoff

    def test_admits_only_sealed_candidate_without_upgrading_quality_authority(self):
        with tempfile.TemporaryDirectory() as td:
            repo, handoff_path, _source_path, _candidate, _source, _handoff = self._fixture(Path(td))
            out = repo / "artifacts" / "cs303"
            run = admission.admit_canonical_candidate_bytes(handoff_path, out, repo_root=repo)
            result = admission.verify_canonical_candidate_byte_admission(run.receipt_path, repo_root=repo)
            self.assertTrue(result["handoff_sealed"])
            self.assertTrue(result["candidate_bytes_admitted_for_post_generation_qa"])
            self.assertEqual(result["cost_mode"], "$0-local")
            self.assertFalse(result["network_allowed"])
            self.assertTrue(result["local_files_only"])
            self.assertFalse(result["genuine_golden_png_created"])
            self.assertFalse(result["semantic_approved"])
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])

    def test_rejects_bare_canonical_receipt_as_admission_source(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _handoff_path, source_path, _candidate, _source, _handoff = self._fixture(Path(td))
            with self.assertRaisesRegex(ValueError, "HANDOFF_SCHEMA_STATUS_DRIFT"):
                admission.admit_canonical_candidate_bytes(
                    source_path,
                    repo / "artifacts" / "cs303",
                    repo_root=repo,
                )

    def test_rejects_candidate_tamper_after_admission(self):
        with tempfile.TemporaryDirectory() as td:
            repo, handoff_path, _source_path, candidate, _source, _handoff = self._fixture(Path(td))
            run = admission.admit_canonical_candidate_bytes(
                handoff_path, repo / "artifacts" / "cs303", repo_root=repo
            )
            candidate.write_bytes(_png(31, 24))
            with self.assertRaisesRegex(ValueError, "PNG_INVALID_BYTE_DRIFT"):
                admission.verify_canonical_candidate_byte_admission(run.receipt_path, repo_root=repo)

    def test_rejects_premature_semantic_authority_in_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            repo, handoff_path, _source_path, _candidate, _source, handoff = self._fixture(Path(td))
            handoff["semantic_approved"] = True
            with self.assertRaisesRegex(
                ValueError, "PREMATURE_AUTHORITY:semantic_approved"
            ):
                admission.admit_canonical_candidate_bytes(
                    handoff_path, repo / "artifacts" / "cs303", repo_root=repo
                )

    def test_rejects_symlinked_candidate_from_handoff(self):
        with tempfile.TemporaryDirectory() as td:
            repo, handoff_path, _source_path, candidate, _source, handoff = self._fixture(Path(td))
            real = candidate.with_name("real.png")
            candidate.rename(real)
            candidate.symlink_to(real)
            handoff["canonical_candidate_png"] = {
                **_binding(repo, real),
                "repository_relative_path": candidate.relative_to(repo).as_posix(),
                "width": 32,
                "height": 24,
            }
            with self.assertRaisesRegex(ValueError, "PNG_INVALID"):
                admission.admit_canonical_candidate_bytes(
                    handoff_path, repo / "artifacts" / "cs303", repo_root=repo
                )

    def test_rejects_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as td:
            repo, handoff_path, _source_path, _candidate, _source, _handoff = self._fixture(Path(td))
            out = repo / "artifacts" / "cs303"
            out.mkdir()
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                admission.admit_canonical_candidate_bytes(handoff_path, out, repo_root=repo)


if __name__ == "__main__":
    unittest.main()

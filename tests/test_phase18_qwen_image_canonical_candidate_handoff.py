from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_handoff import (
    SOURCE_FILES,
    build_canonical_candidate_handoff,
    verify_canonical_candidate_handoff,
)


class QwenImageCanonicalCandidateHandoffTests(unittest.TestCase):
    @staticmethod
    def _attestation(output: Path) -> dict:
        candidate = output / "canonical_candidate.png"
        raw = candidate.read_bytes()
        import hashlib

        return {
            "story_snapshot_sha256": "a" * 64,
            "model_id": "Qwen/Qwen-Image-2512",
            "model_revision": "b" * 40,
            "inference_settings": {
                "width": 1024,
                "height": 1024,
                "seed": 17,
                "num_inference_steps": 8,
                "guidance_scale": 1.0,
            },
            "canonical_candidate_png": {
                "repository_relative_path": candidate.as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_size": len(raw),
                "width": 1024,
                "height": 1024,
            },
            "genuine_canonical_inference_executed": True,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _materialize(root: Path) -> Path:
        output = root / "runs/output"
        output.mkdir(parents=True)
        (output / "canonical_candidate.png").write_bytes(b"png-bytes")
        for filename in SOURCE_FILES[1:]:
            (output / filename).write_text("{}\n", encoding="utf-8")
        return output

    def test_build_seals_exact_sources_without_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = self._materialize(root)
            attestation = self._attestation(output)
            attestation["canonical_candidate_png"]["repository_relative_path"] = (
                output / "canonical_candidate.png"
            ).relative_to(root).as_posix()
            handoff = output / "canonical_candidate_handoff.json"
            with patch(
                "engine.intelligence.qwen_image_canonical_candidate_handoff.verify_launch_to_output_attestation",
                return_value=attestation,
            ):
                payload = build_canonical_candidate_handoff(output, handoff, repo_root=root)
            self.assertTrue(payload["handoff_sealed"])
            self.assertTrue(payload["genuine_canonical_inference_executed"])
            self.assertFalse(payload["semantic_approved"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertFalse(payload["genuine_golden_png_created"])
            self.assertFalse(payload["publication_ready"])
            self.assertEqual(set(payload["source_bindings"]), set(SOURCE_FILES))
            self.assertTrue(handoff.is_file())

    def test_build_rejects_premature_upstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = self._materialize(root)
            attestation = self._attestation(output)
            attestation["canonical_candidate_png"]["repository_relative_path"] = (
                output / "canonical_candidate.png"
            ).relative_to(root).as_posix()
            attestation["semantic_approved"] = True
            with patch(
                "engine.intelligence.qwen_image_canonical_candidate_handoff.verify_launch_to_output_attestation",
                return_value=attestation,
            ):
                with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
                    build_canonical_candidate_handoff(
                        output,
                        output / "canonical_candidate_handoff.json",
                        repo_root=root,
                    )

    def test_verify_detects_source_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = self._materialize(root)
            attestation = self._attestation(output)
            attestation["canonical_candidate_png"]["repository_relative_path"] = (
                output / "canonical_candidate.png"
            ).relative_to(root).as_posix()
            handoff = output / "canonical_candidate_handoff.json"
            with patch(
                "engine.intelligence.qwen_image_canonical_candidate_handoff.verify_launch_to_output_attestation",
                return_value=attestation,
            ):
                build_canonical_candidate_handoff(output, handoff, repo_root=root)
            (output / "canonical_inference_receipt.json").write_text('{"drift":true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT:canonical_inference_receipt.json"):
                verify_canonical_candidate_handoff(handoff, repo_root=root)

    def test_verify_rejects_handoff_authority_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = self._materialize(root)
            attestation = self._attestation(output)
            attestation["canonical_candidate_png"]["repository_relative_path"] = (
                output / "canonical_candidate.png"
            ).relative_to(root).as_posix()
            handoff = output / "canonical_candidate_handoff.json"
            with patch(
                "engine.intelligence.qwen_image_canonical_candidate_handoff.verify_launch_to_output_attestation",
                return_value=attestation,
            ):
                build_canonical_candidate_handoff(output, handoff, repo_root=root)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            handoff.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DIGEST_MISMATCH"):
                verify_canonical_candidate_handoff(handoff, repo_root=root)


if __name__ == "__main__":
    unittest.main()

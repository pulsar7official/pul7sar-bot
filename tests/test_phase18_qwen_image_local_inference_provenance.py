from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_local_inference_provenance import (
    build_local_inference_provenance,
    verify_local_inference_provenance,
)


class LocalInferenceProvenanceTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path, Path, dict]:
        (root / "engine/intelligence").mkdir(parents=True)
        (root / "tools").mkdir(parents=True)
        (root / "runs/one").mkdir(parents=True)
        (root / "cache/snapshots" / QWEN_IMAGE_2512_REVISION).mkdir(parents=True)
        (root / "engine/intelligence/qwen_image_local_inference_runtime.py").write_text(
            "runtime-contract\n", encoding="utf-8"
        )
        (root / "tools/phase18_run_one_shot_canonical_inference.py").write_text(
            "inference-edge\n", encoding="utf-8"
        )
        receipt = root / "runs/one/canonical_inference_receipt.json"
        receipt.write_text("{\"fixture\":true}\n", encoding="utf-8")
        png = root / "runs/one/canonical_candidate.png"
        png.write_bytes(b"fake-png-bytes")
        verified = {
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": "b" * 64,
            "cost_mode": "$0-local",
            "width": 1024,
            "height": 1024,
            "genuine_canonical_inference_executed": True,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        snapshot = root / "cache/snapshots" / QWEN_IMAGE_2512_REVISION
        return receipt, png, snapshot, verified

    def test_build_binds_local_snapshot_candidate_and_contract_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, _png, snapshot, verified = self._fixture(root)
            output = root / "runs/one/local_inference_provenance.json"
            with patch(
                "engine.intelligence.qwen_image_local_inference_provenance.verify_one_shot_canonical_inference",
                return_value=verified,
            ):
                result = build_local_inference_provenance(
                    receipt, snapshot, output, repo_root=root
                )
            self.assertTrue(output.is_file())
            self.assertTrue(result["local_only_execution_attested"])
            self.assertFalse(result["network_allowed"])
            self.assertTrue(result["local_files_only"])
            self.assertEqual(result["snapshot"]["revision"], QWEN_IMAGE_2512_REVISION)
            self.assertEqual(
                result["canonical_candidate_png"]["repository_relative_path"],
                "runs/one/canonical_candidate.png",
            )
            self.assertEqual(len(result["execution_contract_sources"]), 2)
            self.assertFalse(result["genuine_golden_png_created"])
            self.assertFalse(result["publication_ready"])

    def test_build_rejects_premature_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, _png, snapshot, verified = self._fixture(root)
            verified["semantic_approved"] = True
            with patch(
                "engine.intelligence.qwen_image_local_inference_provenance.verify_one_shot_canonical_inference",
                return_value=verified,
            ):
                with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                    build_local_inference_provenance(
                        receipt,
                        snapshot,
                        root / "runs/one/local_inference_provenance.json",
                        repo_root=root,
                    )

    def test_build_rejects_snapshot_revision_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, _png, _snapshot, verified = self._fixture(root)
            wrong = root / "cache/snapshots" / ("1" * 40)
            wrong.mkdir(parents=True)
            with patch(
                "engine.intelligence.qwen_image_local_inference_provenance.verify_one_shot_canonical_inference",
                return_value=verified,
            ):
                with self.assertRaises(RuntimeError):
                    build_local_inference_provenance(
                        receipt,
                        wrong,
                        root / "runs/one/local_inference_provenance.json",
                        repo_root=root,
                    )

    def test_verify_detects_execution_contract_source_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, _png, snapshot, verified = self._fixture(root)
            output = root / "runs/one/local_inference_provenance.json"
            with patch(
                "engine.intelligence.qwen_image_local_inference_provenance.verify_one_shot_canonical_inference",
                return_value=verified,
            ):
                build_local_inference_provenance(
                    receipt, snapshot, output, repo_root=root
                )
                (root / "engine/intelligence/qwen_image_local_inference_runtime.py").write_text(
                    "mutated\n", encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, "SOURCE_BYTE_DRIFT"):
                    verify_local_inference_provenance(output, repo_root=root)

    def test_verify_rejects_tampered_receipt_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt, _png, snapshot, verified = self._fixture(root)
            output = root / "runs/one/local_inference_provenance.json"
            with patch(
                "engine.intelligence.qwen_image_local_inference_provenance.verify_one_shot_canonical_inference",
                return_value=verified,
            ):
                build_local_inference_provenance(
                    receipt, snapshot, output, repo_root=root
                )
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["network_allowed"] = True
            output.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DIGEST_MISMATCH"):
                verify_local_inference_provenance(output, repo_root=root)


if __name__ == "__main__":
    unittest.main()

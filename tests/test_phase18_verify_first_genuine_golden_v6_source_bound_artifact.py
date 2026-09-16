from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
import phase18_verify_first_genuine_golden_v6_source_bound_artifact as source_bound

SOURCE_SHA = "1" * 40


def _resource_lock() -> dict[str, object]:
    return {
        "schema": "pul7sar-first-genuine-golden-v6-resource-lock-v4",
        "status": "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _replay_result() -> dict[str, object]:
    return {
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_REPLAY_VERIFIED",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "evidence_files_verified": 10,
        "evidence_semantics_verified": True,
        "png": "/artifact/candidate.png",
        "png_sha256": "2" * 64,
        "png_bytes": 123,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class SourceBoundArtifactReplayTests(unittest.TestCase):
    def _fixture(self, root: Path, *, source_sha: str = SOURCE_SHA, flattened: bool = False) -> Path:
        receipt = root / "resource-lock.json"
        receipt.write_text(json.dumps(_resource_lock(), sort_keys=True), encoding="utf-8")
        data = receipt.read_bytes()
        prefix = root if flattened else root / "output"
        binding = prefix / "phase18_gpu_smoke" / "first-genuine-golden-v6-source-binding.json"
        binding.parent.mkdir(parents=True, exist_ok=True)
        binding.write_text(
            json.dumps(
                {
                    "schema": "pul7sar-first-genuine-golden-v6-source-binding-v1",
                    "status": "FIRST_GENUINE_GOLDEN_V6_SOURCE_COMMIT_BOUND",
                    "branch": "phase18/story-intelligence",
                    "candidate": 1,
                    "source_commit_sha": source_sha,
                    "resource_lock_sha256": hashlib.sha256(data).hexdigest(),
                    "resource_lock_bytes": len(data),
                    "human_visual_review_approved": False,
                    "golden_quality_approved": False,
                    "publication_ready": False,
                    "seeds_2_to_4_authorized": False,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return receipt

    def test_accepts_exact_external_source_sha_without_opening_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                result = source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)
            self.assertEqual(result["status"], "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED")
            self.assertEqual(result["source_commit_sha"], SOURCE_SHA)
            self.assertTrue(result["source_commit_verified"])
            self.assertEqual(result["evidence_files_verified"], 10)
            self.assertTrue(result["local_only_model_receipts_verified"])
            self.assertFalse(result["network_download_authorized"])
            self.assertTrue(result["local_files_only"])
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["golden_quality_approved"])

    def test_readiness_manifest_preserves_ten_evidence_and_offline_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                result = source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)
            manifest = source_bound.build_artifact_ready_manifest(result, workflow_run_id=123, workflow_run_attempt=1)
            self.assertEqual(manifest["evidence_files_verified"], 10)
            self.assertTrue(manifest["evidence_semantics_verified"])
            self.assertTrue(manifest["local_only_model_receipts_verified"])
            self.assertFalse(manifest["network_download_authorized"])
            self.assertTrue(manifest["local_files_only"])
            self.assertEqual(manifest["qwen_model_id"], QWEN25_VL_3B_MODEL_ID)
            self.assertEqual(manifest["qwen_model_revision"], QWEN25_VL_3B_REVISION)
            self.assertEqual(manifest["flux_model_id"], FLUX2_KLEIN_4B_MODEL_ID)
            self.assertEqual(manifest["flux_model_revision"], FLUX2_KLEIN_4B_REVISION)
            self.assertFalse(manifest["publication_ready"])
            self.assertFalse(manifest["seeds_2_to_4_authorized"])

    def test_readiness_rejects_legacy_nine_evidence_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            legacy_replay = _replay_result()
            legacy_replay["evidence_files_verified"] = 9
            with mock.patch.object(source_bound, "verify_artifact", return_value=legacy_replay):
                result = source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)
            with self.assertRaisesRegex(RuntimeError, "ARTIFACT_READY_EVIDENCE_NOT_VERIFIED"):
                source_bound.build_artifact_ready_manifest(result, workflow_run_id=123, workflow_run_attempt=1)

    def test_readiness_rejects_offline_provenance_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                result = source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)
            for patch in (
                {"local_only_model_receipts_verified": False},
                {"network_download_authorized": True},
                {"local_files_only": False},
                {"qwen_model_revision": "f" * 40},
                {"flux_model_revision": "e" * 40},
            ):
                with self.subTest(patch=patch):
                    with self.assertRaisesRegex(RuntimeError, "LOCAL_ONLY_NOT_VERIFIED|QWEN_IDENTITY_DRIFT|FLUX_IDENTITY_DRIFT"):
                        source_bound.build_artifact_ready_manifest({**result, **patch}, workflow_run_id=123, workflow_run_attempt=1)

    def test_accepts_upload_artifact_flattened_output_topology(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root, flattened=True)
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                result = source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)
            self.assertEqual(Path(result["source_binding"]), (root / "phase18_gpu_smoke" / "first-genuine-golden-v6-source-binding.json").resolve())

    def test_rejects_binding_to_different_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root, source_sha="3" * 40)
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_COMMIT_DRIFT"):
                    source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)

    def test_rejects_resource_lock_tampering_after_source_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            receipt.write_text(json.dumps({**_resource_lock(), "tampered": True}), encoding="utf-8")
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                with self.assertRaisesRegex(RuntimeError, "RESOURCE_LOCK_SHA_DRIFT|RESOURCE_LOCK_BYTES_DRIFT"):
                    source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)

    def test_rejects_missing_source_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = root / "resource-lock.json"
            receipt.write_text(json.dumps(_resource_lock()), encoding="utf-8")
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_BINDING_ARTIFACT_MISSING"):
                    source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)

    def test_rejects_ambiguous_source_binding_topology(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            flattened = root / "phase18_gpu_smoke" / "first-genuine-golden-v6-source-binding.json"
            flattened.parent.mkdir(parents=True, exist_ok=True)
            flattened.write_bytes((root / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-source-binding.json").read_bytes())
            with mock.patch.object(source_bound, "verify_artifact", return_value=_replay_result()):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_BINDING_ARTIFACT_AMBIGUOUS"):
                    source_bound.verify(receipt, artifact_root=root, expected_source_sha=SOURCE_SHA)


if __name__ == "__main__":
    unittest.main()

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from engine.intelligence.golden_offload_provenance import GoldenOffloadProvenanceLock


class GoldenOffloadProvenanceTests(unittest.TestCase):
    def _write(self, root: Path, name: str, payload: dict) -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        return path

    def _fixtures(self, root: Path, *, selected: str = "sequential_cpu", actual: str = "sequential_cpu"):
        preflight = self._write(
            root,
            "preflight.json",
            {
                "schema": "pul7sar-phase18-flux2-offload-preflight-v1",
                "ready": True,
                "model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "cost_mode": "$0-local",
                "selected_safe_mode": selected,
                "low_vram_host": selected == "sequential_cpu",
                "model_loaded": False,
                "downloads_performed": False,
                "generation_authorized": False,
                "queue_mutated": False,
                "png_created": False,
                "semantic_approved": False,
                "golden_quality_approved": False,
                "publication_ready": False,
            },
        )
        executor = self._write(
            root,
            "executor.json",
            {
                "status": "REAL_VISUAL_PROOF_GENERATED",
                "request_id": "golden-v6-candidate-1",
                "seed": 7007001,
                "payload_sha256": "a" * 64,
                "model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "model_revision": FLUX2_KLEIN_4B_REVISION,
                "cost_mode": "$0-local",
                "resolved_dtype": "bfloat16",
                "precision_quality_tier": "golden_reference",
                "offload_mode_proven": True,
                "actual_offload_mode": actual,
            },
        )
        staging = self._write(
            root,
            "staging.json",
            {
                "schema": "pul7sar-first-genuine-golden-staging-v3",
                "candidate": 1,
                "request_id": "golden-v6-candidate-1",
                "seed": 7007001,
                "payload_sha256": "a" * 64,
                "model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "model_revision": FLUX2_KLEIN_4B_REVISION,
                "cost_mode": "$0-local",
                "resolved_dtype": "bfloat16",
                "precision_quality_tier": "golden_reference",
                "executor_result": str(executor),
                "executor_result_sha256": hashlib.sha256(executor.read_bytes()).hexdigest(),
                "golden_quality_approved": False,
                "publication_ready": False,
            },
        )
        return preflight, staging, executor

    def test_binds_selected_mode_to_actual_executor_mode(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, staging, executor = self._fixtures(root)
            receipt = GoldenOffloadProvenanceLock().verify(
                repository_root=root,
                preflight_receipt=preflight,
                staging_receipt=staging,
            )
            self.assertEqual(receipt["status"], "GOLDEN_FLUX_ACTUAL_OFFLOAD_PROVENANCE_VERIFIED")
            self.assertEqual(receipt["selected_safe_offload_mode"], "sequential_cpu")
            self.assertEqual(receipt["actual_offload_mode"], "sequential_cpu")
            self.assertTrue(receipt["actual_offload_mode_bound"])
            self.assertEqual(receipt["executor_result_sha256"], hashlib.sha256(executor.read_bytes()).hexdigest())
            self.assertFalse(receipt["publication_ready"])

    def test_rejects_selected_actual_mode_mismatch(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, staging, _ = self._fixtures(root, selected="sequential_cpu", actual="model_cpu")
            with self.assertRaisesRegex(RuntimeError, "SELECTED_ACTUAL_MODE_MISMATCH"):
                GoldenOffloadProvenanceLock().verify(
                    repository_root=root,
                    preflight_receipt=preflight,
                    staging_receipt=staging,
                )

    def test_rejects_executor_tampering_after_staging_hash(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, staging, executor = self._fixtures(root)
            payload = json.loads(executor.read_text(encoding="utf-8"))
            payload["actual_offload_mode"] = "model_cpu"
            executor.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EXECUTOR_SHA_DRIFT"):
                GoldenOffloadProvenanceLock().verify(
                    repository_root=root,
                    preflight_receipt=preflight,
                    staging_receipt=staging,
                )

    def test_rejects_unproven_actual_mode(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, staging, executor = self._fixtures(root)
            payload = json.loads(executor.read_text(encoding="utf-8"))
            payload["offload_mode_proven"] = False
            executor.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            staging_payload = json.loads(staging.read_text(encoding="utf-8"))
            staging_payload["executor_result_sha256"] = hashlib.sha256(executor.read_bytes()).hexdigest()
            staging.write_text(json.dumps(staging_payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ACTUAL_MODE_NOT_PROVEN"):
                GoldenOffloadProvenanceLock().verify(
                    repository_root=root,
                    preflight_receipt=preflight,
                    staging_receipt=staging,
                )

    def test_rejects_preflight_authority_drift(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, staging, _ = self._fixtures(root)
            payload = json.loads(preflight.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            preflight.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PREFLIGHT_AUTHORITY_DRIFT"):
                GoldenOffloadProvenanceLock().verify(
                    repository_root=root,
                    preflight_receipt=preflight,
                    staging_receipt=staging,
                )


if __name__ == "__main__":
    unittest.main()

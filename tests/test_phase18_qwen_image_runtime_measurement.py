from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_runtime_measurement import (
    LOAD_MEASUREMENT_SCHEMA,
    QwenImagePipelineLoadObservation,
    QwenImageRuntimeLoadMeasurement,
    sha256_json,
    verify_measurement_admission,
    verify_runtime_load_receipt,
)
from engine.intelligence.qwen_image_measurement_admission import MEASUREMENT_SCHEMA


class QwenImageRuntimeMeasurementTests(unittest.TestCase):
    def _snapshot(self, root: Path) -> Path:
        snapshot = root / "models--Qwen--Qwen-Image-2512" / "snapshots" / QWEN_IMAGE_2512_REVISION
        snapshot.mkdir(parents=True)
        (snapshot / "model_index.json").write_text("{}\n", encoding="utf-8")
        (snapshot / "transformer.safetensors").write_bytes(b"fixture")
        return snapshot

    def _admission(self, snapshot: Path) -> dict:
        payload = {
            "schema": MEASUREMENT_SCHEMA,
            "status": "QWEN_IMAGE_2512_LOCAL_MEASUREMENT_ADMISSION_READY",
            "measurement_ready": True,
            "reasons": [],
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "gpu_name": "fixture-gpu",
            "gpu_total_vram_gb": 24.0,
            "gpu_free_vram_gb": 22.0,
            "native_bf16": True,
            "compute_capability": "8.0",
            "host_available_ram_gb": 80.0,
            "diffusers_version": "0.fixture",
            "qwen_image_pipeline_available": True,
            "exact_snapshot_cached": True,
            "exact_snapshot_path": str(snapshot),
            "cache_free_gib": 100.0,
            "required_free_gib_if_uncached": 8.0,
            "declaration_sha256": "a" * 64,
            "cost_mode": "$0-local",
            "measurement_only": True,
            "runtime_floor_proven": False,
            "local_runtime_qualified": False,
            "model_loaded": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["receipt_sha256"] = sha256_json(payload)
        return payload

    def _success_observation(self) -> QwenImagePipelineLoadObservation:
        return QwenImagePipelineLoadObservation(
            child_exit_code=0,
            pipeline_load_succeeded=True,
            pipeline_class="QwenImagePipeline",
            torch_version="2.fixture",
            cuda_version="12.fixture",
            diffusers_version="0.fixture",
            native_bf16=True,
            gpu_name="fixture-gpu",
            gpu_total_vram_gb=24.0,
            gpu_free_vram_gb_before=22.0,
            gpu_free_vram_gb_after=21.9,
            max_cuda_allocated_gb=0.0,
            max_cuda_reserved_gb=0.0,
            process_max_rss_gb=42.0,
            elapsed_seconds=10.5,
        )

    def test_admission_is_sha_bound_and_requires_exact_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = self._snapshot(Path(tmp))
            admission = self._admission(snapshot)
            digest = verify_measurement_admission(admission)
            self.assertEqual(digest, admission["receipt_sha256"])

            admission["generation_authorized"] = True
            admission["receipt_sha256"] = sha256_json({k: v for k, v in admission.items() if k != "receipt_sha256"})
            with self.assertRaisesRegex(ValueError, "AUTHORITY_DRIFT"):
                verify_measurement_admission(admission)

    def test_successful_pipeline_load_never_proves_runtime_floor(self) -> None:
        measurement = QwenImageRuntimeLoadMeasurement(
            admission_sha256="a" * 64,
            admission_file_sha256="b" * 64,
            exact_snapshot_path=f"/tmp/snapshots/{QWEN_IMAGE_2512_REVISION}",
            observation=self._success_observation(),
        )
        receipt = measurement.as_receipt()
        self.assertEqual(receipt["schema"], LOAD_MEASUREMENT_SCHEMA)
        self.assertEqual(receipt["status"], "QWEN_IMAGE_2512_PIPELINE_LOAD_MEASURED")
        self.assertTrue(receipt["pipeline_load_proven"])
        self.assertFalse(receipt["inference_executed"])
        self.assertFalse(receipt["runtime_floor_proven"])
        self.assertFalse(receipt["generation_authorized"])
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(verify_runtime_load_receipt(receipt), receipt["receipt_sha256"])

    def test_failed_child_cannot_claim_pipeline_load(self) -> None:
        failed = QwenImagePipelineLoadObservation(
            child_exit_code=137,
            pipeline_load_succeeded=False,
            pipeline_class=None,
            torch_version=None,
            cuda_version=None,
            diffusers_version=None,
            native_bf16=None,
            gpu_name=None,
            gpu_total_vram_gb=None,
            gpu_free_vram_gb_before=None,
            gpu_free_vram_gb_after=None,
            max_cuda_allocated_gb=None,
            max_cuda_reserved_gb=None,
            process_max_rss_gb=None,
            elapsed_seconds=None,
            failure_type="ChildProcessTerminated",
            failure_message="OOM-killed",
        )
        receipt = QwenImageRuntimeLoadMeasurement(
            admission_sha256="a" * 64,
            admission_file_sha256="b" * 64,
            exact_snapshot_path=f"/tmp/snapshots/{QWEN_IMAGE_2512_REVISION}",
            observation=failed,
        ).as_receipt()
        self.assertEqual(receipt["status"], "QWEN_IMAGE_2512_PIPELINE_LOAD_FAILED")
        self.assertFalse(receipt["pipeline_load_proven"])
        self.assertFalse(receipt["runtime_floor_proven"])
        self.assertFalse(receipt["generation_authorized"])
        self.assertEqual(verify_runtime_load_receipt(receipt), receipt["receipt_sha256"])

    def test_tampered_runtime_measurement_fails_replay(self) -> None:
        receipt = QwenImageRuntimeLoadMeasurement(
            admission_sha256="a" * 64,
            admission_file_sha256="b" * 64,
            exact_snapshot_path=f"/tmp/snapshots/{QWEN_IMAGE_2512_REVISION}",
            observation=self._success_observation(),
        ).as_receipt()
        receipt["gpu_name"] = "tampered-gpu"
        with self.assertRaisesRegex(ValueError, "SHA_MISMATCH"):
            verify_runtime_load_receipt(receipt)

    def test_measurement_tool_contains_no_image_inference_call(self) -> None:
        tool = (Path(__file__).resolve().parents[1] / "tools" / "phase18_measure_qwen_image_runtime_load.py").read_text(encoding="utf-8")
        self.assertIn("QwenImagePipeline", tool)
        self.assertIn("from_pretrained", tool)
        self.assertIn("inference_executed", (Path(__file__).resolve().parents[1] / "engine" / "intelligence" / "qwen_image_runtime_measurement.py").read_text(encoding="utf-8"))
        self.assertNotIn("pipe(prompt=", tool)
        self.assertNotIn("pipe(\n            prompt=", tool)


if __name__ == "__main__":
    unittest.main()

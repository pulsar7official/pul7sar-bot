from __future__ import annotations

import copy
from pathlib import Path
import unittest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import (
    COST_MODE,
    INFERENCE_MEASUREMENT_SCHEMA,
    PROBE_HEIGHT,
    PROBE_OFFLOAD_MODE,
    PROBE_PROMPT,
    PROBE_SEED,
    PROBE_STEPS,
    PROBE_WIDTH,
    QwenImageInferenceMeasurement,
    QwenImageInferenceObservation,
    sha256_json,
    validate_probe_prompt,
    verify_inference_measurement_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_measure_qwen_image_single_inference.py"


class QwenImageInferenceMeasurementTests(unittest.TestCase):
    def _observation(self, *, success: bool = True) -> QwenImageInferenceObservation:
        return QwenImageInferenceObservation(
            child_exit_code=0 if success else 2,
            inference_succeeded=success,
            pipeline_class="QwenImagePipeline" if success else None,
            offload_mode=PROBE_OFFLOAD_MODE if success else None,
            torch_version="2.x",
            cuda_version="12.x",
            diffusers_version="0.x",
            gpu_name="Synthetic GPU",
            native_bf16=True,
            gpu_total_vram_gb=24.0,
            gpu_free_vram_gb_before=23.0,
            gpu_free_vram_gb_after=20.0 if success else None,
            max_cuda_allocated_gb=2.0 if success else None,
            max_cuda_reserved_gb=3.0 if success else None,
            process_max_rss_gb=30.0,
            elapsed_seconds=12.0,
            output_png_path="output/phase18_gpu_smoke/probe.png" if success else None,
            output_png_sha256="a" * 64 if success else None,
            output_png_size_bytes=1234 if success else None,
            failure_type=None if success else "RuntimeError",
            failure_message=None if success else "synthetic failure",
        )

    def _receipt(self, *, success: bool = True) -> dict:
        measurement = QwenImageInferenceMeasurement(
            load_receipt_sha256="b" * 64,
            load_receipt_file_sha256="c" * 64,
            exact_snapshot_path=f"/tmp/snapshots/{QWEN_IMAGE_2512_REVISION}",
            observation=self._observation(success=success),
        )
        return measurement.as_receipt()

    @staticmethod
    def _resign(receipt: dict) -> dict:
        receipt.pop("receipt_sha256", None)
        receipt["receipt_sha256"] = sha256_json(receipt)
        return receipt

    def test_probe_prompt_is_identity_neutral_and_guarded(self) -> None:
        normalized = validate_probe_prompt(PROBE_PROMPT)
        lowered = normalized.lower()
        self.assertNotIn("pul7sar", lowered)
        self.assertNotIn("pulsar", lowered)
        self.assertIn("no people", lowered)
        self.assertIn("no faces", lowered)
        self.assertIn("no readable text", lowered)
        self.assertIn("no exact sport geometry", lowered)

    def test_successful_probe_still_has_no_canonical_or_publication_authority(self) -> None:
        receipt = self._receipt(success=True)
        self.assertEqual(receipt["schema"], INFERENCE_MEASUREMENT_SCHEMA)
        self.assertEqual(receipt["status"], "QWEN_IMAGE_2512_SINGLE_INFERENCE_MEASURED")
        self.assertEqual(receipt["model_id"], QWEN_IMAGE_2512_MODEL_ID)
        self.assertEqual(receipt["model_revision"], QWEN_IMAGE_2512_REVISION)
        self.assertEqual(receipt["cost_mode"], COST_MODE)
        self.assertTrue(receipt["single_inference_proven"])
        self.assertTrue(receipt["engineering_measurement_only"])
        self.assertFalse(receipt["canonical_pixels_reusable"])
        self.assertFalse(receipt["runtime_floor_proven"])
        self.assertFalse(receipt["local_runtime_qualified"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(verify_inference_measurement_receipt(receipt), receipt["receipt_sha256"])

    def test_probe_contract_is_fixed_and_small(self) -> None:
        receipt = self._receipt(success=True)
        self.assertEqual(receipt["probe_width"], PROBE_WIDTH)
        self.assertEqual(PROBE_WIDTH, 512)
        self.assertEqual(receipt["probe_height"], PROBE_HEIGHT)
        self.assertEqual(PROBE_HEIGHT, 512)
        self.assertEqual(receipt["probe_steps"], PROBE_STEPS)
        self.assertEqual(PROBE_STEPS, 4)
        self.assertEqual(receipt["probe_seed"], PROBE_SEED)
        self.assertEqual(receipt["required_offload_mode"], PROBE_OFFLOAD_MODE)
        self.assertEqual(PROBE_OFFLOAD_MODE, "sequential_cpu")

    def test_authority_drift_is_rejected_even_with_recomputed_sha(self) -> None:
        tampered = copy.deepcopy(self._receipt(success=True))
        tampered["publication_ready"] = True
        self._resign(tampered)
        with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
            verify_inference_measurement_receipt(tampered)

    def test_probe_prompt_entity_leak_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "ENTITY_OR_PLATFORM_LEAK"):
            validate_probe_prompt(PROBE_PROMPT + " PUL7SAR")

    def test_probe_prompt_missing_geometry_marker_is_rejected(self) -> None:
        damaged = PROBE_PROMPT.replace("no exact sport geometry, ", "")
        self.assertNotEqual(damaged, PROBE_PROMPT)
        with self.assertRaisesRegex(ValueError, "SAFETY_MARKER_MISSING"):
            validate_probe_prompt(damaged)

    def test_tool_uses_local_only_bf16_sequential_offload_and_one_image(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        self.assertIn("local_files_only=True", source)
        self.assertIn("torch_dtype=torch.bfloat16", source)
        self.assertIn("enable_sequential_cpu_offload", source)
        self.assertIn('torch.Generator(device="cpu").manual_seed(PROBE_SEED)', source)
        self.assertIn("len(images) != 1", source)
        self.assertIn('images[0].save(png_path, format="PNG")', source)
        self.assertIn("pipeline_cls.from_pretrained", source)

    def test_tool_does_not_call_queue_or_publication_paths(self) -> None:
        source = TOOL.read_text(encoding="utf-8").lower()
        forbidden = (
            "generationjobstore",
            "queue_mutated = true",
            "publication_ready = true",
            "golden_quality_approved = true",
            "semantic_approved = true",
        )
        for token in forbidden:
            self.assertNotIn(token, source)

    def test_failed_probe_remains_non_authoritative(self) -> None:
        receipt = self._receipt(success=False)
        self.assertEqual(receipt["status"], "QWEN_IMAGE_2512_SINGLE_INFERENCE_FAILED")
        self.assertFalse(receipt["single_inference_proven"])
        self.assertFalse(receipt["runtime_floor_proven"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["publication_ready"])
        verify_inference_measurement_receipt(receipt)

    def test_success_outcome_cannot_be_forged_with_recomputed_sha(self) -> None:
        tampered = copy.deepcopy(self._receipt(success=False))
        tampered["status"] = "QWEN_IMAGE_2512_SINGLE_INFERENCE_MEASURED"
        tampered["single_inference_proven"] = True
        self._resign(tampered)
        with self.assertRaisesRegex(ValueError, "OUTCOME_INCONSISTENT"):
            verify_inference_measurement_receipt(tampered)

    def test_success_requires_actual_sequential_offload_and_bf16(self) -> None:
        for field, value, message in (
            ("offload_mode", "model_cpu", "ACTUAL_OFFLOAD_MISMATCH"),
            ("native_bf16", False, "NATIVE_BF16_UNPROVEN"),
        ):
            with self.subTest(field=field):
                tampered = copy.deepcopy(self._receipt(success=True))
                tampered[field] = value
                self._resign(tampered)
                with self.assertRaisesRegex(ValueError, message):
                    verify_inference_measurement_receipt(tampered)

    def test_success_requires_bound_png_evidence(self) -> None:
        for field, value, message in (
            ("output_png_sha256", "not-a-sha", "OUTPUT_SHA_INVALID"),
            ("output_png_size_bytes", 0, "OUTPUT_SIZE_INVALID"),
            ("output_png_path", "output/probe.jpg", "OUTPUT_PATH_INVALID"),
        ):
            with self.subTest(field=field):
                tampered = copy.deepcopy(self._receipt(success=True))
                tampered[field] = value
                self._resign(tampered)
                with self.assertRaisesRegex(ValueError, message):
                    verify_inference_measurement_receipt(tampered)


if __name__ == "__main__":
    unittest.main()

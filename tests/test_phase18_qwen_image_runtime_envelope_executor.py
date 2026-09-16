from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import (
    COST_MODE,
    PROBE_GUIDANCE_SCALE,
    PROBE_PROMPT,
    PROBE_SEED,
    sha256_file,
    sha256_json,
    validate_probe_prompt,
)
from engine.intelligence.qwen_image_runtime_envelope_executor import (
    RUNTIME_ENVELOPE_EXECUTION_SCHEMA,
    build_runtime_envelope_execution_receipt,
    verify_runtime_envelope_execution_receipt,
)
from engine.intelligence.qwen_image_runtime_envelope_plan import (
    DTYPE,
    OFFLOAD_MODE,
    PROBES,
    RUNTIME_ENVELOPE_PLAN_SCHEMA,
)
from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _valid_plan() -> dict:
    payload = {
        "schema": RUNTIME_ENVELOPE_PLAN_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_PLAN_LOCKED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_admission_sha256": SHA_A,
        "source_admission_file_sha256": SHA_B,
        "source_engineering_png_sha256": SHA_C,
        "required_dtype": DTYPE,
        "required_offload_mode": OFFLOAD_MODE,
        "probe_order": [dict(item) for item in PROBES],
        "stop_conditions": [
            "cuda_oom", "child_nonzero_exit", "missing_or_invalid_png", "native_bf16_lost",
            "offload_contract_drift", "telemetry_missing_or_inconsistent",
        ],
        "stop_on_first_failure": True,
        "reuse_same_seed_and_identity_neutral_prompt_family": True,
        "measurement_plan_only": True,
        "engineering_evidence_only": True,
        "runtime_floor_proven": False,
        "local_runtime_qualified": False,
        "canonical_generation_authorized": False,
        "canonical_pixels_reusable": False,
        "queue_mutated": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    payload["plan_sha256"] = sha256_json(payload)
    return payload


def _success_observation(probe: dict, png_path: Path) -> dict:
    png_path.write_bytes(PNG_SIGNATURE + b"phase18-engineering-probe")
    return {
        **dict(probe),
        "seed": PROBE_SEED,
        "guidance_scale": PROBE_GUIDANCE_SCALE,
        "dtype": DTYPE,
        "offload_mode": OFFLOAD_MODE,
        "prompt_sha256": hashlib.sha256(validate_probe_prompt(PROBE_PROMPT).encode("utf-8")).hexdigest(),
        "child_exit_code": 0,
        "inference_succeeded": True,
        "pipeline_class": "QwenImagePipeline",
        "torch_version": "2.x",
        "cuda_version": "12.x",
        "diffusers_version": "0.x",
        "gpu_name": "test-gpu",
        "native_bf16": True,
        "gpu_total_vram_gb": 24.0,
        "gpu_free_vram_gb_before": 20.0,
        "gpu_free_vram_gb_after": 18.0,
        "max_cuda_allocated_gb": 5.0,
        "max_cuda_reserved_gb": 6.0,
        "process_max_rss_gb": 10.0,
        "elapsed_seconds": 12.0,
        "output_png_path": str(png_path),
        "output_png_sha256": sha256_file(png_path),
        "output_png_size_bytes": png_path.stat().st_size,
        "failure_type": None,
        "failure_message": None,
    }


def _failure_observation(probe: dict) -> dict:
    return {
        **dict(probe),
        "seed": PROBE_SEED,
        "guidance_scale": PROBE_GUIDANCE_SCALE,
        "dtype": DTYPE,
        "offload_mode": None,
        "prompt_sha256": hashlib.sha256(validate_probe_prompt(PROBE_PROMPT).encode("utf-8")).hexdigest(),
        "child_exit_code": 2,
        "inference_succeeded": False,
        "pipeline_class": "QwenImagePipeline",
        "torch_version": "2.x",
        "cuda_version": "12.x",
        "diffusers_version": "0.x",
        "gpu_name": "test-gpu",
        "native_bf16": True,
        "gpu_total_vram_gb": 24.0,
        "gpu_free_vram_gb_before": 20.0,
        "gpu_free_vram_gb_after": None,
        "max_cuda_allocated_gb": None,
        "max_cuda_reserved_gb": None,
        "process_max_rss_gb": 10.0,
        "elapsed_seconds": 4.0,
        "output_png_path": None,
        "output_png_sha256": None,
        "output_png_size_bytes": None,
        "failure_type": "OutOfMemoryError",
        "failure_message": "CUDA out of memory",
    }


class QwenRuntimeEnvelopeExecutorTests(unittest.TestCase):
    def test_all_three_successes_remain_non_authoritative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observations = [_success_observation(dict(probe), root / f"{probe['probe_id']}.png") for probe in PROBES]
            receipt = build_runtime_envelope_execution_receipt(
                _valid_plan(), plan_file_sha256=SHA_D,
                exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION),
                observations=observations, repo_root=root,
            )
            self.assertEqual(receipt["schema"], RUNTIME_ENVELOPE_EXECUTION_SCHEMA)
            self.assertTrue(receipt["all_planned_probes_completed"])
            self.assertFalse(receipt["runtime_floor_proven"])
            self.assertFalse(receipt["canonical_generation_authorized"])
            self.assertFalse(receipt["canonical_pixels_reusable"])
            self.assertFalse(receipt["publication_ready"])
            self.assertEqual(verify_runtime_envelope_execution_receipt(receipt, repo_root=root), receipt["execution_sha256"])

    def test_first_failure_is_valid_stopped_evidence_without_claiming_offload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = build_runtime_envelope_execution_receipt(
                _valid_plan(), plan_file_sha256=SHA_D,
                exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION),
                observations=[_failure_observation(dict(PROBES[0]))], repo_root=root,
            )
            self.assertEqual(receipt["status"], "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_STOPPED")
            self.assertTrue(receipt["stopped_on_first_failure"])
            self.assertEqual(receipt["completed_probe_count"], 1)
            self.assertIsNone(receipt["probe_results"][0]["offload_mode"])

    def test_continuing_after_failure_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            later = _success_observation(dict(PROBES[1]), root / "later.png")
            with self.assertRaisesRegex(ValueError, "CONTINUED_AFTER_FAILURE"):
                build_runtime_envelope_execution_receipt(
                    _valid_plan(), plan_file_sha256=SHA_D,
                    exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION),
                    observations=[_failure_observation(dict(PROBES[0])), later], repo_root=root,
                )

    def test_incomplete_success_sequence_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = _success_observation(dict(PROBES[0]), root / "first.png")
            with self.assertRaisesRegex(ValueError, "INCOMPLETE_WITHOUT_FAILURE"):
                build_runtime_envelope_execution_receipt(
                    _valid_plan(), plan_file_sha256=SHA_D,
                    exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=[first], repo_root=root,
                )

    def test_success_without_observed_offload_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = _success_observation(dict(PROBES[0]), root / "first.png")
            first["offload_mode"] = None
            with self.assertRaisesRegex(ValueError, "ACTUAL_OFFLOAD_UNPROVEN"):
                build_runtime_envelope_execution_receipt(
                    _valid_plan(), plan_file_sha256=SHA_D,
                    exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=[first], repo_root=root,
                )

    def test_png_byte_tamper_is_detected_on_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observations = [_success_observation(dict(probe), root / f"{probe['probe_id']}.png") for probe in PROBES]
            receipt = build_runtime_envelope_execution_receipt(
                _valid_plan(), plan_file_sha256=SHA_D,
                exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=observations, repo_root=root,
            )
            Path(observations[1]["output_png_path"]).write_bytes(PNG_SIGNATURE + b"tampered")
            with self.assertRaisesRegex(ValueError, "PNG_(SIZE|SHA)_MISMATCH"):
                verify_runtime_envelope_execution_receipt(receipt, repo_root=root)

    def test_probe_order_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observation = _failure_observation(dict(PROBES[1]))
            with self.assertRaisesRegex(ValueError, "PROBE_PARAMETER_DRIFT"):
                build_runtime_envelope_execution_receipt(
                    _valid_plan(), plan_file_sha256=SHA_D,
                    exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=[observation], repo_root=root,
                )

    def test_authority_forgery_fails_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = build_runtime_envelope_execution_receipt(
                _valid_plan(), plan_file_sha256=SHA_D,
                exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=[_failure_observation(dict(PROBES[0]))], repo_root=root,
            )
            forged = copy.deepcopy(receipt)
            forged["canonical_generation_authorized"] = True
            forged["execution_sha256"] = sha256_json({k: v for k, v in forged.items() if k != "execution_sha256"})
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_runtime_envelope_execution_receipt(forged, repo_root=root)

    def test_runtime_contract_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failed = _failure_observation(dict(PROBES[0]))
            failed["offload_mode"] = "model_cpu_offload"
            with self.assertRaisesRegex(ValueError, "RUNTIME_CONTRACT_DRIFT"):
                build_runtime_envelope_execution_receipt(
                    _valid_plan(), plan_file_sha256=SHA_D,
                    exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION), observations=[failed], repo_root=root,
                )


if __name__ == "__main__":
    unittest.main()

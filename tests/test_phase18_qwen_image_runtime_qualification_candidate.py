from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
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
    build_runtime_envelope_execution_receipt,
)
from engine.intelligence.qwen_image_runtime_envelope_plan import (
    DTYPE,
    OFFLOAD_MODE,
    PROBES,
    RUNTIME_ENVELOPE_PLAN_SCHEMA,
)
from engine.intelligence.qwen_image_runtime_qualification_candidate import (
    RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA,
    build_runtime_qualification_candidate,
    verify_runtime_qualification_candidate,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64
SHA_E = "e" * 64
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
            "cuda_oom",
            "child_nonzero_exit",
            "missing_or_invalid_png",
            "native_bf16_lost",
            "offload_contract_drift",
            "telemetry_missing_or_inconsistent",
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


def _success_observation(probe: dict, png_path: Path, *, index: int = 0) -> dict:
    png_path.write_bytes(PNG_SIGNATURE + f"phase18-qualification-{index}".encode("utf-8"))
    return {
        **dict(probe),
        "seed": PROBE_SEED,
        "guidance_scale": PROBE_GUIDANCE_SCALE,
        "dtype": DTYPE,
        "offload_mode": OFFLOAD_MODE,
        "prompt_sha256": hashlib.sha256(
            validate_probe_prompt(PROBE_PROMPT).encode("utf-8")
        ).hexdigest(),
        "child_exit_code": 0,
        "inference_succeeded": True,
        "pipeline_class": "QwenImagePipeline",
        "torch_version": "2.8.0",
        "cuda_version": "12.8",
        "diffusers_version": "0.35.1",
        "gpu_name": "test-gpu",
        "native_bf16": True,
        "gpu_total_vram_gb": 24.0,
        "gpu_free_vram_gb_before": 20.0 - index,
        "gpu_free_vram_gb_after": 18.0 - index,
        "max_cuda_allocated_gb": 5.0 + index,
        "max_cuda_reserved_gb": 6.0 + index,
        "process_max_rss_gb": 10.0 + index,
        "elapsed_seconds": 12.0 + index,
        "output_png_path": str(png_path),
        "output_png_sha256": sha256_file(png_path),
        "output_png_size_bytes": png_path.stat().st_size,
        "failure_type": None,
        "failure_message": None,
    }


def _complete_execution(root: Path) -> dict:
    observations = [
        _success_observation(dict(probe), root / f"{probe['probe_id']}.png", index=index)
        for index, probe in enumerate(PROBES)
    ]
    return build_runtime_envelope_execution_receipt(
        _valid_plan(),
        plan_file_sha256=SHA_D,
        exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION),
        observations=observations,
        repo_root=root,
    )


class QwenRuntimeQualificationCandidateTests(unittest.TestCase):
    def test_complete_same_host_envelope_builds_non_authoritative_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = build_runtime_qualification_candidate(
                _complete_execution(root),
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            self.assertEqual(candidate["schema"], RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA)
            self.assertTrue(candidate["same_runtime_environment_proven"])
            self.assertTrue(candidate["all_locked_probes_succeeded"])
            self.assertTrue(candidate["candidate_ready_for_explicit_qualification_review"])
            self.assertEqual(candidate["measured_envelope_summary"]["largest_successful_width"], 1024)
            self.assertEqual(candidate["measured_envelope_summary"]["largest_successful_steps"], 8)
            self.assertFalse(candidate["runtime_floor_proven"])
            self.assertFalse(candidate["local_runtime_qualified"])
            self.assertFalse(candidate["canonical_generation_authorized"])
            self.assertFalse(candidate["publication_ready"])
            self.assertEqual(
                verify_runtime_qualification_candidate(candidate),
                candidate["candidate_sha256"],
            )

    def test_mixed_gpu_name_fails_closed_even_when_execution_receipt_is_rehashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution = _complete_execution(root)
            execution["probe_results"][1]["gpu_name"] = "different-gpu"
            execution["execution_sha256"] = sha256_json(
                {k: v for k, v in execution.items() if k != "execution_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "MIXED_RUNTIME_EVIDENCE:gpu_name"):
                build_runtime_qualification_candidate(
                    execution, execution_file_sha256=SHA_E, repo_root=root
                )

    def test_mixed_cuda_version_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution = _complete_execution(root)
            execution["probe_results"][2]["cuda_version"] = "12.9"
            execution["execution_sha256"] = sha256_json(
                {k: v for k, v in execution.items() if k != "execution_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "MIXED_RUNTIME_EVIDENCE:cuda_version"):
                build_runtime_qualification_candidate(
                    execution, execution_file_sha256=SHA_E, repo_root=root
                )

    def test_mixed_total_vram_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution = _complete_execution(root)
            execution["probe_results"][1]["gpu_total_vram_gb"] = 48.0
            execution["execution_sha256"] = sha256_json(
                {k: v for k, v in execution.items() if k != "execution_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "MIXED_RUNTIME_EVIDENCE:gpu_total_vram_gb"):
                build_runtime_qualification_candidate(
                    execution, execution_file_sha256=SHA_E, repo_root=root
                )

    def test_stopped_envelope_cannot_become_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution = _complete_execution(root)
            execution["status"] = "QWEN_IMAGE_2512_RUNTIME_ENVELOPE_STOPPED"
            execution["all_planned_probes_completed"] = False
            execution["stopped_on_first_failure"] = True
            execution["execution_sha256"] = sha256_json(
                {k: v for k, v in execution.items() if k != "execution_sha256"}
            )
            with self.assertRaises(ValueError):
                build_runtime_qualification_candidate(
                    execution, execution_file_sha256=SHA_E, repo_root=root
                )

    def test_authority_forgery_fails_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = build_runtime_qualification_candidate(
                _complete_execution(root),
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            forged = copy.deepcopy(candidate)
            forged["local_runtime_qualified"] = True
            forged["canonical_generation_authorized"] = True
            forged["candidate_sha256"] = sha256_json(
                {k: v for k, v in forged.items() if k != "candidate_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_runtime_qualification_candidate(forged)

    def test_candidate_digest_tamper_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = build_runtime_qualification_candidate(
                _complete_execution(root),
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            candidate["measured_envelope_summary"]["maximum_elapsed_seconds"] = 999.0
            with self.assertRaisesRegex(ValueError, "DIGEST_MISMATCH"):
                verify_runtime_qualification_candidate(candidate)


if __name__ == "__main__":
    unittest.main()

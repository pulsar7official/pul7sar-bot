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
from engine.intelligence.qwen_image_host_bound_runtime_qualification import (
    HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA,
    build_host_bound_runtime_qualification,
    verify_host_bound_runtime_qualification,
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
    build_runtime_qualification_candidate,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64
SHA_E = "e" * 64
SHA_F = "f" * 64
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


def _observation(probe: dict, path: Path, index: int) -> dict:
    path.write_bytes(PNG_SIGNATURE + f"host-bound-{index}".encode())
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
        "output_png_path": str(path),
        "output_png_sha256": sha256_file(path),
        "output_png_size_bytes": path.stat().st_size,
        "failure_type": None,
        "failure_message": None,
    }


def _sources(root: Path) -> tuple[dict, dict]:
    observations = [
        _observation(dict(probe), root / f"{probe['probe_id']}.png", index)
        for index, probe in enumerate(PROBES)
    ]
    execution = build_runtime_envelope_execution_receipt(
        _valid_plan(),
        plan_file_sha256=SHA_D,
        exact_snapshot_path=str(root / QWEN_IMAGE_2512_REVISION),
        observations=observations,
        repo_root=root,
    )
    candidate = build_runtime_qualification_candidate(
        execution,
        execution_file_sha256=SHA_E,
        repo_root=root,
    )
    return execution, candidate


class HostBoundRuntimeQualificationTests(unittest.TestCase):
    def test_complete_replayed_envelope_qualifies_only_exact_host_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            receipt = build_host_bound_runtime_qualification(
                candidate,
                execution,
                candidate_file_sha256=SHA_F,
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            self.assertEqual(receipt["schema"], HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA)
            self.assertTrue(receipt["runtime_envelope_measured"])
            self.assertTrue(receipt["host_bound_runtime_qualified"])
            self.assertEqual(receipt["qualification_scope"], "exact_observed_runtime_only")
            self.assertEqual(receipt["largest_qualified_width"], 1024)
            self.assertEqual(receipt["largest_qualified_height"], 1024)
            self.assertEqual(receipt["largest_qualified_steps"], 8)
            self.assertTrue(receipt["live_host_identity_recheck_required"])
            self.assertFalse(receipt["runtime_floor_proven"])
            self.assertFalse(receipt["local_runtime_qualified"])
            self.assertFalse(receipt["canonical_generation_authorized"])
            self.assertFalse(receipt["publication_ready"])
            self.assertEqual(
                verify_host_bound_runtime_qualification(
                    receipt,
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                ),
                receipt["qualification_sha256"],
            )

    def test_candidate_metadata_forgery_is_rejected_by_source_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            forged = copy.deepcopy(candidate)
            forged["runtime_identity"]["gpu_name"] = "forged-gpu"
            forged["candidate_sha256"] = sha256_json(
                {k: v for k, v in forged.items() if k != "candidate_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "SOURCE_REPLAY_MISMATCH"):
                build_host_bound_runtime_qualification(
                    forged,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                )

    def test_engineering_png_mutation_is_rejected_during_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            Path(execution["probe_results"][1]["output_png_path"]).write_bytes(
                PNG_SIGNATURE + b"mutated"
            )
            with self.assertRaises(ValueError):
                build_host_bound_runtime_qualification(
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                )

    def test_execution_file_sha_must_match_candidate_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            with self.assertRaisesRegex(ValueError, "EXECUTION_FILE_SHA_MISMATCH"):
                build_host_bound_runtime_qualification(
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_A,
                    repo_root=root,
                )

    def test_portable_runtime_floor_cannot_be_forged_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            receipt = build_host_bound_runtime_qualification(
                candidate,
                execution,
                candidate_file_sha256=SHA_F,
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            forged = copy.deepcopy(receipt)
            forged["runtime_floor_proven"] = True
            forged["local_runtime_qualified"] = True
            forged["canonical_generation_authorized"] = True
            forged["qualification_sha256"] = sha256_json(
                {k: v for k, v in forged.items() if k != "qualification_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_host_bound_runtime_qualification(
                    forged,
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                )

    def test_envelope_expansion_is_rejected_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            receipt = build_host_bound_runtime_qualification(
                candidate,
                execution,
                candidate_file_sha256=SHA_F,
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            forged = copy.deepcopy(receipt)
            forged["largest_qualified_width"] = 2048
            forged["qualification_sha256"] = sha256_json(
                {k: v for k, v in forged.items() if k != "qualification_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "ENVELOPE_BOUND_DRIFT"):
                verify_host_bound_runtime_qualification(
                    forged,
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                )

    def test_runtime_identity_drift_is_rejected_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            execution, candidate = _sources(root)
            receipt = build_host_bound_runtime_qualification(
                candidate,
                execution,
                candidate_file_sha256=SHA_F,
                execution_file_sha256=SHA_E,
                repo_root=root,
            )
            forged = copy.deepcopy(receipt)
            forged["runtime_identity"]["cuda_version"] = "99.0"
            forged["runtime_fingerprint_sha256"] = sha256_json(
                {"runtime_identity": forged["runtime_identity"]}
            )
            forged["qualification_sha256"] = sha256_json(
                {k: v for k, v in forged.items() if k != "qualification_sha256"}
            )
            with self.assertRaisesRegex(ValueError, "RUNTIME_IDENTITY_DRIFT"):
                verify_host_bound_runtime_qualification(
                    forged,
                    candidate,
                    execution,
                    candidate_file_sha256=SHA_F,
                    execution_file_sha256=SHA_E,
                    repo_root=root,
                )


if __name__ == "__main__":
    unittest.main()

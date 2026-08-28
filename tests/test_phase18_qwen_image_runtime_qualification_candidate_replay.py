from __future__ import annotations

import copy
import unittest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_runtime_qualification_candidate import (
    RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA,
    verify_runtime_qualification_candidate,
)

SHA_A = "a" * 64
SHA_B = "b" * 64


def _candidate() -> dict:
    payload = {
        "schema": RUNTIME_QUALIFICATION_CANDIDATE_SCHEMA,
        "status": "QWEN_IMAGE_2512_RUNTIME_QUALIFICATION_CANDIDATE_READY",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_execution_sha256": SHA_A,
        "source_execution_file_sha256": SHA_B,
        "runtime_identity": {
            "gpu_name": "test-gpu",
            "gpu_total_vram_gb": 24.0,
            "torch_version": "2.8.0",
            "cuda_version": "12.8",
            "diffusers_version": "0.35.1",
            "pipeline_class": "QwenImagePipeline",
            "dtype": "bfloat16",
            "offload_mode": "sequential_cpu",
            "native_bf16": True,
        },
        "measured_envelope_summary": {
            "largest_successful_width": 1024,
            "largest_successful_height": 1024,
            "largest_successful_steps": 8,
            "minimum_free_vram_before_gb": 18.0,
            "minimum_free_vram_after_gb": 16.0,
            "maximum_cuda_allocated_gb": 7.0,
            "maximum_cuda_reserved_gb": 8.0,
            "maximum_process_rss_gb": 12.0,
            "maximum_elapsed_seconds": 14.0,
        },
        "same_runtime_environment_proven": True,
        "all_locked_probes_succeeded": True,
        "candidate_ready_for_explicit_qualification_review": True,
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
    payload["candidate_sha256"] = sha256_json(payload)
    return payload


class QwenRuntimeQualificationCandidateReplayTests(unittest.TestCase):
    def test_locked_probe_extent_cannot_be_forged_after_rehash(self) -> None:
        forged = copy.deepcopy(_candidate())
        forged["measured_envelope_summary"]["largest_successful_width"] = 2048
        forged["candidate_sha256"] = sha256_json({k: v for k, v in forged.items() if k != "candidate_sha256"})
        with self.assertRaisesRegex(ValueError, "SUMMARY_GEOMETRY_DRIFT"):
            verify_runtime_qualification_candidate(forged)

    def test_cuda_summary_inconsistency_fails_after_rehash(self) -> None:
        forged = copy.deepcopy(_candidate())
        forged["measured_envelope_summary"]["maximum_cuda_allocated_gb"] = 9.0
        forged["candidate_sha256"] = sha256_json({k: v for k, v in forged.items() if k != "candidate_sha256"})
        with self.assertRaisesRegex(ValueError, "SUMMARY_CUDA_INCONSISTENT"):
            verify_runtime_qualification_candidate(forged)

    def test_free_vram_above_total_vram_fails_after_rehash(self) -> None:
        forged = copy.deepcopy(_candidate())
        forged["measured_envelope_summary"]["minimum_free_vram_before_gb"] = 25.0
        forged["candidate_sha256"] = sha256_json({k: v for k, v in forged.items() if k != "candidate_sha256"})
        with self.assertRaisesRegex(ValueError, "SUMMARY_VRAM_INCONSISTENT"):
            verify_runtime_qualification_candidate(forged)


if __name__ == "__main__":
    unittest.main()

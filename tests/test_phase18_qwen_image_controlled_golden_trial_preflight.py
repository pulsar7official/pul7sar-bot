from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
    REQUIRED_FRESH_GATE_EVIDENCE,
    REQUIRED_PIXEL_BOUNDARIES,
    REQUIRED_POST_GENERATION_GATES,
    build_controlled_golden_trial_preflight_contract,
    verify_controlled_golden_trial_preflight_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64


def _qualification() -> dict:
    return {
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "host_bound_runtime_qualified": True,
        "qualification_scope": "exact_observed_runtime_only",
        "live_host_identity_recheck_required": True,
        "controlled_golden_trial_ready_for_gate_review": True,
        "runtime_identity": {
            "gpu_name": "test-gpu",
            "gpu_total_vram_gb": 24.0,
            "torch_version": "2.8.0",
            "cuda_version": "12.8",
            "diffusers_version": "0.35.1",
            "pipeline_class": "QwenImagePipeline",
            "native_bf16": True,
            "dtype": "bfloat16",
            "offload_mode": "sequential_cpu",
        },
        "runtime_fingerprint_sha256": SHA_D,
    }


def _build() -> tuple[dict, dict, dict, dict]:
    qualification = _qualification()
    candidate = {"candidate": "fixture"}
    execution = {"execution": "fixture"}
    with patch(
        "engine.intelligence.qwen_image_controlled_golden_trial_preflight.verify_host_bound_runtime_qualification",
        return_value=SHA_A,
    ):
        contract = build_controlled_golden_trial_preflight_contract(
            qualification,
            candidate,
            execution,
            qualification_file_sha256=SHA_B,
            candidate_file_sha256=SHA_C,
            execution_file_sha256=SHA_D,
        )
    return contract, qualification, candidate, execution


def _verify(contract: dict, qualification: dict, candidate: dict, execution: dict) -> str:
    with patch(
        "engine.intelligence.qwen_image_controlled_golden_trial_preflight.verify_host_bound_runtime_qualification",
        return_value=SHA_A,
    ):
        return verify_controlled_golden_trial_preflight_contract(
            contract,
            qualification,
            candidate,
            execution,
            qualification_file_sha256=SHA_B,
            candidate_file_sha256=SHA_C,
            execution_file_sha256=SHA_D,
        )


class ControlledGoldenTrialPreflightTests(unittest.TestCase):
    def test_contract_locks_requirements_without_granting_generation_authority(self) -> None:
        contract, qualification, candidate, execution = _build()
        self.assertEqual(contract["schema"], CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA)
        self.assertTrue(contract["preflight_contract_locked"])
        self.assertTrue(contract["live_same_host_recheck_required"])
        self.assertTrue(contract["fresh_story_gate_evidence_required"])
        self.assertEqual(tuple(contract["fresh_gate_evidence_required"]), REQUIRED_FRESH_GATE_EVIDENCE)
        self.assertEqual(tuple(contract["pixel_boundaries_required"]), REQUIRED_PIXEL_BOUNDARIES)
        self.assertEqual(tuple(contract["post_generation_gates_required"]), REQUIRED_POST_GENERATION_GATES)
        self.assertEqual(contract["golden_minimum_score"], 8.5)
        self.assertEqual(contract["elite_quality_score"], 9.0)
        self.assertFalse(contract["controlled_trial_preflight_valid"])
        self.assertFalse(contract["canonical_generation_authorized"])
        self.assertFalse(contract["genuine_golden_png_created"])
        self.assertFalse(contract["publication_ready"])
        self.assertEqual(_verify(contract, qualification, candidate, execution), contract["preflight_contract_sha256"])

    def test_host_qualification_replay_is_mandatory(self) -> None:
        qualification = _qualification()
        with patch(
            "engine.intelligence.qwen_image_controlled_golden_trial_preflight.verify_host_bound_runtime_qualification",
            side_effect=ValueError("upstream replay failed"),
        ):
            with self.assertRaisesRegex(ValueError, "upstream replay failed"):
                build_controlled_golden_trial_preflight_contract(
                    qualification,
                    {},
                    {},
                    qualification_file_sha256=SHA_B,
                    candidate_file_sha256=SHA_C,
                    execution_file_sha256=SHA_D,
                )

    def test_live_host_recheck_boundary_cannot_be_removed(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["live_same_host_recheck_required"] = False
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "REQUIRED_BOUNDARY_MISSING"):
            _verify(forged, qualification, candidate, execution)

    def test_story_gate_set_cannot_be_weakened_after_rehash(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["fresh_gate_evidence_required"].remove("entity_identity_verification")
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "STORY_GATE_SET_DRIFT"):
            _verify(forged, qualification, candidate, execution)

    def test_pixel_boundary_set_cannot_be_weakened_after_rehash(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["pixel_boundaries_required"].remove("generated_branding_forbidden")
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "PIXEL_BOUNDARY_DRIFT"):
            _verify(forged, qualification, candidate, execution)

    def test_post_generation_semantic_publication_gate_cannot_be_removed(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["post_generation_gates_required"].remove("semantic_publication_gate")
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "POST_GATE_SET_DRIFT"):
            _verify(forged, qualification, candidate, execution)

    def test_quality_thresholds_cannot_be_lowered_after_rehash(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["golden_minimum_score"] = 7.0
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "QUALITY_THRESHOLD_DRIFT"):
            _verify(forged, qualification, candidate, execution)

    def test_generation_authority_cannot_be_forged_after_rehash(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["controlled_trial_preflight_valid"] = True
        forged["canonical_generation_authorized"] = True
        forged["genuine_golden_png_created"] = True
        forged["publication_ready"] = True
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
            _verify(forged, qualification, candidate, execution)

    def test_runtime_identity_drift_is_rejected(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["expected_runtime_identity"]["gpu_name"] = "other-gpu"
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "RUNTIME_IDENTITY_DRIFT"):
            _verify(forged, qualification, candidate, execution)

    def test_zero_cost_mode_is_immutable(self) -> None:
        contract, qualification, candidate, execution = _build()
        forged = copy.deepcopy(contract)
        forged["cost_mode"] = "paid-remote"
        forged["preflight_contract_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "preflight_contract_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "COST_MODE_MISMATCH"):
            _verify(forged, qualification, candidate, execution)


if __name__ == "__main__":
    unittest.main()

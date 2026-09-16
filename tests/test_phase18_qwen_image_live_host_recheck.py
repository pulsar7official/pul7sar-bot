from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_host_recheck import (
    LIVE_HOST_RECHECK_SCHEMA,
    build_live_host_recheck_receipt,
    verify_live_host_recheck_receipt,
)

SHA_A = "a" * 64


def _identity() -> dict:
    return {
        "gpu_name": "test-gpu",
        "gpu_total_vram_gb": 24.0,
        "torch_version": "2.8.0",
        "cuda_version": "12.8",
        "diffusers_version": "0.35.1",
        "pipeline_class": "QwenImagePipeline",
        "dtype": "bfloat16",
        "offload_mode": "sequential_cpu",
        "native_bf16": True,
    }


def _contract() -> dict:
    identity = _identity()
    return {
        "preflight_contract_sha256": SHA_A,
        "expected_runtime_identity": identity,
        "expected_runtime_fingerprint_sha256": sha256_json({"runtime_identity": identity}),
    }


def _build(live_identity: dict | None = None) -> tuple[dict, dict]:
    contract = _contract()
    with patch(
        "engine.intelligence.qwen_image_live_host_recheck.verify_controlled_golden_trial_preflight_contract",
        return_value=SHA_A,
    ):
        receipt = build_live_host_recheck_receipt(
            contract,
            {},
            {},
            {},
            qualification_file_sha256="b" * 64,
            candidate_file_sha256="c" * 64,
            execution_file_sha256="d" * 64,
            live_identity=live_identity or _identity(),
        )
    return receipt, contract


class QwenImageLiveHostRecheckTests(unittest.TestCase):
    def test_exact_live_identity_match_is_evidence_only(self) -> None:
        receipt, contract = _build()
        self.assertEqual(receipt["schema"], LIVE_HOST_RECHECK_SCHEMA)
        self.assertEqual(receipt["cost_mode"], COST_MODE)
        self.assertTrue(receipt["live_host_recheck_passed"])
        self.assertTrue(receipt["exact_observed_runtime_match"])
        self.assertFalse(receipt["model_weights_loaded"])
        self.assertFalse(receipt["inference_executed"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["controlled_trial_preflight_valid"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(verify_live_host_recheck_receipt(receipt, contract), receipt["live_host_recheck_sha256"])

    def test_gpu_name_drift_is_rejected(self) -> None:
        live = _identity()
        live["gpu_name"] = "other-gpu"
        with self.assertRaisesRegex(ValueError, "IDENTITY_MISMATCH:gpu_name"):
            _build(live)

    def test_cuda_version_drift_is_rejected(self) -> None:
        live = _identity()
        live["cuda_version"] = "12.7"
        with self.assertRaisesRegex(ValueError, "IDENTITY_MISMATCH:cuda_version"):
            _build(live)

    def test_total_vram_drift_is_rejected(self) -> None:
        live = _identity()
        live["gpu_total_vram_gb"] = 23.0
        with self.assertRaisesRegex(ValueError, "IDENTITY_MISMATCH:gpu_total_vram_gb"):
            _build(live)

    def test_native_bf16_must_remain_true(self) -> None:
        live = _identity()
        live["native_bf16"] = False
        with self.assertRaisesRegex(ValueError, "BF16_UNPROVEN"):
            _build(live)

    def test_runtime_mode_cannot_drift(self) -> None:
        live = _identity()
        live["offload_mode"] = "model_cpu"
        with self.assertRaisesRegex(ValueError, "RUNTIME_MODE_DRIFT"):
            _build(live)

    def test_authority_cannot_be_forged_after_rehash(self) -> None:
        receipt, contract = _build()
        forged = copy.deepcopy(receipt)
        forged["canonical_generation_authorized"] = True
        forged["publication_ready"] = True
        forged["live_host_recheck_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "live_host_recheck_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
            verify_live_host_recheck_receipt(forged, contract)

    def test_contract_fingerprint_drift_is_rejected(self) -> None:
        receipt, contract = _build()
        forged_contract = copy.deepcopy(contract)
        forged_contract["expected_runtime_fingerprint_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "EXPECTED_FINGERPRINT_DRIFT|FINGERPRINT_MISMATCH"):
            verify_live_host_recheck_receipt(receipt, forged_contract)

    def test_receipt_identity_tampering_is_detected_even_after_rehash(self) -> None:
        receipt, contract = _build()
        forged = copy.deepcopy(receipt)
        forged["live_runtime_identity"]["torch_version"] = "9.9.9"
        forged["live_runtime_fingerprint_sha256"] = sha256_json(
            {"runtime_identity": forged["live_runtime_identity"]}
        )
        forged["live_host_recheck_sha256"] = sha256_json(
            {k: v for k, v in forged.items() if k != "live_host_recheck_sha256"}
        )
        with self.assertRaisesRegex(ValueError, "IDENTITY_DRIFT"):
            verify_live_host_recheck_receipt(forged, contract)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_runtime_envelope_plan import (
    DTYPE,
    OFFLOAD_MODE,
    PROBES,
    RUNTIME_ENVELOPE_PLAN_SCHEMA,
    STOP_CONDITIONS,
    build_runtime_envelope_plan,
    verify_runtime_envelope_plan,
)
from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


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
        "stop_conditions": list(STOP_CONDITIONS),
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


class QwenRuntimeEnvelopePlanTests(unittest.TestCase):
    def test_valid_plan_replays(self) -> None:
        plan = _valid_plan()
        self.assertEqual(verify_runtime_envelope_plan(plan), plan["plan_sha256"])

    def test_builder_binds_verified_admission(self) -> None:
        admission = {"schema": "pul7sar-phase18-qwen-image-2512-runtime-envelope-admission-v1", "source_engineering_png_sha256": SHA_C}
        with patch("engine.intelligence.qwen_image_runtime_envelope_plan.verify_runtime_envelope_admission", return_value=SHA_A):
            plan = build_runtime_envelope_plan(admission, admission_file_sha256=SHA_B)
        self.assertEqual(plan["source_admission_sha256"], SHA_A)
        self.assertFalse(plan["canonical_generation_authorized"])
        self.assertFalse(plan["runtime_floor_proven"])

    def test_probe_order_drift_fails_closed(self) -> None:
        plan = _valid_plan()
        plan["probe_order"] = list(reversed(plan["probe_order"]))
        plan["plan_sha256"] = sha256_json({k: v for k, v in plan.items() if k != "plan_sha256"})
        with self.assertRaisesRegex(ValueError, "PROBE_ORDER_DRIFT"):
            verify_runtime_envelope_plan(plan)

    def test_authority_drift_fails_even_with_rehashed_plan(self) -> None:
        plan = _valid_plan()
        plan["canonical_generation_authorized"] = True
        plan["plan_sha256"] = sha256_json({k: v for k, v in plan.items() if k != "plan_sha256"})
        with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
            verify_runtime_envelope_plan(plan)

    def test_runtime_contract_drift_fails_closed(self) -> None:
        plan = _valid_plan()
        plan["required_offload_mode"] = "model_cpu_offload"
        plan["plan_sha256"] = sha256_json({k: v for k, v in plan.items() if k != "plan_sha256"})
        with self.assertRaisesRegex(ValueError, "RUNTIME_CONTRACT_DRIFT"):
            verify_runtime_envelope_plan(plan)

    def test_stop_policy_cannot_be_weakened(self) -> None:
        plan = _valid_plan()
        plan["stop_on_first_failure"] = False
        plan["plan_sha256"] = sha256_json({k: v for k, v in plan.items() if k != "plan_sha256"})
        with self.assertRaisesRegex(ValueError, "STOP_POLICY_DRIFT"):
            verify_runtime_envelope_plan(plan)


if __name__ == "__main__":
    unittest.main()

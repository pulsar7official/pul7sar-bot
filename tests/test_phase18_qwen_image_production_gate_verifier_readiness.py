from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_production_gate_verifier_readiness import (
    audit_production_gate_verifier_readiness,
    verify_production_gate_verifier_readiness,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)


def _verifier(gate_id: str):
    def verifier(evidence_path, story_snapshot_sha256, receipt):
        raise AssertionError("readiness audit must never execute semantic verifier code")

    verifier.PUL7SAR_VERIFIER_ID = f"pul7sar.production.{gate_id}"
    verifier.PUL7SAR_VERIFIER_VERSION = "1.0.0"
    return verifier


class ProductionGateVerifierReadinessTests(unittest.TestCase):
    def test_canonical_registry_is_explicitly_not_ready_until_real_adapters_exist(self):
        receipt = audit_production_gate_verifier_readiness(GATE_REPLAY_VERIFIERS)
        self.assertFalse(receipt["all_production_verifiers_bound"])
        self.assertEqual(receipt["missing_gate_ids"], list(REQUIRED_FRESH_GATE_EVIDENCE))
        self.assertEqual(receipt["invalid_gate_ids"], [])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["publication_ready"])

    def test_complete_compatible_registry_can_be_ready_without_granting_authority(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        receipt = audit_production_gate_verifier_readiness(registry)
        self.assertTrue(receipt["all_production_verifiers_bound"])
        self.assertEqual(receipt["missing_gate_ids"], [])
        self.assertEqual(receipt["invalid_gate_ids"], [])
        self.assertFalse(receipt["production_semantic_replay_executed"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["genuine_golden_png_created"])

    def test_extra_gate_fails_closed(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        registry["not_a_real_gate"] = _verifier("not_a_real_gate")
        with self.assertRaisesRegex(ValueError, "QWEN_PRODUCTION_VERIFIER_REGISTRY_EXTRA_GATE"):
            audit_production_gate_verifier_readiness(registry)

    def test_incompatible_signature_is_invalid(self):
        def bad_verifier(one_argument):
            return one_argument

        bad_verifier.PUL7SAR_VERIFIER_ID = "pul7sar.production.bad"
        bad_verifier.PUL7SAR_VERIFIER_VERSION = "1.0.0"
        registry = {"fact_lock": bad_verifier}
        receipt = audit_production_gate_verifier_readiness(registry)
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(receipt["all_production_verifiers_bound"])

    def test_missing_identity_metadata_is_invalid(self):
        def anonymous_verifier(evidence_path, story_snapshot_sha256, receipt):
            return {}

        receipt = audit_production_gate_verifier_readiness({"fact_lock": anonymous_verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])

    def test_duplicate_verifier_identity_is_invalid(self):
        first = _verifier("shared")
        second = _verifier("shared")
        registry = {
            REQUIRED_FRESH_GATE_EVIDENCE[0]: first,
            REQUIRED_FRESH_GATE_EVIDENCE[1]: second,
        }
        receipt = audit_production_gate_verifier_readiness(registry)
        self.assertIn(REQUIRED_FRESH_GATE_EVIDENCE[1], receipt["invalid_gate_ids"])
        self.assertFalse(receipt["all_production_verifiers_bound"])

    def test_tampered_authority_fails_replay_even_after_rehash(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        receipt = audit_production_gate_verifier_readiness(registry)
        receipt["canonical_generation_authorized"] = True
        receipt["production_gate_verifier_readiness_sha256"] = sha256_json(
            {k: v for k, v in receipt.items() if k != "production_gate_verifier_readiness_sha256"}
        )
        with self.assertRaisesRegex(
            ValueError,
            "QWEN_PRODUCTION_VERIFIER_READINESS_RECEIPT_MISMATCH",
        ):
            verify_production_gate_verifier_readiness(receipt, registry)

    def test_registry_module_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "QWEN_PRODUCTION_VERIFIER_REGISTRY_MODULE_DRIFT"):
            audit_production_gate_verifier_readiness({}, registry_module="tests.fake_registry")


if __name__ == "__main__":
    unittest.main()

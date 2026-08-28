from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
import engine.intelligence.qwen_image_production_gate_verifier_readiness as readiness_module
from engine.intelligence.qwen_image_production_gate_verifier_readiness import (
    audit_production_gate_verifier_readiness,
    verify_production_gate_verifier_readiness,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)


def _source_callable(source_module: str, source_callable: str):
    def source(evidence_path, story_snapshot_sha256, receipt):
        return {}

    source.__module__ = source_module
    source.__name__ = source_callable
    source.__qualname__ = source_callable
    return source


def _verifier(
    gate_id: str,
    *,
    source_module: str | None = None,
    source_callable: str | None = None,
    bind_source_object: bool = True,
):
    def verifier(evidence_path, story_snapshot_sha256, receipt):
        raise AssertionError("readiness audit must never execute semantic verifier code")

    source_module = source_module or f"engine.intelligence.production.{gate_id}"
    source_callable = source_callable or f"verify_{gate_id}"
    verifier.PUL7SAR_VERIFIER_ID = f"pul7sar.production.{gate_id}"
    verifier.PUL7SAR_VERIFIER_VERSION = "1.0.0"
    verifier.PUL7SAR_VERIFIER_GATE_ID = gate_id
    verifier.PUL7SAR_PRODUCTION_BACKED = True
    verifier.PUL7SAR_SOURCE_MODULE = source_module
    verifier.PUL7SAR_SOURCE_CALLABLE = source_callable
    if bind_source_object:
        verifier.PUL7SAR_SOURCE_CALLABLE_OBJECT = _source_callable(
            source_module,
            source_callable,
        )
    return verifier


def _audit(registry):
    production_source_path = str(Path(readiness_module.__file__).resolve())
    with patch.object(
        readiness_module.inspect,
        "getsourcefile",
        return_value=production_source_path,
    ):
        return audit_production_gate_verifier_readiness(registry)


def _verify(receipt, registry):
    production_source_path = str(Path(readiness_module.__file__).resolve())
    with patch.object(
        readiness_module.inspect,
        "getsourcefile",
        return_value=production_source_path,
    ):
        return verify_production_gate_verifier_readiness(receipt, registry)


class ProductionGateVerifierReadinessTests(unittest.TestCase):
    def test_canonical_registry_is_explicitly_not_ready_until_real_adapters_exist(self):
        receipt = audit_production_gate_verifier_readiness(GATE_REPLAY_VERIFIERS)
        self.assertFalse(receipt["all_production_verifiers_bound"])
        self.assertFalse(receipt["all_bindings_provenance_complete"])
        self.assertFalse(receipt["all_source_objects_bound"])
        self.assertFalse(receipt["all_source_files_byte_bound"])
        self.assertEqual(receipt["missing_gate_ids"], list(REQUIRED_FRESH_GATE_EVIDENCE))
        self.assertEqual(receipt["invalid_gate_ids"], [])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["publication_ready"])

    def test_complete_compatible_registry_can_be_structurally_ready_without_authority(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        receipt = _audit(registry)
        self.assertTrue(receipt["all_production_verifiers_bound"])
        self.assertTrue(receipt["all_bindings_provenance_complete"])
        self.assertTrue(receipt["all_source_objects_bound"])
        self.assertTrue(receipt["all_source_files_byte_bound"])
        self.assertEqual(receipt["missing_gate_ids"], [])
        self.assertEqual(receipt["invalid_gate_ids"], [])
        self.assertFalse(receipt["production_semantic_replay_executed"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["genuine_golden_png_created"])

    def test_successful_binding_records_source_file_sha_and_size(self):
        receipt = _audit({"fact_lock": _verifier("fact_lock")})
        binding = receipt["bindings"][0]
        self.assertEqual(binding["binding_status"], "ready")
        self.assertTrue(binding["source_object_bound"])
        self.assertTrue(binding["source_object_matches_declaration"])
        self.assertTrue(binding["source_signature_compatible"])
        self.assertTrue(binding["source_file_byte_bound"])
        self.assertIsInstance(binding["source_repository_relative_path"], str)
        self.assertGreater(binding["source_file_byte_size"], 0)
        self.assertEqual(len(binding["source_file_sha256"]), 64)

    def test_extra_gate_fails_closed(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        registry["not_a_real_gate"] = _verifier("not_a_real_gate")
        with self.assertRaisesRegex(ValueError, "QWEN_PRODUCTION_VERIFIER_REGISTRY_EXTRA_GATE"):
            _audit(registry)

    def test_incompatible_signature_is_invalid(self):
        def bad_verifier(one_argument):
            return one_argument

        source = _source_callable(
            "engine.intelligence.production.fact_lock",
            "verify_fact_lock",
        )
        bad_verifier.PUL7SAR_VERIFIER_ID = "pul7sar.production.fact_lock"
        bad_verifier.PUL7SAR_VERIFIER_VERSION = "1.0.0"
        bad_verifier.PUL7SAR_VERIFIER_GATE_ID = "fact_lock"
        bad_verifier.PUL7SAR_PRODUCTION_BACKED = True
        bad_verifier.PUL7SAR_SOURCE_MODULE = "engine.intelligence.production.fact_lock"
        bad_verifier.PUL7SAR_SOURCE_CALLABLE = "verify_fact_lock"
        bad_verifier.PUL7SAR_SOURCE_CALLABLE_OBJECT = source
        receipt = _audit({"fact_lock": bad_verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(receipt["all_production_verifiers_bound"])

    def test_missing_identity_metadata_is_invalid(self):
        def anonymous_verifier(evidence_path, story_snapshot_sha256, receipt):
            return {}

        receipt = _audit({"fact_lock": anonymous_verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])

    def test_missing_provenance_metadata_is_invalid(self):
        def weak_verifier(evidence_path, story_snapshot_sha256, receipt):
            return {}

        weak_verifier.PUL7SAR_VERIFIER_ID = "pul7sar.production.fact_lock"
        weak_verifier.PUL7SAR_VERIFIER_VERSION = "1.0.0"
        receipt = _audit({"fact_lock": weak_verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(receipt["bindings"][0]["provenance_complete"])

    def test_string_only_provenance_is_no_longer_sufficient(self):
        verifier = _verifier("fact_lock", bind_source_object=False)
        receipt = _audit({"fact_lock": verifier})
        binding = receipt["bindings"][0]
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(binding["source_object_bound"])
        self.assertFalse(binding["source_file_byte_bound"])
        self.assertFalse(binding["provenance_complete"])

    def test_declared_gate_mismatch_is_invalid(self):
        verifier = _verifier("entity_identity_verification")
        receipt = _audit({"fact_lock": verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])

    def test_source_object_declaration_mismatch_is_invalid(self):
        verifier = _verifier("fact_lock")
        verifier.PUL7SAR_SOURCE_CALLABLE = "verify_something_else"
        receipt = _audit({"fact_lock": verifier})
        binding = receipt["bindings"][0]
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(binding["source_object_matches_declaration"])
        self.assertFalse(binding["source_file_byte_bound"])

    def test_source_object_signature_must_accept_replay_call(self):
        verifier = _verifier("fact_lock")

        def bad_source(one_argument):
            return one_argument

        bad_source.__module__ = verifier.PUL7SAR_SOURCE_MODULE
        bad_source.__name__ = verifier.PUL7SAR_SOURCE_CALLABLE
        bad_source.__qualname__ = verifier.PUL7SAR_SOURCE_CALLABLE
        verifier.PUL7SAR_SOURCE_CALLABLE_OBJECT = bad_source
        receipt = _audit({"fact_lock": verifier})
        binding = receipt["bindings"][0]
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(binding["source_signature_compatible"])
        self.assertFalse(binding["source_file_byte_bound"])

    def test_repository_external_source_file_is_invalid(self):
        verifier = _verifier("fact_lock")
        with patch.object(
            readiness_module.inspect,
            "getsourcefile",
            return_value="/tmp/pul7sar_external_verifier.py",
        ):
            receipt = audit_production_gate_verifier_readiness({"fact_lock": verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertFalse(receipt["bindings"][0]["source_file_byte_bound"])

    def test_test_or_stub_source_is_invalid(self):
        verifier = _verifier(
            "fact_lock",
            source_module="tests.fake_fact_lock",
            source_callable="fixture_verify_fact_lock",
        )
        receipt = _audit({"fact_lock": verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])
        self.assertIsNone(receipt["bindings"][0]["source_module"])
        self.assertIsNone(receipt["bindings"][0]["source_callable"])

    def test_production_backed_must_be_literal_true(self):
        verifier = _verifier("fact_lock")
        verifier.PUL7SAR_PRODUCTION_BACKED = "true"
        receipt = _audit({"fact_lock": verifier})
        self.assertIn("fact_lock", receipt["invalid_gate_ids"])

    def test_duplicate_verifier_identity_is_invalid(self):
        first = _verifier("fact_lock")
        second = _verifier("entity_identity_verification")
        second.PUL7SAR_VERIFIER_ID = first.PUL7SAR_VERIFIER_ID
        registry = {
            REQUIRED_FRESH_GATE_EVIDENCE[0]: first,
            REQUIRED_FRESH_GATE_EVIDENCE[1]: second,
        }
        receipt = _audit(registry)
        self.assertIn(REQUIRED_FRESH_GATE_EVIDENCE[1], receipt["invalid_gate_ids"])
        self.assertFalse(receipt["all_production_verifiers_bound"])

    def test_duplicate_source_binding_is_invalid(self):
        first = _verifier(
            "fact_lock",
            source_module="engine.intelligence.production.shared",
            source_callable="verify",
        )
        second = _verifier(
            "entity_identity_verification",
            source_module="engine.intelligence.production.shared",
            source_callable="verify",
        )
        registry = {
            REQUIRED_FRESH_GATE_EVIDENCE[0]: first,
            REQUIRED_FRESH_GATE_EVIDENCE[1]: second,
        }
        receipt = _audit(registry)
        self.assertIn(REQUIRED_FRESH_GATE_EVIDENCE[1], receipt["invalid_gate_ids"])

    def test_tampered_source_file_digest_fails_replay_even_after_rehash(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        receipt = _audit(registry)
        receipt["bindings"][0]["source_file_sha256"] = "0" * 64
        receipt["production_gate_verifier_readiness_sha256"] = sha256_json(
            {
                k: v
                for k, v in receipt.items()
                if k != "production_gate_verifier_readiness_sha256"
            }
        )
        with self.assertRaisesRegex(
            ValueError,
            "QWEN_PRODUCTION_VERIFIER_READINESS_RECEIPT_MISMATCH",
        ):
            _verify(receipt, registry)

    def test_tampered_authority_fails_replay_even_after_rehash(self):
        registry = {gate_id: _verifier(gate_id) for gate_id in REQUIRED_FRESH_GATE_EVIDENCE}
        receipt = _audit(registry)
        receipt["canonical_generation_authorized"] = True
        receipt["production_gate_verifier_readiness_sha256"] = sha256_json(
            {k: v for k, v in receipt.items() if k != "production_gate_verifier_readiness_sha256"}
        )
        with self.assertRaisesRegex(
            ValueError,
            "QWEN_PRODUCTION_VERIFIER_READINESS_RECEIPT_MISMATCH",
        ):
            _verify(receipt, registry)

    def test_registry_module_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "QWEN_PRODUCTION_VERIFIER_REGISTRY_MODULE_DRIFT"):
            audit_production_gate_verifier_readiness({}, registry_module="tests.fake_registry")


if __name__ == "__main__":
    unittest.main()

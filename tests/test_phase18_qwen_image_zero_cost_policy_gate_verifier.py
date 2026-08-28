from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.cost_policy import BillingClass
from engine.intelligence.qwen_image_inference_measurement import COST_MODE
from engine.intelligence.qwen_image_zero_cost_policy_gate_verifier import (
    VERIFIER_ID,
    VERIFIER_VERSION,
    ZERO_COST_EVIDENCE_SCHEMA,
    replay_zero_cost_policy_gate,
    verify_zero_cost_policy_evidence,
)


class ZeroCostPolicyGateVerifierTests(unittest.TestCase):
    STORY_SHA = "a" * 64

    def _receipt(self) -> dict:
        return {
            "verifier_id": VERIFIER_ID,
            "verifier_version": VERIFIER_VERSION,
        }

    def _evidence(self, **overrides) -> dict:
        payload = {
            "schema": ZERO_COST_EVIDENCE_SCHEMA,
            "gate_id": "zero_cost_policy",
            "story_snapshot_sha256": self.STORY_SHA,
            "cost_mode": COST_MODE,
            "provider_id": "qwen-image-2512-local",
            "billing_class": BillingClass.LOCAL_FREE.value,
            "requires_payment_method": False,
            "external_paid_api_used": False,
            "canonical_execution_local_only": True,
        }
        payload.update(overrides)
        return payload

    def _write(self, root: Path, payload: dict) -> Path:
        path = root / "zero_cost_policy.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_strict_local_free_evidence_replays_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            result = replay_zero_cost_policy_gate(path, self.STORY_SHA, self._receipt())
            self.assertTrue(result["gate_passed"])
            self.assertEqual(result["gate_id"], "zero_cost_policy")
            self.assertEqual(result["verifier_id"], VERIFIER_ID)
            self.assertEqual(result["verifier_version"], VERIFIER_VERSION)
            self.assertEqual(result["verification_details"]["policy"], COST_MODE)
            self.assertTrue(result["verification_details"]["development_cost_policy_allowed"])
            self.assertTrue(result["verification_details"]["canonical_execution_local_only"])
            self.assertFalse(result["verification_details"]["external_paid_api_used"])

    def test_free_tier_is_rejected_even_if_generic_development_policy_could_allow_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(billing_class=BillingClass.FREE_TIER.value),
            )
            with self.assertRaisesRegex(ValueError, "PROVIDER_NOT_LOCAL_FREE"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, self._receipt())

    def test_payment_method_requirement_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(requires_payment_method=True))
            with self.assertRaisesRegex(ValueError, "PAYMENT_METHOD_REQUIRED"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, self._receipt())

    def test_external_paid_api_use_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(external_paid_api_used=True))
            with self.assertRaisesRegex(ValueError, "EXTERNAL_PAID_API_USED"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, self._receipt())

    def test_non_local_canonical_execution_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(canonical_execution_local_only=False))
            with self.assertRaisesRegex(ValueError, "LOCAL_EXECUTION_NOT_PROVEN"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, self._receipt())

    def test_cross_story_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(story_snapshot_sha256="b" * 64))
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, self._receipt())

    def test_receipt_verifier_identity_cannot_select_another_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            receipt = self._receipt()
            receipt["verifier_id"] = "wrong"
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                verify_zero_cost_policy_evidence(path, self.STORY_SHA, receipt)

    def test_adapter_exposes_production_provenance_metadata(self) -> None:
        self.assertIs(replay_zero_cost_policy_gate.PUL7SAR_PRODUCTION_BACKED, True)
        self.assertEqual(replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_GATE_ID, "zero_cost_policy")
        self.assertEqual(replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_ID, VERIFIER_ID)
        self.assertEqual(replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_VERSION, VERIFIER_VERSION)
        self.assertIs(
            replay_zero_cost_policy_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_zero_cost_policy_evidence,
        )


if __name__ == "__main__":
    unittest.main()

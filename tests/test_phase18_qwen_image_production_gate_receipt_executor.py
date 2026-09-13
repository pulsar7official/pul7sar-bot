from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    REQUIRED_GATE_RECEIPT_FIELDS,
)
from engine.intelligence.qwen_image_production_gate_receipt_executor import (
    PRODUCTION_GATE_RECEIPT_SCHEMA,
    build_production_gate_receipt,
    build_production_gate_receipt_set,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)
from engine.intelligence.qwen_image_zero_cost_policy_gate_verifier import (
    VERIFIER_ID as ZERO_COST_VERIFIER_ID,
    VERIFIER_VERSION as ZERO_COST_VERIFIER_VERSION,
)


class ProductionGateReceiptExecutorTests(unittest.TestCase):
    STORY_SHA = "c" * 64
    EVALUATED_AT = "2026-08-29T04:05:00Z"

    def _write_zero_cost(self, root: Path, **overrides) -> Path:
        payload = {
            "schema": "pul7sar-phase18-zero-cost-policy-evidence-v1",
            "gate_id": "zero_cost_policy",
            "story_snapshot_sha256": self.STORY_SHA,
            "cost_mode": "$0-local",
            "provider_id": "local_qwen_image_2512",
            "billing_class": "local_free",
            "requires_payment_method": False,
            "external_paid_api_used": False,
            "canonical_execution_local_only": True,
        }
        payload.update(overrides)
        path = root / "zero_cost_policy.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_zero_cost_receipt_is_created_only_from_real_production_verifier_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(Path(tmp))
            receipt = build_production_gate_receipt(
                "zero_cost_policy",
                path,
                self.STORY_SHA,
                evaluated_at_utc=self.EVALUATED_AT,
            )
            raw = path.read_bytes()
            self.assertEqual(tuple(receipt.keys()), REQUIRED_GATE_RECEIPT_FIELDS)
            self.assertEqual(receipt["schema"], PRODUCTION_GATE_RECEIPT_SCHEMA)
            self.assertEqual(receipt["gate_id"], "zero_cost_policy")
            self.assertEqual(receipt["story_snapshot_sha256"], self.STORY_SHA)
            self.assertEqual(receipt["source_evidence_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(receipt["source_evidence_byte_size"], len(raw))
            self.assertEqual(receipt["verifier_id"], ZERO_COST_VERIFIER_ID)
            self.assertEqual(receipt["verifier_version"], ZERO_COST_VERIFIER_VERSION)
            self.assertEqual(receipt["evaluated_at_utc"], self.EVALUATED_AT)
            self.assertTrue(receipt["gate_passed"])
            self.assertEqual(len(receipt["verification_details_sha256"]), 64)

    def test_invalid_zero_cost_evidence_cannot_be_turned_into_pass_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(
                Path(tmp),
                canonical_execution_local_only=False,
            )
            with self.assertRaisesRegex(ValueError, "LOCAL_EXECUTION_NOT_PROVEN"):
                build_production_gate_receipt(
                    "zero_cost_policy",
                    path,
                    self.STORY_SHA,
                    evaluated_at_utc=self.EVALUATED_AT,
                )

    def test_cross_story_evidence_cannot_be_turned_into_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(
                Path(tmp),
                story_snapshot_sha256="d" * 64,
            )
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                build_production_gate_receipt(
                    "zero_cost_policy",
                    path,
                    self.STORY_SHA,
                    evaluated_at_utc=self.EVALUATED_AT,
                )

    def test_receipt_requires_strict_utc_evaluation_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(Path(tmp))
            with self.assertRaisesRegex(ValueError, "TIME_INVALID"):
                build_production_gate_receipt(
                    "zero_cost_policy",
                    path,
                    self.STORY_SHA,
                    evaluated_at_utc="2026-08-29 04:05:00",
                )

    def test_unknown_gate_fails_before_any_verifier_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(Path(tmp))
            with self.assertRaisesRegex(ValueError, "GATE_UNKNOWN"):
                build_production_gate_receipt(
                    "not_a_gate",
                    path,
                    self.STORY_SHA,
                    evaluated_at_utc=self.EVALUATED_AT,
                )

    def test_six_gate_receipt_set_requires_exact_canonical_order_and_set(self) -> None:
        with self.assertRaisesRegex(ValueError, "GATE_ORDER_OR_SET_MISMATCH"):
            build_production_gate_receipt_set(
                {"zero_cost_policy": Path("unused.json")},
                self.STORY_SHA,
                evaluated_at_utc=self.EVALUATED_AT,
            )

    def test_verifier_details_cannot_smuggle_generation_or_publication_authority(self) -> None:
        def malicious(evidence_path, story_snapshot_sha256, receipt):
            raw = evidence_path.read_bytes()
            return {
                "gate_id": "zero_cost_policy",
                "story_snapshot_sha256": story_snapshot_sha256,
                "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
                "source_evidence_byte_size": len(raw),
                "verifier_id": "pul7sar.production.malicious",
                "verifier_version": "1.0.0",
                "gate_passed": True,
                "verification_details": {
                    "nested": {"canonical_generation_authorized": True}
                },
            }

        malicious.PUL7SAR_PRODUCTION_BACKED = True
        malicious.PUL7SAR_VERIFIER_GATE_ID = "zero_cost_policy"
        malicious.PUL7SAR_VERIFIER_ID = "pul7sar.production.malicious"
        malicious.PUL7SAR_VERIFIER_VERSION = "1.0.0"

        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_zero_cost(Path(tmp))
            with patch.dict(
                GATE_REPLAY_VERIFIERS,
                {"zero_cost_policy": malicious},
                clear=False,
            ):
                with self.assertRaisesRegex(ValueError, "DETAILS_AUTHORITY_FORBIDDEN"):
                    build_production_gate_receipt(
                        "zero_cost_policy",
                        path,
                        self.STORY_SHA,
                        evaluated_at_utc=self.EVALUATED_AT,
                    )

    def test_all_six_canonical_registry_entries_are_production_backed(self) -> None:
        self.assertEqual(tuple(GATE_REPLAY_VERIFIERS), REQUIRED_FRESH_GATE_EVIDENCE)
        for gate_id, verifier in GATE_REPLAY_VERIFIERS.items():
            self.assertTrue(callable(verifier), gate_id)
            self.assertIs(verifier.PUL7SAR_PRODUCTION_BACKED, True, gate_id)
            self.assertEqual(verifier.PUL7SAR_VERIFIER_GATE_ID, gate_id)


if __name__ == "__main__":
    unittest.main()

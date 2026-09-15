from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from tools.phase18_audit_qwen_production_gate_verifiers import (
    build_readiness_receipt,
    write_readiness_receipt,
)


class ProductionGateReadinessReceiptCliTests(unittest.TestCase):
    def test_live_canonical_registry_builds_replay_verified_fail_closed_receipt(self) -> None:
        receipt = build_readiness_receipt()
        self.assertEqual(
            receipt["status"],
            "QWEN_IMAGE_2512_PRODUCTION_GATE_VERIFIERS_READY",
        )
        self.assertEqual(
            tuple(receipt["required_gate_order"]),
            REQUIRED_FRESH_GATE_EVIDENCE,
        )
        self.assertTrue(receipt["all_production_verifiers_bound"])
        self.assertTrue(receipt["all_bindings_provenance_complete"])
        self.assertTrue(receipt["all_source_objects_bound"])
        self.assertTrue(receipt["all_source_files_byte_bound"])
        self.assertEqual(receipt["missing_gate_ids"], [])
        self.assertEqual(receipt["invalid_gate_ids"], [])
        self.assertEqual(len(receipt["bindings"]), 6)
        for binding in receipt["bindings"]:
            self.assertEqual(binding["binding_status"], "ready")
            self.assertTrue(binding["production_backed"])
            self.assertTrue(binding["source_object_bound"])
            self.assertTrue(binding["source_object_matches_declaration"])
            self.assertTrue(binding["source_signature_compatible"])
            self.assertTrue(binding["source_file_byte_bound"])
            self.assertEqual(len(binding["source_file_sha256"]), 64)
            self.assertGreater(binding["source_file_byte_size"], 0)

        self.assertFalse(receipt["production_semantic_replay_executed"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["controlled_trial_preflight_valid"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["model_weights_loaded"])
        self.assertFalse(receipt["inference_executed"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertFalse(receipt["publication_ready"])

    def test_persisted_receipt_is_deterministic_json_equivalent_to_live_receipt(self) -> None:
        receipt = build_readiness_receipt()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "receipts" / "production_gate_readiness.json"
            write_readiness_receipt(receipt, output)
            self.assertTrue(output.is_file())
            self.assertTrue(output.read_bytes().endswith(b"\n"))
            persisted = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(persisted, receipt)
            self.assertFalse(persisted["canonical_generation_authorized"])
            self.assertFalse(persisted["publication_ready"])

    def test_output_argument_must_be_path(self) -> None:
        with self.assertRaisesRegex(TypeError, "output must be pathlib.Path"):
            write_readiness_receipt(build_readiness_receipt(), "receipt.json")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

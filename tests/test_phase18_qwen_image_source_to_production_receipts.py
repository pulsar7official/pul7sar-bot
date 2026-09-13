from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_source_backed_story_evidence_pack import (
    SourceBackedStoryEvidencePack,
)
from engine.intelligence.qwen_image_source_to_production_receipts import (
    SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA,
    run_source_to_production_receipts,
)


class SourceToProductionReceiptsTests(unittest.TestCase):
    def _inputs(self, root: Path):
        sources = root / "sources"
        sources.mkdir()
        (sources / "capture.bin").write_bytes(b"captured source")
        binding = root / "binding.json"
        binding.write_text('{"binding":true}\n', encoding="utf-8")
        manifest = root / "manifest.json"
        manifest.write_text('{"manifest":true}\n', encoding="utf-8")
        return binding, manifest, sources

    def _fake_pack(self, root: Path) -> SourceBackedStoryEvidencePack:
        evidence_dir = root / "evidence"
        evidence_dir.mkdir()
        paths = {}
        evidence_meta = []
        for index, gate_id in enumerate(REQUIRED_FRESH_GATE_EVIDENCE, start=1):
            path = evidence_dir / f"{index:02d}_{gate_id}.json"
            path.write_text(json.dumps({"gate_id": gate_id}) + "\n", encoding="utf-8")
            paths[gate_id] = path
            evidence_meta.append({"gate_id": gate_id})
        pack_receipt = evidence_dir / "evidence_pack_receipt.json"
        pack_receipt.write_text(json.dumps({"evidence": evidence_meta}) + "\n", encoding="utf-8")
        return SourceBackedStoryEvidencePack(
            manifest_path=root / "manifest.json",
            story_snapshot_sha256="a" * 64,
            story_snapshot_byte_size=18,
            evidence_paths=paths,
            pack_receipt_path=pack_receipt,
        )

    def _fake_receipts(self):
        return [
            {
                "schema": "pul7sar-phase18-production-gate-receipt-v1",
                "gate_id": gate_id,
                "story_snapshot_sha256": "a" * 64,
                "gate_passed": True,
            }
            for gate_id in REQUIRED_FRESH_GATE_EVIDENCE
        ]

    def test_success_publishes_complete_receipt_set_with_authority_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, manifest, sources = self._inputs(root)
            output = root / "run"

            def compile_side_effect(*args, **kwargs):
                staging_output = args[3]
                return self._fake_pack(staging_output.parent)

            with patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.compile_replayed_source_binding_to_evidence_pack",
                side_effect=compile_side_effect,
            ), patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.build_production_gate_receipt_set",
                return_value=self._fake_receipts(),
            ):
                result = run_source_to_production_receipts(
                    binding,
                    manifest,
                    sources,
                    output,
                    evaluated_at_utc="2026-08-29T07:30:00Z",
                )

            self.assertTrue(result.run_receipt_path.is_file())
            payload = json.loads(result.run_receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA)
            self.assertTrue(payload["production_gate_execution_completed"])
            self.assertEqual(
                [item["gate_id"] for item in payload["production_gate_receipts"]],
                list(REQUIRED_FRESH_GATE_EVIDENCE),
            )
            for key in (
                "production_semantic_replay_executed",
                "fresh_story_gates_passed",
                "controlled_trial_preflight_valid",
                "canonical_generation_authorized",
                "model_weights_loaded",
                "inference_executed",
                "genuine_golden_png_created",
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "publication_ready",
            ):
                self.assertFalse(payload[key])

    def test_gate_failure_publishes_no_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, manifest, sources = self._inputs(root)
            output = root / "run"

            def compile_side_effect(*args, **kwargs):
                return self._fake_pack(args[3].parent)

            with patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.compile_replayed_source_binding_to_evidence_pack",
                side_effect=compile_side_effect,
            ), patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.build_production_gate_receipt_set",
                side_effect=ValueError("QWEN_PRODUCTION_GATE_RECEIPT_GATE_FAILED"),
            ):
                with self.assertRaisesRegex(ValueError, "GATE_FAILED"):
                    run_source_to_production_receipts(
                        binding,
                        manifest,
                        sources,
                        output,
                        evaluated_at_utc="2026-08-29T07:30:00Z",
                    )

            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".run.stage-*")), [])

    def test_existing_output_is_rejected_before_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, manifest, sources = self._inputs(root)
            output = root / "run"
            output.mkdir()
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                run_source_to_production_receipts(
                    binding,
                    manifest,
                    sources,
                    output,
                    evaluated_at_utc="2026-08-29T07:30:00Z",
                )

    def test_receipt_gate_order_drift_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding, manifest, sources = self._inputs(root)
            output = root / "run"

            def compile_side_effect(*args, **kwargs):
                return self._fake_pack(args[3].parent)

            receipts = self._fake_receipts()
            receipts[0] = dict(receipts[0], gate_id="zero_cost_policy")
            with patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.compile_replayed_source_binding_to_evidence_pack",
                side_effect=compile_side_effect,
            ), patch(
                "engine.intelligence.qwen_image_source_to_production_receipts.build_production_gate_receipt_set",
                return_value=receipts,
            ):
                with self.assertRaisesRegex(RuntimeError, "RECEIPT_GATE_DRIFT"):
                    run_source_to_production_receipts(
                        binding,
                        manifest,
                        sources,
                        output,
                        evaluated_at_utc="2026-08-29T07:30:00Z",
                    )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

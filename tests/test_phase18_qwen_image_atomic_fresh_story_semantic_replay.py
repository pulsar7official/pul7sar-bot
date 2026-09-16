from __future__ import annotations

from collections import OrderedDict
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay import (
    ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
    run_atomic_fresh_story_semantic_replay,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_source_to_production_receipts import (
    SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA,
)


class AtomicFreshStorySemanticReplayTests(unittest.TestCase):
    STORY_SHA = "a" * 64
    RECEIPT_TIME = "2026-08-29T12:00:00Z"
    BUNDLE_TIME = "2026-08-29T12:05:00Z"
    REPLAY_TIME = "2026-08-29T12:06:00Z"

    def _write_json(self, path: Path, payload: dict) -> bytes:
        raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
        path.write_bytes(raw)
        return raw

    def _preflight(self, root: Path) -> Path:
        payload = {
            "preflight_contract_locked": True,
            "fresh_story_gate_evidence_required": True,
            "fresh_gate_evidence_required": list(REQUIRED_FRESH_GATE_EVIDENCE),
            "cost_mode": COST_MODE,
            "canonical_generation_authorized": False,
        }
        payload["preflight_contract_sha256"] = sha256_json(payload)
        path = root / "preflight.json"
        self._write_json(path, payload)
        return path

    def _source_run(self, root: Path) -> tuple[Path, OrderedDict]:
        run = root / "artifacts" / "cs256"
        evidence_dir = run / "evidence"
        receipts_dir = run / "production_gate_receipts"
        evidence_dir.mkdir(parents=True)
        receipts_dir.mkdir()

        details_by_gate = {
            gate_id: {"fixture_semantics": "passed", "gate_id": gate_id}
            for gate_id in REQUIRED_FRESH_GATE_EVIDENCE
        }
        evidence_entries = []
        receipt_bindings = []
        verifiers = OrderedDict()

        for index, gate_id in enumerate(REQUIRED_FRESH_GATE_EVIDENCE, start=1):
            evidence_path = evidence_dir / f"{index:02d}_{gate_id}.json"
            evidence_raw = self._write_json(
                evidence_path,
                {"gate_id": gate_id, "story_snapshot_sha256": self.STORY_SHA, "fixture": True},
            )
            evidence_sha = hashlib.sha256(evidence_raw).hexdigest()
            evidence_entries.append(
                {
                    "gate_id": gate_id,
                    "path": evidence_path.name,
                    "sha256": evidence_sha,
                    "byte_size": len(evidence_raw),
                }
            )

            details = details_by_gate[gate_id]
            receipt = {
                "schema": "pul7sar-phase18-production-gate-receipt-v1",
                "gate_id": gate_id,
                "story_snapshot_sha256": self.STORY_SHA,
                "source_evidence_sha256": evidence_sha,
                "source_evidence_byte_size": len(evidence_raw),
                "verifier_id": f"phase18.{gate_id}.production",
                "verifier_version": "1",
                "evaluated_at_utc": self.RECEIPT_TIME,
                "gate_passed": True,
                "verification_details_sha256": sha256_json(details),
            }
            receipt_path = receipts_dir / f"{index:02d}_{gate_id}_receipt.json"
            receipt_raw = self._write_json(receipt_path, receipt)
            receipt_bindings.append(
                {
                    "gate_id": gate_id,
                    "path": f"production_gate_receipts/{receipt_path.name}",
                    "sha256": hashlib.sha256(receipt_raw).hexdigest(),
                    "byte_size": len(receipt_raw),
                }
            )

            def verifier(path, story_sha, source_receipt, *, _gate=gate_id, _details=details):
                raw = path.read_bytes()
                return {
                    "gate_id": _gate,
                    "story_snapshot_sha256": story_sha,
                    "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
                    "source_evidence_byte_size": len(raw),
                    "verifier_id": source_receipt["verifier_id"],
                    "verifier_version": source_receipt["verifier_version"],
                    "gate_passed": True,
                    "verification_details": dict(_details),
                }

            verifiers[gate_id] = verifier

        pack = {
            "story_snapshot_sha256": self.STORY_SHA,
            "evidence": evidence_entries,
        }
        pack_path = evidence_dir / "evidence_pack_receipt.json"
        pack_raw = self._write_json(pack_path, pack)
        run_receipt = {
            "schema": SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA,
            "story_snapshot_sha256": self.STORY_SHA,
            "binding_receipt": {"sha256": "b" * 64, "byte_size": 1},
            "bound_manifest": {"sha256": "c" * 64, "byte_size": 1},
            "evidence_pack_receipt": {
                "path": "evidence/evidence_pack_receipt.json",
                "sha256": hashlib.sha256(pack_raw).hexdigest(),
                "byte_size": len(pack_raw),
            },
            "production_gate_receipts": receipt_bindings,
            "production_gate_execution_completed": True,
            "production_semantic_replay_executed": False,
            "fresh_story_gates_passed": False,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        self._write_json(run / "source_to_production_receipts.json", run_receipt)
        return run, verifiers

    def test_success_executes_237_and_238_but_keeps_downstream_authority_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            source_run, verifiers = self._source_run(root)
            output = root / "artifacts" / "cs257"
            with patch(
                "engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay._production_verifiers",
                return_value=verifiers,
            ):
                result = run_atomic_fresh_story_semantic_replay(
                    source_run,
                    preflight,
                    output,
                    evaluated_at_utc=self.BUNDLE_TIME,
                    replayed_at_utc=self.REPLAY_TIME,
                    max_gate_age_seconds=600,
                    repo_root=root,
                )

            payload = json.loads(result.run_receipt_path.read_text())
            self.assertEqual(payload["schema"], ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA)
            self.assertTrue(payload["production_semantic_replay_executed"])
            self.assertTrue(payload["fresh_story_gates_passed"])
            for field in (
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
                self.assertFalse(payload[field])
            replay = json.loads(result.semantic_replay_path.read_text())
            self.assertTrue(replay["all_gate_specific_verifiers_executed"])
            self.assertTrue(replay["fresh_story_gates_passed"])

    def test_stale_receipts_fail_without_publishing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            source_run, verifiers = self._source_run(root)
            output = root / "artifacts" / "cs257"
            with patch(
                "engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay._production_verifiers",
                return_value=verifiers,
            ):
                with self.assertRaisesRegex(ValueError, "RECEIPT_STALE"):
                    run_atomic_fresh_story_semantic_replay(
                        source_run,
                        preflight,
                        output,
                        evaluated_at_utc="2026-08-29T12:20:00Z",
                        replayed_at_utc="2026-08-29T12:21:00Z",
                        max_gate_age_seconds=600,
                        repo_root=root,
                    )
            self.assertFalse(output.exists())
            self.assertEqual(list((root / "artifacts").glob(".cs257.stage-*")), [])

    def test_receipt_byte_tamper_fails_before_structural_admission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            source_run, verifiers = self._source_run(root)
            receipt_path = source_run / "production_gate_receipts" / "01_fact_lock_receipt.json"
            receipt_path.write_text("{}\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay._production_verifiers",
                return_value=verifiers,
            ):
                with self.assertRaisesRegex(ValueError, "RECEIPT_BYTE_BINDING_DRIFT"):
                    run_atomic_fresh_story_semantic_replay(
                        source_run,
                        preflight,
                        root / "artifacts" / "cs257",
                        evaluated_at_utc=self.BUNDLE_TIME,
                        replayed_at_utc=self.REPLAY_TIME,
                        max_gate_age_seconds=600,
                        repo_root=root,
                    )

    def test_semantic_details_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            source_run, verifiers = self._source_run(root)
            original = verifiers["fact_lock"]

            def drifted(path, story_sha, receipt):
                result = dict(original(path, story_sha, receipt))
                result["verification_details"] = {"changed": True}
                return result

            verifiers["fact_lock"] = drifted
            with patch(
                "engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay._production_verifiers",
                return_value=verifiers,
            ):
                with self.assertRaisesRegex(ValueError, "DETAILS_SHA_MISMATCH"):
                    run_atomic_fresh_story_semantic_replay(
                        source_run,
                        preflight,
                        root / "artifacts" / "cs257",
                        evaluated_at_utc=self.BUNDLE_TIME,
                        replayed_at_utc=self.REPLAY_TIME,
                        max_gate_age_seconds=600,
                        repo_root=root,
                    )


if __name__ == "__main__":
    unittest.main()

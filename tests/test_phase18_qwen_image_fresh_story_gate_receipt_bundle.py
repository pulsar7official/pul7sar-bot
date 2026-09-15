from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    build_fresh_story_evidence_manifest,
)
from engine.intelligence.qwen_image_fresh_story_gate_receipt_bundle import (
    build_fresh_story_gate_receipt_bundle,
    verify_fresh_story_gate_receipt_bundle,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    build_fresh_story_gate_verification_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json


class FreshStoryGateReceiptBundleTests(unittest.TestCase):
    STORY_SHA = "a" * 64
    NOW = "2026-08-28T14:00:00Z"

    def _preflight(self) -> dict:
        payload = {
            "preflight_contract_locked": True,
            "fresh_story_gate_evidence_required": True,
            "fresh_gate_evidence_required": list(REQUIRED_FRESH_GATE_EVIDENCE),
            "cost_mode": COST_MODE,
            "canonical_generation_authorized": False,
        }
        payload["preflight_contract_sha256"] = sha256_json(payload)
        return payload

    def _fixture(self, root: Path):
        preflight = self._preflight()
        evidence_dir = root / "artifacts" / "phase18" / "fresh-story"
        evidence_dir.mkdir(parents=True)
        evidence: dict[str, str] = {}
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            path = evidence_dir / f"{gate_id}.json"
            path.write_text(json.dumps({"gate_id": gate_id, "fixture": True}), encoding="utf-8")
            evidence[gate_id] = path.relative_to(root).as_posix()
        manifest = build_fresh_story_evidence_manifest(preflight, evidence, repo_root=root)
        contract = build_fresh_story_gate_verification_contract(
            manifest,
            preflight,
            story_snapshot_sha256=self.STORY_SHA,
            repo_root=root,
        )
        requirements = {item["gate_id"]: item for item in contract["gate_requirements"]}
        receipts = []
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            requirement = requirements[gate_id]
            receipts.append(
                {
                    "schema": f"fixture-{gate_id}-receipt-v1",
                    "gate_id": gate_id,
                    "story_snapshot_sha256": self.STORY_SHA,
                    "source_evidence_sha256": requirement["source_evidence_sha256"],
                    "source_evidence_byte_size": requirement["source_evidence_byte_size"],
                    "verifier_id": f"phase18.{gate_id}.verifier",
                    "verifier_version": "1",
                    "evaluated_at_utc": "2026-08-28T13:55:00Z",
                    "gate_passed": True,
                    "verification_details_sha256": "b" * 64,
                }
            )
        return preflight, manifest, contract, receipts

    def _build(self, root: Path):
        preflight, manifest, contract, receipts = self._fixture(root)
        bundle = build_fresh_story_gate_receipt_bundle(
            contract,
            manifest,
            preflight,
            receipts,
            evaluated_at_utc=self.NOW,
            max_gate_age_seconds=600,
            repo_root=root,
        )
        return preflight, manifest, contract, receipts, bundle

    def test_admits_complete_fresh_same_story_bundle_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle = self._build(root)
            digest = verify_fresh_story_gate_receipt_bundle(
                bundle, contract, manifest, preflight, receipts, repo_root=root
            )
            self.assertEqual(digest, bundle["fresh_story_gate_receipt_bundle_sha256"])
            self.assertTrue(bundle["gate_receipt_bundle_admitted"])
            self.assertTrue(bundle["freshness_window_confirmed"])
            self.assertFalse(bundle["fresh_story_gates_passed"])
            self.assertFalse(bundle["canonical_generation_authorized"])
            self.assertFalse(bundle["publication_ready"])

    def test_rejects_cross_story_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            receipts[2]["story_snapshot_sha256"] = "c" * 64
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_RECEIPT"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=600, repo_root=root
                )

    def test_rejects_stale_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            receipts[0]["evaluated_at_utc"] = "2026-08-28T13:40:00Z"
            with self.assertRaisesRegex(ValueError, "RECEIPT_STALE"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=600, repo_root=root
                )

    def test_rejects_future_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            receipts[0]["evaluated_at_utc"] = "2026-08-28T14:01:00Z"
            with self.assertRaisesRegex(ValueError, "RECEIPT_FROM_FUTURE"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=600, repo_root=root
                )

    def test_rejects_failed_gate_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            receipts[4]["gate_passed"] = False
            with self.assertRaisesRegex(ValueError, "GATE_NOT_PASSED"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=600, repo_root=root
                )

    def test_rejects_evidence_binding_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            receipts[1]["source_evidence_sha256"] = "d" * 64
            with self.assertRaisesRegex(ValueError, "EVIDENCE_SHA_MISMATCH"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=600, repo_root=root
                )

    def test_replay_rejects_receipt_mutation_after_bundle_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle = self._build(root)
            receipts[0]["verifier_version"] = "2"
            with self.assertRaisesRegex(ValueError, "REPLAY_MISMATCH"):
                verify_fresh_story_gate_receipt_bundle(
                    bundle, contract, manifest, preflight, receipts, repo_root=root
                )

    def test_replay_rejects_authority_forgery_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle = self._build(root)
            bundle["canonical_generation_authorized"] = True
            bundle.pop("fresh_story_gate_receipt_bundle_sha256")
            bundle["fresh_story_gate_receipt_bundle_sha256"] = sha256_json(bundle)
            with self.assertRaisesRegex(ValueError, "REPLAY_MISMATCH"):
                verify_fresh_story_gate_receipt_bundle(
                    bundle, contract, manifest, preflight, receipts, repo_root=root
                )

    def test_rejects_unbounded_freshness_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts = self._fixture(root)
            with self.assertRaisesRegex(ValueError, "MAX_AGE_OUT_OF_RANGE"):
                build_fresh_story_gate_receipt_bundle(
                    contract, manifest, preflight, receipts,
                    evaluated_at_utc=self.NOW, max_gate_age_seconds=7200, repo_root=root
                )

    def test_parent_manifest_byte_tamper_still_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle = self._build(root)
            path = root / manifest["evidence_bindings"][0]["repository_relative_path"]
            path.write_text('{"tampered": true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_(SIZE|SHA)_MISMATCH"):
                verify_fresh_story_gate_receipt_bundle(
                    bundle, contract, manifest, preflight, receipts, repo_root=root
                )


if __name__ == "__main__":
    unittest.main()

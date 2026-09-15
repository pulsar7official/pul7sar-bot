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
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    REQUIRED_GATE_RECEIPT_FIELDS,
    build_fresh_story_gate_verification_contract,
    verify_fresh_story_gate_verification_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json


class FreshStoryGateVerificationContractTests(unittest.TestCase):
    STORY_SHA = "a" * 64

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

    def _manifest(self, root: Path, preflight: dict) -> dict:
        evidence_dir = root / "artifacts" / "phase18" / "fresh-story"
        evidence_dir.mkdir(parents=True)
        evidence: dict[str, str] = {}
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            path = evidence_dir / f"{gate_id}.json"
            path.write_text(json.dumps({"gate_id": gate_id, "fixture": True}), encoding="utf-8")
            evidence[gate_id] = path.relative_to(root).as_posix()
        return build_fresh_story_evidence_manifest(preflight, evidence, repo_root=root)

    def test_locks_same_story_and_exact_evidence_requirements_without_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest,
                preflight,
                story_snapshot_sha256=self.STORY_SHA,
                repo_root=root,
            )
            digest = verify_fresh_story_gate_verification_contract(
                contract, manifest, preflight, repo_root=root
            )
            self.assertEqual(digest, contract["fresh_story_gate_verification_contract_sha256"])
            self.assertEqual(contract["story_snapshot_sha256"], self.STORY_SHA)
            self.assertTrue(contract["same_story_snapshot_required"])
            self.assertFalse(contract["fresh_story_gates_passed"])
            self.assertFalse(contract["canonical_generation_authorized"])
            self.assertFalse(contract["publication_ready"])

    def test_requires_gate_receipts_to_bind_expected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest, preflight, story_snapshot_sha256=self.STORY_SHA, repo_root=root
            )
            self.assertEqual(
                tuple(contract["gate_requirements"][0]["required_receipt_fields"]),
                REQUIRED_GATE_RECEIPT_FIELDS,
            )

    def test_rejects_invalid_story_snapshot_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            with self.assertRaisesRegex(ValueError, "STORY_SNAPSHOT_SHA_INVALID"):
                build_fresh_story_gate_verification_contract(
                    manifest, preflight, story_snapshot_sha256="not-a-sha", repo_root=root
                )

    def test_rejects_evidence_binding_drift_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest, preflight, story_snapshot_sha256=self.STORY_SHA, repo_root=root
            )
            contract["gate_requirements"][0]["source_evidence_sha256"] = "b" * 64
            contract.pop("fresh_story_gate_verification_contract_sha256")
            contract["fresh_story_gate_verification_contract_sha256"] = sha256_json(contract)
            with self.assertRaisesRegex(ValueError, "EVIDENCE_SHA_DRIFT"):
                verify_fresh_story_gate_verification_contract(
                    contract, manifest, preflight, repo_root=root
                )

    def test_rejects_dropping_same_story_requirement_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest, preflight, story_snapshot_sha256=self.STORY_SHA, repo_root=root
            )
            contract["same_story_snapshot_required"] = False
            contract.pop("fresh_story_gate_verification_contract_sha256")
            contract["fresh_story_gate_verification_contract_sha256"] = sha256_json(contract)
            with self.assertRaisesRegex(ValueError, "REQUIRED_BOUNDARY_MISSING"):
                verify_fresh_story_gate_verification_contract(
                    contract, manifest, preflight, repo_root=root
                )

    def test_rejects_authority_forgery_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest, preflight, story_snapshot_sha256=self.STORY_SHA, repo_root=root
            )
            contract["canonical_generation_authorized"] = True
            contract.pop("fresh_story_gate_verification_contract_sha256")
            contract["fresh_story_gate_verification_contract_sha256"] = sha256_json(contract)
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_fresh_story_gate_verification_contract(
                    contract, manifest, preflight, repo_root=root
                )

    def test_rejects_manifest_byte_substitution_through_parent_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight()
            manifest = self._manifest(root, preflight)
            contract = build_fresh_story_gate_verification_contract(
                manifest, preflight, story_snapshot_sha256=self.STORY_SHA, repo_root=root
            )
            bound_path = root / manifest["evidence_bindings"][0]["repository_relative_path"]
            bound_path.write_text('{"tampered": true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_(SIZE|SHA)_MISMATCH"):
                verify_fresh_story_gate_verification_contract(
                    contract, manifest, preflight, repo_root=root
                )


if __name__ == "__main__":
    unittest.main()

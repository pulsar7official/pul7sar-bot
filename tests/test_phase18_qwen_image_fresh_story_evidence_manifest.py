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
    verify_fresh_story_evidence_manifest,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json


class FreshStoryEvidenceManifestTests(unittest.TestCase):
    def _contract(self) -> dict:
        contract = {
            "preflight_contract_locked": True,
            "fresh_story_gate_evidence_required": True,
            "fresh_gate_evidence_required": list(REQUIRED_FRESH_GATE_EVIDENCE),
            "cost_mode": COST_MODE,
            "canonical_generation_authorized": False,
        }
        contract["preflight_contract_sha256"] = sha256_json(contract)
        return contract

    def _evidence_files(self, root: Path) -> dict[str, str]:
        evidence_dir = root / "artifacts" / "phase18" / "story-evidence"
        evidence_dir.mkdir(parents=True)
        result: dict[str, str] = {}
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            path = evidence_dir / f"{gate_id}.json"
            path.write_text(
                json.dumps({"gate": gate_id, "fixture": True}, sort_keys=True),
                encoding="utf-8",
            )
            result[gate_id] = path.relative_to(root).as_posix()
        return result

    def test_binds_all_required_evidence_without_granting_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            manifest = build_fresh_story_evidence_manifest(
                contract,
                self._evidence_files(root),
                repo_root=root,
            )
            digest = verify_fresh_story_evidence_manifest(manifest, contract, repo_root=root)
            self.assertEqual(digest, manifest["fresh_story_evidence_manifest_sha256"])
            self.assertTrue(manifest["all_required_evidence_bytes_bound"])
            self.assertFalse(manifest["fresh_story_gates_passed"])
            self.assertFalse(manifest["canonical_generation_authorized"])
            self.assertFalse(manifest["publication_ready"])

    def test_rejects_missing_gate_or_order_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            evidence = self._evidence_files(root)
            evidence.pop(REQUIRED_FRESH_GATE_EVIDENCE[-1])
            with self.assertRaisesRegex(ValueError, "INPUT_GATE_SET_OR_ORDER_MISMATCH"):
                build_fresh_story_evidence_manifest(contract, evidence, repo_root=root)

    def test_rejects_evidence_byte_substitution_after_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            evidence = self._evidence_files(root)
            manifest = build_fresh_story_evidence_manifest(contract, evidence, repo_root=root)
            first = root / evidence[REQUIRED_FRESH_GATE_EVIDENCE[0]]
            first.write_text('{"tampered": true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_(SIZE|SHA)_MISMATCH"):
                verify_fresh_story_evidence_manifest(manifest, contract, repo_root=root)

    def test_rejects_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            root = Path(tmp)
            contract = self._contract()
            evidence = self._evidence_files(root)
            outside = Path(outside_tmp) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            evidence[REQUIRED_FRESH_GATE_EVIDENCE[0]] = str(outside)
            with self.assertRaisesRegex(ValueError, "PATH_OUTSIDE_REPOSITORY"):
                build_fresh_story_evidence_manifest(contract, evidence, repo_root=root)

    def test_rejects_duplicate_file_across_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            evidence = self._evidence_files(root)
            evidence[REQUIRED_FRESH_GATE_EVIDENCE[1]] = evidence[REQUIRED_FRESH_GATE_EVIDENCE[0]]
            with self.assertRaisesRegex(ValueError, "DUPLICATE_FILE_FORBIDDEN"):
                build_fresh_story_evidence_manifest(contract, evidence, repo_root=root)

    def test_rejects_authority_forgery_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            manifest = build_fresh_story_evidence_manifest(
                contract,
                self._evidence_files(root),
                repo_root=root,
            )
            manifest["canonical_generation_authorized"] = True
            manifest.pop("fresh_story_evidence_manifest_sha256")
            manifest["fresh_story_evidence_manifest_sha256"] = sha256_json(manifest)
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_fresh_story_evidence_manifest(manifest, contract, repo_root=root)

    def test_rejects_dropping_future_semantic_and_freshness_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            manifest = build_fresh_story_evidence_manifest(
                contract,
                self._evidence_files(root),
                repo_root=root,
            )
            manifest["gate_specific_semantic_verification_required"] = False
            manifest.pop("fresh_story_evidence_manifest_sha256")
            manifest["fresh_story_evidence_manifest_sha256"] = sha256_json(manifest)
            with self.assertRaisesRegex(ValueError, "REQUIRED_BOUNDARY_MISSING"):
                verify_fresh_story_evidence_manifest(manifest, contract, repo_root=root)

    def test_rejects_parent_contract_tamper_even_when_manifest_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = self._contract()
            manifest = build_fresh_story_evidence_manifest(
                contract,
                self._evidence_files(root),
                repo_root=root,
            )
            contract["cost_mode"] = "paid-cloud"
            contract.pop("preflight_contract_sha256")
            contract["preflight_contract_sha256"] = sha256_json(contract)
            with self.assertRaisesRegex(ValueError, "COST_MODE_DRIFT"):
                verify_fresh_story_evidence_manifest(manifest, contract, repo_root=root)


if __name__ == "__main__":
    unittest.main()

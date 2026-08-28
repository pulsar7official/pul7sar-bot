from __future__ import annotations

import json
import tempfile
import unittest
from collections import OrderedDict
from pathlib import Path

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    build_fresh_story_evidence_manifest,
)
from engine.intelligence.qwen_image_fresh_story_gate_receipt_bundle import (
    build_fresh_story_gate_receipt_bundle,
)
from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import (
    build_fresh_story_gate_semantic_replay,
    verify_fresh_story_gate_semantic_replay,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    build_fresh_story_gate_verification_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json


class FreshStoryGateSemanticReplayTests(unittest.TestCase):
    STORY_SHA = "a" * 64
    BUNDLE_TIME = "2026-08-28T14:00:00Z"
    REPLAY_TIME = "2026-08-28T14:04:00Z"

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
        details_by_gate: dict[str, dict] = {}
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            path = evidence_dir / f"{gate_id}.json"
            body = {"gate_id": gate_id, "story_snapshot_sha256": self.STORY_SHA, "fixture": True}
            path.write_text(json.dumps(body, sort_keys=True), encoding="utf-8")
            evidence[gate_id] = path.relative_to(root).as_posix()
            details_by_gate[gate_id] = {
                "semantic_replay": "passed",
                "gate_id": gate_id,
                "story_snapshot_sha256": self.STORY_SHA,
            }

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
                    "verification_details_sha256": sha256_json(details_by_gate[gate_id]),
                }
            )

        bundle = build_fresh_story_gate_receipt_bundle(
            contract,
            manifest,
            preflight,
            receipts,
            evaluated_at_utc=self.BUNDLE_TIME,
            max_gate_age_seconds=600,
            repo_root=root,
        )

        bindings = {item["gate_id"]: item for item in manifest["evidence_bindings"]}
        verifiers = OrderedDict()
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
            binding = bindings[gate_id]
            details = details_by_gate[gate_id]

            def verifier(path, story_sha, receipt, *, _gate=gate_id, _binding=binding, _details=details):
                return {
                    "gate_id": _gate,
                    "story_snapshot_sha256": story_sha,
                    "source_evidence_sha256": _binding["sha256"],
                    "source_evidence_byte_size": _binding["byte_size"],
                    "verifier_id": receipt["verifier_id"],
                    "verifier_version": receipt["verifier_version"],
                    "gate_passed": True,
                    "verification_details": dict(_details),
                }

            verifiers[gate_id] = verifier
        return preflight, manifest, contract, receipts, bundle, verifiers

    def _build(self, root: Path):
        preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
        replay = build_fresh_story_gate_semantic_replay(
            bundle,
            contract,
            manifest,
            preflight,
            receipts,
            verifiers,
            replayed_at_utc=self.REPLAY_TIME,
            repo_root=root,
        )
        return preflight, manifest, contract, receipts, bundle, verifiers, replay

    def test_all_gate_specific_replays_can_promote_only_fresh_story_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers, replay = self._build(root)
            digest = verify_fresh_story_gate_semantic_replay(
                replay, bundle, contract, manifest, preflight, receipts, verifiers, repo_root=root
            )
            self.assertEqual(digest, replay["fresh_story_gate_semantic_replay_sha256"])
            self.assertTrue(replay["fresh_story_gates_passed"])
            self.assertTrue(replay["all_gate_specific_verifiers_executed"])
            self.assertFalse(replay["canonical_generation_authorized"])
            self.assertFalse(replay["inference_executed"])
            self.assertFalse(replay["publication_ready"])

    def test_missing_verifier_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            verifiers.pop(REQUIRED_FRESH_GATE_EVIDENCE[-1])
            with self.assertRaisesRegex(ValueError, "VERIFIER_SET_OR_ORDER_MISMATCH"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_rejects_verifier_identity_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            gate_id = REQUIRED_FRESH_GATE_EVIDENCE[0]
            original = verifiers[gate_id]

            def mismatched(path, story_sha, receipt):
                output = dict(original(path, story_sha, receipt))
                output["verifier_id"] = "wrong.verifier"
                return output

            verifiers[gate_id] = mismatched
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_rejects_semantic_details_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            gate_id = REQUIRED_FRESH_GATE_EVIDENCE[2]
            original = verifiers[gate_id]

            def changed_details(path, story_sha, receipt):
                output = dict(original(path, story_sha, receipt))
                output["verification_details"] = {"semantic_replay": "different"}
                return output

            verifiers[gate_id] = changed_details
            with self.assertRaisesRegex(ValueError, "DETAILS_SHA_MISMATCH"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_rejects_gate_specific_replay_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            gate_id = REQUIRED_FRESH_GATE_EVIDENCE[4]
            original = verifiers[gate_id]

            def failed(path, story_sha, receipt):
                output = dict(original(path, story_sha, receipt))
                output["gate_passed"] = False
                return output

            verifiers[gate_id] = failed
            with self.assertRaisesRegex(ValueError, "GATE_FAILED"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_rechecks_freshness_at_semantic_replay_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            with self.assertRaisesRegex(ValueError, "RECEIPT_STALE_AT_REPLAY"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc="2026-08-28T14:06:00Z", repo_root=root
                )

    def test_parent_evidence_byte_tamper_still_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            path = root / manifest["evidence_bindings"][0]["repository_relative_path"]
            path.write_text('{"tampered": true}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_(SIZE|SHA)_MISMATCH"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_rejects_cross_story_replay_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers = self._fixture(root)
            gate_id = REQUIRED_FRESH_GATE_EVIDENCE[1]
            original = verifiers[gate_id]

            def cross_story(path, story_sha, receipt):
                output = dict(original(path, story_sha, receipt))
                output["story_snapshot_sha256"] = "c" * 64
                return output

            verifiers[gate_id] = cross_story
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_OUTPUT"):
                build_fresh_story_gate_semantic_replay(
                    bundle, contract, manifest, preflight, receipts, verifiers,
                    replayed_at_utc=self.REPLAY_TIME, repo_root=root
                )

    def test_replay_receipt_authority_forgery_fails_even_after_rehash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight, manifest, contract, receipts, bundle, verifiers, replay = self._build(root)
            replay["canonical_generation_authorized"] = True
            replay.pop("fresh_story_gate_semantic_replay_sha256")
            replay["fresh_story_gate_semantic_replay_sha256"] = sha256_json(replay)
            with self.assertRaisesRegex(ValueError, "RECEIPT_MISMATCH"):
                verify_fresh_story_gate_semantic_replay(
                    replay, bundle, contract, manifest, preflight, receipts, verifiers, repo_root=root
                )


if __name__ == "__main__":
    unittest.main()

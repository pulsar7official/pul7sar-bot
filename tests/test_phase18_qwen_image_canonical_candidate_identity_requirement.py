from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    _identity_binding_from_manifest,
    run_identity_requirement,
    verify_identity_requirement,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
)

STORY_SHA = "a" * 64


def _write(path: Path, payload: dict) -> bytes:
    raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


class CS265IdentityRequirementTests(unittest.TestCase):
    def _fixture(self, root: Path, *, kind: str = "player"):
        candidate_path = root / "candidate.png"
        candidate_raw = b"synthetic-control-plane-png-bytes"
        candidate_path.write_bytes(candidate_raw)
        evidence_path = root / "artifacts" / "identity.json"
        evidence = {
            "schema": "pul7sar-phase18-entity-identity-evidence-v1",
            "gate_id": "entity_identity_verification",
            "story_snapshot_sha256": STORY_SHA,
            "canonical_entities": [{
                "entity_id": "player.test",
                "kind": kind,
                "display_name": "Test Player",
                "aliases": ["Test Player"],
                "identity_source_refs": ["source:official"],
            }],
            "story_entity_references": [{
                "field": "headline", "text": "Test Player", "expected_entity_id": "player.test"
            }],
            "exact_entity_assets": [],
        }
        evidence_raw = _write(evidence_path, evidence)
        source = {
            "schema": CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
            "receipt_sha256": "d" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "semantic_base_scene_approved": True,
            "candidate_png": {
                "repository_relative_path": "candidate.png",
                "sha256": hashlib.sha256(candidate_raw).hexdigest(),
                "byte_size": len(candidate_raw),
            },
            "identity_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        identity_binding = {
            "repository_relative_path": "artifacts/identity.json",
            "sha256": hashlib.sha256(evidence_raw).hexdigest(),
            "byte_size": len(evidence_raw),
        }
        lineage = {
            "binding_source": "candidate_launch_manifest",
            "candidate_handoff_sha256": "b" * 64,
            "launch_manifest": {
                "repository_relative_path": "runs/launch_manifest.json",
                "sha256": "c" * 64,
                "byte_size": 123,
            },
            "cs257_evidence": {
                "repository_relative_directory": "runs/cs257",
                "files": [],
            },
        }
        cs264 = root / "cs264.json"
        cs264.write_text("{}", encoding="utf-8")
        return source, evidence, identity_binding, lineage, evidence_path, candidate_path, cs264

    def _build(self, root: Path, *, kind: str = "player"):
        source, evidence, identity_binding, lineage, evidence_path, candidate_path, cs264 = self._fixture(
            root, kind=kind
        )
        semantic_target = (
            "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
            "verify_canonical_candidate_semantic_base_qa"
        )
        lineage_target = (
            "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
            "_lineage_bound_identity"
        )
        with patch(semantic_target, return_value=source), patch(
            lineage_target,
            return_value=(evidence, identity_binding, lineage),
        ):
            result = run_identity_requirement(cs264, root / "out", repo_root=root)
            receipt = verify_identity_requirement(result.receipt_path, repo_root=root)
        return result, receipt, source, evidence, identity_binding, lineage, evidence_path, candidate_path, cs264

    def test_human_entity_requires_pixel_identity_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, receipt, _, _, _, lineage, _, _, _ = self._build(root)
            self.assertTrue(result.pixel_identity_review_required)
            self.assertFalse(receipt["identity_approved"])
            self.assertFalse(receipt["publication_ready"])
            self.assertEqual(receipt["human_identity_targets"][0]["display_name"], "Test Player")
            self.assertIn("source_cs264_receipt", receipt)
            self.assertEqual(receipt["lineage_bound_identity_source"], lineage)

    def test_nonhuman_entity_does_not_claim_identity_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _, receipt, _, _, _, _, _, _, _ = self._build(root, kind="club")
            self.assertFalse(receipt["pixel_identity_review_required"])
            self.assertFalse(receipt["identity_approved"])

    def test_production_api_has_no_independent_cs257_selector(self):
        parameters = inspect.signature(run_identity_requirement).parameters
        self.assertNotIn("cs257_run_dir", parameters)
        self.assertEqual(list(parameters), ["cs264_receipt_path", "output_dir", "repo_root"])

    def test_launch_bound_identity_evidence_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs257_dir = root / "runs" / "cs257"
            evidence_path = root / "artifacts" / "identity.json"
            evidence = {
                "schema": "pul7sar-phase18-entity-identity-evidence-v1",
                "gate_id": "entity_identity_verification",
                "story_snapshot_sha256": STORY_SHA,
                "canonical_entities": [{
                    "entity_id": "player.test",
                    "kind": "player",
                    "display_name": "Test Player",
                    "aliases": ["Test Player"],
                    "identity_source_refs": ["source:official"],
                }],
                "story_entity_references": [{
                    "field": "headline",
                    "text": "Test Player",
                    "expected_entity_id": "player.test",
                }],
                "exact_entity_assets": [],
            }
            evidence_raw = _write(evidence_path, evidence)
            _write(
                cs257_dir / "atomic_fresh_story_semantic_replay.json",
                {
                    "story_snapshot_sha256": STORY_SHA,
                    "fresh_story_gates_passed": True,
                    "production_semantic_replay_executed": True,
                },
            )
            _write(
                cs257_dir / "fresh_story_evidence_manifest.json",
                {
                    "evidence_bindings": [{
                        "gate_id": "entity_identity_verification",
                        "repository_relative_path": "artifacts/identity.json",
                        "sha256": hashlib.sha256(evidence_raw).hexdigest(),
                        "byte_size": len(evidence_raw),
                    }]
                },
            )
            derived_evidence, binding = _identity_binding_from_manifest(
                cs257_dir, root, STORY_SHA
            )
            self.assertEqual(derived_evidence["story_snapshot_sha256"], STORY_SHA)
            self.assertEqual(binding["sha256"], hashlib.sha256(evidence_raw).hexdigest())

            evidence_path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "IDENTITY_BYTE_DRIFT"):
                _identity_binding_from_manifest(cs257_dir, root, STORY_SHA)

    def test_candidate_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, source, evidence, identity_binding, lineage, _, candidate_path, _ = self._build(root)
            candidate_path.write_bytes(b"tampered-candidate")
            semantic_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "verify_canonical_candidate_semantic_base_qa"
            )
            lineage_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "_lineage_bound_identity"
            )
            with patch(semantic_target, return_value=source), patch(
                lineage_target,
                return_value=(evidence, identity_binding, lineage),
            ):
                with self.assertRaisesRegex(ValueError, "CANDIDATE_INVALID_BYTE_DRIFT"):
                    verify_identity_requirement(result.receipt_path, repo_root=root)

    def test_source_cs264_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, source, evidence, identity_binding, lineage, _, _, cs264 = self._build(root)
            cs264.write_text('{"tampered":true}', encoding="utf-8")
            semantic_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "verify_canonical_candidate_semantic_base_qa"
            )
            lineage_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "_lineage_bound_identity"
            )
            with patch(semantic_target, return_value=source), patch(
                lineage_target,
                return_value=(evidence, identity_binding, lineage),
            ):
                with self.assertRaisesRegex(ValueError, "CS264_RECEIPT_INVALID_BYTE_DRIFT"):
                    verify_identity_requirement(result.receipt_path, repo_root=root)

    def test_lineage_source_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, source, evidence, identity_binding, lineage, _, _, _ = self._build(root)
            changed = dict(lineage)
            changed["candidate_handoff_sha256"] = "e" * 64
            semantic_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "verify_canonical_candidate_semantic_base_qa"
            )
            lineage_target = (
                "engine.intelligence.qwen_image_canonical_candidate_identity_requirement."
                "_lineage_bound_identity"
            )
            with patch(semantic_target, return_value=source), patch(
                lineage_target,
                return_value=(evidence, identity_binding, changed),
            ):
                with self.assertRaisesRegex(ValueError, "LINEAGE_IDENTITY_SOURCE_DRIFT"):
                    verify_identity_requirement(result.receipt_path, repo_root=root)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    run_identity_requirement,
    verify_identity_requirement,
)

STORY_SHA = "a" * 64


def _write(path: Path, payload: dict) -> bytes:
    raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


class CS265IdentityRequirementTests(unittest.TestCase):
    def _fixture(self, root: Path, *, kind: str = "player"):
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
        raw = _write(evidence_path, evidence)
        run_dir = root / "cs257"; run_dir.mkdir()
        _write(run_dir / "atomic_fresh_story_semantic_replay.json", {
            "story_snapshot_sha256": STORY_SHA,
            "fresh_story_gates_passed": True,
            "production_semantic_replay_executed": True,
        })
        _write(run_dir / "fresh_story_evidence_manifest.json", {
            "evidence_bindings": [{
                "gate_id": "entity_identity_verification",
                "repository_relative_path": evidence_path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_size": len(raw),
            }]
        })
        source = {
            "schema": "pul7sar-phase18-qwen-image-canonical-candidate-semantic-base-qa-v1",
            "story_snapshot_sha256": STORY_SHA,
            "semantic_base_scene_approved": True,
            "candidate_png": {"repository_relative_path": "candidate.png", "sha256": "b" * 64, "byte_size": 100},
            "identity_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        return run_dir, source, evidence_path

    def test_human_entity_requires_pixel_identity_review(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "candidate.png").write_bytes(b"png")
            run_dir, source, _ = self._fixture(root)
            cs264 = root / "cs264.json"; cs264.write_text("{}")
            with patch("engine.intelligence.qwen_image_canonical_candidate_identity_requirement.verify_canonical_candidate_semantic_base_qa", return_value=source):
                result = run_identity_requirement(cs264, run_dir, root / "out", repo_root=root)
            self.assertTrue(result.pixel_identity_review_required)
            receipt = verify_identity_requirement(result.receipt_path, repo_root=root)
            self.assertFalse(receipt["identity_approved"])
            self.assertFalse(receipt["publication_ready"])
            self.assertEqual(receipt["human_identity_targets"][0]["display_name"], "Test Player")

    def test_nonhuman_entity_does_not_claim_identity_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "candidate.png").write_bytes(b"png")
            run_dir, source, _ = self._fixture(root, kind="club")
            cs264 = root / "cs264.json"; cs264.write_text("{}")
            with patch("engine.intelligence.qwen_image_canonical_candidate_identity_requirement.verify_canonical_candidate_semantic_base_qa", return_value=source):
                result = run_identity_requirement(cs264, run_dir, root / "out", repo_root=root)
            receipt = verify_identity_requirement(result.receipt_path, repo_root=root)
            self.assertFalse(receipt["pixel_identity_review_required"])
            self.assertFalse(receipt["identity_approved"])

    def test_identity_evidence_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "candidate.png").write_bytes(b"png")
            run_dir, source, evidence_path = self._fixture(root)
            cs264 = root / "cs264.json"; cs264.write_text("{}")
            with patch("engine.intelligence.qwen_image_canonical_candidate_identity_requirement.verify_canonical_candidate_semantic_base_qa", return_value=source):
                result = run_identity_requirement(cs264, run_dir, root / "out", repo_root=root)
            evidence_path.write_text("{}")
            with self.assertRaisesRegex(ValueError, "IDENTITY_BYTE_DRIFT"):
                verify_identity_requirement(result.receipt_path, repo_root=root)


if __name__ == "__main__":
    unittest.main()

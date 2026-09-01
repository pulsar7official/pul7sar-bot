from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    build_pixel_identity_review_request,
    verify_pixel_identity_review_request,
)

STORY_SHA = "a" * 64


def _write_json(path: Path, payload: dict) -> bytes:
    raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return raw


class CS266PixelIdentityReviewRequestTests(unittest.TestCase):
    def _fixture(self, root: Path, *, human: bool = True, with_source_refs: bool = True):
        candidate = root / "candidate.png"
        candidate_raw = b"synthetic-candidate-bytes"
        candidate.write_bytes(candidate_raw)

        identity_path = root / "evidence" / "identity.json"
        kind = "player" if human else "club"
        source_refs = ["source:official-profile"] if with_source_refs else []
        identity_payload = {
            "schema": "pul7sar-phase18-entity-identity-evidence-v1",
            "story_snapshot_sha256": STORY_SHA,
            "canonical_entities": [{
                "entity_id": "entity.test",
                "kind": kind,
                "display_name": "Test Entity",
                "aliases": ["Test Entity"],
                "identity_source_refs": source_refs,
            }],
        }
        identity_raw = _write_json(identity_path, identity_payload)

        cs265 = root / "cs265.json"
        cs265.write_text("{}", encoding="utf-8")
        source = {
            "schema": IDENTITY_REQUIREMENT_SCHEMA,
            "receipt_sha256": "c" * 64,
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": {
                "repository_relative_path": "candidate.png",
                "sha256": hashlib.sha256(candidate_raw).hexdigest(),
                "byte_size": len(candidate_raw),
            },
            "identity_evidence": {
                "repository_relative_path": "evidence/identity.json",
                "sha256": hashlib.sha256(identity_raw).hexdigest(),
                "byte_size": len(identity_raw),
            },
            "human_identity_targets": ([{
                "entity_id": "entity.test",
                "display_name": "Test Entity",
                "kind": "player",
            }] if human else []),
            "pixel_identity_review_required": human,
            "identity_requirement_classified": True,
            "identity_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        return cs265, source, candidate, identity_path

    def _build(self, root: Path, *, human: bool = True, with_source_refs: bool = True):
        cs265, source, candidate, identity_path = self._fixture(
            root, human=human, with_source_refs=with_source_refs
        )
        target = (
            "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request."
            "verify_identity_requirement"
        )
        with patch(target, return_value=source):
            result = build_pixel_identity_review_request(
                cs265, root / "out", repo_root=root
            )
            receipt = verify_pixel_identity_review_request(
                result.receipt_path, repo_root=root
            )
        return result, receipt, source, cs265, candidate, identity_path

    def test_human_candidate_creates_fail_closed_review_request(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, receipt, _, _, _, _ = self._build(root, human=True)
            self.assertTrue(result.review_required)
            self.assertFalse(receipt["identity_approved"])
            self.assertFalse(receipt["pixel_identity_review_executed"])
            self.assertFalse(receipt["publication_ready"])
            self.assertEqual(receipt["required_checks"], [
                "candidate_subject_matches_canonical_entity",
                "no_identity_substitution",
                "no_ambiguous_or_conflicting_identity",
                "source_backed_reference_evidence_used",
            ])

    def test_nonhuman_candidate_does_not_open_review_request(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, receipt, _, _, _, _ = self._build(root, human=False)
            self.assertFalse(result.review_required)
            self.assertFalse(receipt["pixel_identity_review_required"])
            self.assertFalse(receipt["identity_approved"])

    def test_missing_source_backed_identity_refs_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs265, source, _, _ = self._fixture(root, human=True, with_source_refs=False)
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request."
                "verify_identity_requirement"
            )
            with patch(target, return_value=source):
                with self.assertRaisesRegex(ValueError, "IDENTITY_SOURCE_REFS_MISSING"):
                    build_pixel_identity_review_request(cs265, root / "out", repo_root=root)

    def test_candidate_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, source, _, candidate, _ = self._build(root, human=True)
            candidate.write_bytes(b"tampered")
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request."
                "verify_identity_requirement"
            )
            with patch(target, return_value=source):
                with self.assertRaisesRegex(ValueError, "CANDIDATE_INVALID_BYTE_DRIFT"):
                    verify_pixel_identity_review_request(result.receipt_path, repo_root=root)

    def test_identity_evidence_byte_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result, _, source, _, _, identity_path = self._build(root, human=True)
            identity_path.write_text("{}", encoding="utf-8")
            target = (
                "engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request."
                "verify_identity_requirement"
            )
            with patch(target, return_value=source):
                with self.assertRaisesRegex(ValueError, "IDENTITY_INVALID_BYTE_DRIFT"):
                    verify_pixel_identity_review_request(result.receipt_path, repo_root=root)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.entity_identity_verification import (
    IDENTITY_EVIDENCE_SCHEMA,
    IDENTITY_GATE_ID,
    VERIFIER_ID,
    VERIFIER_VERSION,
    verify_entity_identity_evidence,
)
from engine.intelligence.qwen_image_entity_identity_gate_verifier import (
    replay_entity_identity_gate,
)


STORY_SHA = "a" * 64
ASSET_SHA = "b" * 64


def _receipt() -> dict[str, str]:
    return {"verifier_id": VERIFIER_ID, "verifier_version": VERIFIER_VERSION}


def _payload() -> dict[str, object]:
    return {
        "schema": IDENTITY_EVIDENCE_SCHEMA,
        "gate_id": IDENTITY_GATE_ID,
        "story_snapshot_sha256": STORY_SHA,
        "canonical_entities": [
            {
                "entity_id": "real_madrid",
                "kind": "club",
                "display_name": "Real Madrid",
                "aliases": ["Real Madrid CF", "ريال مدريد"],
                "identity_source_refs": ["source:official-club-record"],
            },
            {
                "entity_id": "barcelona",
                "kind": "club",
                "display_name": "FC Barcelona",
                "aliases": ["Barcelona", "برشلونة"],
                "identity_source_refs": ["source:official-opponent-record"],
            },
        ],
        "story_entity_references": [
            {"field": "headline", "text": "Real Madrid CF", "expected_entity_id": "real_madrid"},
            {"field": "caption", "text": "برشلونة", "expected_entity_id": "barcelona"},
        ],
        "exact_entity_assets": [
            {
                "entity_id": "real_madrid",
                "asset_kind": "crest",
                "asset_sha256": ASSET_SHA,
                "origin": "approved_exact_asset",
                "generated": False,
                "approved_for_exact_use": True,
            }
        ],
    }


class EntityIdentityGateVerifierTests(unittest.TestCase):
    def _write(self, root: Path, payload: dict[str, object]) -> Path:
        path = root / "identity.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        return path

    def test_identity_verifier_passes_source_backed_unique_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._write(Path(temp_dir), _payload())
            result = replay_entity_identity_gate(path, STORY_SHA, _receipt())
            raw = path.read_bytes()
            self.assertIs(result["gate_passed"], True)
            self.assertEqual(result["source_evidence_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["source_evidence_byte_size"], len(raw))
            self.assertEqual(result["verification_details"]["canonical_entity_count"], 2)
            self.assertEqual(result["verification_details"]["resolved_reference_count"], 2)
            self.assertIs(
                result["verification_details"]["generated_exact_entity_assets_forbidden"],
                True,
            )

    def test_identity_verifier_rejects_alias_collision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["canonical_entities"][1]["aliases"].append("Real Madrid")
            with self.assertRaisesRegex(ValueError, "PUL7SAR_IDENTITY_ALIAS_COLLISION"):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_wrong_expected_entity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["story_entity_references"][0]["expected_entity_id"] = "barcelona"
            with self.assertRaisesRegex(
                ValueError, "PUL7SAR_IDENTITY_REFERENCE_UNRESOLVED_OR_MISMATCHED"
            ):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_missing_identity_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["canonical_entities"][0]["identity_source_refs"] = []
            with self.assertRaisesRegex(ValueError, "PUL7SAR_IDENTITY_SOURCE_REFS_REQUIRED"):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_generated_exact_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["exact_entity_assets"][0]["generated"] = True
            with self.assertRaisesRegex(
                ValueError, "PUL7SAR_IDENTITY_GENERATED_EXACT_ASSET_FORBIDDEN"
            ):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_unapproved_exact_asset_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["exact_entity_assets"][0]["origin"] = "generated"
            with self.assertRaisesRegex(ValueError, "PUL7SAR_IDENTITY_ASSET_ORIGIN_NOT_APPROVED"):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_cross_story_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = _payload()
            payload["story_snapshot_sha256"] = "c" * 64
            with self.assertRaisesRegex(ValueError, "QWEN_IDENTITY_CROSS_STORY_EVIDENCE"):
                replay_entity_identity_gate(
                    self._write(Path(temp_dir), payload), STORY_SHA, _receipt()
                )

    def test_identity_verifier_rejects_verifier_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt = _receipt()
            receipt["verifier_id"] = "pul7sar.production.other"
            with self.assertRaisesRegex(ValueError, "QWEN_IDENTITY_VERIFIER_ID_MISMATCH"):
                verify_entity_identity_evidence(
                    self._write(Path(temp_dir), _payload()), STORY_SHA, receipt
                )

    def test_identity_adapter_exposes_production_source_object(self) -> None:
        self.assertIs(replay_entity_identity_gate.PUL7SAR_PRODUCTION_BACKED, True)
        self.assertEqual(replay_entity_identity_gate.PUL7SAR_VERIFIER_GATE_ID, IDENTITY_GATE_ID)
        self.assertEqual(replay_entity_identity_gate.PUL7SAR_VERIFIER_ID, VERIFIER_ID)
        self.assertEqual(replay_entity_identity_gate.PUL7SAR_VERIFIER_VERSION, VERIFIER_VERSION)
        self.assertIs(
            replay_entity_identity_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_entity_identity_evidence,
        )
        self.assertEqual(
            replay_entity_identity_gate.PUL7SAR_SOURCE_MODULE,
            "engine.intelligence.entity_identity_verification",
        )


if __name__ == "__main__":
    unittest.main()

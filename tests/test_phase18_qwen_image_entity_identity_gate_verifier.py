from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

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


def _write(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "identity.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def test_identity_verifier_passes_source_backed_unique_resolution(tmp_path: Path) -> None:
    path = _write(tmp_path, _payload())
    result = replay_entity_identity_gate(path, STORY_SHA, _receipt())
    raw = path.read_bytes()
    assert result["gate_passed"] is True
    assert result["source_evidence_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["source_evidence_byte_size"] == len(raw)
    assert result["verification_details"]["canonical_entity_count"] == 2
    assert result["verification_details"]["resolved_reference_count"] == 2
    assert result["verification_details"]["generated_exact_entity_assets_forbidden"] is True


def test_identity_verifier_rejects_alias_collision(tmp_path: Path) -> None:
    payload = _payload()
    payload["canonical_entities"][1]["aliases"].append("Real Madrid")
    with pytest.raises(ValueError, match="PUL7SAR_IDENTITY_ALIAS_COLLISION"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_wrong_expected_entity(tmp_path: Path) -> None:
    payload = _payload()
    payload["story_entity_references"][0]["expected_entity_id"] = "barcelona"
    with pytest.raises(ValueError, match="PUL7SAR_IDENTITY_REFERENCE_UNRESOLVED_OR_MISMATCHED"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_missing_identity_source(tmp_path: Path) -> None:
    payload = _payload()
    payload["canonical_entities"][0]["identity_source_refs"] = []
    with pytest.raises(ValueError, match="PUL7SAR_IDENTITY_SOURCE_REFS_REQUIRED"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_generated_exact_asset(tmp_path: Path) -> None:
    payload = _payload()
    payload["exact_entity_assets"][0]["generated"] = True
    with pytest.raises(ValueError, match="PUL7SAR_IDENTITY_GENERATED_EXACT_ASSET_FORBIDDEN"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_unapproved_exact_asset_origin(tmp_path: Path) -> None:
    payload = _payload()
    payload["exact_entity_assets"][0]["origin"] = "generated"
    with pytest.raises(ValueError, match="PUL7SAR_IDENTITY_ASSET_ORIGIN_NOT_APPROVED"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_cross_story_evidence(tmp_path: Path) -> None:
    payload = _payload()
    payload["story_snapshot_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="QWEN_IDENTITY_CROSS_STORY_EVIDENCE"):
        replay_entity_identity_gate(_write(tmp_path, payload), STORY_SHA, _receipt())


def test_identity_verifier_rejects_verifier_identity_drift(tmp_path: Path) -> None:
    receipt = _receipt()
    receipt["verifier_id"] = "pul7sar.production.other"
    with pytest.raises(ValueError, match="QWEN_IDENTITY_VERIFIER_ID_MISMATCH"):
        verify_entity_identity_evidence(_write(tmp_path, _payload()), STORY_SHA, receipt)


def test_identity_adapter_exposes_production_source_object() -> None:
    assert replay_entity_identity_gate.PUL7SAR_PRODUCTION_BACKED is True
    assert replay_entity_identity_gate.PUL7SAR_VERIFIER_GATE_ID == IDENTITY_GATE_ID
    assert replay_entity_identity_gate.PUL7SAR_VERIFIER_ID == VERIFIER_ID
    assert replay_entity_identity_gate.PUL7SAR_VERIFIER_VERSION == VERIFIER_VERSION
    assert replay_entity_identity_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT is verify_entity_identity_evidence
    assert replay_entity_identity_gate.PUL7SAR_SOURCE_MODULE == "engine.intelligence.entity_identity_verification"

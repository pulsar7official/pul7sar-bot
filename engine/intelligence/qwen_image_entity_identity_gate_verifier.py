"""Production-backed entity/identity replay adapter for PUL7SAR Phase 18.

Semantic identity verification lives in ``entity_identity_verification`` so Change
Set 241 binds the actual policy source bytes rather than only this adapter.  Passing
this adapter grants no generation, visual-quality, brand, Golden, or publication
authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.entity_identity_verification import (
    IDENTITY_GATE_ID,
    VERIFIER_ID,
    VERIFIER_VERSION,
    verify_entity_identity_evidence,
)


def replay_entity_identity_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter over the byte-bound production identity policy."""
    return verify_entity_identity_evidence(evidence_path, story_snapshot_sha256, receipt)


replay_entity_identity_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_entity_identity_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_entity_identity_gate.PUL7SAR_VERIFIER_GATE_ID = IDENTITY_GATE_ID
replay_entity_identity_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_entity_identity_gate.PUL7SAR_SOURCE_MODULE = "engine.intelligence.entity_identity_verification"
replay_entity_identity_gate.PUL7SAR_SOURCE_CALLABLE = "verify_entity_identity_evidence"
replay_entity_identity_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = verify_entity_identity_evidence

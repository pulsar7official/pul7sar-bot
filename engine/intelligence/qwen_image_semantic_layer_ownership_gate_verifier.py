"""Production-backed semantic/layer ownership replay adapter for PUL7SAR Phase 18.

The semantic policy lives in ``semantic_layer_ownership`` so Change Set 241 binds the
actual policy source bytes, not merely this adapter. Passing this adapter grants no
generation, visual-quality, brand, Golden, human-review, or publication authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.semantic_layer_ownership import (
    SEMANTIC_LAYER_OWNERSHIP_GATE_ID,
    VERIFIER_ID,
    VERIFIER_VERSION,
    verify_semantic_layer_ownership_evidence,
)


def replay_semantic_layer_ownership_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter over the byte-bound production ownership policy."""
    return verify_semantic_layer_ownership_evidence(
        evidence_path,
        story_snapshot_sha256,
        receipt,
    )


replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_semantic_layer_ownership_gate.PUL7SAR_VERIFIER_GATE_ID = (
    SEMANTIC_LAYER_OWNERSHIP_GATE_ID
)
replay_semantic_layer_ownership_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_semantic_layer_ownership_gate.PUL7SAR_SOURCE_MODULE = (
    "engine.intelligence.semantic_layer_ownership"
)
replay_semantic_layer_ownership_gate.PUL7SAR_SOURCE_CALLABLE = (
    "verify_semantic_layer_ownership_evidence"
)
replay_semantic_layer_ownership_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = (
    verify_semantic_layer_ownership_evidence
)

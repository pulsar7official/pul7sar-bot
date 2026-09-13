"""Production-backed story semantic preflight replay adapter for PUL7SAR Phase 18.

The deterministic semantic policy lives in ``story_semantic_preflight`` so Change Set
241 binds the actual production policy source bytes. Passing this adapter grants no
CUDA, generation, visual-quality, Golden, human-review, brand, or publication authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.story_semantic_preflight import (
    STORY_SEMANTIC_PREFLIGHT_GATE_ID,
    VERIFIER_ID,
    VERIFIER_VERSION,
    verify_story_semantic_preflight_evidence,
)


def replay_story_semantic_preflight_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter over the byte-bound production semantic policy."""
    return verify_story_semantic_preflight_evidence(
        evidence_path,
        story_snapshot_sha256,
        receipt,
    )


replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_GATE_ID = (
    STORY_SEMANTIC_PREFLIGHT_GATE_ID
)
replay_story_semantic_preflight_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_story_semantic_preflight_gate.PUL7SAR_SOURCE_MODULE = (
    "engine.intelligence.story_semantic_preflight"
)
replay_story_semantic_preflight_gate.PUL7SAR_SOURCE_CALLABLE = (
    "verify_story_semantic_preflight_evidence"
)
replay_story_semantic_preflight_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = (
    verify_story_semantic_preflight_evidence
)

"""Production-backed sentiment/neutrality gate replay adapter for Phase 18.

All evidence parsing and semantic evaluation live in ``sentiment_neutrality`` so the
Change Set 241 source-byte binding covers the actual production policy, not only this
adapter. No generation, visual-quality, brand, human-review, Golden, or publication
authority is granted here.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.sentiment_neutrality import (
    SENTIMENT_EVIDENCE_SCHEMA,
    SENTIMENT_GATE_ID,
    VERIFIER_ID,
    VERIFIER_VERSION,
    verify_sentiment_neutrality_evidence,
)


def replay_sentiment_neutrality_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter; delegates to the byte-bound production source."""
    return verify_sentiment_neutrality_evidence(evidence_path, story_snapshot_sha256, receipt)


replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_GATE_ID = SENTIMENT_GATE_ID
replay_sentiment_neutrality_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_MODULE = "engine.intelligence.sentiment_neutrality"
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_CALLABLE = "verify_sentiment_neutrality_evidence"
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = verify_sentiment_neutrality_evidence

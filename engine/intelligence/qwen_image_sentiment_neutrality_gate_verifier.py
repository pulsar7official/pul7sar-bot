"""Production-backed sentiment/neutrality gate replay verifier for Phase 18.

The verifier recomputes editorial neutrality from the exact byte-bound evidence and
PUL7SAR's deterministic sentiment policy. It grants no generation, semantic-layer,
visual-quality, brand, human-review, Golden-quality, or publication authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.sentiment_neutrality import evaluate_sentiment_neutrality

SENTIMENT_EVIDENCE_SCHEMA = "pul7sar-phase18-sentiment-neutrality-evidence-v1"
SENTIMENT_GATE_ID = "sentiment_neutrality"
VERIFIER_ID = "pul7sar.production.sentiment_neutrality"
VERIFIER_VERSION = "1.0.0"

_REQUIRED_EVIDENCE_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "outcome_is_competitive_result",
    "opponent_or_loser_present",
    "editorial_text_fields",
    "source_backed_emotional_attributions",
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _load_evidence(evidence_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_SENTIMENT_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_SENTIMENT_EVIDENCE_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_SENTIMENT_EVIDENCE_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _REQUIRED_EVIDENCE_FIELDS:
        raise ValueError("QWEN_SENTIMENT_EVIDENCE_SHAPE_INVALID")
    return payload, raw


def verify_sentiment_neutrality_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Recompute respectful editorial sentiment semantics from exact evidence bytes."""
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_SENTIMENT_STORY_SHA_INVALID")
    if not isinstance(receipt, Mapping):
        raise ValueError("QWEN_SENTIMENT_RECEIPT_INVALID")
    if receipt.get("verifier_id") != VERIFIER_ID:
        raise ValueError("QWEN_SENTIMENT_VERIFIER_ID_MISMATCH")
    if receipt.get("verifier_version") != VERIFIER_VERSION:
        raise ValueError("QWEN_SENTIMENT_VERIFIER_VERSION_MISMATCH")

    evidence, raw = _load_evidence(evidence_path)
    if evidence["schema"] != SENTIMENT_EVIDENCE_SCHEMA:
        raise ValueError("QWEN_SENTIMENT_EVIDENCE_SCHEMA_DRIFT")
    if evidence["gate_id"] != SENTIMENT_GATE_ID:
        raise ValueError("QWEN_SENTIMENT_GATE_DRIFT")
    if evidence["story_snapshot_sha256"] != story_snapshot_sha256:
        raise ValueError("QWEN_SENTIMENT_CROSS_STORY_EVIDENCE")
    if not isinstance(evidence["editorial_text_fields"], dict):
        raise ValueError("QWEN_SENTIMENT_TEXT_FIELDS_INVALID")
    if not isinstance(evidence["source_backed_emotional_attributions"], list):
        raise ValueError("QWEN_SENTIMENT_BACKED_EMOTIONS_INVALID")

    decision = evaluate_sentiment_neutrality(
        editorial_text_fields=evidence["editorial_text_fields"],
        outcome_is_competitive_result=evidence["outcome_is_competitive_result"],
        opponent_or_loser_present=evidence["opponent_or_loser_present"],
        source_backed_emotional_attributions=evidence["source_backed_emotional_attributions"],
    )
    if decision.allowed is not True:
        codes = sorted({finding.code for finding in decision.findings})
        raise ValueError("QWEN_SENTIMENT_SEMANTIC_REJECTED:" + ",".join(codes))

    details = {
        "checked_text_fields": decision.checked_text_fields,
        "outcome_is_competitive_result": decision.outcome_is_competitive_result,
        "opponent_or_loser_present": decision.opponent_or_loser_present,
        "finding_count": 0,
        "respectful_neutrality_allowed": True,
        "invented_emotional_attribution_found": False,
        "degrading_or_humiliating_language_found": False,
    }
    return {
        "gate_id": SENTIMENT_GATE_ID,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "source_evidence_byte_size": len(raw),
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "gate_passed": True,
        "verification_details": details,
    }


def replay_sentiment_neutrality_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter; delegates to the production sentiment verifier."""
    return verify_sentiment_neutrality_evidence(evidence_path, story_snapshot_sha256, receipt)


replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_GATE_ID = SENTIMENT_GATE_ID
replay_sentiment_neutrality_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_MODULE = __name__
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_CALLABLE = "verify_sentiment_neutrality_evidence"
replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = verify_sentiment_neutrality_evidence

"""Production-backed Fact Lock gate replay verifier for the first Golden trial.

The verifier does not discover facts. It replays the existing deterministic
FactLock against byte-bound, already-classified story claims and requires every
canonical required fact to exist as an explicit FACT at the configured confidence
floor. Forbidden claims fail closed. Safe inferences can never satisfy a required
fact. No generation, pixel, semantic-publication, or Golden-quality authority is
granted here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.fact_lock import FactLock, FactLockViolation
from engine.intelligence.models import ClaimKind, LockedClaim

FACT_LOCK_EVIDENCE_SCHEMA = "pul7sar-phase18-fact-lock-evidence-v1"
FACT_LOCK_GATE_ID = "fact_lock"
VERIFIER_ID = "pul7sar.production.fact_lock"
VERIFIER_VERSION = "1.0.0"

_REQUIRED_EVIDENCE_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "minimum_fact_confidence",
    "claims",
    "required_facts",
)
_REQUIRED_CLAIM_FIELDS = (
    "text",
    "kind",
    "source",
    "confidence",
    "metadata",
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _load_evidence(evidence_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_FACT_LOCK_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_FACT_LOCK_EVIDENCE_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_FACT_LOCK_EVIDENCE_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _REQUIRED_EVIDENCE_FIELDS:
        raise ValueError("QWEN_FACT_LOCK_EVIDENCE_SHAPE_INVALID")
    return payload, raw


def _build_claim(raw_claim: Any) -> LockedClaim:
    if not isinstance(raw_claim, dict) or tuple(raw_claim.keys()) != _REQUIRED_CLAIM_FIELDS:
        raise ValueError("QWEN_FACT_LOCK_CLAIM_SHAPE_INVALID")
    if not isinstance(raw_claim["metadata"], dict):
        raise ValueError("QWEN_FACT_LOCK_CLAIM_METADATA_INVALID")
    try:
        kind = ClaimKind(raw_claim["kind"])
    except (TypeError, ValueError) as exc:
        raise ValueError("QWEN_FACT_LOCK_CLAIM_KIND_INVALID") from exc
    claim = LockedClaim(
        text=raw_claim["text"],
        kind=kind,
        source=raw_claim["source"],
        confidence=raw_claim["confidence"],
        metadata=raw_claim["metadata"],
    )
    if claim.kind is ClaimKind.FACT and claim.source is None:
        raise ValueError("QWEN_FACT_LOCK_FACT_SOURCE_MISSING")
    return claim


def verify_fact_lock_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Replay deterministic FactLock semantics from the exact evidence bytes."""
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_FACT_LOCK_STORY_SHA_INVALID")
    if not isinstance(receipt, Mapping):
        raise ValueError("QWEN_FACT_LOCK_RECEIPT_INVALID")
    if receipt.get("verifier_id") != VERIFIER_ID:
        raise ValueError("QWEN_FACT_LOCK_VERIFIER_ID_MISMATCH")
    if receipt.get("verifier_version") != VERIFIER_VERSION:
        raise ValueError("QWEN_FACT_LOCK_VERIFIER_VERSION_MISMATCH")

    evidence, raw = _load_evidence(evidence_path)
    if evidence["schema"] != FACT_LOCK_EVIDENCE_SCHEMA:
        raise ValueError("QWEN_FACT_LOCK_EVIDENCE_SCHEMA_DRIFT")
    if evidence["gate_id"] != FACT_LOCK_GATE_ID:
        raise ValueError("QWEN_FACT_LOCK_GATE_DRIFT")
    if evidence["story_snapshot_sha256"] != story_snapshot_sha256:
        raise ValueError("QWEN_FACT_LOCK_CROSS_STORY_EVIDENCE")

    minimum_confidence = evidence["minimum_fact_confidence"]
    if not isinstance(minimum_confidence, (int, float)) or isinstance(minimum_confidence, bool):
        raise ValueError("QWEN_FACT_LOCK_CONFIDENCE_FLOOR_INVALID")
    minimum_confidence = float(minimum_confidence)
    if not 0.0 <= minimum_confidence <= 1.0:
        raise ValueError("QWEN_FACT_LOCK_CONFIDENCE_FLOOR_INVALID")

    raw_claims = evidence["claims"]
    if not isinstance(raw_claims, list) or not raw_claims:
        raise ValueError("QWEN_FACT_LOCK_CLAIMS_MISSING")
    claims = tuple(_build_claim(item) for item in raw_claims)

    required_facts = evidence["required_facts"]
    if (
        not isinstance(required_facts, list)
        or not required_facts
        or any(not isinstance(item, str) or not item.strip() for item in required_facts)
    ):
        raise ValueError("QWEN_FACT_LOCK_REQUIRED_FACTS_INVALID")
    normalized_required = [" ".join(item.split()).casefold() for item in required_facts]
    if len(set(normalized_required)) != len(normalized_required):
        raise ValueError("QWEN_FACT_LOCK_REQUIRED_FACTS_DUPLICATE")

    lock = FactLock(claims)
    try:
        lock.assert_publishable()
        matched = tuple(
            lock.require_fact(text, minimum_confidence=minimum_confidence)
            for text in required_facts
        )
    except FactLockViolation as exc:
        raise ValueError("QWEN_FACT_LOCK_SEMANTIC_REJECTED") from exc

    facts = lock.facts
    safe_inferences = lock.safe_inferences
    details = {
        "minimum_fact_confidence": minimum_confidence,
        "claim_count": len(claims),
        "fact_count": len(facts),
        "safe_inference_count": len(safe_inferences),
        "forbidden_count": 0,
        "required_fact_count": len(required_facts),
        "required_facts_matched": [claim.text for claim in matched],
        "fact_sources_present": all(claim.source is not None for claim in facts),
        "safe_inference_cannot_satisfy_required_fact": True,
        "fact_lock_publishable": True,
    }
    return {
        "gate_id": FACT_LOCK_GATE_ID,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "source_evidence_byte_size": len(raw),
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "gate_passed": True,
        "verification_details": details,
    }


def replay_fact_lock_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter; delegates to the production Fact Lock verifier."""
    return verify_fact_lock_evidence(evidence_path, story_snapshot_sha256, receipt)


replay_fact_lock_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_fact_lock_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_fact_lock_gate.PUL7SAR_VERIFIER_GATE_ID = FACT_LOCK_GATE_ID
replay_fact_lock_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_fact_lock_gate.PUL7SAR_SOURCE_MODULE = __name__
replay_fact_lock_gate.PUL7SAR_SOURCE_CALLABLE = "verify_fact_lock_evidence"
replay_fact_lock_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = verify_fact_lock_evidence

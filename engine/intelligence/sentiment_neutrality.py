"""Deterministic editorial sentiment/neutrality policy for PUL7SAR result coverage.

The policy is intentionally conservative. It does not infer intent or emotion. It
checks the supplied editorial copy and explicit semantic annotations for language
that humiliates, mocks, degrades, or invents emotions for a losing/opposing side.
A pass is only a sentiment/neutrality decision; it grants no factual, identity,
generation, visual-quality, brand, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence


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

_NORMALIZE_WS = re.compile(r"\s+")

# High precision phrases only. Ambiguous sports terms are not silently promoted into
# neutral language for canonical Golden work.
_DISRESPECT_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bpathetic\b",
        r"\bhumiliat(?:e|ed|ing|ion)\b",
        r"\bembarrass(?:ed|ing|ment)?\b",
        r"\bshameful\b",
        r"\bclown(?:s|ed|ing)?\b",
        r"\bloser(?:s)?\b",
        r"\bworthless\b",
        r"\binferior\b",
        r"\bdisgrace(?:d|ful)?\b",
        r"\bمذل(?:ة|ون|ين)?\b",
        r"\bمهين(?:ة|ون|ين)?\b",
        r"\bعار\b",
        r"\bفضيحة\b",
        r"\bمثير(?:ة)?\s+للشفقة\b",
        r"\bسخرية\b",
        r"\bمهرج(?:ون|ين|ة)?\b",
    )
)

# Emotional states may be reported only when the evidence explicitly says they are
# source-backed. This avoids converting visual/editorial drama into factual claims.
_EMOTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bdevastated\b",
        r"\bhumiliated\b",
        r"\bashamed\b",
        r"\bbroken\b",
        r"\bdesperate\b",
        r"\bfurious\b",
        r"\bheartbroken\b",
        r"\bمحبط(?:ة|ون|ين)?\b",
        r"\bمنكسر(?:ة|ون|ين)?\b",
        r"\bمذلول(?:ة|ون|ين)?\b",
        r"\bغاضب(?:ة|ون|ين)?\b",
        r"\bيائس(?:ة|ون|ين)?\b",
    )
)


@dataclass(frozen=True)
class SentimentFinding:
    code: str
    field: str
    token: str


@dataclass(frozen=True)
class SentimentNeutralityDecision:
    allowed: bool
    findings: tuple[SentimentFinding, ...]
    checked_text_fields: int
    opponent_or_loser_present: bool
    outcome_is_competitive_result: bool


def _clean(value: str) -> str:
    return _NORMALIZE_WS.sub(" ", value.strip())


def _match_tokens(text: str, patterns: Iterable[re.Pattern[str]]) -> tuple[str, ...]:
    hits: list[str] = []
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            token = _clean(match.group(0)).casefold()
            if token not in hits:
                hits.append(token)
    return tuple(hits)


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


def evaluate_sentiment_neutrality(
    *,
    editorial_text_fields: Mapping[str, str],
    outcome_is_competitive_result: bool,
    opponent_or_loser_present: bool,
    source_backed_emotional_attributions: Sequence[str] = (),
) -> SentimentNeutralityDecision:
    """Evaluate respectful, non-invented sentiment framing from raw editorial copy."""
    if not isinstance(editorial_text_fields, Mapping) or not editorial_text_fields:
        raise ValueError("PUL7SAR_SENTIMENT_TEXT_FIELDS_REQUIRED")
    if outcome_is_competitive_result is not True and outcome_is_competitive_result is not False:
        raise ValueError("PUL7SAR_SENTIMENT_RESULT_FLAG_INVALID")
    if opponent_or_loser_present is not True and opponent_or_loser_present is not False:
        raise ValueError("PUL7SAR_SENTIMENT_OPPONENT_FLAG_INVALID")
    if outcome_is_competitive_result and not opponent_or_loser_present:
        raise ValueError("PUL7SAR_SENTIMENT_RESULT_OPPONENT_CONTEXT_REQUIRED")

    normalized_backed: set[str] = set()
    for value in source_backed_emotional_attributions:
        if not isinstance(value, str) or not _clean(value):
            raise ValueError("PUL7SAR_SENTIMENT_BACKED_EMOTION_INVALID")
        normalized_backed.add(_clean(value).casefold())

    findings: list[SentimentFinding] = []
    checked = 0
    for field, raw_text in editorial_text_fields.items():
        if not isinstance(field, str) or not _clean(field):
            raise ValueError("PUL7SAR_SENTIMENT_FIELD_NAME_INVALID")
        if not isinstance(raw_text, str) or not _clean(raw_text):
            raise ValueError("PUL7SAR_SENTIMENT_FIELD_TEXT_INVALID")
        checked += 1
        text = _clean(raw_text)

        for token in _match_tokens(text, _DISRESPECT_PATTERNS):
            findings.append(SentimentFinding("disrespectful_or_degrading_language", field, token))

        for token in _match_tokens(text, _EMOTION_PATTERNS):
            if token not in normalized_backed:
                findings.append(SentimentFinding("unsupported_emotional_attribution", field, token))

    return SentimentNeutralityDecision(
        allowed=not findings,
        findings=tuple(findings),
        checked_text_fields=checked,
        opponent_or_loser_present=opponent_or_loser_present,
        outcome_is_competitive_result=outcome_is_competitive_result,
    )


def verify_sentiment_neutrality_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Replay-compatible production verifier over exact sentiment evidence bytes."""
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

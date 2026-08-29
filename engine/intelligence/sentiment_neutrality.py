"""Deterministic editorial sentiment/neutrality policy for PUL7SAR result coverage.

The policy is intentionally conservative. It does not infer intent or emotion. It
checks the supplied editorial copy and explicit semantic annotations for language
that humiliates, mocks, degrades, or invents emotions for a losing/opposing side.
A pass is only a sentiment/neutrality decision; it grants no factual, identity,
generation, visual-quality, brand, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Mapping, Sequence


_NORMALIZE_WS = re.compile(r"\s+")

# High precision phrases only. Ambiguous sports terms such as "crushed" are not
# silently accepted; the evidence producer must avoid them for canonical Golden work.
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


def evaluate_sentiment_neutrality(
    *,
    editorial_text_fields: Mapping[str, str],
    outcome_is_competitive_result: bool,
    opponent_or_loser_present: bool,
    source_backed_emotional_attributions: Sequence[str] = (),
) -> SentimentNeutralityDecision:
    """Evaluate respectful, non-invented sentiment framing from raw editorial copy.

    The caller must provide every publication-facing text field that belongs to the
    story package. For competitive-result coverage, an opposing/losing side must be
    explicitly represented in the semantic evidence even if not named in the copy.
    """
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

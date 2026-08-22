"""Sentiment-provider contract and conservative resolution policy.

Discovery/classification providers may suggest emotional direction, but the
stable resolver owns normalization, confidence, and fail-closed behavior. A
provider suggestion is evidence, not authority over editorial neutrality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Protocol, Sequence

from engine.intelligence.models import Sentiment, StoryBrief


@dataclass(frozen=True)
class SentimentEvidence:
    sentiment: Sentiment
    confidence: float
    source: str
    rationale: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.sentiment, Sentiment):
            raise TypeError("sentiment must be Sentiment")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be non-empty")
        if self.rationale is not None and (
            not isinstance(self.rationale, str) or not self.rationale.strip()
        ):
            raise ValueError("rationale must be non-empty or None")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class SentimentProvider(Protocol):
    """Provider boundary for future rules/LLM classifiers."""

    def classify(self, brief: StoryBrief) -> Sequence[SentimentEvidence]: ...


@dataclass(frozen=True)
class SentimentDecision:
    sentiment: Sentiment
    confidence: float
    reason: str
    conflicted: bool = False


class SentimentResolver:
    """Resolve evidence conservatively; strong conflicts collapse to NEUTRAL."""

    def __init__(self, *, minimum_confidence: float = 0.65, conflict_floor: float = 0.75):
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if not 0.0 <= conflict_floor <= 1.0:
            raise ValueError("conflict_floor must be between 0 and 1")
        self.minimum_confidence = minimum_confidence
        self.conflict_floor = conflict_floor

    def resolve(self, evidence: Sequence[SentimentEvidence]) -> SentimentDecision:
        items = tuple(evidence)
        if not items:
            return SentimentDecision(Sentiment.NEUTRAL, 0.0, "no sentiment evidence")
        strong = [item for item in items if item.confidence >= self.conflict_floor]
        strong_labels = {item.sentiment for item in strong}
        if len(strong_labels) > 1:
            return SentimentDecision(
                Sentiment.NEUTRAL,
                min(item.confidence for item in strong),
                "conflicting high-confidence sentiment evidence",
                conflicted=True,
            )
        best = max(items, key=lambda item: item.confidence)
        if best.confidence < self.minimum_confidence:
            return SentimentDecision(
                Sentiment.NEUTRAL,
                best.confidence,
                "sentiment evidence below confidence threshold",
            )
        return SentimentDecision(best.sentiment, best.confidence, "highest-confidence evidence")

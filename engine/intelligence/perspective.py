"""Perspective-aware emotion contracts for competitive sports stories.

A result story does not have one universal emotion. The winner, loser, and
PUL7SAR editorial voice may legitimately carry different perspectives. This
module keeps those perspectives separate so visual direction cannot confuse a
winner's triumph with permission to attack the losing side.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.models import Sentiment


class EditorialRole(str, Enum):
    WINNER = "winner"
    LOSER = "loser"
    SUBJECT = "subject"
    COUNTERPART = "counterpart"
    EDITORIAL = "editorial"


@dataclass(frozen=True)
class PerspectiveSentiment:
    role: EditorialRole
    sentiment: Sentiment
    entity: Optional[str] = None
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.role, EditorialRole):
            raise TypeError("role must be EditorialRole")
        if not isinstance(self.sentiment, Sentiment):
            raise TypeError("sentiment must be Sentiment")
        if self.entity is not None and (
            not isinstance(self.entity, str) or not self.entity.strip()
        ):
            raise ValueError("entity must be non-empty or None")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ResultPerspectives:
    winner: PerspectiveSentiment
    loser: PerspectiveSentiment
    editorial: PerspectiveSentiment

    def __post_init__(self) -> None:
        if self.winner.role is not EditorialRole.WINNER:
            raise ValueError("winner perspective must use WINNER role")
        if self.loser.role is not EditorialRole.LOSER:
            raise ValueError("loser perspective must use LOSER role")
        if self.editorial.role is not EditorialRole.EDITORIAL:
            raise ValueError("editorial perspective must use EDITORIAL role")
        if self.editorial.sentiment is not Sentiment.NEUTRAL:
            raise ValueError("PUL7SAR editorial result perspective must remain neutral")

    @classmethod
    def competitive_result(
        cls,
        *,
        winner_entity: str,
        loser_entity: str,
        winner_sentiment: Sentiment = Sentiment.POSITIVE,
        loser_sentiment: Sentiment = Sentiment.NEGATIVE,
    ) -> "ResultPerspectives":
        return cls(
            winner=PerspectiveSentiment(
                role=EditorialRole.WINNER,
                entity=winner_entity,
                sentiment=winner_sentiment,
            ),
            loser=PerspectiveSentiment(
                role=EditorialRole.LOSER,
                entity=loser_entity,
                sentiment=loser_sentiment,
            ),
            editorial=PerspectiveSentiment(
                role=EditorialRole.EDITORIAL,
                sentiment=Sentiment.NEUTRAL,
            ),
        )

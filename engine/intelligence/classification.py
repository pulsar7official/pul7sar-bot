"""Deterministic story-classification contracts for Phase 18.

This module normalizes already-supplied editorial signals. It deliberately does
not call a model or the network. Later providers may discover candidates, but
this layer owns the stable vocabulary used by routing and policy gates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional


class StoryScope(str, Enum):
    GENERAL = "general"
    ENTITY_LED = "entity_led"
    MULTI_ENTITY = "multi_entity"


class StoryType(str, Enum):
    RESULT = "result"
    TRANSFER = "transfer"
    PREVIEW = "preview"
    PLAYER_STORY = "player_story"
    INJURY = "injury"
    DISCIPLINE = "discipline"
    ORGANIZATION = "organization"
    GENERAL = "general"


class EntityKind(str, Enum):
    PERSON = "person"
    TEAM = "team"
    CLUB = "club"
    COMPETITION = "competition"
    ORGANIZATION = "organization"
    OTHER = "other"


@dataclass(frozen=True)
class EntityCandidate:
    """A candidate mention; never equivalent to verified identity."""

    name: str
    kind: EntityKind
    confidence: float = 0.0
    source: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("entity candidate name must be non-empty")
        if not isinstance(self.kind, EntityKind):
            raise TypeError("kind must be EntityKind")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.source is not None and (
            not isinstance(self.source, str) or not self.source.strip()
        ):
            raise ValueError("source must be non-empty or None")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class StoryClassification:
    story_type: StoryType
    scope: StoryScope
    entity_candidates: tuple[EntityCandidate, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.story_type, StoryType):
            raise TypeError("story_type must be StoryType")
        if not isinstance(self.scope, StoryScope):
            raise TypeError("scope must be StoryScope")
        candidates = tuple(self.entity_candidates)
        if any(not isinstance(item, EntityCandidate) for item in candidates):
            raise TypeError("entity_candidates must contain EntityCandidate values")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.scope is StoryScope.GENERAL and candidates:
            raise ValueError("GENERAL scope must not carry entity candidates")
        if self.scope is StoryScope.ENTITY_LED and not candidates:
            raise ValueError("ENTITY_LED scope requires at least one candidate")
        if self.scope is StoryScope.MULTI_ENTITY and len(candidates) < 2:
            raise ValueError("MULTI_ENTITY scope requires at least two candidates")
        object.__setattr__(self, "entity_candidates", candidates)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class StoryClassifier:
    """Normalize explicit classification signals without inventing missing facts."""

    _TYPE_ALIASES = {
        "result": StoryType.RESULT,
        "score": StoryType.RESULT,
        "match_result": StoryType.RESULT,
        "transfer": StoryType.TRANSFER,
        "rumor": StoryType.TRANSFER,
        "preview": StoryType.PREVIEW,
        "player_story": StoryType.PLAYER_STORY,
        "profile": StoryType.PLAYER_STORY,
        "injury": StoryType.INJURY,
        "discipline": StoryType.DISCIPLINE,
        "organization": StoryType.ORGANIZATION,
        "general": StoryType.GENERAL,
    }

    def classify(
        self,
        *,
        story_type: Optional[str],
        entity_candidates: Iterable[EntityCandidate] = (),
        confidence: float = 1.0,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> StoryClassification:
        normalized_type = self._normalize_type(story_type)
        candidates = tuple(entity_candidates)
        if not candidates:
            scope = StoryScope.GENERAL
        elif len(candidates) == 1:
            scope = StoryScope.ENTITY_LED
        else:
            scope = StoryScope.MULTI_ENTITY
        return StoryClassification(
            story_type=normalized_type,
            scope=scope,
            entity_candidates=candidates,
            confidence=confidence,
            metadata=metadata or {},
        )

    def _normalize_type(self, value: Optional[str]) -> StoryType:
        if value is None:
            return StoryType.GENERAL
        if not isinstance(value, str) or not value.strip():
            raise ValueError("story_type must be non-empty or None")
        key = value.strip().casefold().replace("-", "_").replace(" ", "_")
        try:
            return self._TYPE_ALIASES[key]
        except KeyError as exc:
            raise ValueError(f"unsupported story_type: {value}") from exc

"""Immutable Phase 18 story-intelligence contracts.

The rendering engine should receive already-understood editorial state. These
models deliberately separate story meaning from low-level rendering objects so
identity verification, factual safety, sentiment, and visual routing can evolve
without turning ``RenderContext`` into a catch-all object.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class ClaimKind(str, Enum):
    """How strongly a claim is allowed to influence text or visuals."""

    FACT = "fact"
    SAFE_INFERENCE = "safe_inference"
    FORBIDDEN = "forbidden"


class Sentiment(str, Enum):
    """Editorial/emotional direction used by later visual planning."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    TENSE = "tense"
    NEUTRAL = "neutral"
    ANTICIPATORY = "anticipatory"
    SERIOUS = "serious"


class IdentityStatus(str, Enum):
    """Whether a real-person depiction may safely be attempted."""

    VERIFIED = "verified"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"
    NOT_REQUIRED = "not_required"


@dataclass(frozen=True)
class LockedClaim:
    """One normalized statement after factual classification."""

    text: str
    kind: ClaimKind
    source: Optional[str] = None
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("claim text must be a non-empty string")
        if not isinstance(self.kind, ClaimKind):
            raise TypeError("kind must be ClaimKind")
        if self.source is not None and (
            not isinstance(self.source, str) or not self.source.strip()
        ):
            raise ValueError("source must be a non-empty string or None")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class StoryBrief:
    """Canonical meaning of one news story before visual direction."""

    headline: str
    summary: str
    sport: Optional[str] = None
    story_type: Optional[str] = None
    primary_entity: Optional[str] = None
    secondary_entities: tuple[str, ...] = field(default_factory=tuple)
    sentiment: Sentiment = Sentiment.NEUTRAL
    event_status: Optional[str] = None
    location: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.headline, str) or not self.headline.strip():
            raise ValueError("headline must be a non-empty string")
        if not isinstance(self.summary, str):
            raise TypeError("summary must be str")
        for name in ("sport", "story_type", "primary_entity", "event_status", "location"):
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{name} must be a non-empty string or None")
        if not isinstance(self.sentiment, Sentiment):
            raise TypeError("sentiment must be Sentiment")
        object.__setattr__(self, "secondary_entities", tuple(self.secondary_entities))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class IdentityPlan:
    """Identity safety decision for a person/entity used in the visual."""

    entity_name: Optional[str]
    status: IdentityStatus
    sport: Optional[str] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    team_or_affiliation: Optional[str] = None
    confidence: float = 0.0
    depiction_allowed: bool = False
    reason: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.entity_name is not None and (
            not isinstance(self.entity_name, str) or not self.entity_name.strip()
        ):
            raise ValueError("entity_name must be a non-empty string or None")
        if not isinstance(self.status, IdentityStatus):
            raise TypeError("status must be IdentityStatus")
        for name in (
            "sport",
            "role",
            "gender",
            "nationality",
            "team_or_affiliation",
            "reason",
        ):
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{name} must be a non-empty string or None")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.depiction_allowed and self.status is not IdentityStatus.VERIFIED:
            raise ValueError(
                "depiction_allowed requires VERIFIED identity status"
            )
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class VisualIntent:
    """High-level art-direction decision before deterministic composition."""

    family: str
    concept: str
    sentiment: Sentiment
    hero_entity: Optional[str] = None
    visual_copy: Optional[str] = None
    color_strategy: Optional[str] = None
    identity_plan: Optional[IdentityPlan] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("family", "concept"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("hero_entity", "visual_copy", "color_strategy"):
            value = getattr(self, name)
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{name} must be a non-empty string or None")
        if not isinstance(self.sentiment, Sentiment):
            raise TypeError("sentiment must be Sentiment")
        if self.identity_plan is not None and not isinstance(
            self.identity_plan, IdentityPlan
        ):
            raise TypeError("identity_plan must be IdentityPlan or None")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

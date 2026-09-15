"""Evidence-based identity verification for Phase 18.

This module deliberately does not search the web or call an LLM. It defines the
safety contract between future identity providers and visual planning. External
providers may discover evidence, but depiction permission is decided here using
explicit constraints, confidence, and conflict detection.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Optional

from engine.intelligence.models import IdentityPlan, IdentityStatus


class IdentityVerificationError(ValueError):
    """Raised when identity-verification input is structurally invalid."""


def _clean_optional(value: Optional[str], *, field_name: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise IdentityVerificationError(
            f"{field_name} must be a non-empty string or None"
        )
    return value.strip()


def _canonical(value: Optional[str]) -> Optional[str]:
    """Canonicalize identity text for comparison without changing display text."""

    if value is None:
        return None
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    normalized = re.sub(r"[^\w\u0600-\u06ff]+", " ", normalized, flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


@dataclass(frozen=True)
class IdentityEvidence:
    """One provider's evidence about a real-world entity."""

    canonical_name: str
    source: str
    confidence: float
    sport: Optional[str] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    team_or_affiliation: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.canonical_name, str) or not self.canonical_name.strip():
            raise IdentityVerificationError("canonical_name must be non-empty")
        if not isinstance(self.source, str) or not self.source.strip():
            raise IdentityVerificationError("source must be non-empty")
        if not isinstance(self.confidence, (int, float)):
            raise IdentityVerificationError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise IdentityVerificationError("confidence must be between 0.0 and 1.0")

        object.__setattr__(self, "canonical_name", self.canonical_name.strip())
        object.__setattr__(self, "source", self.source.strip())
        object.__setattr__(self, "confidence", confidence)
        for name in (
            "sport",
            "role",
            "gender",
            "nationality",
            "team_or_affiliation",
        ):
            object.__setattr__(
                self,
                name,
                _clean_optional(getattr(self, name), field_name=name),
            )
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class IdentityRequirements:
    """Context that must be satisfied before a real-person depiction is allowed."""

    entity_name: str
    sport: Optional[str] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    team_or_affiliation: Optional[str] = None
    min_confidence: float = 0.85
    conflict_confidence: float = 0.75

    def __post_init__(self) -> None:
        if not isinstance(self.entity_name, str) or not self.entity_name.strip():
            raise IdentityVerificationError("entity_name must be non-empty")
        object.__setattr__(self, "entity_name", self.entity_name.strip())
        for name in (
            "sport",
            "role",
            "gender",
            "nationality",
            "team_or_affiliation",
        ):
            object.__setattr__(
                self,
                name,
                _clean_optional(getattr(self, name), field_name=name),
            )
        for name in ("min_confidence", "conflict_confidence"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)):
                raise IdentityVerificationError(f"{name} must be numeric")
            value = float(value)
            if not 0.0 <= value <= 1.0:
                raise IdentityVerificationError(f"{name} must be between 0.0 and 1.0")
            object.__setattr__(self, name, value)


class IdentityVerifier:
    """Convert trusted provider evidence into a conservative IdentityPlan.

    The verifier fails closed:
    - name mismatch -> UNVERIFIED
    - required-context mismatch -> UNVERIFIED
    - high-confidence provider conflict -> PARTIAL
    - insufficient confidence -> PARTIAL
    - only a context-consistent, high-confidence result -> VERIFIED
    """

    _CONTEXT_FIELDS = (
        "sport",
        "role",
        "gender",
        "nationality",
        "team_or_affiliation",
    )

    def verify(
        self,
        requirements: IdentityRequirements,
        evidence: Iterable[IdentityEvidence],
    ) -> IdentityPlan:
        if not isinstance(requirements, IdentityRequirements):
            raise TypeError("requirements must be IdentityRequirements")

        items = tuple(evidence)
        if any(not isinstance(item, IdentityEvidence) for item in items):
            raise TypeError("all evidence items must be IdentityEvidence")

        requested_name = _canonical(requirements.entity_name)
        name_matches = tuple(
            item for item in items if _canonical(item.canonical_name) == requested_name
        )
        if not name_matches:
            return self._plan(
                requirements,
                status=IdentityStatus.UNVERIFIED,
                confidence=0.0,
                reason="no evidence matched the requested entity name",
            )

        eligible = tuple(
            item for item in name_matches if self._matches_requirements(requirements, item)
        )
        if not eligible:
            return self._plan(
                requirements,
                status=IdentityStatus.UNVERIFIED,
                confidence=max(item.confidence for item in name_matches),
                reason="name matched but story context did not match identity evidence",
            )

        if self._has_material_conflict(requirements, name_matches):
            return self._plan(
                requirements,
                status=IdentityStatus.PARTIAL,
                confidence=max(item.confidence for item in eligible),
                reason="high-confidence identity evidence contains a material conflict",
            )

        best = max(eligible, key=lambda item: item.confidence)
        if best.confidence < requirements.min_confidence:
            return self._plan(
                requirements,
                status=IdentityStatus.PARTIAL,
                confidence=best.confidence,
                reason="matching identity evidence is below depiction confidence threshold",
                evidence=best,
            )

        return self._plan(
            requirements,
            status=IdentityStatus.VERIFIED,
            confidence=best.confidence,
            reason="identity and required story context verified",
            evidence=best,
        )

    def _matches_requirements(
        self,
        requirements: IdentityRequirements,
        evidence: IdentityEvidence,
    ) -> bool:
        for field_name in self._CONTEXT_FIELDS:
            expected = getattr(requirements, field_name)
            if expected is None:
                continue
            actual = getattr(evidence, field_name)
            if actual is None or _canonical(actual) != _canonical(expected):
                return False
        return True

    def _has_material_conflict(
        self,
        requirements: IdentityRequirements,
        evidence: tuple[IdentityEvidence, ...],
    ) -> bool:
        strong = tuple(
            item
            for item in evidence
            if item.confidence >= requirements.conflict_confidence
        )
        if len(strong) < 2:
            return False

        for field_name in self._CONTEXT_FIELDS:
            values = {
                _canonical(getattr(item, field_name))
                for item in strong
                if getattr(item, field_name) is not None
            }
            if len(values) > 1:
                return True
        return False

    @staticmethod
    def _plan(
        requirements: IdentityRequirements,
        *,
        status: IdentityStatus,
        confidence: float,
        reason: str,
        evidence: Optional[IdentityEvidence] = None,
    ) -> IdentityPlan:
        return IdentityPlan(
            entity_name=requirements.entity_name,
            status=status,
            sport=(evidence.sport if evidence else requirements.sport),
            role=(evidence.role if evidence else requirements.role),
            gender=(evidence.gender if evidence else requirements.gender),
            nationality=(evidence.nationality if evidence else requirements.nationality),
            team_or_affiliation=(
                evidence.team_or_affiliation
                if evidence
                else requirements.team_or_affiliation
            ),
            confidence=confidence,
            depiction_allowed=status is IdentityStatus.VERIFIED,
            reason=reason,
            metadata={
                "evidence_source": evidence.source if evidence else None,
            },
        )

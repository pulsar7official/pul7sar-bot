"""Deterministic factual-safety gate for Phase 18 visual intelligence.

FactLock does not discover facts and does not call a model or the network. It
receives already-classified claims and enforces what downstream editorial and
visual components are allowed to use.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.intelligence.models import ClaimKind, LockedClaim


class FactLockViolation(ValueError):
    """Raised when forbidden or insufficiently trusted claims are requested."""


@dataclass(frozen=True)
class FactLock:
    """Immutable collection of classified claims with strict accessors."""

    claims: tuple[LockedClaim, ...]

    def __init__(self, claims: Iterable[LockedClaim]) -> None:
        normalized = tuple(claims)
        if any(not isinstance(claim, LockedClaim) for claim in normalized):
            raise TypeError("all claims must be LockedClaim instances")
        object.__setattr__(self, "claims", normalized)

    @property
    def facts(self) -> tuple[LockedClaim, ...]:
        return tuple(claim for claim in self.claims if claim.kind is ClaimKind.FACT)

    @property
    def safe_inferences(self) -> tuple[LockedClaim, ...]:
        return tuple(
            claim for claim in self.claims if claim.kind is ClaimKind.SAFE_INFERENCE
        )

    @property
    def forbidden(self) -> tuple[LockedClaim, ...]:
        return tuple(
            claim for claim in self.claims if claim.kind is ClaimKind.FORBIDDEN
        )

    def usable_claims(
        self,
        *,
        include_safe_inference: bool = True,
        minimum_confidence: float = 0.0,
    ) -> tuple[LockedClaim, ...]:
        """Return claims allowed to drive copy/visuals under a confidence floor."""
        if not isinstance(minimum_confidence, (int, float)):
            raise TypeError("minimum_confidence must be numeric")
        minimum_confidence = float(minimum_confidence)
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0.0 and 1.0")

        allowed_kinds = {ClaimKind.FACT}
        if include_safe_inference:
            allowed_kinds.add(ClaimKind.SAFE_INFERENCE)

        return tuple(
            claim
            for claim in self.claims
            if claim.kind in allowed_kinds
            and claim.confidence >= minimum_confidence
        )

    def assert_publishable(self) -> None:
        """Fail closed when a forbidden claim is present in the lock."""
        if self.forbidden:
            texts = "; ".join(claim.text for claim in self.forbidden)
            raise FactLockViolation(f"forbidden claims present: {texts}")

    def require_fact(self, text: str, *, minimum_confidence: float = 1.0) -> LockedClaim:
        """Return an exact normalized fact or fail instead of silently inferring it."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        if not isinstance(minimum_confidence, (int, float)):
            raise TypeError("minimum_confidence must be numeric")
        minimum_confidence = float(minimum_confidence)
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0.0 and 1.0")

        target = " ".join(text.split()).casefold()
        for claim in self.facts:
            normalized = " ".join(claim.text.split()).casefold()
            if normalized == target and claim.confidence >= minimum_confidence:
                return claim

        raise FactLockViolation(
            f"required fact is not locked at confidence >= {minimum_confidence:.2f}: {text}"
        )

"""Final authorization boundary before any original-scene provider is called.

Nothing in this module generates an image. It aggregates the safety decisions
made earlier in Phase 18 and produces one explicit allow/deny decision. Future
image providers must receive an authorization token from this gate rather than
being called directly from story analysis or routing code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.concept_director import (
    ConceptBrief,
    ConceptDirectionError,
    ConceptDirector,
    ProposedConcept,
)
from engine.intelligence.fact_lock import FactLock, FactLockViolation
from engine.intelligence.models import IdentityPlan, IdentityStatus, VisualIntent
from engine.intelligence.sentiment import SentimentDecision


class AuthorizationFailure(str, Enum):
    FACT_LOCK = "fact_lock"
    IDENTITY = "identity"
    SENTIMENT = "sentiment"
    CONCEPT = "concept"


@dataclass(frozen=True)
class GenerationAuthorization:
    allowed: bool
    failures: tuple[AuthorizationFailure, ...] = field(default_factory=tuple)
    reasons: tuple[str, ...] = field(default_factory=tuple)
    token: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        failures = tuple(self.failures)
        reasons = tuple(self.reasons)
        if self.allowed and failures:
            raise ValueError("allowed authorization cannot contain failures")
        if self.allowed and (not isinstance(self.token, str) or not self.token.strip()):
            raise ValueError("allowed authorization requires a non-empty token")
        if not self.allowed and self.token is not None:
            raise ValueError("denied authorization cannot contain a token")
        if any(not isinstance(item, AuthorizationFailure) for item in failures):
            raise TypeError("failures must contain AuthorizationFailure values")
        if any(not isinstance(reason, str) or not reason.strip() for reason in reasons):
            raise ValueError("reasons must contain non-empty strings")
        object.__setattr__(self, "failures", failures)
        object.__setattr__(self, "reasons", reasons)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class GenerationAuthorizer:
    """Aggregate prior gates and fail closed before provider invocation."""

    TOKEN = "phase18-generation-authorized"

    def __init__(self, concept_director: Optional[ConceptDirector] = None) -> None:
        self._concept_director = concept_director or ConceptDirector()

    def authorize(
        self,
        *,
        fact_lock: FactLock,
        intent: VisualIntent,
        concept_brief: ConceptBrief,
        proposed_concept: ProposedConcept,
        identity_plan: Optional[IdentityPlan] = None,
        sentiment_decision: Optional[SentimentDecision] = None,
    ) -> GenerationAuthorization:
        if not isinstance(fact_lock, FactLock):
            raise TypeError("fact_lock must be FactLock")
        if not isinstance(intent, VisualIntent):
            raise TypeError("intent must be VisualIntent")
        if not isinstance(concept_brief, ConceptBrief):
            raise TypeError("concept_brief must be ConceptBrief")
        if not isinstance(proposed_concept, ProposedConcept):
            raise TypeError("proposed_concept must be ProposedConcept")

        failures = []
        reasons = []

        try:
            fact_lock.assert_publishable()
        except FactLockViolation as exc:
            failures.append(AuthorizationFailure.FACT_LOCK)
            reasons.append(str(exc))

        requires_identity = bool(intent.metadata.get("requires_identity_gate"))
        if requires_identity:
            plan = identity_plan or intent.identity_plan
            if plan is None:
                failures.append(AuthorizationFailure.IDENTITY)
                reasons.append("visual intent requires identity verification but no IdentityPlan was supplied")
            elif plan.status is not IdentityStatus.VERIFIED or not plan.depiction_allowed:
                failures.append(AuthorizationFailure.IDENTITY)
                reasons.append("real-person depiction requires VERIFIED identity with depiction_allowed=True")

        if sentiment_decision is not None and sentiment_decision.conflicted:
            failures.append(AuthorizationFailure.SENTIMENT)
            reasons.append("high-confidence sentiment evidence is conflicted")

        try:
            self._concept_director.validate(concept_brief, proposed_concept)
        except (ConceptDirectionError, ValueError) as exc:
            failures.append(AuthorizationFailure.CONCEPT)
            reasons.append(str(exc))

        if failures:
            return GenerationAuthorization(
                allowed=False,
                failures=tuple(failures),
                reasons=tuple(reasons),
                metadata={"family": intent.family},
            )

        return GenerationAuthorization(
            allowed=True,
            token=self.TOKEN,
            metadata={
                "family": intent.family,
                "hero_entity": intent.hero_entity,
                "color_strategy": intent.color_strategy,
            },
        )

    def assert_authorized(self, authorization: GenerationAuthorization) -> str:
        if not isinstance(authorization, GenerationAuthorization):
            raise TypeError("authorization must be GenerationAuthorization")
        if not authorization.allowed or authorization.token != self.TOKEN:
            details = "; ".join(authorization.reasons) or "generation was not authorized"
            raise PermissionError(details)
        return authorization.token

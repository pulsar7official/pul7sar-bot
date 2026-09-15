"""Editorial-neutrality policy for competitive sports visuals.

PUL7SAR may celebrate a winner, but it must not turn the losing side into a
target. This gate protects clubs, teams, athletes, institutions, and fanbases
from accidental humiliation while preserving truthful emotional contrast.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class NeutralityViolation(ValueError):
    pass


class LoserTreatment(str, Enum):
    ABSENT = "absent"
    RESPECTFUL = "respectful"
    REALISTIC_DISAPPOINTMENT = "realistic_disappointment"
    HUMILIATING = "humiliating"


@dataclass(frozen=True)
class ResultVisualTreatment:
    """Policy-relevant description of a proposed result visual."""

    celebrates_winner: bool = True
    loser_treatment: LoserTreatment = LoserTreatment.RESPECTFUL
    mocking_copy: bool = False
    degrading_symbolism: bool = False
    domination_symbolism: bool = False
    exaggerated_shame: bool = False
    verified_story_requires_harsh_context: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.loser_treatment, LoserTreatment):
            raise TypeError("loser_treatment must be LoserTreatment")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class NeutralityDecision:
    allowed: bool
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be non-empty")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class EditorialNeutralityGate:
    """Fail closed on humiliating treatment of the losing side."""

    def evaluate(self, treatment: ResultVisualTreatment) -> NeutralityDecision:
        if not isinstance(treatment, ResultVisualTreatment):
            raise TypeError("treatment must be ResultVisualTreatment")

        violations = []
        if treatment.mocking_copy:
            violations.append("mocking copy")
        if treatment.degrading_symbolism:
            violations.append("degrading symbolism")
        if treatment.domination_symbolism:
            violations.append("domination symbolism")
        if treatment.exaggerated_shame:
            violations.append("exaggerated shame")
        if treatment.loser_treatment is LoserTreatment.HUMILIATING:
            violations.append("humiliating loser treatment")

        # A verified harsh context may justify realistic disappointment or a
        # serious tone. It never authorizes mockery, degradation, or humiliation.
        if violations:
            return NeutralityDecision(
                allowed=False,
                reason="result visual violates PUL7SAR neutrality: " + ", ".join(violations),
                metadata={"violations": tuple(violations)},
            )

        return NeutralityDecision(
            allowed=True,
            reason=(
                "winner may be celebrated while the losing side remains absent, "
                "respectful, or realistically disappointed"
            ),
        )

    def assert_allowed(self, treatment: ResultVisualTreatment) -> None:
        decision = self.evaluate(treatment)
        if not decision.allowed:
            raise NeutralityViolation(decision.reason)

"""Quality-first candidate acceptance and bounded regeneration policy.

Zero-cost development must never lower quality thresholds. If no candidate passes
all gates, the outcome is NO_ACCEPTABLE_SCENE rather than degraded publication.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.base_scene_quality import (
    BaseSceneAcceptanceDecision,
    BaseSceneEvidence,
    BaseSceneVisualAcceptanceGate,
)
from engine.intelligence.generation_package import GenerationPackage


class CandidateOutcome(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NO_ACCEPTABLE_SCENE = "no_acceptable_scene"


@dataclass(frozen=True)
class CandidateEvaluation:
    evidence: BaseSceneEvidence
    decision: BaseSceneAcceptanceDecision
    quality_score: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError("quality_score must be between 0 and 1")
        if not self.decision.accepted and self.quality_score != 0.0:
            raise ValueError("rejected candidates must have quality_score 0.0")


@dataclass(frozen=True)
class CandidateSelectionResult:
    outcome: CandidateOutcome
    selected: CandidateEvaluation | None
    evaluations: tuple[CandidateEvaluation, ...]
    attempts_used: int
    rejection_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class RegenerationPolicy:
    max_attempts: int = 4
    candidates_per_attempt: int = 2

    def __post_init__(self) -> None:
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.candidates_per_attempt <= 0:
            raise ValueError("candidates_per_attempt must be positive")


class QualityFirstCandidateSelector:
    """Rank only candidates that already passed the strict acceptance gate."""

    def __init__(self, gate: BaseSceneVisualAcceptanceGate | None = None) -> None:
        self._gate = gate or BaseSceneVisualAcceptanceGate()

    def evaluate(self, package: GenerationPackage, evidence: BaseSceneEvidence) -> CandidateEvaluation:
        decision = self._gate.evaluate(package, evidence)
        if not decision.accepted:
            return CandidateEvaluation(evidence, decision, 0.0)

        identity = evidence.identity.confidence if evidence.identity.required else 1.0
        framing = evidence.framing.confidence
        nonhero = [region for region in evidence.protected_regions if region.role != "hero"]
        if nonhero:
            cleanliness = 1.0 - (sum(region.occupancy_ratio for region in nonhero) / len(nonhero))
        else:
            cleanliness = 1.0
        cleanliness = max(0.0, min(1.0, cleanliness))

        # Quality weighting is intentionally independent of cost. Economics may
        # decide eligibility upstream; once candidates exist, visual quality wins.
        score = (identity * 0.45) + (framing * 0.35) + (cleanliness * 0.20)
        return CandidateEvaluation(evidence, decision, round(score, 6))

    def select(
        self,
        package: GenerationPackage,
        candidates: tuple[BaseSceneEvidence, ...],
        *,
        attempts_used: int,
    ) -> CandidateSelectionResult:
        if attempts_used <= 0:
            raise ValueError("attempts_used must be positive")
        evaluations = tuple(self.evaluate(package, item) for item in candidates)
        accepted = [item for item in evaluations if item.decision.accepted]
        if not accepted:
            reasons: list[str] = []
            for item in evaluations:
                reasons.extend(item.decision.failures)
            return CandidateSelectionResult(
                CandidateOutcome.NO_ACCEPTABLE_SCENE,
                None,
                evaluations,
                attempts_used,
                tuple(dict.fromkeys(reasons)),
            )
        selected = max(accepted, key=lambda item: item.quality_score)
        return CandidateSelectionResult(
            CandidateOutcome.ACCEPTED,
            selected,
            evaluations,
            attempts_used,
        )


class BoundedRegenerationController:
    """Decide whether another free generation attempt is permitted.

    This class does not call a provider. It only enforces bounded attempts and
    preserves the rule that reaching the limit never authorizes a rejected scene.
    """

    def __init__(self, policy: RegenerationPolicy = RegenerationPolicy()) -> None:
        self.policy = policy

    def may_retry(self, *, attempts_used: int, selection: CandidateSelectionResult) -> bool:
        if attempts_used < 0:
            raise ValueError("attempts_used must be non-negative")
        if selection.outcome is CandidateOutcome.ACCEPTED:
            return False
        return attempts_used < self.policy.max_attempts

    def assert_within_bounds(self, *, attempts_used: int) -> None:
        if attempts_used >= self.policy.max_attempts:
            raise ValueError("regeneration attempt limit reached; no degraded fallback is allowed")

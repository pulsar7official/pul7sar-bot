"""Renderer-agnostic orchestration for PUL7SAR Visual Brain.

This module owns retry/selection semantics. Pixels may come from any renderer and
vision evidence may come from any approved critic adapter, but publication can
never be inferred from generation success alone.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.intelligence.visual_brain import VisualCriticDecision, VisualCriticEvidence, VisualCriticGate


@dataclass(frozen=True)
class CritiquedCandidate:
    concept_id: str
    attempt: int
    artifact: str
    decision: VisualCriticDecision


@dataclass(frozen=True)
class VisualBrainSelection:
    status: str
    winner: CritiquedCandidate | None
    accepted: tuple[CritiquedCandidate, ...]
    rejected: tuple[CritiquedCandidate, ...]
    publication_ready: bool = False


class VisualBrainOrchestrator:
    """Fail closed and choose quality, never first-success pixels."""

    CONTRACT = "pul7sar-visual-brain-orchestrator-v1"

    def __init__(self, *, max_attempts_per_concept: int = 2) -> None:
        if max_attempts_per_concept < 1:
            raise ValueError("max_attempts_per_concept must be >= 1")
        self.max_attempts_per_concept = max_attempts_per_concept
        self.critic = VisualCriticGate()

    def critique(self, *, artifact: str, attempt: int, evidence: VisualCriticEvidence) -> CritiquedCandidate:
        if not artifact.strip():
            raise ValueError("artifact must be non-empty")
        if attempt < 1 or attempt > self.max_attempts_per_concept:
            raise ValueError("attempt is outside the configured retry budget")
        return CritiquedCandidate(evidence.concept_id, attempt, artifact, self.critic.evaluate(evidence))

    def should_retry(self, candidate: CritiquedCandidate) -> bool:
        return (not candidate.decision.accepted) and candidate.attempt < self.max_attempts_per_concept

    @staticmethod
    def select(candidates: Iterable[CritiquedCandidate]) -> VisualBrainSelection:
        items = tuple(candidates)
        accepted = tuple(item for item in items if item.decision.accepted)
        rejected = tuple(item for item in items if not item.decision.accepted)
        if not accepted:
            return VisualBrainSelection("VISUAL_BRAIN_NO_PUBLISHABLE_BASE_VISUAL", None, (), rejected)
        # Deterministic tie-breaking: critic score, then lower retry count, then concept id.
        winner = sorted(accepted, key=lambda item: (-item.decision.score, item.attempt, item.concept_id))[0]
        return VisualBrainSelection("VISUAL_BRAIN_BASE_VISUAL_SELECTED", winner, accepted, rejected)

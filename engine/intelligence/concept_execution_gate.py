"""Authoritative execution admission after visual-concept selection.

Provider-level routing is intentionally lower-level. A visual concept may remain
contract-only even when generic grammar says generation is possible. This gate
prevents that lower-level route from executing a provider or renderer before the
chosen concept has an implemented, approved pixel path.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.concept_renderer_registry import (
    ConceptRendererCapability,
    ConceptRendererStatus,
    ConceptSurfaceClass,
)


class ConceptExecutionStatus(str, Enum):
    ADMITTED = "admitted"
    BLOCKED_RENDERER_NOT_IMPLEMENTED = "blocked_renderer_not_implemented"
    BLOCKED_LOCAL_GENERATOR_NOT_QUALIFIED = "blocked_local_generator_not_qualified"


@dataclass(frozen=True)
class ConceptExecutionDecision:
    status: ConceptExecutionStatus
    execution_allowed: bool
    renderer_execution_allowed: bool
    provider_selection_allowed: bool
    generator_execution_allowed: bool
    reason: str
    concept_renderer_contract: str | None
    contract: str = "pul7sar-concept-execution-gate-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.status, ConceptExecutionStatus):
            raise TypeError("status must be ConceptExecutionStatus")
        if not self.reason.strip():
            raise ValueError("reason is required")
        if not self.execution_allowed and any((
            self.renderer_execution_allowed,
            self.provider_selection_allowed,
            self.generator_execution_allowed,
        )):
            raise ValueError("BLOCKED_CONCEPT_MAY_NOT_AUTHORIZE_ANY_EXECUTION")
        if self.execution_allowed and not self.renderer_execution_allowed:
            raise ValueError("ADMITTED_CONCEPT_REQUIRES_RENDERER_EXECUTION")


class ConceptExecutionGate:
    def evaluate(self, capability: ConceptRendererCapability) -> ConceptExecutionDecision:
        if not isinstance(capability, ConceptRendererCapability):
            raise TypeError("capability must be ConceptRendererCapability")

        if capability.status is ConceptRendererStatus.IMPLEMENTED:
            return ConceptExecutionDecision(
                status=ConceptExecutionStatus.ADMITTED,
                execution_allowed=True,
                renderer_execution_allowed=True,
                provider_selection_allowed=False,
                generator_execution_allowed=False,
                reason="chosen visual concept has an explicit local deterministic/asset renderer",
                concept_renderer_contract=capability.renderer_contract,
            )

        if capability.surface_class is ConceptSurfaceClass.LOCAL_GENERATIVE_ATMOSPHERE:
            return ConceptExecutionDecision(
                status=ConceptExecutionStatus.BLOCKED_LOCAL_GENERATOR_NOT_QUALIFIED,
                execution_allowed=False,
                renderer_execution_allowed=False,
                provider_selection_allowed=False,
                generator_execution_allowed=False,
                reason="local generative atmosphere remains contract-only until runtime qualification and semantic inspection are implemented",
                concept_renderer_contract=None,
            )

        return ConceptExecutionDecision(
            status=ConceptExecutionStatus.BLOCKED_RENDERER_NOT_IMPLEMENTED,
            execution_allowed=False,
            renderer_execution_allowed=False,
            provider_selection_allowed=False,
            generator_execution_allowed=False,
            reason="chosen visual concept has no implemented renderer and may not fall back to a different concept",
            concept_renderer_contract=None,
        )

    def assert_allowed(self, capability: ConceptRendererCapability) -> ConceptExecutionDecision:
        decision = self.evaluate(capability)
        if not decision.execution_allowed:
            raise ValueError(f"VISUAL_CONCEPT_EXECUTION_BLOCKED:{decision.status.value}:{decision.reason}")
        return decision

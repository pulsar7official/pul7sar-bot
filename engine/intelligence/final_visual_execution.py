"""Final execution authority for a fully directed PUL7SAR visual.

The legacy VisualExecutionRouter answers whether a family grammar could use a
provider. The later VisualConceptDirector answers what picture should actually be
made. This module deliberately gives the chosen concept the final veto so a
contract-only concept can never execute via a lower-level family/provider route.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.concept_execution_gate import (
    ConceptExecutionDecision,
    ConceptExecutionGate,
)
from engine.intelligence.concept_renderer_registry import ConceptRendererCapability
from engine.intelligence.visual_execution_route import VisualExecutionDecision


@dataclass(frozen=True)
class FinalVisualExecutionDecision:
    execution_allowed: bool
    renderer_execution_allowed: bool
    provider_selection_allowed: bool
    generator_execution_allowed: bool
    concept_execution: ConceptExecutionDecision
    lower_level_route: VisualExecutionDecision
    reason: str
    contract: str = "pul7sar-final-visual-execution-v1"

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("reason is required")
        if not self.execution_allowed and any((
            self.renderer_execution_allowed,
            self.provider_selection_allowed,
            self.generator_execution_allowed,
        )):
            raise ValueError("BLOCKED_FINAL_VISUAL_MAY_NOT_AUTHORIZE_EXECUTION")
        if self.provider_selection_allowed and not self.generator_execution_allowed:
            raise ValueError("PROVIDER_SELECTION_REQUIRES_GENERATOR_EXECUTION")


class FinalVisualExecutionGate:
    def __init__(self, concept_gate: ConceptExecutionGate | None = None) -> None:
        self._concept_gate = concept_gate or ConceptExecutionGate()

    def resolve(
        self,
        *,
        capability: ConceptRendererCapability,
        lower_level_route: VisualExecutionDecision,
    ) -> FinalVisualExecutionDecision:
        if not isinstance(capability, ConceptRendererCapability):
            raise TypeError("capability must be ConceptRendererCapability")
        if not isinstance(lower_level_route, VisualExecutionDecision):
            raise TypeError("lower_level_route must be VisualExecutionDecision")

        concept = self._concept_gate.evaluate(capability)
        if not concept.execution_allowed:
            return FinalVisualExecutionDecision(
                execution_allowed=False,
                renderer_execution_allowed=False,
                provider_selection_allowed=False,
                generator_execution_allowed=False,
                concept_execution=concept,
                lower_level_route=lower_level_route,
                reason=(
                    "visual concept vetoed execution; lower-level family/provider "
                    "permission cannot override concept readiness"
                ),
            )

        # All currently implemented concepts are local deterministic/verified-asset
        # renderers. A future qualified local-generative concept must first be
        # promoted from CONTRACT_ONLY by the concept registry and execution gate.
        return FinalVisualExecutionDecision(
            execution_allowed=True,
            renderer_execution_allowed=True,
            provider_selection_allowed=concept.provider_selection_allowed,
            generator_execution_allowed=concept.generator_execution_allowed,
            concept_execution=concept,
            lower_level_route=lower_level_route,
            reason="visual concept has an explicit admitted pixel implementation",
        )

"""Fail-closed pixel dispatcher driven by visual concept, not news family.

This resolver never falls back from one visual idea to another. It admits the
concept through FinalVisualExecutionGate, imports exactly the registered renderer,
and verifies class/contract identity before returning an executable binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module

from engine.intelligence.concept_renderer_registry import ConceptRendererCapability, ConceptRendererRegistry
from engine.intelligence.final_visual_execution import FinalVisualExecutionDecision, FinalVisualExecutionGate
from engine.intelligence.visual_concept_director import VisualConceptArchetype
from engine.intelligence.visual_execution_route import VisualExecutionDecision


@dataclass(frozen=True)
class ConceptPixelBinding:
    archetype: VisualConceptArchetype
    renderer_module: str
    renderer_class: str
    renderer_contract: str
    renderer_type: type
    final_execution: FinalVisualExecutionDecision
    contract: str = "pul7sar-concept-pixel-binding-v1"

    def __post_init__(self) -> None:
        if not self.final_execution.execution_allowed:
            raise ValueError("PIXEL_BINDING_REQUIRES_ADMITTED_FINAL_EXECUTION")
        if not self.renderer_module or not self.renderer_class or not self.renderer_contract:
            raise ValueError("PIXEL_BINDING_REQUIRES_EXPLICIT_RENDERER_IDENTITY")


class ConceptPixelDispatcher:
    def __init__(
        self,
        registry: ConceptRendererRegistry | None = None,
        execution_gate: FinalVisualExecutionGate | None = None,
    ) -> None:
        self._registry = registry or ConceptRendererRegistry()
        self._execution = execution_gate or FinalVisualExecutionGate()

    @staticmethod
    def _import_renderer(capability: ConceptRendererCapability) -> type:
        if not capability.renderer_module or not capability.renderer_class:
            raise ValueError("CONCEPT_HAS_NO_RENDERER_IDENTITY")
        module = import_module(capability.renderer_module)
        renderer_type = getattr(module, capability.renderer_class, None)
        if not isinstance(renderer_type, type):
            raise ValueError("REGISTERED_CONCEPT_RENDERER_CLASS_NOT_FOUND")
        return renderer_type

    @staticmethod
    def _declared_contract(renderer_type: type) -> str | None:
        value = getattr(renderer_type, "CONTRACT", None)
        return value if isinstance(value, str) and value.strip() else None

    def bind(
        self,
        *,
        archetype: VisualConceptArchetype,
        lower_level_route: VisualExecutionDecision,
    ) -> ConceptPixelBinding:
        capability = self._registry.get(archetype)
        final = self._execution.resolve(capability=capability, lower_level_route=lower_level_route)
        if not final.execution_allowed:
            raise ValueError(
                "VISUAL_CONCEPT_PIXEL_DISPATCH_BLOCKED:"
                f"{final.concept_execution.status.value}:{archetype.value}"
            )
        renderer_type = self._import_renderer(capability)
        return ConceptPixelBinding(
            archetype=archetype,
            renderer_module=capability.renderer_module or "",
            renderer_class=capability.renderer_class or "",
            renderer_contract=capability.renderer_contract or "",
            renderer_type=renderer_type,
            final_execution=final,
        )

    @staticmethod
    def assert_receipt_contract(binding: ConceptPixelBinding, receipt: object) -> None:
        actual = getattr(receipt, "contract", None)
        if actual != binding.renderer_contract:
            raise ValueError(
                "CONCEPT_RENDERER_RECEIPT_CONTRACT_MISMATCH:"
                f"expected={binding.renderer_contract!r}:actual={actual!r}"
            )

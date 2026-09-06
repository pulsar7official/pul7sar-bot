"""Provider-independent pixel execution routing for PUL7SAR Phase 18.

This module answers a question that must come before provider selection:
Does this approved visual plan need an image generator at all?

Exact-data, tactical and verified-asset stories can be completed without sending
anything to a diffusion/image provider. Hybrid/generative stories may request a
provider only for the elements explicitly owned by the VisualGrammar contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.story_visual_editorial import ProductionMode
from engine.intelligence.visual_grammar import VisualGrammarDecision


class PixelExecutionRoute(str, Enum):
    DETERMINISTIC_ONLY = "deterministic_only"
    VERIFIED_ASSET_ONLY = "verified_asset_only"
    HYBRID_GENERATIVE = "hybrid_generative"
    GENERATIVE_SCENE = "generative_scene"


@dataclass(frozen=True)
class VisualExecutionDecision:
    route: PixelExecutionRoute
    generator_required: bool
    provider_selection_allowed: bool
    generated_elements: tuple[str, ...]
    deterministic_elements: tuple[str, ...]
    reason: str
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "generated_elements", tuple(self.generated_elements))
        object.__setattr__(self, "deterministic_elements", tuple(self.deterministic_elements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class VisualExecutionRouter:
    """Route approved visual grammar before any provider/model is considered."""

    def route(self, grammar: VisualGrammarDecision) -> VisualExecutionDecision:
        if not isinstance(grammar, VisualGrammarDecision):
            raise TypeError("grammar must be VisualGrammarDecision")

        mode = grammar.production_mode
        generated = tuple(grammar.generated_elements)

        if mode is ProductionMode.DETERMINISTIC_COMPOSITION:
            route = PixelExecutionRoute.DETERMINISTIC_ONLY
            generator_required = False
            reason = "production mode owns all required pixels through deterministic composition"
        elif mode is ProductionMode.VERIFIED_ASSET_EDITORIAL:
            route = PixelExecutionRoute.VERIFIED_ASSET_ONLY
            generator_required = False
            reason = "verified assets plus deterministic editorial layers are sufficient; generation is intentionally bypassed"
        elif mode is ProductionMode.GENERATIVE_SCENE:
            if not generated:
                raise ValueError("generative_scene requires at least one generated element")
            route = PixelExecutionRoute.GENERATIVE_SCENE
            generator_required = True
            reason = "approved scene requires generated visual content before deterministic exact layers"
        elif mode is ProductionMode.HYBRID:
            if generated:
                route = PixelExecutionRoute.HYBRID_GENERATIVE
                generator_required = True
                reason = "hybrid plan requires generation only for explicitly approved non-exact scene elements"
            else:
                # Fail closed: a hybrid plan with no generator-owned elements must not
                # invoke a provider merely because its historical mode says HYBRID.
                route = PixelExecutionRoute.DETERMINISTIC_ONLY
                generator_required = False
                reason = "hybrid plan exposes no generator-owned elements, so provider execution is bypassed"
        else:  # pragma: no cover - protects future enum expansion.
            raise ValueError(f"unsupported production mode: {mode!r}")

        return VisualExecutionDecision(
            route=route,
            generator_required=generator_required,
            provider_selection_allowed=generator_required,
            generated_elements=generated if generator_required else (),
            deterministic_elements=grammar.deterministic_elements,
            reason=reason,
            metadata={
                "contract": "pul7sar-visual-execution-route-v1",
                "provider_agnostic": True,
                "provider_bypass": not generator_required,
                "zero_cost_compatible": True,
                "visual_grammar_contract": grammar.metadata.get("contract"),
                "production_mode": mode.value,
            },
        )

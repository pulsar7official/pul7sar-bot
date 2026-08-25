"""Compile Phase 18 art direction into a fail-closed hybrid final composition plan.

This module does not render pixels. It is the production boundary between original
scene synthesis and exact/verified composition. A generated base may contribute
only the non-identifying world; every factual or identity-sensitive layer keeps an
explicit owner and requiredness before a renderer is allowed to compose it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.hybrid_scene_composition import HybridCompositionRegistry, LayerOwner
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_scene_blueprint import VisualSceneBlueprintCompiler


class FinalCompositionMode(str, Enum):
    HYBRID = "hybrid"
    DETERMINISTIC_FIRST = "deterministic_first"


@dataclass(frozen=True)
class FinalCompositionLayer:
    name: str
    owner: LayerOwner
    required: bool


@dataclass(frozen=True)
class HybridFinalCompositionPlan:
    family: EditorialSceneFamily
    archetype_id: str
    mode: FinalCompositionMode
    hero_layer: str
    environment_layer: str
    layers: tuple[FinalCompositionLayer, ...]
    composition_rules: tuple[str, ...]
    forbidden: tuple[str, ...]
    generated_base_required: bool
    generated_base_must_be_unbranded: bool
    generated_base_must_have_no_readable_facts: bool
    publication_ready: bool = False
    contract: str = "pul7sar-hybrid-final-composer-v1"

    def validate(self) -> None:
        exact_names = {
            "pul7sar_brand", "headline", "score", "statistics", "club_crest",
            "verified_subject", "club_name", "competition_mark", "date_time",
        }
        for layer in self.layers:
            if layer.name in exact_names and layer.owner is LayerOwner.SYNTHESIS:
                raise ValueError(f"FINAL_EXACT_LAYER_SYNTHESIS_OWNERSHIP:{layer.name}")
        if self.family is EditorialSceneFamily.TACTICAL_BOARD:
            if self.mode is not FinalCompositionMode.DETERMINISTIC_FIRST or self.generated_base_required:
                raise ValueError("TACTICAL_MUST_REMAIN_DETERMINISTIC_FIRST")
        elif self.mode is not FinalCompositionMode.HYBRID or not self.generated_base_required:
            raise ValueError("GENERATIVE_FAMILY_REQUIRES_HYBRID_BASE")
        if self.publication_ready:
            raise ValueError("PHASE18_PLAN_CANNOT_SELF_DECLARE_PUBLICATION_READY")


class HybridFinalComposer:
    """Create renderer-facing final plans without allowing ownership drift."""

    @classmethod
    def compile(
        cls,
        *,
        family: EditorialSceneFamily,
        story_key: str,
        recent_archetypes: tuple[str, ...] = (),
        seed: int = 0,
    ) -> HybridFinalCompositionPlan:
        decision = CrossFamilyVisualSystem.choose(
            family=family,
            story_key=story_key,
            recent_archetypes=recent_archetypes,
            seed=seed,
        )
        blueprint = VisualSceneBlueprintCompiler().compile(decision)

        if family is EditorialSceneFamily.TACTICAL_BOARD:
            layers = (
                FinalCompositionLayer("pul7sar_brand", LayerOwner.DETERMINISTIC, True),
                FinalCompositionLayer("headline", LayerOwner.DETERMINISTIC, True),
                FinalCompositionLayer("statistics", LayerOwner.DETERMINISTIC, False),
                FinalCompositionLayer("exact_tactical_geometry", LayerOwner.DETERMINISTIC, True),
            )
            plan = HybridFinalCompositionPlan(
                family=family,
                archetype_id=decision.archetype.id,
                mode=FinalCompositionMode.DETERMINISTIC_FIRST,
                hero_layer=blueprint.hero_layer,
                environment_layer=blueprint.environment_layer,
                layers=layers,
                composition_rules=blueprint.composition_rules,
                forbidden=blueprint.forbidden,
                generated_base_required=False,
                generated_base_must_be_unbranded=True,
                generated_base_must_have_no_readable_facts=True,
            )
        else:
            ownership = HybridCompositionRegistry.get(family)
            layers = tuple(
                FinalCompositionLayer(layer.name, layer.owner, layer.required)
                for layer in ownership.layers
            )
            plan = HybridFinalCompositionPlan(
                family=family,
                archetype_id=decision.archetype.id,
                mode=FinalCompositionMode.HYBRID,
                hero_layer=blueprint.hero_layer,
                environment_layer=blueprint.environment_layer,
                layers=layers,
                composition_rules=blueprint.composition_rules,
                forbidden=blueprint.forbidden,
                generated_base_required=True,
                generated_base_must_be_unbranded=ownership.generated_base_must_be_unbranded,
                generated_base_must_have_no_readable_facts=ownership.generated_base_must_have_no_readable_facts,
            )
        plan.validate()
        return plan

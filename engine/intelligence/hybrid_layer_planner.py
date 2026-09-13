"""Hybrid visual layer planner for PUL7SAR Phase 18.

The final editorial image is split into layers by reliability. Diffusion is used
for atmosphere and non-exact texture; code/assets own geometry, identities,
branding, typography, scores and data. This prevents one generative model from
being responsible for every pixel and every factual invariant.

Sport rules define how exact geometry should be produced when a story needs it.
Story complexity decides whether that geometry belongs in the composition at all.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.scene_complexity_policy import SceneComplexityPolicy, SurfaceVisibility
from engine.intelligence.sport_visual_rules import SportVisualRule
from engine.intelligence.story_visual_editorial import EditorialVisualPlan, ProductionMode


class LayerSource(str, Enum):
    GENERATIVE = "generative"
    DETERMINISTIC = "deterministic"
    VERIFIED_ASSET = "verified_asset"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class VisualLayer:
    name: str
    source: LayerSource
    purpose: str
    required: bool = True


@dataclass(frozen=True)
class HybridLayerPlan:
    layers: tuple[VisualLayer, ...]

    def by_name(self, name: str) -> VisualLayer:
        for layer in self.layers:
            if layer.name == name:
                return layer
        raise KeyError(name)


class HybridVisualLayerPlanner:
    def __init__(self, complexity_policy: SceneComplexityPolicy | None = None) -> None:
        self._complexity = complexity_policy or SceneComplexityPolicy()

    def plan(self, editorial: EditorialVisualPlan, sport_rule: SportVisualRule) -> HybridLayerPlan:
        if not isinstance(editorial, EditorialVisualPlan):
            raise TypeError("editorial must be EditorialVisualPlan")
        if not isinstance(sport_rule, SportVisualRule):
            raise TypeError("sport_rule must be SportVisualRule")

        layers: list[VisualLayer] = []
        if editorial.production_mode in {ProductionMode.HYBRID, ProductionMode.GENERATIVE_SCENE}:
            layers.append(VisualLayer(
                "atmosphere_base",
                LayerSource.GENERATIVE,
                "lighting, depth, crowd/environment mood and non-factual texture only",
            ))
        else:
            layers.append(VisualLayer(
                "atmosphere_base",
                LayerSource.OPTIONAL,
                "restrained non-factual background texture only",
                required=False,
            ))

        complexity = self._complexity.decide(
            editorial.event,
            secondary_subject_count=len(editorial.secondary_subjects),
        )
        exact_surface_required = (
            sport_rule.exact_geometry_preferred
            and complexity.surface_visibility in {
                SurfaceVisibility.PARTIAL_DETERMINISTIC,
                SurfaceVisibility.FULL_DETERMINISTIC,
            }
        )
        if exact_surface_required:
            layers.append(VisualLayer(
                "sport_surface_geometry",
                LayerSource.DETERMINISTIC,
                "regulation playing-surface geometry rendered by code under perspective",
            ))
        else:
            layers.append(VisualLayer(
                "sport_surface_geometry",
                LayerSource.OPTIONAL,
                "sport-surface geometry is not a story dependency; use only contextual texture if composition benefits",
                required=False,
            ))

        # Identity-sensitive subjects never come from an unconstrained diffusion guess.
        if editorial.primary_subject:
            layers.append(VisualLayer(
                "hero_identity",
                LayerSource.VERIFIED_ASSET,
                "verified real subject asset or separately identity-verified depiction",
            ))

        layers.extend((
            VisualLayer("exact_entity_marks", LayerSource.VERIFIED_ASSET, "official club/team/competition marks when required", required=False),
            VisualLayer("data_and_score", LayerSource.DETERMINISTIC, "scores, statistics, tables, dates and exact numbers", required=False),
            VisualLayer("editorial_typography", LayerSource.DETERMINISTIC, "headline and supporting editorial copy"),
            VisualLayer("pul7sar_brand", LayerSource.VERIFIED_ASSET, "exact approved PUL7SAR logo, number-7/pulse treatment and social footer"),
        ))
        return HybridLayerPlan(tuple(layers))

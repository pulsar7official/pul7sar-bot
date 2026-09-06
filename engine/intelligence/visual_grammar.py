"""Provider-agnostic visual grammar for PUL7SAR Phase 18.

This module turns an approved EditorialVisualPlan into art-direction rules before
any image generator is selected. The generator is deliberately not named here:
FLUX.2 Klein remains a valid zero-cost backend, but PUL7SAR's visual identity must
not depend on one model, notebook, API, or compute runtime.

The grammar also enforces the Phase 18 complexity rule: football news does not
imply a full football pitch. Exact sport geometry is requested only when the
story itself needs it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.scene_complexity_policy import SceneComplexityDecision, SceneComplexityPolicy, SurfaceVisibility
from engine.intelligence.story_visual_editorial import EditorialEvent, EditorialVisualPlan, ProductionMode, VisualFamily


class FantasyLevel(str, Enum):
    NONE = "none"
    RESTRAINED = "restrained"
    EDITORIAL = "editorial"


class CameraLanguage(str, Enum):
    HERO_CLOSE = "hero_close"
    HERO_MEDIUM = "hero_medium"
    ENVIRONMENTAL_WIDE = "environmental_wide"
    OBJECT_CLOSE = "object_close"
    DUAL_SUBJECT = "dual_subject"
    GRAPHIC_FRONT = "graphic_front"
    TACTICAL_TOP = "tactical_top"


@dataclass(frozen=True)
class VisualGrammarDecision:
    family: VisualFamily
    production_mode: ProductionMode
    surface_visibility: SurfaceVisibility
    camera_language: CameraLanguage
    fantasy_level: FantasyLevel
    hero_subject_limit: int
    environment_direction: str
    lighting_direction: str
    composition_direction: str
    generated_elements: tuple[str, ...]
    deterministic_elements: tuple[str, ...]
    forbidden_generated_elements: tuple[str, ...]
    rationale: str
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "generated_elements", tuple(self.generated_elements))
        object.__setattr__(self, "deterministic_elements", tuple(self.deterministic_elements))
        object.__setattr__(self, "forbidden_generated_elements", tuple(self.forbidden_generated_elements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


_FAMILY_CAMERA = {
    VisualFamily.SCORE_MONUMENT: CameraLanguage.GRAPHIC_FRONT,
    VisualFamily.HERO_MOMENT: CameraLanguage.HERO_MEDIUM,
    VisualFamily.DUEL: CameraLanguage.DUAL_SUBJECT,
    VisualFamily.DESTINATION: CameraLanguage.ENVIRONMENTAL_WIDE,
    VisualFamily.EDITORIAL_PORTRAIT: CameraLanguage.HERO_CLOSE,
    VisualFamily.COMEBACK: CameraLanguage.HERO_MEDIUM,
    VisualFamily.EXIT: CameraLanguage.HERO_MEDIUM,
    VisualFamily.ACHIEVEMENT: CameraLanguage.HERO_MEDIUM,
    VisualFamily.TROPHY_PRESTIGE: CameraLanguage.OBJECT_CLOSE,
    VisualFamily.BRACKET: CameraLanguage.GRAPHIC_FRONT,
    VisualFamily.DATA_EDITORIAL: CameraLanguage.GRAPHIC_FRONT,
    VisualFamily.TACTICAL_INTELLIGENCE: CameraLanguage.TACTICAL_TOP,
    VisualFamily.SERIOUS_NEWS: CameraLanguage.HERO_CLOSE,
    VisualFamily.EVENT_ATMOSPHERE: CameraLanguage.ENVIRONMENTAL_WIDE,
    VisualFamily.ABSTRACT_EDITORIAL: CameraLanguage.OBJECT_CLOSE,
}

_NO_FANTASY_EVENTS = {
    EditorialEvent.INJURY,
    EditorialEvent.SUSPENSION,
    EditorialEvent.OFFICIATING,
    EditorialEvent.CONTROVERSY,
    EditorialEvent.FINANCIAL,
    EditorialEvent.STATEMENT,
}

_RESTRAINED_FANTASY_EVENTS = {
    EditorialEvent.RESULT,
    EditorialEvent.LIVE_MOMENT,
    EditorialEvent.PREVIEW,
    EditorialEvent.TRANSFER_CONFIRMED,
    EditorialEvent.TRANSFER_RUMOUR,
    EditorialEvent.CONTRACT,
    EditorialEvent.RETIREMENT,
    EditorialEvent.APPOINTMENT,
    EditorialEvent.DISMISSAL,
    EditorialEvent.TACTICS,
}


class VisualGrammar:
    """Create stable PUL7SAR art direction without choosing a generator."""

    def __init__(self, complexity_policy: SceneComplexityPolicy | None = None) -> None:
        self._complexity = complexity_policy or SceneComplexityPolicy()

    @staticmethod
    def _fantasy(event: EditorialEvent) -> FantasyLevel:
        if event in _NO_FANTASY_EVENTS:
            return FantasyLevel.NONE
        if event in _RESTRAINED_FANTASY_EVENTS:
            return FantasyLevel.RESTRAINED
        return FantasyLevel.EDITORIAL

    @staticmethod
    def _deterministic_elements(plan: EditorialVisualPlan, complexity: SceneComplexityDecision) -> tuple[str, ...]:
        elements = ["PUL7SAR brand", "headline typography"]
        elements.extend(plan.exact_assets)
        elements.extend(plan.geometry_requirements)
        if complexity.surface_visibility in {SurfaceVisibility.PARTIAL_DETERMINISTIC, SurfaceVisibility.FULL_DETERMINISTIC}:
            elements.append("sport surface geometry")
        if plan.event == EditorialEvent.RESULT:
            elements.extend(("score", "club identity"))
        if plan.event in {EditorialEvent.TABLE, EditorialEvent.DRAW, EditorialEvent.SCHEDULE, EditorialEvent.FINANCIAL}:
            elements.append("exact data")
        return tuple(dict.fromkeys(elements))

    def direct(self, plan: EditorialVisualPlan) -> VisualGrammarDecision:
        if not isinstance(plan, EditorialVisualPlan):
            raise TypeError("plan must be EditorialVisualPlan")
        complexity = self._complexity.decide(plan.event, secondary_subject_count=len(plan.secondary_subjects))
        camera = _FAMILY_CAMERA[plan.visual_family]
        fantasy = self._fantasy(plan.event)

        generated = tuple(plan.generated_elements)
        if plan.production_mode in {ProductionMode.DETERMINISTIC_COMPOSITION, ProductionMode.VERIFIED_ASSET_EDITORIAL}:
            generated = ()

        return VisualGrammarDecision(
            family=plan.visual_family,
            production_mode=plan.production_mode,
            surface_visibility=complexity.surface_visibility,
            camera_language=camera,
            fantasy_level=fantasy,
            hero_subject_limit=complexity.max_hero_subjects,
            environment_direction=complexity.background_strategy,
            lighting_direction="cinematic sports-editorial light; preserve subject readability and clean brand zones",
            composition_direction="single coherent editorial scene; strong focal hierarchy; no collage unless explicitly fact-required",
            generated_elements=generated,
            deterministic_elements=self._deterministic_elements(plan, complexity),
            forbidden_generated_elements=tuple(plan.forbidden_generated_elements),
            rationale=complexity.rationale,
            metadata={
                "contract": "pul7sar-visual-grammar-v1",
                "provider_agnostic": True,
                "avoid_full_venue_generation": complexity.avoid_full_venue_generation,
                "zero_cost_compatible": True,
            },
        )

"""Story-to-Visual Editorial Engine for PUL7SAR Phase 18.

This module is the deterministic editorial contract between story understanding
and visual production. It makes the editorial angle and the visual strategy one
decision, rather than asking an image model to reinterpret a finished caption.

It deliberately does not generate pixels, fabricate facts, or write branding
inside a generative image. Exact text, scores, logos and geometric diagrams are
reserved for deterministic composition layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Optional


class EditorialEvent(str, Enum):
    RESULT = "result"
    LIVE_MOMENT = "live_moment"
    PREVIEW = "preview"
    TRANSFER_CONFIRMED = "transfer_confirmed"
    TRANSFER_RUMOUR = "transfer_rumour"
    CONTRACT = "contract"
    INJURY = "injury"
    COMEBACK = "comeback"
    SUSPENSION = "suspension"
    RETIREMENT = "retirement"
    APPOINTMENT = "appointment"
    DISMISSAL = "dismissal"
    STATEMENT = "statement"
    RECORD = "record"
    AWARD = "award"
    TROPHY = "trophy"
    DRAW = "draw"
    TABLE = "table"
    TACTICS = "tactics"
    OFFICIATING = "officiating"
    CONTROVERSY = "controversy"
    FINANCIAL = "financial"
    ORGANIZATION = "organization"
    SCHEDULE = "schedule"
    QUALIFICATION = "qualification"
    ELIMINATION = "elimination"
    GENERAL = "general"


class VisualFamily(str, Enum):
    SCORE_MONUMENT = "score_monument"
    HERO_MOMENT = "hero_moment"
    DUEL = "duel"
    DESTINATION = "destination"
    EDITORIAL_PORTRAIT = "editorial_portrait"
    COMEBACK = "comeback"
    EXIT = "exit"
    ACHIEVEMENT = "achievement"
    TROPHY_PRESTIGE = "trophy_prestige"
    BRACKET = "bracket"
    DATA_EDITORIAL = "data_editorial"
    TACTICAL_INTELLIGENCE = "tactical_intelligence"
    SERIOUS_NEWS = "serious_news"
    EVENT_ATMOSPHERE = "event_atmosphere"
    ABSTRACT_EDITORIAL = "abstract_editorial"


class ProductionMode(str, Enum):
    GENERATIVE_SCENE = "generative_scene"
    HYBRID = "hybrid"
    DETERMINISTIC_COMPOSITION = "deterministic_composition"
    VERIFIED_ASSET_EDITORIAL = "verified_asset_editorial"


@dataclass(frozen=True)
class EditorialVisualPlan:
    event: EditorialEvent
    sport: str
    story_core: str
    editorial_angle: str
    headline_short: str
    visual_family: VisualFamily
    production_mode: ProductionMode
    primary_subject: Optional[str] = None
    secondary_subjects: tuple[str, ...] = ()
    stakes: str = "normal"
    sentiment: str = "neutral"
    scene_concept: str = ""
    exact_assets: tuple[str, ...] = ()
    generated_elements: tuple[str, ...] = ()
    forbidden_generated_elements: tuple[str, ...] = (
        "PUL7SAR logo",
        "brand wordmark",
        "headline text",
        "scores",
        "statistics",
        "club crests",
        "competition logos",
    )
    geometry_requirements: tuple[str, ...] = ()
    fallback_mode: ProductionMode = ProductionMode.VERIFIED_ASSET_EDITORIAL
    confidence: float = 1.0
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sport.strip() or not self.story_core.strip() or not self.editorial_angle.strip():
            raise ValueError("sport, story_core and editorial_angle are required")
        if not self.headline_short.strip():
            raise ValueError("headline_short is required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "secondary_subjects", tuple(self.secondary_subjects))
        object.__setattr__(self, "exact_assets", tuple(self.exact_assets))
        object.__setattr__(self, "generated_elements", tuple(self.generated_elements))
        object.__setattr__(self, "forbidden_generated_elements", tuple(self.forbidden_generated_elements))
        object.__setattr__(self, "geometry_requirements", tuple(self.geometry_requirements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


_EVENT_POLICY = {
    EditorialEvent.RESULT: (VisualFamily.SCORE_MONUMENT, ProductionMode.HYBRID),
    EditorialEvent.LIVE_MOMENT: (VisualFamily.HERO_MOMENT, ProductionMode.HYBRID),
    EditorialEvent.PREVIEW: (VisualFamily.DUEL, ProductionMode.HYBRID),
    EditorialEvent.TRANSFER_CONFIRMED: (VisualFamily.DESTINATION, ProductionMode.HYBRID),
    EditorialEvent.TRANSFER_RUMOUR: (VisualFamily.EDITORIAL_PORTRAIT, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.CONTRACT: (VisualFamily.EDITORIAL_PORTRAIT, ProductionMode.HYBRID),
    EditorialEvent.INJURY: (VisualFamily.SERIOUS_NEWS, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.COMEBACK: (VisualFamily.COMEBACK, ProductionMode.HYBRID),
    EditorialEvent.SUSPENSION: (VisualFamily.SERIOUS_NEWS, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.RETIREMENT: (VisualFamily.EXIT, ProductionMode.HYBRID),
    EditorialEvent.APPOINTMENT: (VisualFamily.EDITORIAL_PORTRAIT, ProductionMode.HYBRID),
    EditorialEvent.DISMISSAL: (VisualFamily.EXIT, ProductionMode.HYBRID),
    EditorialEvent.STATEMENT: (VisualFamily.EDITORIAL_PORTRAIT, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.RECORD: (VisualFamily.ACHIEVEMENT, ProductionMode.HYBRID),
    EditorialEvent.AWARD: (VisualFamily.ACHIEVEMENT, ProductionMode.HYBRID),
    EditorialEvent.TROPHY: (VisualFamily.TROPHY_PRESTIGE, ProductionMode.HYBRID),
    EditorialEvent.DRAW: (VisualFamily.BRACKET, ProductionMode.DETERMINISTIC_COMPOSITION),
    EditorialEvent.TABLE: (VisualFamily.DATA_EDITORIAL, ProductionMode.DETERMINISTIC_COMPOSITION),
    EditorialEvent.TACTICS: (VisualFamily.TACTICAL_INTELLIGENCE, ProductionMode.DETERMINISTIC_COMPOSITION),
    EditorialEvent.OFFICIATING: (VisualFamily.SERIOUS_NEWS, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.CONTROVERSY: (VisualFamily.SERIOUS_NEWS, ProductionMode.VERIFIED_ASSET_EDITORIAL),
    EditorialEvent.FINANCIAL: (VisualFamily.DATA_EDITORIAL, ProductionMode.DETERMINISTIC_COMPOSITION),
    EditorialEvent.ORGANIZATION: (VisualFamily.ABSTRACT_EDITORIAL, ProductionMode.HYBRID),
    EditorialEvent.SCHEDULE: (VisualFamily.DATA_EDITORIAL, ProductionMode.DETERMINISTIC_COMPOSITION),
    EditorialEvent.QUALIFICATION: (VisualFamily.ACHIEVEMENT, ProductionMode.HYBRID),
    EditorialEvent.ELIMINATION: (VisualFamily.EXIT, ProductionMode.HYBRID),
    EditorialEvent.GENERAL: (VisualFamily.EVENT_ATMOSPHERE, ProductionMode.HYBRID),
}


class StoryVisualEditorialEngine:
    """Select a safe production grammar from an already fact-locked story."""

    def plan(
        self,
        *,
        event: EditorialEvent,
        sport: str,
        story_core: str,
        editorial_angle: str,
        headline_short: str,
        primary_subject: Optional[str] = None,
        secondary_subjects: tuple[str, ...] = (),
        stakes: str = "normal",
        sentiment: str = "neutral",
        exact_assets: tuple[str, ...] = (),
        geometry_requirements: tuple[str, ...] = (),
        confidence: float = 1.0,
    ) -> EditorialVisualPlan:
        family, mode = _EVENT_POLICY[event]
        # Low confidence must never be rescued by increasingly imaginative generation.
        if confidence < 0.72:
            mode = ProductionMode.VERIFIED_ASSET_EDITORIAL
        # Exact geometry/data belongs to code, not diffusion.
        if geometry_requirements and event in {
            EditorialEvent.TACTICS, EditorialEvent.TABLE, EditorialEvent.DRAW,
            EditorialEvent.SCHEDULE, EditorialEvent.FINANCIAL,
        }:
            mode = ProductionMode.DETERMINISTIC_COMPOSITION
        return EditorialVisualPlan(
            event=event,
            sport=sport,
            story_core=story_core,
            editorial_angle=editorial_angle,
            headline_short=headline_short,
            visual_family=family,
            production_mode=mode,
            primary_subject=primary_subject,
            secondary_subjects=secondary_subjects,
            stakes=stakes,
            sentiment=sentiment,
            scene_concept=editorial_angle,
            exact_assets=exact_assets,
            generated_elements=("atmosphere", "lighting", "depth", "environmental texture") if mode in {ProductionMode.HYBRID, ProductionMode.GENERATIVE_SCENE} else (),
            geometry_requirements=geometry_requirements,
            confidence=confidence,
            metadata={"contract": "pul7sar-story-to-visual-v1"},
        )

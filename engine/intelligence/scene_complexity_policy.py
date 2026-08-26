"""Minimize visual complexity before generation.

PUL7SAR should not render a full stadium/pitch simply because a story is about
football. The safest strong editorial concept is usually the one with the fewest
exact physical dependencies. This policy decides how much sport surface is
actually needed for each event family.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.story_visual_editorial import EditorialEvent


class SurfaceVisibility(str, Enum):
    NONE = "none"
    CONTEXT_ONLY = "context_only"
    PARTIAL_DETERMINISTIC = "partial_deterministic"
    FULL_DETERMINISTIC = "full_deterministic"


@dataclass(frozen=True)
class SceneComplexityDecision:
    surface_visibility: SurfaceVisibility
    max_hero_subjects: int
    background_strategy: str
    avoid_full_venue_generation: bool
    rationale: str


class SceneComplexityPolicy:
    _FULL_SURFACE_EVENTS = {EditorialEvent.TACTICS}
    _PARTIAL_SURFACE_EVENTS = {EditorialEvent.RESULT, EditorialEvent.LIVE_MOMENT}
    _CONTEXT_SURFACE_EVENTS = {EditorialEvent.PREVIEW}
    _NO_SURFACE_EVENTS = {
        EditorialEvent.TRANSFER_CONFIRMED,
        EditorialEvent.TRANSFER_RUMOUR,
        EditorialEvent.CONTRACT,
        EditorialEvent.INJURY,
        EditorialEvent.COMEBACK,
        EditorialEvent.SUSPENSION,
        EditorialEvent.RETIREMENT,
        EditorialEvent.APPOINTMENT,
        EditorialEvent.DISMISSAL,
        EditorialEvent.STATEMENT,
        EditorialEvent.RECORD,
        EditorialEvent.AWARD,
        EditorialEvent.TROPHY,
        EditorialEvent.DRAW,
        EditorialEvent.TABLE,
        EditorialEvent.OFFICIATING,
        EditorialEvent.CONTROVERSY,
        EditorialEvent.FINANCIAL,
        EditorialEvent.ORGANIZATION,
        EditorialEvent.SCHEDULE,
        EditorialEvent.QUALIFICATION,
        EditorialEvent.ELIMINATION,
    }

    def decide(self, event: EditorialEvent, *, secondary_subject_count: int = 0) -> SceneComplexityDecision:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        if secondary_subject_count < 0:
            raise ValueError("secondary_subject_count must be non-negative")

        if event in self._FULL_SURFACE_EVENTS:
            return SceneComplexityDecision(
                SurfaceVisibility.FULL_DETERMINISTIC,
                max_hero_subjects=0,
                background_strategy="deterministic tactical surface with restrained atmospheric surround",
                avoid_full_venue_generation=True,
                rationale="exact tactical geometry is the story and must be rendered by code",
            )
        if event in self._PARTIAL_SURFACE_EVENTS:
            return SceneComplexityDecision(
                SurfaceVisibility.PARTIAL_DETERMINISTIC,
                max_hero_subjects=2,
                background_strategy="venue atmosphere plus only the minimum deterministic surface needed for context",
                avoid_full_venue_generation=True,
                rationale="the sporting action/result benefits from limited exact surface context without making a full venue the visual dependency",
            )
        if event in self._CONTEXT_SURFACE_EVENTS:
            return SceneComplexityDecision(
                SurfaceVisibility.CONTEXT_ONLY,
                max_hero_subjects=2,
                background_strategy="editorial sport atmosphere with optional surface texture only when it strengthens the focal story",
                avoid_full_venue_generation=True,
                rationale="a preview needs anticipation and place, not mandatory playing-surface geometry",
            )
        if event in self._NO_SURFACE_EVENTS:
            return SceneComplexityDecision(
                SurfaceVisibility.NONE,
                max_hero_subjects=2,
                background_strategy="portrait, object, data or abstract editorial environment",
                avoid_full_venue_generation=True,
                rationale="the story meaning does not require exact playing-surface depiction",
            )
        return SceneComplexityDecision(
            SurfaceVisibility.CONTEXT_ONLY,
            max_hero_subjects=1 if secondary_subject_count == 0 else 2,
            background_strategy="abstract sport atmosphere with no exact venue dependency",
            avoid_full_venue_generation=True,
            rationale="general stories should communicate atmosphere without unnecessary geometric risk",
        )

"""Unified Story -> Editorial Copy -> Visual Production orchestration.

This is the first Phase 18 contract where wording and image strategy are planned
together. It accepts already-verified fact slots; it does not extract or invent
facts from raw reporting.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional

from engine.intelligence.editorial_headline_grammar import EditorialHeadlineGrammar, HeadlineInput, HeadlineTone
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, EditorialVisualPlan, ProductionMode, StoryVisualEditorialEngine


@dataclass(frozen=True)
class VerifiedEditorialStory:
    event: EditorialEvent
    sport: str
    subject: str
    fact_phrase: str
    story_core: str
    tone: HeadlineTone = HeadlineTone.NEUTRAL
    secondary_subjects: tuple[str, ...] = ()
    competition: Optional[str] = None
    number: Optional[str] = None
    stakes: str = "normal"
    exact_assets: tuple[str, ...] = ()
    confidence: float = 1.0
    metadata: Mapping[str, object] = MappingProxyType({})

    def __post_init__(self) -> None:
        for name in ("sport", "subject", "fact_phrase", "story_core"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "secondary_subjects", tuple(self.secondary_subjects))
        object.__setattr__(self, "exact_assets", tuple(self.exact_assets))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class StoryToVisualDecision:
    headline: str
    editorial_angle: str
    visual_anchor: str
    plan: EditorialVisualPlan
    sport_geometry_requirements: tuple[str, ...]
    high_risk_generated_elements: tuple[str, ...]
    fallback_reason: Optional[str]


class StoryToVisualOrchestrator:
    def __init__(self) -> None:
        self._headlines = EditorialHeadlineGrammar()
        self._sports = SportVisualRuleRegistry()
        self._visuals = StoryVisualEditorialEngine()

    def decide(self, story: VerifiedEditorialStory) -> StoryToVisualDecision:
        rule = self._sports.get(story.sport)
        secondary = story.secondary_subjects[0] if story.secondary_subjects else None
        headline = self._headlines.compose(HeadlineInput(
            event=story.event,
            subject=story.subject,
            fact_phrase=story.fact_phrase,
            tone=story.tone,
            secondary=secondary,
            competition=story.competition,
            number=story.number,
        ))

        # Exact sport geometry is a production constraint, not a diffusion wish.
        geometry = rule.geometry_requirements if rule.exact_geometry_preferred else ()
        plan = self._visuals.plan(
            event=story.event,
            sport=rule.sport,
            story_core=story.story_core,
            editorial_angle=headline.editorial_angle,
            headline_short=headline.headline,
            primary_subject=story.subject,
            secondary_subjects=story.secondary_subjects,
            stakes=story.stakes,
            sentiment=story.tone.value,
            exact_assets=story.exact_assets,
            geometry_requirements=geometry,
            confidence=story.confidence,
        )

        fallback_reason = None
        if not headline.safe_for_visualization:
            plan = EditorialVisualPlan(
                event=plan.event,
                sport=plan.sport,
                story_core=plan.story_core,
                editorial_angle=plan.editorial_angle,
                headline_short=plan.headline_short,
                visual_family=plan.visual_family,
                production_mode=ProductionMode.VERIFIED_ASSET_EDITORIAL,
                primary_subject=plan.primary_subject,
                secondary_subjects=plan.secondary_subjects,
                stakes=plan.stakes,
                sentiment=plan.sentiment,
                scene_concept=plan.scene_concept,
                exact_assets=plan.exact_assets,
                generated_elements=(),
                forbidden_generated_elements=plan.forbidden_generated_elements,
                geometry_requirements=plan.geometry_requirements,
                fallback_mode=plan.fallback_mode,
                confidence=plan.confidence,
                metadata={**dict(plan.metadata), "visualization_fallback": "headline_complexity"},
            )
            fallback_reason = "headline_complexity"
        elif story.confidence < 0.72:
            fallback_reason = "low_story_confidence"

        return StoryToVisualDecision(
            headline=headline.headline,
            editorial_angle=headline.editorial_angle,
            visual_anchor=headline.visual_anchor,
            plan=plan,
            sport_geometry_requirements=geometry,
            high_risk_generated_elements=rule.high_risk_generated_elements,
            fallback_reason=fallback_reason,
        )

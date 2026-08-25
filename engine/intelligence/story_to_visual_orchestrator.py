"""Unified Story -> Editorial Copy -> Visual Concept -> Production orchestration.

The visual concept is selected before renderer execution so a family renderer never
becomes the idea of the picture by default. Copy, scene grammar, concept, exact
ownership and execution routing are derived together from already-verified facts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional

from engine.intelligence.editorial_headline_grammar import EditorialHeadlineGrammar, HeadlineInput, HeadlineTone
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.sports_editorial_scene import SportsEditorialSceneDirector, SportsEditorialScenePlan, EditorialSceneFamily
from engine.intelligence.story_visual_editorial import EditorialEvent, EditorialVisualPlan, ProductionMode, StoryVisualEditorialEngine
from engine.intelligence.visual_concept_director import VisualConceptDecision, VisualConceptDirector, VisualConceptSignals
from engine.intelligence.visual_execution_route import VisualExecutionDecision, VisualExecutionRouter
from engine.intelligence.visual_grammar import VisualGrammar, VisualGrammarDecision


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
    metadata: Mapping[str, object] = field(default_factory=dict)

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
    visual_grammar: VisualGrammarDecision
    sports_editorial_scene: SportsEditorialScenePlan
    visual_concept: VisualConceptDecision
    execution_route: VisualExecutionDecision
    sport_geometry_requirements: tuple[str, ...]
    high_risk_generated_elements: tuple[str, ...]
    fallback_reason: Optional[str]


class StoryToVisualOrchestrator:
    def __init__(self) -> None:
        self._headlines = EditorialHeadlineGrammar()
        self._sports = SportVisualRuleRegistry()
        self._visuals = StoryVisualEditorialEngine()
        self._grammar = VisualGrammar()
        self._scene = SportsEditorialSceneDirector()
        self._concepts = VisualConceptDirector()
        self._execution = VisualExecutionRouter()

    @staticmethod
    def _flag(metadata: Mapping[str, object], key: str) -> bool:
        return metadata.get(key) is True

    def _concept_signals(self, story: VerifiedEditorialStory, family: EditorialSceneFamily) -> VisualConceptSignals:
        metadata = story.metadata
        exact_assets = {str(value).strip().lower() for value in story.exact_assets}
        verified_subject = (
            self._flag(metadata, "verified_subject_asset")
            or any("verified_subject" in value or "verified_player" in value for value in exact_assets)
        )
        verified_action = self._flag(metadata, "verified_action_photo")
        verified_celebration = self._flag(metadata, "verified_celebration_photo")
        # Action/celebration are person-bearing by definition and must not silently
        # bypass provenance. Story metadata must therefore also establish subject provenance.
        verified_subject = verified_subject or verified_action or verified_celebration
        score_margin = metadata.get("score_margin")
        if score_margin is not None:
            if isinstance(score_margin, bool) or not isinstance(score_margin, int):
                raise TypeError("metadata.score_margin must be an integer")
        safe_generated_context = (
            family is EditorialSceneFamily.EVENT_EDITORIAL
            and metadata.get("allow_generated_context", True) is not False
        )
        return VisualConceptSignals(
            verified_subject_asset=verified_subject,
            verified_action_photo=verified_action,
            verified_celebration_photo=verified_celebration,
            verified_context_photo=self._flag(metadata, "verified_context_photo"),
            verified_detail_asset=self._flag(metadata, "verified_detail_asset"),
            exact_club_assets=self._flag(metadata, "exact_club_assets") or any("club" in value for value in exact_assets),
            exact_tactical_data=(family is EditorialSceneFamily.TACTICAL_BOARD) or self._flag(metadata, "exact_tactical_data"),
            exact_data_anchor=(family is EditorialSceneFamily.DATA_MONUMENT) or self._flag(metadata, "exact_data_anchor"),
            decisive_moment_known=self._flag(metadata, "decisive_moment_known"),
            story_requires_person=(family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS),
            story_requires_pitch=(family is EditorialSceneFamily.TACTICAL_BOARD),
            safe_generated_context=safe_generated_context,
            score_margin=score_margin,
        )

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

        grammar = self._grammar.direct(plan)
        sports_scene = self._scene.direct(story.event, grammar)
        visual_concept = self._concepts.direct(
            sports_scene.family,
            self._concept_signals(story, sports_scene.family),
        )
        execution_route = self._execution.route(grammar)

        return StoryToVisualDecision(
            headline=headline.headline,
            editorial_angle=headline.editorial_angle,
            visual_anchor=headline.visual_anchor,
            plan=plan,
            visual_grammar=grammar,
            sports_editorial_scene=sports_scene,
            visual_concept=visual_concept,
            execution_route=execution_route,
            sport_geometry_requirements=geometry,
            high_risk_generated_elements=rule.high_risk_generated_elements,
            fallback_reason=fallback_reason,
        )

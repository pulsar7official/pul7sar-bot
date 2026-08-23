"""End-to-end CPU-safe editorial planning service for PUL7SAR Phase 18.

Input: several fact-locked editorial angles for the same story.
Output: one selected angle, concise headline, production mode, sport-aware geometry,
scene-complexity policy and deterministic/generative layer ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate, EditorialAngleScore, VisualAwareEditorialAngleSelector
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, HybridVisualLayerPlanner
from engine.intelligence.scene_complexity_policy import SceneComplexityDecision, SceneComplexityPolicy
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision, StoryToVisualOrchestrator, VerifiedEditorialStory


@dataclass(frozen=True)
class EditorialPlanningResult:
    selected_angle: Optional[EditorialAngleScore]
    decision: Optional[StoryToVisualDecision]
    layers: Optional[HybridLayerPlan]
    complexity: Optional[SceneComplexityDecision]
    rejected_angle_ids: tuple[str, ...]
    status: str


class EditorialPlanningService:
    def __init__(self) -> None:
        self._angles = VisualAwareEditorialAngleSelector()
        self._orchestrator = StoryToVisualOrchestrator()
        self._sports = SportVisualRuleRegistry()
        self._layers = HybridVisualLayerPlanner()
        self._complexity = SceneComplexityPolicy()

    def plan(
        self,
        *,
        sport: str,
        candidates: tuple[EditorialAngleCandidate, ...],
        tone: HeadlineTone = HeadlineTone.NEUTRAL,
        competition: str | None = None,
        number: str | None = None,
        stakes: str = "normal",
        exact_assets: tuple[str, ...] = (),
    ) -> EditorialPlanningResult:
        selection = self._angles.select(candidates)
        rejected = tuple(item.candidate.angle_id for item in selection.ranked if not item.eligible)
        if selection.selected is None:
            return EditorialPlanningResult(
                selected_angle=None,
                decision=None,
                layers=None,
                complexity=None,
                rejected_angle_ids=rejected,
                status="NO_SAFE_EDITORIAL_ANGLE",
            )

        chosen = selection.selected.candidate
        story = VerifiedEditorialStory(
            event=chosen.event,
            sport=sport,
            subject=chosen.primary_subject,
            fact_phrase=chosen.fact_phrase,
            story_core=chosen.story_core,
            tone=tone,
            secondary_subjects=chosen.secondary_subjects,
            competition=competition,
            number=number,
            stakes=stakes,
            exact_assets=exact_assets,
            confidence=min(chosen.fact_confidence, chosen.identity_confidence if chosen.identity_confidence is not None else 1.0),
            metadata={"selected_angle_id": chosen.angle_id},
        )
        decision = self._orchestrator.decide(story)
        sport_rule = self._sports.get(sport)
        layers = self._layers.plan(decision.plan, sport_rule)
        complexity = self._complexity.decide(chosen.event, secondary_subject_count=len(chosen.secondary_subjects))
        return EditorialPlanningResult(
            selected_angle=selection.selected,
            decision=decision,
            layers=layers,
            complexity=complexity,
            rejected_angle_ids=rejected,
            status="EDITORIAL_VISUAL_PLAN_READY",
        )

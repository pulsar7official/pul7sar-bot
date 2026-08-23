"""End-to-end CPU-safe editorial planning service for PUL7SAR Phase 18.

The service selects one fact-locked editorial angle, builds concise copy, applies
sport/scene complexity policy, verifies deterministic geometry capability, and
then assigns exact visual layers before any expensive generation occurs.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate, EditorialAngleScore, VisualAwareEditorialAngleSelector
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.geometry_capabilities import DeterministicGeometryCapabilityRegistry, GeometryCapability
from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, HybridVisualLayerPlanner
from engine.intelligence.scene_complexity_policy import SceneComplexityDecision, SceneComplexityPolicy, SurfaceVisibility
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision, StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import ProductionMode


@dataclass(frozen=True)
class EditorialPlanningResult:
    selected_angle: Optional[EditorialAngleScore]
    decision: Optional[StoryToVisualDecision]
    layers: Optional[HybridLayerPlan]
    complexity: Optional[SceneComplexityDecision]
    geometry_capability: Optional[GeometryCapability]
    rejected_angle_ids: tuple[str, ...]
    status: str


class EditorialPlanningService:
    def __init__(self) -> None:
        self._angles = VisualAwareEditorialAngleSelector()
        self._orchestrator = StoryToVisualOrchestrator()
        self._sports = SportVisualRuleRegistry()
        self._layers = HybridVisualLayerPlanner()
        self._complexity = SceneComplexityPolicy()
        self._geometry = DeterministicGeometryCapabilityRegistry()

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
            return EditorialPlanningResult(None, None, None, None, None, rejected, "NO_SAFE_EDITORIAL_ANGLE")

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
        complexity = self._complexity.decide(chosen.event, secondary_subject_count=len(chosen.secondary_subjects))
        geometry_capability = self._geometry.evaluate(sport_rule)

        deterministic_surface_required = complexity.surface_visibility in {
            SurfaceVisibility.PARTIAL_DETERMINISTIC,
            SurfaceVisibility.FULL_DETERMINISTIC,
        }
        if deterministic_surface_required and not geometry_capability.ready:
            if complexity.surface_visibility is SurfaceVisibility.FULL_DETERMINISTIC:
                return EditorialPlanningResult(
                    selected_angle=selection.selected,
                    decision=decision,
                    layers=None,
                    complexity=complexity,
                    geometry_capability=geometry_capability,
                    rejected_angle_ids=rejected,
                    status="GEOMETRY_CAPABILITY_BLOCKED",
                )

            # Partial sport context can be safely removed. Use a verified-asset
            # editorial composition rather than allowing diffusion to improvise
            # geometry that PUL7SAR cannot yet render deterministically.
            safe_plan = replace(
                decision.plan,
                production_mode=ProductionMode.VERIFIED_ASSET_EDITORIAL,
                generated_elements=(),
                geometry_requirements=(),
                metadata={**dict(decision.plan.metadata), "geometry_fallback": "surface_removed"},
            )
            decision = replace(decision, plan=safe_plan, sport_geometry_requirements=(), fallback_reason="deterministic_geometry_unavailable")
            complexity = SceneComplexityDecision(
                surface_visibility=SurfaceVisibility.NONE,
                max_hero_subjects=complexity.max_hero_subjects,
                background_strategy="verified subject/assets with abstract non-geometric sport atmosphere",
                avoid_full_venue_generation=True,
                rationale="required deterministic sport renderer is unavailable; surface removed instead of generated",
            )
            sport_rule = replace(sport_rule, exact_geometry_preferred=False, geometry_requirements=())

        layers = self._layers.plan(decision.plan, sport_rule)
        return EditorialPlanningResult(
            selected_angle=selection.selected,
            decision=decision,
            layers=layers,
            complexity=complexity,
            geometry_capability=geometry_capability,
            rejected_angle_ids=rejected,
            status="EDITORIAL_VISUAL_PLAN_READY",
        )

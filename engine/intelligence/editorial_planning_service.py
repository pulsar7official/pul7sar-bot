"""End-to-end CPU-safe editorial planning service for PUL7SAR Phase 18.

The service selects one fact-locked editorial angle, builds concise copy, applies
sport/scene complexity policy, verifies deterministic geometry capability,
resolves the dynamic PUL7SAR accent, and assigns exact visual layers before any
expensive generation occurs.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from engine.intelligence.dynamic_brand import DynamicBrandDecision, DynamicBrandResolver, StoryHeroEvidence
from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate, EditorialAngleScore, VisualAwareEditorialAngleSelector
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.entity_theme import EntityPaletteEvidence
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
    brand: Optional[DynamicBrandDecision]
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
        self._brand = DynamicBrandResolver()

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
        hero_palette: EntityPaletteEvidence | None = None,
        hero_is_unambiguous: bool | None = None,
    ) -> EditorialPlanningResult:
        selection = self._angles.select(candidates)
        rejected = tuple(item.candidate.angle_id for item in selection.ranked if not item.eligible)
        if selection.selected is None:
            return EditorialPlanningResult(None, None, None, None, None, None, rejected, "NO_SAFE_EDITORIAL_ANGLE")

        chosen = selection.selected.candidate
        story_confidence = min(
            chosen.fact_confidence,
            chosen.identity_confidence if chosen.identity_confidence is not None else 1.0,
        )
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
            confidence=story_confidence,
            metadata={"selected_angle_id": chosen.angle_id},
        )
        decision = self._orchestrator.decide(story)
        sport_rule = self._sports.get(sport)
        complexity = self._complexity.decide(chosen.event, secondary_subject_count=len(chosen.secondary_subjects))
        geometry_capability = self._geometry.evaluate(sport_rule)

        if hero_is_unambiguous is None:
            hero_is_unambiguous = len(chosen.secondary_subjects) == 0
        brand = self._brand.resolve(StoryHeroEvidence(
            entity_name=chosen.primary_subject,
            confidence=story_confidence,
            is_unambiguous=hero_is_unambiguous,
            palette=hero_palette,
        ))

        deterministic_surface_required = complexity.surface_visibility in {
            SurfaceVisibility.PARTIAL_DETERMINISTIC,
            SurfaceVisibility.FULL_DETERMINISTIC,
        }

        # Sport policy may know exact geometry for a surface, while the selected
        # editorial scene does not need that surface at all. In NONE/CONTEXT_ONLY
        # modes the layer plan must not accidentally re-introduce exact geometry.
        if not deterministic_surface_required:
            sport_rule = replace(sport_rule, exact_geometry_preferred=False, geometry_requirements=())
            decision = replace(decision, sport_geometry_requirements=())

        elif not geometry_capability.ready:
            if complexity.surface_visibility is SurfaceVisibility.FULL_DETERMINISTIC:
                return EditorialPlanningResult(
                    selected_angle=selection.selected,
                    decision=decision,
                    layers=None,
                    complexity=complexity,
                    geometry_capability=geometry_capability,
                    brand=brand,
                    rejected_angle_ids=rejected,
                    status="GEOMETRY_CAPABILITY_BLOCKED",
                )

            # Partial context may be removed instead of asking generation to
            # improvise exact geometry which PUL7SAR cannot yet render.
            safe_plan = replace(
                decision.plan,
                production_mode=ProductionMode.VERIFIED_ASSET_EDITORIAL,
                generated_elements=(),
                geometry_requirements=(),
                metadata={**dict(decision.plan.metadata), "geometry_fallback": "surface_removed"},
            )
            decision = replace(
                decision,
                plan=safe_plan,
                sport_geometry_requirements=(),
                fallback_reason="deterministic_geometry_unavailable",
            )
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
            brand=brand,
            rejected_angle_ids=rejected,
            status="EDITORIAL_VISUAL_PLAN_READY",
        )

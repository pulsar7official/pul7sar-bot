"""Final CPU-side authorization before any visual generation or composition.

The Story-to-Visual architecture is useful only if the GPU path cannot bypass it.
This gate converts the planning result into an explicit allow/block decision.
It never authorizes publication; it only authorizes the next production stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.editorial_planning_service import EditorialPlanningResult
from engine.intelligence.hybrid_layer_planner import LayerSource
from engine.intelligence.story_visual_editorial import ProductionMode


class VisualProductionAction(str, Enum):
    GENERATE_ATMOSPHERE = "generate_atmosphere"
    BUILD_DETERMINISTIC = "build_deterministic"
    COMPOSE_VERIFIED_ASSETS = "compose_verified_assets"
    BLOCK = "block"


@dataclass(frozen=True)
class EditorialVisualAuthorization:
    allowed: bool
    actions: tuple[VisualProductionAction, ...]
    blockers: tuple[str, ...]
    publication_ready: bool = False


class EditorialVisualAuthorizationGate:
    def evaluate(self, result: EditorialPlanningResult) -> EditorialVisualAuthorization:
        if not isinstance(result, EditorialPlanningResult):
            raise TypeError("result must be EditorialPlanningResult")
        blockers: list[str] = []
        actions: list[VisualProductionAction] = []

        if result.status != "EDITORIAL_VISUAL_PLAN_READY":
            blockers.append("editorial_visual_plan_not_ready")
        if result.selected_angle is None:
            blockers.append("safe_editorial_angle_missing")
        if result.decision is None:
            blockers.append("story_to_visual_decision_missing")
        if result.layers is None:
            blockers.append("hybrid_layer_plan_missing")
        if result.complexity is None:
            blockers.append("scene_complexity_decision_missing")

        if blockers:
            return EditorialVisualAuthorization(False, (VisualProductionAction.BLOCK,), tuple(blockers), False)

        assert result.decision is not None and result.layers is not None
        mode = result.decision.plan.production_mode
        sources = {layer.source for layer in result.layers.layers if layer.required}

        if mode in {ProductionMode.HYBRID, ProductionMode.GENERATIVE_SCENE}:
            if LayerSource.GENERATIVE in sources:
                actions.append(VisualProductionAction.GENERATE_ATMOSPHERE)
        if LayerSource.DETERMINISTIC in sources:
            actions.append(VisualProductionAction.BUILD_DETERMINISTIC)
        if LayerSource.VERIFIED_ASSET in sources:
            actions.append(VisualProductionAction.COMPOSE_VERIFIED_ASSETS)

        if mode is ProductionMode.DETERMINISTIC_COMPOSITION and VisualProductionAction.BUILD_DETERMINISTIC not in actions:
            blockers.append("deterministic_mode_without_deterministic_layer")
        if mode is ProductionMode.VERIFIED_ASSET_EDITORIAL and VisualProductionAction.COMPOSE_VERIFIED_ASSETS not in actions:
            blockers.append("verified_asset_mode_without_verified_asset_layer")
        if result.geometry_capability is not None and not result.geometry_capability.ready:
            # Safe partial-surface fallbacks are permitted only when geometry has
            # already been removed from the plan by EditorialPlanningService.
            geometry_layer = result.layers.by_name("sport_surface_geometry")
            if geometry_layer.required:
                blockers.append("required_geometry_renderer_unavailable")

        if blockers:
            return EditorialVisualAuthorization(False, (VisualProductionAction.BLOCK,), tuple(blockers), False)
        if not actions:
            blockers.append("no_visual_production_action")
            return EditorialVisualAuthorization(False, (VisualProductionAction.BLOCK,), tuple(blockers), False)

        return EditorialVisualAuthorization(True, tuple(dict.fromkeys(actions)), (), False)

    def assert_allowed(self, result: EditorialPlanningResult) -> EditorialVisualAuthorization:
        decision = self.evaluate(result)
        if not decision.allowed:
            raise ValueError("EDITORIAL_VISUAL_AUTHORIZATION_BLOCKED: " + "; ".join(decision.blockers))
        return decision

"""Compile one durable execution plan from approved editorial planning state.

This is the handoff boundary between CPU-side Story-to-Visual intelligence and
actual generation/composition. It records exactly which layer is generative,
which geometry renderer is required, which dynamic brand state was selected,
why that entity owns the 7/pulse accent, and what must be verified before export.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.editorial_planning_service import EditorialPlanningResult
from engine.intelligence.football_pitch_placement import FootballCameraPreset
from engine.intelligence.hybrid_base_scene_contract import HybridBaseSceneContract, HybridBaseSceneContractCompiler
from engine.intelligence.hybrid_layer_planner import LayerSource


@dataclass(frozen=True)
class VisualExecutionPlan:
    status: str
    headline: str
    visual_family: str
    production_mode: str
    base_scene_contract: HybridBaseSceneContract
    geometry_executor: Optional[str]
    football_camera_preset: Optional[FootballCameraPreset]
    dynamic_brand_accent_hex: str
    dynamic_brand_reason: str
    dominant_entity: Optional[str]
    story_dominance_reason: Optional[str]
    layer_sources: tuple[tuple[str, str], ...]
    hard_verification_requirements: tuple[str, ...]


class VisualExecutionPlanCompiler:
    def compile(self, planning: EditorialPlanningResult) -> VisualExecutionPlan:
        if planning.status != "EDITORIAL_VISUAL_PLAN_READY":
            raise ValueError(f"editorial planning is not executable: {planning.status}")
        if planning.decision is None or planning.layers is None or planning.brand is None:
            raise ValueError("editorial planning is incomplete")

        contract = HybridBaseSceneContractCompiler().compile(planning.layers)
        source_by_name = {layer.name: layer.source for layer in planning.layers.layers}
        geometry_executor = None
        camera = None
        if source_by_name.get("sport_surface_geometry") is LayerSource.DETERMINISTIC:
            if planning.geometry_capability is None or not planning.geometry_capability.ready:
                raise ValueError("deterministic sport geometry required without a ready capability")
            geometry_executor = planning.geometry_capability.renderer_id
            if geometry_executor == "football_pitch_projective_v1":
                camera = FootballCameraPreset.HIGH_WIDE_CENTRAL

        requirements = [
            "no_generated_readable_text",
            "no_generated_pul7sar_brand",
            "no_generated_fake_entity_marks",
            "single_continuous_scene",
            "deterministic_typography_applied",
            "dynamic_brand_layer_applied",
        ]
        if geometry_executor:
            requirements.append("deterministic_sport_geometry_applied")
        if "hero_identity" in source_by_name:
            requirements.append("verified_hero_identity_applied")

        return VisualExecutionPlan(
            status="VISUAL_EXECUTION_PLAN_READY",
            headline=planning.decision.headline,
            visual_family=planning.decision.plan.visual_family.value,
            production_mode=planning.decision.plan.production_mode.value,
            base_scene_contract=contract,
            geometry_executor=geometry_executor,
            football_camera_preset=camera,
            dynamic_brand_accent_hex=planning.brand.accent_hex,
            dynamic_brand_reason=planning.brand.reason.value,
            dominant_entity=planning.brand.hero_entity,
            story_dominance_reason=planning.brand.story_dominance_reason,
            layer_sources=tuple((layer.name, layer.source.value) for layer in planning.layers.layers),
            hard_verification_requirements=tuple(requirements),
        )

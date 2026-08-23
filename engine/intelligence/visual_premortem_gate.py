"""Fail-closed pre-mortem gate for PUL7SAR visual production.

The gate converts predictable editorial/visual failure scenarios into an explicit
execution decision before GPU work and again before publication. It does not try
to make a bad plan prettier; it either chooses a safe fallback, allows an
engineering-only proof, or blocks the path that cannot be proven safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from engine.intelligence.editorial_planning_service import EditorialPlanningResult
from engine.intelligence.hybrid_layer_planner import LayerSource
from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionPolicy
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.story_visual_editorial import ProductionMode
from engine.intelligence.visual_failure_scenarios import FailureScenarioReport, FailureSeverity, VisualFailureScenarioEngine


class PremortemAction(str, Enum):
    PROCEED = "proceed"
    ENGINEERING_PROOF_ONLY = "engineering_proof_only"
    REPLAN_TO_SAFE_FALLBACK = "replan_to_safe_fallback"
    BLOCK = "block"


@dataclass(frozen=True)
class VisualPremortemDecision:
    action: PremortemAction
    gpu_execution_allowed: bool
    publication_allowed: bool
    report: FailureScenarioReport
    fallback_reasons: tuple[str, ...]
    blockers: tuple[str, ...]


class VisualPremortemGate:
    """Anticipate likely failures from the approved plan and runtime capabilities."""

    def __init__(self) -> None:
        self._scenarios = VisualFailureScenarioEngine()
        self._inspection = HybridVisualInspectionPolicy()

    def evaluate(
        self,
        *,
        planning: EditorialPlanningResult,
        verified_facts: Mapping[str, object],
        vision_capabilities: LocalVisionCapabilityReport,
        identity_required: bool,
        identity_verified: bool,
        dominant_palette_verified: bool,
        brand_geometry_approved: bool,
        readable_text_required: bool = True,
    ) -> VisualPremortemDecision:
        if planning.status != "EDITORIAL_VISUAL_PLAN_READY" or planning.decision is None or planning.layers is None:
            return VisualPremortemDecision(
                PremortemAction.BLOCK, False, False, FailureScenarioReport(()), (), ("editorial_visual_plan_not_ready",)
            )

        source_by_name = {layer.name: layer.source for layer in planning.layers.layers}
        geometry_required = source_by_name.get("sport_surface_geometry") is LayerSource.DETERMINISTIC
        geometry_ready = bool(planning.geometry_capability and planning.geometry_capability.ready) if geometry_required else True
        production_mode = planning.decision.plan.production_mode
        inspection = self._inspection.evaluate(vision_capabilities, identity_required=identity_required)

        report = self._scenarios.evaluate(
            event=planning.selected_angle.candidate.event if planning.selected_angle else planning.decision.plan.event,
            production_mode=production_mode,
            verified_facts=verified_facts,
            has_verified_palette_for_dominant_entity=dominant_palette_verified,
            identity_required=identity_required,
            identity_verified=identity_verified,
            deterministic_geometry_required=geometry_required,
            deterministic_geometry_ready=geometry_ready,
            readable_text_required=readable_text_required,
            brand_geometry_approved=brand_geometry_approved,
            semantic_visual_inspection_ready=inspection.automatic_visual_qa_ready,
            subject_count=1 + len(planning.decision.plan.secondary_subjects),
        )

        hard = tuple(item.scenario_id for item in report.scenarios if item.severity is FailureSeverity.HARD_BLOCK)
        warnings = tuple(item.scenario_id for item in report.scenarios if item.severity is FailureSeverity.WARNING)

        # Some hard scenarios block GPU because generation cannot repair them.
        pre_gpu_blockers = {
            "geometry_renderer_missing",
            "identity_unverified",
            "generated_text_dependency",
            "winner_brand_before_final",
            "transfer_not_final",
            "wrong_production_mode_for_exact_data",
        }
        execution_blockers = tuple(item for item in hard if item in pre_gpu_blockers)
        publication_only = tuple(item for item in hard if item not in pre_gpu_blockers)

        if execution_blockers:
            return VisualPremortemDecision(
                PremortemAction.BLOCK, False, False, report, warnings, execution_blockers + publication_only
            )

        # Missing semantic inspection or final brand recipe should not stop a
        # useful engineering proof, but they must never silently become publishable.
        if publication_only:
            return VisualPremortemDecision(
                PremortemAction.ENGINEERING_PROOF_ONLY,
                True,
                False,
                report,
                warnings + publication_only,
                publication_only,
            )

        # Warnings mean the plan is safe only because deterministic fallback is
        # available (for example, default red when a verified team palette is absent).
        if warnings:
            return VisualPremortemDecision(
                PremortemAction.REPLAN_TO_SAFE_FALLBACK,
                True,
                inspection.publication_visual_gate_ready and brand_geometry_approved,
                report,
                warnings,
                (),
            )

        return VisualPremortemDecision(
            PremortemAction.PROCEED,
            True,
            inspection.publication_visual_gate_ready and brand_geometry_approved,
            report,
            (),
            (),
        )

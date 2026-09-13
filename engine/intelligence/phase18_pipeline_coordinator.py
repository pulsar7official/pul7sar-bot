"""Fail-closed CPU coordinator for PUL7SAR Phase 18 Story-to-Visual planning.

This is the high-level boundary before generation. It never generates pixels. It
combines preproduction fact/state integrity, editorial planning, execution-plan
compilation and visual pre-mortem into one auditable decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from engine.intelligence.editorial_angle_selector import EditorialAngleCandidate
from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_planning_service import EditorialPlanningResult, EditorialPlanningService
from engine.intelligence.entity_theme import EntityPaletteEvidence
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport
from engine.intelligence.preproduction_integrity import ExactSlotConsensusRequirement, PreproductionIntegrityDecision, PreproductionIntegrityGate
from engine.intelligence.visual_execution_plan import VisualExecutionPlan, VisualExecutionPlanCompiler
from engine.intelligence.visual_premortem_gate import VisualPremortemDecision, VisualPremortemGate
from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class Phase18PipelineDecision:
    status: str
    preproduction: PreproductionIntegrityDecision
    planning: EditorialPlanningResult | None
    execution_plan: VisualExecutionPlan | None
    premortem: VisualPremortemDecision | None
    gpu_execution_allowed: bool
    publication_allowed_at_this_stage: bool
    blockers: tuple[str, ...]


class Phase18PipelineCoordinator:
    def __init__(self) -> None:
        self._integrity = PreproductionIntegrityGate()
        self._planning = EditorialPlanningService()
        self._premortem = VisualPremortemGate()
        self._execution = VisualExecutionPlanCompiler()

    def prepare(
        self,
        *,
        event: EditorialEvent,
        sport: str,
        facts: Mapping[str, object],
        candidates: tuple[EditorialAngleCandidate, ...],
        vision_capabilities: LocalVisionCapabilityReport,
        identity_required: bool,
        identity_verified: bool,
        brand_geometry_approved: bool,
        source_requirements: Sequence[ExactSlotConsensusRequirement] = (),
        entity_palettes: Mapping[str, EntityPaletteEvidence] | None = None,
        hero_palette: EntityPaletteEvidence | None = None,
        hero_is_unambiguous: bool | None = None,
        tone: HeadlineTone = HeadlineTone.NEUTRAL,
        competition: str | None = None,
        number: str | None = None,
        stakes: str = "normal",
        exact_assets: tuple[str, ...] = (),
        now: datetime | None = None,
        max_fact_age_minutes: int = 30,
    ) -> Phase18PipelineDecision:
        pre = self._integrity.evaluate(
            event=event,
            facts=facts,
            source_requirements=source_requirements,
            now=now,
            max_fact_age_minutes=max_fact_age_minutes,
        )
        if not pre.approved:
            return Phase18PipelineDecision(
                status="PREPRODUCTION_INTEGRITY_BLOCKED",
                preproduction=pre,
                planning=None,
                execution_plan=None,
                premortem=None,
                gpu_execution_allowed=False,
                publication_allowed_at_this_stage=False,
                blockers=pre.failures,
            )

        planning = self._planning.plan(
            sport=sport,
            candidates=candidates,
            tone=tone,
            competition=competition,
            number=number,
            stakes=stakes,
            exact_assets=exact_assets,
            hero_palette=hero_palette,
            hero_is_unambiguous=hero_is_unambiguous,
            verified_facts=facts,
            entity_palettes=entity_palettes,
        )
        if planning.status != "EDITORIAL_VISUAL_PLAN_READY":
            return Phase18PipelineDecision(
                status=planning.status,
                preproduction=pre,
                planning=planning,
                execution_plan=None,
                premortem=None,
                gpu_execution_allowed=False,
                publication_allowed_at_this_stage=False,
                blockers=(planning.status,),
            )

        dominant_palette_verified = bool(planning.brand and planning.brand.contextual)
        premortem = self._premortem.evaluate(
            planning=planning,
            verified_facts=facts,
            vision_capabilities=vision_capabilities,
            identity_required=identity_required,
            identity_verified=identity_verified,
            dominant_palette_verified=dominant_palette_verified,
            brand_geometry_approved=brand_geometry_approved,
            readable_text_required=True,
        )
        if not premortem.gpu_execution_allowed:
            return Phase18PipelineDecision(
                status="VISUAL_PREMORTEM_BLOCKED",
                preproduction=pre,
                planning=planning,
                execution_plan=None,
                premortem=premortem,
                gpu_execution_allowed=False,
                publication_allowed_at_this_stage=False,
                blockers=premortem.blockers,
            )

        execution = self._execution.compile(planning)
        return Phase18PipelineDecision(
            status="PHASE18_EXECUTION_READY" if premortem.publication_allowed else "PHASE18_ENGINEERING_PROOF_READY",
            preproduction=pre,
            planning=planning,
            execution_plan=execution,
            premortem=premortem,
            gpu_execution_allowed=True,
            publication_allowed_at_this_stage=premortem.publication_allowed,
            blockers=premortem.blockers,
        )

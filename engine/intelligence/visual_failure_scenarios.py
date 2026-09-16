"""PUL7SAR Phase 18 visual/editorial failure scenario engine.

The goal is to anticipate predictable production failures before GPU generation or
final export. Scenarios are deterministic, auditable, and fail closed. They do
not inspect pixels by themselves; they define what must be proven or avoided by
upstream/downstream components.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from engine.intelligence.story_visual_editorial import EditorialEvent, ProductionMode


class FailureSeverity(str, Enum):
    WARNING = "warning"
    HARD_BLOCK = "hard_block"


@dataclass(frozen=True)
class FailureScenario:
    scenario_id: str
    severity: FailureSeverity
    trigger: str
    risk: str
    prevention: str
    fallback: str


@dataclass(frozen=True)
class FailureScenarioReport:
    scenarios: tuple[FailureScenario, ...]

    @property
    def hard_blocked(self) -> bool:
        return any(item.severity is FailureSeverity.HARD_BLOCK for item in self.scenarios)


class VisualFailureScenarioEngine:
    """Build event-aware pre-mortem risks from planning facts and capabilities."""

    def evaluate(
        self,
        *,
        event: EditorialEvent,
        production_mode: ProductionMode,
        verified_facts: Mapping[str, object],
        has_verified_palette_for_dominant_entity: bool,
        identity_required: bool,
        identity_verified: bool,
        deterministic_geometry_required: bool,
        deterministic_geometry_ready: bool,
        readable_text_required: bool,
        brand_geometry_approved: bool,
        semantic_visual_inspection_ready: bool,
        subject_count: int = 1,
    ) -> FailureScenarioReport:
        out: list[FailureScenario] = []

        def add(sid: str, sev: FailureSeverity, trigger: str, risk: str, prevention: str, fallback: str) -> None:
            out.append(FailureScenario(sid, sev, trigger, risk, prevention, fallback))

        if deterministic_geometry_required and not deterministic_geometry_ready:
            add(
                "geometry_renderer_missing", FailureSeverity.HARD_BLOCK,
                "exact sport geometry is required but no deterministic renderer is ready",
                "the image model may invent incorrect field/court/rink proportions or markings",
                "never delegate exact geometry to diffusion",
                "remove the surface for a safe editorial composition or block production",
            )

        if identity_required and not identity_verified:
            add(
                "identity_unverified", FailureSeverity.HARD_BLOCK,
                "a real identifiable subject is required without verified identity evidence",
                "wrong athlete/coach likeness or fabricated person",
                "require verified identity asset/similarity evidence before composition",
                "switch to non-identifying editorial treatment or block",
            )

        if readable_text_required and production_mode is ProductionMode.GENERATIVE_SCENE:
            add(
                "generated_text_dependency", FailureSeverity.HARD_BLOCK,
                "the final message depends on exact readable text while generation owns the scene",
                "misspelled names, scores, numbers or pseudo-text",
                "move all exact text to deterministic typography",
                "generate an unbranded background and compose text later",
            )

        if not brand_geometry_approved:
            add(
                "brand_geometry_unapproved", FailureSeverity.HARD_BLOCK,
                "final PUL7SAR brand geometry has not been explicitly approved",
                "a technically valid image could ship with the wrong logo structure",
                "require an approved deterministic brand recipe",
                "keep publication_ready=false and omit final brand export",
            )

        if not semantic_visual_inspection_ready:
            add(
                "semantic_visual_inspection_missing", FailureSeverity.HARD_BLOCK,
                "runtime cannot prove semantic defects/forbidden visuals after generation",
                "fake text, malformed objects, collage leakage or unrelated content can pass unnoticed",
                "require a capable visual inspection stage before publication",
                "allow engineering proof only; publication remains blocked",
            )

        if subject_count > 2 and production_mode in {ProductionMode.HYBRID, ProductionMode.GENERATIVE_SCENE}:
            add(
                "excessive_subject_complexity", FailureSeverity.WARNING,
                f"scene requests {subject_count} important subjects",
                "identity swaps, weak hierarchy and clutter",
                "prefer one hero and at most one secondary subject",
                "select a simpler editorial angle or verified-asset composition",
            )

        if event is EditorialEvent.RESULT:
            status = str(verified_facts.get("result_status", "")).strip().casefold().replace("-", "_").replace(" ", "_")
            if status not in {"completed", "final", "full_time", "subject_win", "subject_won", "winner_subject", "opponent_win", "opponent_won", "winner_opponent", "draw", "tied", "level"}:
                add(
                    "winner_brand_before_final", FailureSeverity.HARD_BLOCK,
                    "result story is not in a recognized final state",
                    "winner color or final-result visual may be published while match is unresolved",
                    "only resolve a winner from final normalized status",
                    "use live/general red state with no winner branding",
                )

        if event is EditorialEvent.TRANSFER_CONFIRMED:
            status = str(verified_facts.get("confirmation_status", "")).strip().casefold().replace("-", "_").replace(" ", "_")
            if status not in {"confirmed", "official", "completed", "signed", "done"}:
                add(
                    "transfer_not_final", FailureSeverity.HARD_BLOCK,
                    "story type says confirmed transfer but confirmation_status is not final",
                    "destination club may be visually presented as if deal were completed",
                    "cross-check event taxonomy against normalized transfer status",
                    "downgrade to transfer-rumour/editorial mode",
                )

        dominant_events = {
            EditorialEvent.RESULT,
            EditorialEvent.TRANSFER_CONFIRMED,
            EditorialEvent.TROPHY,
            EditorialEvent.QUALIFICATION,
            EditorialEvent.ELIMINATION,
        }
        if event in dominant_events and not has_verified_palette_for_dominant_entity:
            add(
                "dominant_palette_missing", FailureSeverity.WARNING,
                "event may have an objective dominant entity but no verified palette is available",
                "wrong contextual 7/pulse color if guessed from memory/name",
                "never guess entity colors",
                "use default PUL7SAR red",
            )

        if production_mode is ProductionMode.GENERATIVE_SCENE and event in {
            EditorialEvent.TABLE, EditorialEvent.DRAW, EditorialEvent.SCHEDULE,
            EditorialEvent.TACTICS, EditorialEvent.FINANCIAL,
        }:
            add(
                "wrong_production_mode_for_exact_data", FailureSeverity.HARD_BLOCK,
                "data/diagram-heavy story routed to unconstrained generation",
                "fabricated standings, pairings, dates, formations or amounts",
                "route exact data stories to deterministic composition",
                "re-plan production mode before GPU execution",
            )

        return FailureScenarioReport(tuple(out))

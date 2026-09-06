"""Unified preproduction integrity gate for PUL7SAR Phase 18.

This gate runs before editorial angle selection / GPU work. It combines event
schema completeness, cross-field sports logic, story lifecycle freshness and
optional exact-slot source consensus. It is intentionally conservative: visual
production never repairs factual inconsistency.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from engine.intelligence.source_consensus import SourceConsensusGuard, SourceConsensusStatus, SourceFactObservation
from engine.intelligence.sports_fact_schema import EventFactSchemaRegistry
from engine.intelligence.sports_story_integrity import SportsStoryIntegrityGuard
from engine.intelligence.story_state_integrity import StoryRevisionAction, StoryStateIntegrityGuard
from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class ExactSlotConsensusRequirement:
    slot: str
    observations: tuple[SourceFactObservation, ...]
    minimum_independent_sources: int = 1


@dataclass(frozen=True)
class PreproductionIntegrityDecision:
    approved: bool
    action: str
    failures: tuple[str, ...]
    exact_values: Mapping[str, object]


class PreproductionIntegrityGate:
    def __init__(self) -> None:
        self._schemas = EventFactSchemaRegistry()
        self._story = SportsStoryIntegrityGuard()
        self._state = StoryStateIntegrityGuard()
        self._sources = SourceConsensusGuard()

    def evaluate(
        self,
        *,
        event: EditorialEvent,
        facts: Mapping[str, object],
        source_requirements: Sequence[ExactSlotConsensusRequirement] = (),
        now: datetime | None = None,
        max_fact_age_minutes: int = 30,
    ) -> PreproductionIntegrityDecision:
        failures: list[str] = []
        schema = self._schemas.validate(event, facts)
        failures.extend("missing_required:" + item for item in schema.missing_required)

        story = self._story.validate(event, facts)
        failures.extend("story_integrity:" + item for item in story.violations)

        state = self._state.validate(
            event=event,
            facts=facts,
            now=now,
            max_fact_age_minutes=max_fact_age_minutes,
        )
        failures.extend("story_state:" + item for item in state.failures)

        for requirement in source_requirements:
            consensus = self._sources.evaluate(
                requirement.observations,
                slot=requirement.slot,
                minimum_independent_sources=requirement.minimum_independent_sources,
            )
            if consensus.status is not SourceConsensusStatus.CONSISTENT:
                failures.extend(
                    f"source_consensus:{requirement.slot}:" + failure
                    for failure in consensus.failures
                )
            elif requirement.slot in schema.exact_render_values:
                expected = str(schema.exact_render_values[requirement.slot]).strip().casefold()
                accepted = str(consensus.accepted_value or "").strip().casefold()
                if expected != accepted:
                    failures.append(f"source_consensus:{requirement.slot}:accepted_value_mismatch")

        unique = tuple(dict.fromkeys(failures))
        if not unique:
            action = "PROCEED_TO_EDITORIAL_PLANNING"
        elif state.action is StoryRevisionAction.WITHDRAW:
            action = "WITHDRAW_STORY"
        elif state.action in {StoryRevisionAction.REFRESH, StoryRevisionAction.RECLASSIFY}:
            action = "REFRESH_OR_RECLASSIFY_STORY"
        else:
            action = "BLOCK_BEFORE_VISUAL_PLANNING"

        return PreproductionIntegrityDecision(
            approved=not unique,
            action=action,
            failures=unique,
            exact_values=schema.exact_render_values,
        )

"""Event-specific verified fact schemas for PUL7SAR Phase 18.

These schemas define what a story must know before copy/visual planning. They do
not extract facts. Upstream extraction and Fact Lock populate the slots; this
module validates completeness and identifies which values must be rendered by
exact deterministic layers rather than invented by image generation.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class EventFactSchema:
    event: EditorialEvent
    required_slots: tuple[str, ...]
    optional_slots: tuple[str, ...] = ()
    exact_render_slots: tuple[str, ...] = ()
    identity_slots: tuple[str, ...] = ()
    forbidden_implications: tuple[str, ...] = ()


@dataclass(frozen=True)
class FactSchemaValidation:
    event: EditorialEvent
    valid: bool
    missing_required: tuple[str, ...]
    supplied: Mapping[str, object]
    exact_render_values: Mapping[str, object]


_SCHEMAS = {
    EditorialEvent.RESULT: EventFactSchema(
        EditorialEvent.RESULT,
        ("subject", "opponent", "result_status"),
        ("score", "competition", "stage", "key_moment"),
        ("score",),
        ("subject", "opponent"),
        ("invented score", "invented scorer", "invented trophy"),
    ),
    EditorialEvent.LIVE_MOMENT: EventFactSchema(
        EditorialEvent.LIVE_MOMENT,
        ("subject", "moment"),
        ("opponent", "minute", "score_state", "competition"),
        ("minute", "score_state"),
        ("subject",),
        ("invented final result",),
    ),
    EditorialEvent.PREVIEW: EventFactSchema(
        EditorialEvent.PREVIEW,
        ("subject", "opponent", "event_status"),
        ("competition", "date", "venue"),
        ("date",),
        ("subject", "opponent"),
        ("invented result", "invented winner"),
    ),
    EditorialEvent.TRANSFER_CONFIRMED: EventFactSchema(
        EditorialEvent.TRANSFER_CONFIRMED,
        ("subject", "destination", "confirmation_status"),
        ("origin", "fee", "contract_length", "competition"),
        ("fee", "contract_length"),
        ("subject", "destination"),
        ("invented fee", "invented contract", "invented presentation"),
    ),
    EditorialEvent.TRANSFER_RUMOUR: EventFactSchema(
        EditorialEvent.TRANSFER_RUMOUR,
        ("subject", "interested_entity", "rumour_status"),
        ("source_strength", "asking_price", "current_team"),
        ("asking_price",),
        ("subject", "interested_entity"),
        ("completed signing", "official presentation", "contract signature"),
    ),
    EditorialEvent.CONTRACT: EventFactSchema(
        EditorialEvent.CONTRACT,
        ("subject", "contract_status"),
        ("team", "new_expiry", "salary"),
        ("new_expiry", "salary"),
        ("subject", "team"),
        ("invented salary", "invented expiry"),
    ),
    EditorialEvent.INJURY: EventFactSchema(
        EditorialEvent.INJURY,
        ("subject", "injury_status"),
        ("injury_type", "expected_absence", "match_context"),
        ("expected_absence",),
        ("subject",),
        ("graphic injury", "invented diagnosis", "invented return date"),
    ),
    EditorialEvent.COMEBACK: EventFactSchema(
        EditorialEvent.COMEBACK,
        ("subject", "return_status"),
        ("absence_duration", "return_event", "return_impact"),
        ("absence_duration",),
        ("subject",),
        ("invented performance",),
    ),
    EditorialEvent.SUSPENSION: EventFactSchema(
        EditorialEvent.SUSPENSION,
        ("subject", "disciplinary_status"),
        ("matches", "reason", "authority"),
        ("matches",),
        ("subject",),
        ("invented misconduct", "invented duration"),
    ),
    EditorialEvent.RETIREMENT: EventFactSchema(
        EditorialEvent.RETIREMENT,
        ("subject", "retirement_status"),
        ("age", "career_highlight", "effective_date"),
        ("age", "effective_date"),
        ("subject",),
    ),
    EditorialEvent.APPOINTMENT: EventFactSchema(
        EditorialEvent.APPOINTMENT,
        ("subject", "role", "entity", "appointment_status"),
        ("contract_length", "start_date"),
        ("contract_length", "start_date"),
        ("subject", "entity"),
    ),
    EditorialEvent.DISMISSAL: EventFactSchema(
        EditorialEvent.DISMISSAL,
        ("subject", "entity", "dismissal_status"),
        ("reason", "tenure", "replacement_status"),
        ("tenure",),
        ("subject", "entity"),
        ("invented replacement",),
    ),
    EditorialEvent.STATEMENT: EventFactSchema(
        EditorialEvent.STATEMENT,
        ("subject", "statement_core"),
        ("context", "target_entity"),
        (),
        ("subject",),
        ("invented quote",),
    ),
    EditorialEvent.RECORD: EventFactSchema(
        EditorialEvent.RECORD,
        ("subject", "record_metric", "record_value"),
        ("previous_record", "competition", "timeframe"),
        ("record_value", "previous_record"),
        ("subject",),
        ("invented metric", "invented value"),
    ),
    EditorialEvent.AWARD: EventFactSchema(
        EditorialEvent.AWARD,
        ("subject", "award", "award_status"),
        ("season", "ranking"),
        ("ranking",),
        ("subject",),
    ),
    EditorialEvent.TROPHY: EventFactSchema(
        EditorialEvent.TROPHY,
        ("subject", "competition", "title_status"),
        ("opponent", "score", "title_number"),
        ("score", "title_number"),
        ("subject",),
        ("invented trophy", "invented score"),
    ),
    EditorialEvent.DRAW: EventFactSchema(
        EditorialEvent.DRAW,
        ("competition", "draw_status", "pairings"),
        ("stage", "dates"),
        ("pairings", "dates"),
        (),
        ("invented pairing",),
    ),
    EditorialEvent.TABLE: EventFactSchema(
        EditorialEvent.TABLE,
        ("competition", "table_status", "positions"),
        ("points", "matches_played"),
        ("positions", "points", "matches_played"),
        (),
        ("invented standings",),
    ),
    EditorialEvent.TACTICS: EventFactSchema(
        EditorialEvent.TACTICS,
        ("subject", "tactical_claim"),
        ("formation", "roles", "phase"),
        ("formation", "roles"),
        ("subject",),
        ("invented formation", "invented player role"),
    ),
    EditorialEvent.OFFICIATING: EventFactSchema(
        EditorialEvent.OFFICIATING,
        ("incident", "decision_status"),
        ("official", "match", "rule_context"),
        (),
        ("official",),
        ("invented rule", "invented sanction"),
    ),
    EditorialEvent.CONTROVERSY: EventFactSchema(
        EditorialEvent.CONTROVERSY,
        ("subject", "verified_issue"),
        ("response", "authority", "timeline"),
        (),
        ("subject",),
        ("invented allegation", "sensationalized harm"),
    ),
    EditorialEvent.FINANCIAL: EventFactSchema(
        EditorialEvent.FINANCIAL,
        ("entity", "financial_fact"),
        ("amount", "period", "impact"),
        ("amount", "period"),
        ("entity",),
        ("invented amount",),
    ),
    EditorialEvent.ORGANIZATION: EventFactSchema(
        EditorialEvent.ORGANIZATION,
        ("entity", "decision"),
        ("effective_date", "affected_competition", "scope"),
        ("effective_date",),
        ("entity",),
    ),
    EditorialEvent.SCHEDULE: EventFactSchema(
        EditorialEvent.SCHEDULE,
        ("event", "schedule_status"),
        ("date", "time", "venue", "opponents"),
        ("date", "time", "opponents"),
        (),
        ("invented date", "invented fixture"),
    ),
    EditorialEvent.QUALIFICATION: EventFactSchema(
        EditorialEvent.QUALIFICATION,
        ("subject", "qualification_status"),
        ("competition", "stage", "deciding_result"),
        ("deciding_result",),
        ("subject",),
    ),
    EditorialEvent.ELIMINATION: EventFactSchema(
        EditorialEvent.ELIMINATION,
        ("subject", "elimination_status"),
        ("competition", "stage", "deciding_result"),
        ("deciding_result",),
        ("subject",),
    ),
    EditorialEvent.GENERAL: EventFactSchema(
        EditorialEvent.GENERAL,
        ("subject", "verified_fact"),
        ("context",),
        (),
        ("subject",),
    ),
}


class EventFactSchemaRegistry:
    def get(self, event: EditorialEvent) -> EventFactSchema:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        return _SCHEMAS[event]

    def validate(self, event: EditorialEvent, values: Mapping[str, object]) -> FactSchemaValidation:
        if not isinstance(values, Mapping):
            raise TypeError("values must be a mapping")
        schema = self.get(event)
        normalized = {str(k): v for k, v in dict(values).items() if v is not None and v != ""}
        missing = tuple(slot for slot in schema.required_slots if slot not in normalized)
        exact = {slot: normalized[slot] for slot in schema.exact_render_slots if slot in normalized}
        return FactSchemaValidation(
            event=event,
            valid=not missing,
            missing_required=missing,
            supplied=MappingProxyType(normalized),
            exact_render_values=MappingProxyType(exact),
        )

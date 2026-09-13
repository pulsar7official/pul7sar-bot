"""Connect Fact Lock evidence to Story-to-Visual fact slots.

Each slot used to formulate copy or visual decisions must be backed by a
`LockedClaim(kind=FACT)` whose metadata declares the same `slot`. Safe inference
and forbidden claims can never satisfy required editorial facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.models import ClaimKind, LockedClaim
from engine.intelligence.sports_fact_schema import EventFactSchemaRegistry, FactSchemaValidation
from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class FactLockedEditorialFacts:
    event: EditorialEvent
    values: Mapping[str, object]
    validation: FactSchemaValidation
    claim_by_slot: Mapping[str, LockedClaim]


class FactLockedEditorialAdapter:
    def __init__(self) -> None:
        self._schemas = EventFactSchemaRegistry()

    def build(
        self,
        *,
        event: EditorialEvent,
        values: Mapping[str, object],
        locked_claims: tuple[LockedClaim, ...],
    ) -> FactLockedEditorialFacts:
        validation = self._schemas.validate(event, values)
        if not validation.valid:
            raise ValueError("missing required editorial fact slots: " + ", ".join(validation.missing_required))

        by_slot: dict[str, LockedClaim] = {}
        for claim in locked_claims:
            if not isinstance(claim, LockedClaim):
                raise TypeError("locked_claims must contain LockedClaim values")
            slot = claim.metadata.get("slot")
            if not isinstance(slot, str) or not slot.strip():
                continue
            if claim.kind is ClaimKind.FACT:
                existing = by_slot.get(slot)
                if existing is None or claim.confidence > existing.confidence:
                    by_slot[slot] = claim

        supplied_slots = tuple(validation.supplied.keys())
        unsupported = tuple(slot for slot in supplied_slots if slot not in by_slot)
        if unsupported:
            raise ValueError("editorial slots are not backed by FACT claims: " + ", ".join(unsupported))

        # A FACT claim below the production confidence floor does not disappear;
        # the adapter rejects it so upstream can select another angle/fallback.
        weak = tuple(slot for slot, claim in by_slot.items() if slot in validation.supplied and claim.confidence < 0.80)
        if weak:
            raise ValueError("editorial FACT claim confidence below 0.80: " + ", ".join(weak))

        return FactLockedEditorialFacts(
            event=event,
            values=MappingProxyType(dict(validation.supplied)),
            validation=validation,
            claim_by_slot=MappingProxyType({slot: by_slot[slot] for slot in supplied_slots}),
        )

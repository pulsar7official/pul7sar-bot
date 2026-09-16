"""Source-consensus guard for fast-moving sports facts.

This layer does not decide truth from popularity. It detects when independently
normalized source claims disagree on an exact fact that the visual would expose
(score, winner, destination, fee, date, injury absence, etc.). Conflicts fail
closed and are returned upstream for refresh/reconciliation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class SourceConsensusStatus(str, Enum):
    CONSISTENT = "consistent"
    INSUFFICIENT = "insufficient"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class SourceFactObservation:
    source_id: str
    slot: str
    value: str
    confidence: float
    authoritative: bool = False

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.slot.strip() or not self.value.strip():
            raise ValueError("source_id, slot and value are required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class SourceConsensusDecision:
    status: SourceConsensusStatus
    slot: str
    accepted_value: str | None
    supporting_sources: tuple[str, ...]
    conflicting_values: tuple[tuple[str, tuple[str, ...]], ...]
    failures: tuple[str, ...]


class SourceConsensusGuard:
    """Detect exact-slot conflicts without inventing a reconciliation."""

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(value.strip().casefold().split())

    def evaluate(
        self,
        observations: Iterable[SourceFactObservation],
        *,
        slot: str,
        minimum_confidence: float = 0.80,
        minimum_independent_sources: int = 1,
    ) -> SourceConsensusDecision:
        if not slot.strip():
            raise ValueError("slot is required")
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if minimum_independent_sources < 1:
            raise ValueError("minimum_independent_sources must be positive")

        eligible = [
            item for item in observations
            if item.slot == slot and item.confidence >= minimum_confidence
        ]
        if not eligible:
            return SourceConsensusDecision(
                SourceConsensusStatus.INSUFFICIENT, slot, None, (), (), ("no_confident_source_observation",)
            )

        groups: dict[str, list[SourceFactObservation]] = {}
        display_value: dict[str, str] = {}
        for item in eligible:
            key = self._norm(item.value)
            groups.setdefault(key, []).append(item)
            display_value.setdefault(key, item.value.strip())

        authoritative_groups = {
            key for key, items in groups.items() if any(item.authoritative for item in items)
        }
        if len(authoritative_groups) > 1:
            conflicts = tuple(
                (display_value[key], tuple(sorted({item.source_id for item in groups[key]})))
                for key in sorted(authoritative_groups)
            )
            return SourceConsensusDecision(
                SourceConsensusStatus.CONFLICT, slot, None, (), conflicts,
                ("authoritative_sources_conflict",),
            )

        # A single authoritative value may resolve non-authoritative disagreement,
        # but the disagreement remains auditable in `conflicting_values`.
        if len(authoritative_groups) == 1:
            accepted_key = next(iter(authoritative_groups))
            supporting = tuple(sorted({item.source_id for item in groups[accepted_key]}))
            other = tuple(
                (display_value[key], tuple(sorted({item.source_id for item in groups[key]})))
                for key in sorted(groups) if key != accepted_key
            )
            return SourceConsensusDecision(
                SourceConsensusStatus.CONSISTENT,
                slot,
                display_value[accepted_key],
                supporting,
                other,
                (),
            )

        if len(groups) > 1:
            conflicts = tuple(
                (display_value[key], tuple(sorted({item.source_id for item in items})))
                for key, items in sorted(groups.items())
            )
            return SourceConsensusDecision(
                SourceConsensusStatus.CONFLICT, slot, None, (), conflicts,
                ("independent_sources_disagree",),
            )

        key, items = next(iter(groups.items()))
        sources = tuple(sorted({item.source_id for item in items}))
        if len(sources) < minimum_independent_sources:
            return SourceConsensusDecision(
                SourceConsensusStatus.INSUFFICIENT, slot, None, sources, (),
                ("insufficient_independent_source_count",),
            )
        return SourceConsensusDecision(
            SourceConsensusStatus.CONSISTENT, slot, display_value[key], sources, (), ()
        )

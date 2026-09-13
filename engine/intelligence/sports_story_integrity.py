"""Cross-field sports story integrity checks for PUL7SAR Phase 18.

Fact Lock proves that individual claims are supported. This guard handles a
different class of failure: individually plausible fields that contradict each
other when combined into one story/visual plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class StoryIntegrityDecision:
    valid: bool
    violations: tuple[str, ...]


class SportsStoryIntegrityGuard:
    FINAL_RESULT_STATES = {
        "completed", "final", "full_time", "subject_win", "subject_won",
        "winner_subject", "opponent_win", "opponent_won", "winner_opponent",
        "draw", "tied", "level",
    }
    DRAW_STATES = {"draw", "tied", "level"}
    FINAL_TRANSFER_STATES = {"confirmed", "official", "completed", "signed", "done"}

    @staticmethod
    def _text(value: object) -> str:
        return str(value).strip()

    @staticmethod
    def _status(value: object) -> str:
        return str(value).strip().casefold().replace("-", "_").replace(" ", "_")

    def validate(self, event: EditorialEvent, facts: Mapping[str, object]) -> StoryIntegrityDecision:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        if not isinstance(facts, Mapping):
            raise TypeError("facts must be a mapping")
        values = {str(k): v for k, v in dict(facts).items() if v is not None and v != ""}
        violations: list[str] = []

        if event in {EditorialEvent.RESULT, EditorialEvent.PREVIEW}:
            subject = self._text(values.get("subject", ""))
            opponent = self._text(values.get("opponent", ""))
            if subject and opponent and subject.casefold() == opponent.casefold():
                violations.append("subject_and_opponent_are_same_entity")

        if event is EditorialEvent.RESULT:
            subject = self._text(values.get("subject", ""))
            opponent = self._text(values.get("opponent", ""))
            winner = self._text(values.get("winner_entity", ""))
            status = self._status(values.get("result_status", ""))
            if winner and subject and opponent and winner.casefold() not in {subject.casefold(), opponent.casefold()}:
                violations.append("winner_is_not_a_match_participant")
            if status in self.DRAW_STATES and winner:
                violations.append("draw_cannot_have_winner_entity")
            if winner and status and status not in self.FINAL_RESULT_STATES:
                violations.append("winner_declared_before_final_result_state")
            if status in {"subject_win", "subject_won", "winner_subject"} and winner and subject and winner.casefold() != subject.casefold():
                violations.append("winner_conflicts_with_subject_win_status")
            if status in {"opponent_win", "opponent_won", "winner_opponent"} and winner and opponent and winner.casefold() != opponent.casefold():
                violations.append("winner_conflicts_with_opponent_win_status")

        if event is EditorialEvent.TRANSFER_CONFIRMED:
            origin = self._text(values.get("origin", ""))
            destination = self._text(values.get("destination", ""))
            status = self._status(values.get("confirmation_status", ""))
            if origin and destination and origin.casefold() == destination.casefold():
                violations.append("transfer_origin_equals_destination")
            if destination and status and status not in self.FINAL_TRANSFER_STATES:
                violations.append("confirmed_transfer_has_nonfinal_status")

        if event is EditorialEvent.TRANSFER_RUMOUR:
            status = self._status(values.get("rumour_status", ""))
            if status in self.FINAL_TRANSFER_STATES:
                violations.append("transfer_rumour_contains_final_transfer_status")

        if event is EditorialEvent.ELIMINATION:
            subject = self._text(values.get("subject", ""))
            eliminator = self._text(values.get("eliminating_entity", ""))
            if subject and eliminator and subject.casefold() == eliminator.casefold():
                violations.append("eliminated_entity_cannot_eliminate_itself")

        if event is EditorialEvent.QUALIFICATION:
            subject = self._text(values.get("subject", ""))
            qualified = self._text(values.get("qualified_entity", ""))
            if qualified and subject and qualified.casefold() != subject.casefold():
                violations.append("qualified_entity_conflicts_with_story_subject")

        if event is EditorialEvent.TROPHY:
            subject = self._text(values.get("subject", ""))
            champion = self._text(values.get("champion_entity", ""))
            if champion and subject and champion.casefold() != subject.casefold():
                violations.append("champion_entity_conflicts_with_story_subject")

        if event is EditorialEvent.SCHEDULE:
            opponents = values.get("opponents")
            if isinstance(opponents, (tuple, list)) and len(opponents) == 2:
                a, b = self._text(opponents[0]), self._text(opponents[1])
                if a and b and a.casefold() == b.casefold():
                    violations.append("scheduled_opponents_are_same_entity")

        return StoryIntegrityDecision(valid=not violations, violations=tuple(violations))

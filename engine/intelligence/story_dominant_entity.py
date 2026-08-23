"""Resolve the fact-driven dominant entity that may control PUL7SAR 7/pulse color.

This is not generic 'main subject' selection. It answers a stricter editorial
question: did the verified event establish one objectively dominant entity?
Examples: match winner, destination club in a completed transfer, champion,
qualifier, or the team that eliminated an opponent.

The resolver never parses prose to guess a winner. It consumes explicit fact
slots / normalized machine statuses. When dominance is not objective, it returns
None and Dynamic Brand falls back to PUL7SAR red.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional

from engine.intelligence.story_visual_editorial import EditorialEvent


class DominantEntityReason(str, Enum):
    RESULT_WINNER = "result_winner"
    TRANSFER_DESTINATION = "transfer_destination"
    TROPHY_CHAMPION = "trophy_champion"
    QUALIFIED_ENTITY = "qualified_entity"
    ELIMINATING_ENTITY = "eliminating_entity"
    AWARD_RECIPIENT = "award_recipient"
    RECORD_HOLDER = "record_holder"
    APPOINTING_ENTITY = "appointing_entity"
    CONTRACT_TEAM = "contract_team"


@dataclass(frozen=True)
class StoryDominantEntity:
    entity_name: str
    reason: DominantEntityReason
    confidence: float
    objective: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.entity_name, str) or not self.entity_name.strip():
            raise ValueError("entity_name is required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


class StoryDominantEntityResolver:
    """Choose contextual-brand owner only from explicit verified event semantics."""

    _SUBJECT_WIN = {"subject_win", "subject_won", "winner_subject"}
    _OPPONENT_WIN = {"opponent_win", "opponent_won", "winner_opponent"}
    _DRAW = {"draw", "tied", "level"}
    _TITLE_WON = {"champion", "title_won", "confirmed_champion"}
    _QUALIFIED = {"qualified", "qualification_confirmed", "advanced"}
    _APPOINTED = {"appointed", "appointment_confirmed"}
    _CONTRACT_CONFIRMED = {"renewed", "extended", "contract_confirmed"}

    @staticmethod
    def _text(value: object) -> str:
        return str(value).strip()

    @staticmethod
    def _status(value: object) -> str:
        return str(value).strip().casefold().replace("-", "_").replace(" ", "_")

    def resolve(
        self,
        *,
        event: EditorialEvent,
        facts: Mapping[str, object],
        confidence: float,
    ) -> Optional[StoryDominantEntity]:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        if not isinstance(facts, Mapping):
            raise TypeError("facts must be a mapping")
        if not 0.0 <= float(confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")

        values = {str(key): value for key, value in dict(facts).items() if value is not None and value != ""}

        if event is EditorialEvent.TRANSFER_CONFIRMED:
            destination = values.get("destination")
            if destination:
                return StoryDominantEntity(self._text(destination), DominantEntityReason.TRANSFER_DESTINATION, confidence)
            return None

        if event is EditorialEvent.RESULT:
            explicit = values.get("winner_entity")
            if explicit:
                return StoryDominantEntity(self._text(explicit), DominantEntityReason.RESULT_WINNER, confidence)
            status = self._status(values.get("result_status", ""))
            if status in self._DRAW:
                return None
            if status in self._SUBJECT_WIN and values.get("subject"):
                return StoryDominantEntity(self._text(values["subject"]), DominantEntityReason.RESULT_WINNER, confidence)
            if status in self._OPPONENT_WIN and values.get("opponent"):
                return StoryDominantEntity(self._text(values["opponent"]), DominantEntityReason.RESULT_WINNER, confidence)
            return None

        if event is EditorialEvent.TROPHY:
            explicit = values.get("champion_entity")
            if explicit:
                return StoryDominantEntity(self._text(explicit), DominantEntityReason.TROPHY_CHAMPION, confidence)
            if self._status(values.get("title_status", "")) in self._TITLE_WON and values.get("subject"):
                return StoryDominantEntity(self._text(values["subject"]), DominantEntityReason.TROPHY_CHAMPION, confidence)
            return None

        if event is EditorialEvent.QUALIFICATION:
            explicit = values.get("qualified_entity")
            if explicit:
                return StoryDominantEntity(self._text(explicit), DominantEntityReason.QUALIFIED_ENTITY, confidence)
            if self._status(values.get("qualification_status", "")) in self._QUALIFIED and values.get("subject"):
                return StoryDominantEntity(self._text(values["subject"]), DominantEntityReason.QUALIFIED_ENTITY, confidence)
            return None

        if event is EditorialEvent.ELIMINATION:
            explicit = values.get("eliminating_entity")
            if explicit:
                return StoryDominantEntity(self._text(explicit), DominantEntityReason.ELIMINATING_ENTITY, confidence)
            # `subject` is the eliminated side in this schema; never color the
            # brand from it unless the actual eliminating side is explicitly known.
            return None

        if event is EditorialEvent.AWARD and values.get("subject"):
            return StoryDominantEntity(self._text(values["subject"]), DominantEntityReason.AWARD_RECIPIENT, confidence)

        if event is EditorialEvent.RECORD and values.get("subject"):
            return StoryDominantEntity(self._text(values["subject"]), DominantEntityReason.RECORD_HOLDER, confidence)

        if event is EditorialEvent.APPOINTMENT:
            if self._status(values.get("appointment_status", "")) in self._APPOINTED and values.get("entity"):
                return StoryDominantEntity(self._text(values["entity"]), DominantEntityReason.APPOINTING_ENTITY, confidence)
            return None

        if event is EditorialEvent.CONTRACT:
            if self._status(values.get("contract_status", "")) in self._CONTRACT_CONFIRMED and values.get("team"):
                return StoryDominantEntity(self._text(values["team"]), DominantEntityReason.CONTRACT_TEAM, confidence)
            return None

        # Rumours, previews, draws, unresolved live states, controversy and
        # general stories do not objectively establish a brand-color winner.
        return None

"""Temporal/revision integrity for sports editorial and visual state.

Sports news changes quickly. A visual that was correct five minutes ago can become
false after full time, an official transfer announcement, postponement, VAR
correction, appeal, or source correction. This guard prevents stale state from
being treated as publication-ready merely because its facts were once verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping

from engine.intelligence.story_visual_editorial import EditorialEvent


class StoryRevisionAction(str, Enum):
    KEEP = "keep"
    REFRESH = "refresh"
    RECLASSIFY = "reclassify"
    WITHDRAW = "withdraw"
    BLOCK = "block"


@dataclass(frozen=True)
class StoryStateDecision:
    valid: bool
    action: StoryRevisionAction
    failures: tuple[str, ...]
    reason: str


class StoryStateIntegrityGuard:
    """Protect visual state against stale or contradictory event lifecycle data."""

    _FINAL_RESULT = {"completed", "final", "full_time", "finished"}
    _LIVE_RESULT = {"live", "in_progress", "half_time", "extra_time", "penalties"}
    _TRANSFER_FINAL = {"confirmed", "official", "completed", "signed", "done"}
    _TRANSFER_NONFINAL = {"rumour", "reported", "talks", "negotiating", "pending", "medical"}
    _SCHEDULE_VOID = {"cancelled", "canceled", "postponed", "abandoned"}

    @staticmethod
    def _norm(value: object) -> str:
        return str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")

    @staticmethod
    def _parse_time(value: object) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            dt = value
        else:
            text = str(value).strip().replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(text)
            except ValueError:
                return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def validate(
        self,
        *,
        event: EditorialEvent,
        facts: Mapping[str, object],
        now: datetime | None = None,
        max_fact_age_minutes: int = 30,
    ) -> StoryStateDecision:
        if max_fact_age_minutes < 1:
            raise ValueError("max_fact_age_minutes must be positive")
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        failures: list[str] = []

        verified_at = self._parse_time(facts.get("verified_at"))
        if verified_at is not None:
            age_minutes = (now - verified_at).total_seconds() / 60.0
            if age_minutes < -2:
                failures.append("fact_verification_time_is_in_future")
            elif age_minutes > max_fact_age_minutes:
                failures.append("fact_state_is_stale")

        correction = self._norm(facts.get("revision_status"))
        if correction in {"retracted", "withdrawn", "false", "invalidated"}:
            return StoryStateDecision(False, StoryRevisionAction.WITHDRAW, ("story_revision_withdrawn",), "source revision invalidated the prior story")
        if correction in {"corrected", "updated", "superseded"}:
            failures.append("newer_story_revision_exists")

        if event is EditorialEvent.RESULT:
            status = self._norm(facts.get("result_status"))
            if status in self._LIVE_RESULT and facts.get("winner_entity"):
                failures.append("winner_present_while_result_is_live")
            if status in self._FINAL_RESULT and not facts.get("score"):
                failures.append("final_result_missing_score")
            schedule = self._norm(facts.get("schedule_status"))
            if schedule in self._SCHEDULE_VOID:
                failures.append("result_attached_to_void_schedule_state")

        if event is EditorialEvent.TRANSFER_CONFIRMED:
            status = self._norm(facts.get("confirmation_status"))
            if status in self._TRANSFER_NONFINAL:
                failures.append("confirmed_transfer_event_has_nonfinal_state")
            if status not in self._TRANSFER_FINAL:
                failures.append("confirmed_transfer_state_unrecognized")

        if event is EditorialEvent.TRANSFER_RUMOUR:
            status = self._norm(facts.get("confirmation_status") or facts.get("rumour_status"))
            if status in self._TRANSFER_FINAL:
                return StoryStateDecision(False, StoryRevisionAction.RECLASSIFY, ("rumour_superseded_by_confirmed_transfer",), "the event should be reclassified as a confirmed transfer")

        if event in {EditorialEvent.PREVIEW, EditorialEvent.SCHEDULE}:
            status = self._norm(facts.get("schedule_status"))
            if status in self._SCHEDULE_VOID:
                return StoryStateDecision(False, StoryRevisionAction.RECLASSIFY, ("scheduled_event_no_longer_active",), "preview/schedule visual must be rebuilt around cancellation/postponement state")

        if failures:
            action = StoryRevisionAction.REFRESH if any(item in {"fact_state_is_stale", "newer_story_revision_exists"} for item in failures) else StoryRevisionAction.BLOCK
            return StoryStateDecision(False, action, tuple(dict.fromkeys(failures)), "story state requires refresh or correction before visual production")
        return StoryStateDecision(True, StoryRevisionAction.KEEP, (), "story lifecycle state is internally coherent")

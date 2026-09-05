"""Bridge explicit StoryBrief/story_type metadata into the richer EditorialEvent taxonomy.

This resolver is deterministic. It does not infer meaning from prose; upstream
analysis must supply an explicit event/story type. Unknown values fail closed to
GENERAL only when the caller explicitly permits fallback.
"""
from __future__ import annotations

from engine.intelligence.story_visual_editorial import EditorialEvent


class StoryEventResolver:
    _ALIASES = {
        "result": EditorialEvent.RESULT,
        "score": EditorialEvent.RESULT,
        "match_result": EditorialEvent.RESULT,
        "live_moment": EditorialEvent.LIVE_MOMENT,
        "late_goal": EditorialEvent.LIVE_MOMENT,
        "preview": EditorialEvent.PREVIEW,
        "match_preview": EditorialEvent.PREVIEW,
        "transfer": EditorialEvent.TRANSFER_RUMOUR,
        "transfer_rumour": EditorialEvent.TRANSFER_RUMOUR,
        "rumor": EditorialEvent.TRANSFER_RUMOUR,
        "rumour": EditorialEvent.TRANSFER_RUMOUR,
        "transfer_confirmed": EditorialEvent.TRANSFER_CONFIRMED,
        "signing": EditorialEvent.TRANSFER_CONFIRMED,
        "contract": EditorialEvent.CONTRACT,
        "renewal": EditorialEvent.CONTRACT,
        "injury": EditorialEvent.INJURY,
        "comeback": EditorialEvent.COMEBACK,
        "return": EditorialEvent.COMEBACK,
        "discipline": EditorialEvent.SUSPENSION,
        "suspension": EditorialEvent.SUSPENSION,
        "retirement": EditorialEvent.RETIREMENT,
        "appointment": EditorialEvent.APPOINTMENT,
        "manager_appointment": EditorialEvent.APPOINTMENT,
        "dismissal": EditorialEvent.DISMISSAL,
        "sacking": EditorialEvent.DISMISSAL,
        "statement": EditorialEvent.STATEMENT,
        "quote": EditorialEvent.STATEMENT,
        "record": EditorialEvent.RECORD,
        "milestone": EditorialEvent.RECORD,
        "award": EditorialEvent.AWARD,
        "trophy": EditorialEvent.TROPHY,
        "title": EditorialEvent.TROPHY,
        "draw": EditorialEvent.DRAW,
        "bracket": EditorialEvent.DRAW,
        "table": EditorialEvent.TABLE,
        "standings": EditorialEvent.TABLE,
        "tactics": EditorialEvent.TACTICS,
        "formation": EditorialEvent.TACTICS,
        "officiating": EditorialEvent.OFFICIATING,
        "referee": EditorialEvent.OFFICIATING,
        "controversy": EditorialEvent.CONTROVERSY,
        "financial": EditorialEvent.FINANCIAL,
        "finance": EditorialEvent.FINANCIAL,
        "organization": EditorialEvent.ORGANIZATION,
        "organisation": EditorialEvent.ORGANIZATION,
        "schedule": EditorialEvent.SCHEDULE,
        "fixture": EditorialEvent.SCHEDULE,
        "qualification": EditorialEvent.QUALIFICATION,
        "qualified": EditorialEvent.QUALIFICATION,
        "elimination": EditorialEvent.ELIMINATION,
        "eliminated": EditorialEvent.ELIMINATION,
        "player_story": EditorialEvent.GENERAL,
        "profile": EditorialEvent.GENERAL,
        "general": EditorialEvent.GENERAL,
    }

    def resolve(self, value: str | None, *, allow_general_fallback: bool = False) -> EditorialEvent:
        if value is None:
            if allow_general_fallback:
                return EditorialEvent.GENERAL
            raise ValueError("story event is required")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("story event must be a non-empty string")
        key = value.strip().casefold().replace("-", "_").replace(" ", "_")
        event = self._ALIASES.get(key)
        if event is not None:
            return event
        if allow_general_fallback:
            return EditorialEvent.GENERAL
        raise ValueError(f"unsupported story event: {value}")

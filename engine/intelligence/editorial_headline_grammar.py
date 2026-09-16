"""Visual-compatible headline grammar for PUL7SAR Phase 18.

The goal is not decorative copywriting. The headline must express the same
editorial angle that drives the visual plan, stay short enough for social media,
and avoid wording that forces the visual system to depict unverified or overly
complex claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.story_visual_editorial import EditorialEvent


class HeadlineTone(str, Enum):
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ANTICIPATORY = "anticipatory"
    URGENT = "urgent"


@dataclass(frozen=True)
class HeadlineInput:
    event: EditorialEvent
    subject: str
    fact_phrase: str
    tone: HeadlineTone = HeadlineTone.NEUTRAL
    secondary: str | None = None
    competition: str | None = None
    number: str | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.fact_phrase.strip():
            raise ValueError("subject and fact_phrase are required")


@dataclass(frozen=True)
class HeadlineDecision:
    headline: str
    editorial_angle: str
    visual_anchor: str
    complexity: str
    safe_for_visualization: bool


class EditorialHeadlineGrammar:
    """Create a concise Arabic headline from verified fact slots only."""

    _ANGLE = {
        EditorialEvent.RESULT: ("الحسم والنتيجة", "result"),
        EditorialEvent.LIVE_MOMENT: ("اللحظة الحاسمة", "decisive_moment"),
        EditorialEvent.PREVIEW: ("المواجهة المنتظرة", "duel"),
        EditorialEvent.TRANSFER_CONFIRMED: ("الوجهة الجديدة", "destination"),
        EditorialEvent.TRANSFER_RUMOUR: ("الاهتمام أو المفاوضات", "subject"),
        EditorialEvent.CONTRACT: ("الاستمرار أو التجديد", "subject"),
        EditorialEvent.INJURY: ("حالة اللاعب وتأثير الغياب", "subject"),
        EditorialEvent.COMEBACK: ("العودة", "subject"),
        EditorialEvent.SUSPENSION: ("الغياب والانضباط", "subject"),
        EditorialEvent.RETIREMENT: ("النهاية والمسيرة", "subject"),
        EditorialEvent.APPOINTMENT: ("البداية الجديدة", "subject"),
        EditorialEvent.DISMISSAL: ("نهاية المرحلة", "subject"),
        EditorialEvent.STATEMENT: ("جوهر التصريح", "subject"),
        EditorialEvent.RECORD: ("الإنجاز الرقمي", "number"),
        EditorialEvent.AWARD: ("التتويج الفردي", "subject"),
        EditorialEvent.TROPHY: ("التتويج", "trophy"),
        EditorialEvent.DRAW: ("المسار الذي صنعته القرعة", "bracket"),
        EditorialEvent.TABLE: ("الموقف في الجدول", "data"),
        EditorialEvent.TACTICS: ("الفكرة التكتيكية", "diagram"),
        EditorialEvent.OFFICIATING: ("القرار التحكيمي", "incident"),
        EditorialEvent.CONTROVERSY: ("جوهر الجدل", "subject"),
        EditorialEvent.FINANCIAL: ("الرقم وتأثيره", "data"),
        EditorialEvent.ORGANIZATION: ("القرار المؤسسي", "institution"),
        EditorialEvent.SCHEDULE: ("الموعد", "calendar"),
        EditorialEvent.QUALIFICATION: ("حسم التأهل", "achievement"),
        EditorialEvent.ELIMINATION: ("نهاية المشوار", "exit"),
        EditorialEvent.GENERAL: ("المعنى الأبرز للخبر", "atmosphere"),
    }

    def compose(self, data: HeadlineInput) -> HeadlineDecision:
        angle, anchor = self._ANGLE[data.event]
        subject = data.subject.strip()
        fact = data.fact_phrase.strip().rstrip(".،؛")

        if data.event is EditorialEvent.RESULT:
            headline = f"{subject}.. {fact}"
        elif data.event is EditorialEvent.TRANSFER_CONFIRMED:
            headline = f"وجهة جديدة.. {subject} {fact}"
        elif data.event is EditorialEvent.TRANSFER_RUMOUR:
            headline = f"{subject} في دائرة الاهتمام.. {fact}"
        elif data.event is EditorialEvent.COMEBACK:
            headline = f"عودة {subject}.. {fact}"
        elif data.event is EditorialEvent.DISMISSAL:
            headline = f"نهاية المرحلة.. {subject} {fact}"
        elif data.event is EditorialEvent.RECORD and data.number:
            headline = f"رقم جديد لـ{subject}.. {data.number} {fact}"
        elif data.event is EditorialEvent.QUALIFICATION:
            headline = f"{subject} يحسم التأهل.. {fact}"
        elif data.event is EditorialEvent.ELIMINATION:
            headline = f"نهاية المشوار.. {subject} {fact}"
        elif data.event is EditorialEvent.PREVIEW and data.secondary:
            headline = f"{subject} × {data.secondary}.. {fact}"
        else:
            headline = f"{subject}.. {fact}"

        # Preserve names and facts but cap visually hostile verbosity.
        headline = " ".join(headline.split())
        complexity = "low" if len(headline) <= 55 else "medium" if len(headline) <= 85 else "high"
        safe = complexity != "high"
        return HeadlineDecision(
            headline=headline,
            editorial_angle=angle,
            visual_anchor=anchor,
            complexity=complexity,
            safe_for_visualization=safe,
        )

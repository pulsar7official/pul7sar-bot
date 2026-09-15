"""Deterministic platform-aware layout planning for PUL7SAR visuals.

The planner allocates actual element boxes before image generation. Layouts are
normalized from each platform safe rectangle, so portrait, vertical and
landscape surfaces receive different art direction rather than resized copies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from engine.intelligence.layout_safety import ElementBox, LayoutRole, PlatformLayoutSafetyGate
from engine.intelligence.platform_profiles import PlatformImageProfile


class LayoutOrientation(str, Enum):
    PORTRAIT = "portrait"
    VERTICAL = "vertical"
    LANDSCAPE = "landscape"


@dataclass(frozen=True)
class LayoutRequirements:
    include_hero: bool = True
    include_logo: bool = True
    include_crest: bool = False
    include_score: bool = False
    include_headline: bool = True
    include_social_footer: bool = True


@dataclass(frozen=True)
class PlannedLayout:
    profile: PlatformImageProfile
    orientation: LayoutOrientation
    boxes: tuple[ElementBox, ...]
    accent_hex: str
    strategy: str = "pul7sar-deterministic-v1"

    def box_for(self, role: LayoutRole) -> Optional[ElementBox]:
        return next((box for box in self.boxes if box.role is role), None)


class DeterministicLayoutPlanner:
    """Plan safe, repeatable PUL7SAR geometry for a platform profile."""

    DEFAULT_ACCENT = "#E10600"

    def __init__(self, safety_gate: Optional[PlatformLayoutSafetyGate] = None):
        self.safety_gate = safety_gate or PlatformLayoutSafetyGate()

    def plan(
        self,
        profile: PlatformImageProfile,
        requirements: LayoutRequirements = LayoutRequirements(),
        *,
        entity_accent_hex: Optional[str] = None,
    ) -> PlannedLayout:
        accent = self._normalize_hex(entity_accent_hex or self.DEFAULT_ACCENT)
        left, top, right, bottom = self._safe_rect(profile)
        safe_w, safe_h = right - left, bottom - top
        orientation = self._orientation(profile)

        boxes: list[ElementBox] = []
        if orientation is LayoutOrientation.LANDSCAPE:
            hero = self._box(LayoutRole.HERO, left, top, safe_w * 0.52, safe_h * 0.74)
            headline = self._box(LayoutRole.HEADLINE, left + safe_w * 0.57, top + safe_h * 0.22, safe_w * 0.43, safe_h * 0.28)
        elif orientation is LayoutOrientation.VERTICAL:
            hero = self._box(LayoutRole.HERO, left + safe_w * 0.08, top + safe_h * 0.13, safe_w * 0.84, safe_h * 0.49)
            headline = self._box(LayoutRole.HEADLINE, left + safe_w * 0.08, top + safe_h * 0.66, safe_w * 0.84, safe_h * 0.14)
        else:
            hero = self._box(LayoutRole.HERO, left + safe_w * 0.04, top + safe_h * 0.13, safe_w * 0.58, safe_h * 0.60)
            headline = self._box(LayoutRole.HEADLINE, left + safe_w * 0.55, top + safe_h * 0.28, safe_w * 0.45, safe_h * 0.25)

        logo = self._box(LayoutRole.LOGO, left, top, safe_w * 0.25, safe_h * 0.07)
        crest = self._box(LayoutRole.CREST, right - safe_w * 0.12, top, safe_w * 0.12, safe_h * 0.09)
        score = self._box(LayoutRole.SCORE, left + safe_w * 0.34, top, safe_w * 0.32, safe_h * 0.09)
        footer = self._box(LayoutRole.SOCIAL_FOOTER, left + safe_w * 0.16, bottom - safe_h * 0.055, safe_w * 0.68, safe_h * 0.055)

        candidates = (
            (requirements.include_hero, hero),
            (requirements.include_logo, logo),
            (requirements.include_crest, crest),
            (requirements.include_score, score),
            (requirements.include_headline, headline),
            (requirements.include_social_footer, footer),
        )
        boxes.extend(box for enabled, box in candidates if enabled)
        result = PlannedLayout(profile, orientation, tuple(boxes), accent)
        self.safety_gate.assert_allowed(profile, result.boxes)
        return result

    @staticmethod
    def _safe_rect(profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            profile.safe_area.left,
            profile.safe_area.top,
            profile.width - profile.safe_area.right,
            profile.height - profile.safe_area.bottom,
        )

    @staticmethod
    def _orientation(profile: PlatformImageProfile) -> LayoutOrientation:
        ratio = profile.height / profile.width
        if ratio >= 1.6:
            return LayoutOrientation.VERTICAL
        if profile.width > profile.height:
            return LayoutOrientation.LANDSCAPE
        return LayoutOrientation.PORTRAIT

    @staticmethod
    def _box(role: LayoutRole, x: float, y: float, width: float, height: float) -> ElementBox:
        return ElementBox(role, round(x), round(y), max(1, round(width)), max(1, round(height)))

    @staticmethod
    def _normalize_hex(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("entity accent must be a hex string")
        value = value.strip().upper()
        if not value.startswith("#"):
            value = "#" + value
        if len(value) != 7 or any(ch not in "0123456789ABCDEF" for ch in value[1:]):
            raise ValueError("entity accent must be #RRGGBB")
        return value

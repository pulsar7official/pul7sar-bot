"""Content-aware deterministic layouts for generator-bypass PUL7SAR visuals."""
from __future__ import annotations

from engine.intelligence.layout_planner import LayoutOrientation, PlannedLayout
from engine.intelligence.layout_safety import ElementBox, LayoutRole, PlatformLayoutSafetyGate
from engine.intelligence.platform_profiles import PlatformImageProfile


class DirectDataLayoutPlanner:
    """Allocate editorial/data regions without inheriting subject-photo layouts."""

    def __init__(self, safety_gate: PlatformLayoutSafetyGate | None = None) -> None:
        self._safety = safety_gate or PlatformLayoutSafetyGate()

    def plan(self, profile: PlatformImageProfile, *, accent_hex: str = "#E10600") -> PlannedLayout:
        left = profile.safe_area.left
        top = profile.safe_area.top
        right = profile.width - profile.safe_area.right
        bottom = profile.height - profile.safe_area.bottom
        safe_w = right - left
        safe_h = bottom - top
        orientation = self._orientation(profile)

        if orientation is LayoutOrientation.LANDSCAPE:
            logo = ElementBox(LayoutRole.LOGO, left, top, round(safe_w * 0.22), round(safe_h * 0.11))
            headline = ElementBox(LayoutRole.HEADLINE, left, top + round(safe_h * 0.16), round(safe_w * 0.42), round(safe_h * 0.28))
            hero = ElementBox(LayoutRole.HERO, left + round(safe_w * 0.47), top + round(safe_h * 0.13), round(safe_w * 0.53), round(safe_h * 0.72))
        else:
            logo = ElementBox(LayoutRole.LOGO, left, top, round(safe_w * 0.28), round(safe_h * 0.075))
            headline = ElementBox(LayoutRole.HEADLINE, left, top + round(safe_h * 0.105), safe_w, round(safe_h * 0.19))
            hero = ElementBox(LayoutRole.HERO, left, top + round(safe_h * 0.34), safe_w, round(safe_h * 0.54))

        boxes = (logo, headline, hero)
        self._safety.assert_allowed(profile, boxes)
        return PlannedLayout(
            profile=profile,
            orientation=orientation,
            boxes=boxes,
            accent_hex=self._normalize_hex(accent_hex),
            strategy="pul7sar-direct-data-v1",
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
    def _normalize_hex(value: str) -> str:
        value = value.strip().upper()
        if not value.startswith("#"):
            value = "#" + value
        if len(value) != 7 or any(ch not in "0123456789ABCDEF" for ch in value[1:]):
            raise ValueError("accent must be #RRGGBB")
        return value

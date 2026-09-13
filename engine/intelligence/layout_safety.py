"""Safe-zone geometry for platform-specific PUL7SAR compositions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.platform_profiles import PlatformImageProfile


class LayoutRole(str, Enum):
    HERO = "hero"
    LOGO = "logo"
    CREST = "crest"
    SCORE = "score"
    HEADLINE = "headline"
    SOCIAL_FOOTER = "social_footer"
    SUPPORTING = "supporting"


@dataclass(frozen=True)
class ElementBox:
    role: LayoutRole
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if not isinstance(self.role, LayoutRole):
            raise TypeError("role must be LayoutRole")
        for name in ("x", "y", "width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be int")
        if self.x < 0 or self.y < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("element box must have non-negative origin and positive size")

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


@dataclass(frozen=True)
class LayoutSafetyDecision:
    allowed: bool
    violations: tuple[str, ...] = ()


class PlatformLayoutSafetyGate:
    """Validate critical editorial elements against canvas and safe area."""

    _CRITICAL = {
        LayoutRole.HERO,
        LayoutRole.LOGO,
        LayoutRole.CREST,
        LayoutRole.SCORE,
        LayoutRole.HEADLINE,
        LayoutRole.SOCIAL_FOOTER,
    }

    def evaluate(
        self,
        profile: PlatformImageProfile,
        boxes: tuple[ElementBox, ...],
    ) -> LayoutSafetyDecision:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        boxes = tuple(boxes)
        violations: list[str] = []

        safe_left = profile.safe_area.left
        safe_top = profile.safe_area.top
        safe_right = profile.width - profile.safe_area.right
        safe_bottom = profile.height - profile.safe_area.bottom

        for box in boxes:
            if not isinstance(box, ElementBox):
                raise TypeError("boxes must contain ElementBox values")
            if box.right > profile.width or box.bottom > profile.height:
                violations.append(f"{box.role.value} exceeds canvas")
                continue
            if box.role in self._CRITICAL:
                if (
                    box.x < safe_left
                    or box.y < safe_top
                    or box.right > safe_right
                    or box.bottom > safe_bottom
                ):
                    violations.append(f"{box.role.value} leaves safe area")

        return LayoutSafetyDecision(not violations, tuple(violations))

    def assert_allowed(self, profile: PlatformImageProfile, boxes: tuple[ElementBox, ...]) -> None:
        decision = self.evaluate(profile, boxes)
        if not decision.allowed:
            raise ValueError("unsafe platform layout: " + "; ".join(decision.violations))

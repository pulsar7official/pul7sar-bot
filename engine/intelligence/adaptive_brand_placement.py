"""Story- and platform-aware deterministic placement for the PUL7SAR signature.

The brand is a signature, not a fixed footer. This planner keeps the approved
reference geometry intact while adapting only scale and placement so it does not
compete with the story hero, score, tactical surface or platform safe areas.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class BrandZone(str, Enum):
    LOWER_CENTER = "lower_center"
    LOWER_LEFT = "lower_left"
    LOWER_RIGHT = "lower_right"
    UPPER_LEFT = "upper_left"
    UPPER_RIGHT = "upper_right"


@dataclass(frozen=True)
class AdaptiveBrandPlacement:
    zone: BrandZone
    center_x_ratio: float
    center_y_ratio: float
    max_width_ratio: float
    max_height_ratio: float
    minimum_clearance_ratio: float
    reason: str
    contract: str = "pul7sar-adaptive-brand-placement-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.zone, BrandZone):
            raise TypeError("zone must be BrandZone")
        for name in ("center_x_ratio", "center_y_ratio", "max_width_ratio", "max_height_ratio", "minimum_clearance_ratio"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 < float(value) <= 1.0:
                raise ValueError(f"{name} must be within (0, 1]")
        if self.max_width_ratio > 0.42:
            raise ValueError("brand signature may not dominate more than 42% of canvas width")
        if self.max_height_ratio > 0.18:
            raise ValueError("brand signature may not dominate more than 18% of canvas height")
        if not self.reason.strip():
            raise ValueError("placement reason is required")


class AdaptiveBrandPlacementResolver:
    """Resolve signature scale/zone without changing approved brand geometry."""

    _FAMILY_WIDTH = {
        EditorialSceneFamily.TRANSFER_SIGNATURE: 0.30,
        EditorialSceneFamily.RESULT_STATEMENT: 0.25,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: 0.24,
        EditorialSceneFamily.TACTICAL_BOARD: 0.21,
        EditorialSceneFamily.DATA_MONUMENT: 0.22,
        EditorialSceneFamily.EVENT_EDITORIAL: 0.25,
    }

    _FAMILY_HEIGHT = {
        EditorialSceneFamily.TRANSFER_SIGNATURE: 0.105,
        EditorialSceneFamily.RESULT_STATEMENT: 0.090,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: 0.085,
        EditorialSceneFamily.TACTICAL_BOARD: 0.075,
        EditorialSceneFamily.DATA_MONUMENT: 0.080,
        EditorialSceneFamily.EVENT_EDITORIAL: 0.085,
    }

    def resolve(
        self,
        *,
        family: EditorialSceneFamily,
        profile: PlatformImageProfile,
        occupied_zones: tuple[BrandZone, ...] = (),
    ) -> AdaptiveBrandPlacement:
        if not isinstance(family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        occupied = set(occupied_zones)
        if any(not isinstance(zone, BrandZone) for zone in occupied):
            raise TypeError("occupied_zones must contain BrandZone values")

        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()
        if not brand.placement_adaptive:
            raise ValueError("PUL7SAR_BRAND_PLACEMENT_MUST_REMAIN_ADAPTIVE")

        preferred = self._preferred_zones(family)
        zone = next((candidate for candidate in preferred if candidate not in occupied), None)
        if zone is None:
            raise ValueError("NO_CLEAR_BRAND_ZONE_AVAILABLE")

        cx, cy = self._center(zone, profile)
        return AdaptiveBrandPlacement(
            zone=zone,
            center_x_ratio=cx,
            center_y_ratio=cy,
            max_width_ratio=self._FAMILY_WIDTH[family],
            max_height_ratio=self._FAMILY_HEIGHT[family],
            minimum_clearance_ratio=0.035,
            reason=self._reason(family, zone),
        )

    @staticmethod
    def _preferred_zones(family: EditorialSceneFamily) -> tuple[BrandZone, ...]:
        if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            return (BrandZone.LOWER_CENTER, BrandZone.LOWER_RIGHT, BrandZone.UPPER_RIGHT)
        if family is EditorialSceneFamily.RESULT_STATEMENT:
            return (BrandZone.LOWER_CENTER, BrandZone.UPPER_RIGHT, BrandZone.UPPER_LEFT)
        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            return (BrandZone.LOWER_RIGHT, BrandZone.LOWER_CENTER, BrandZone.UPPER_RIGHT)
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            return (BrandZone.LOWER_LEFT, BrandZone.UPPER_RIGHT, BrandZone.LOWER_RIGHT)
        if family is EditorialSceneFamily.DATA_MONUMENT:
            return (BrandZone.LOWER_RIGHT, BrandZone.LOWER_LEFT, BrandZone.UPPER_RIGHT)
        return (BrandZone.LOWER_CENTER, BrandZone.LOWER_RIGHT, BrandZone.UPPER_RIGHT)

    @staticmethod
    def _center(zone: BrandZone, profile: PlatformImageProfile) -> tuple[float, float]:
        left = profile.safe_area.left / profile.width
        right = 1.0 - profile.safe_area.right / profile.width
        top = profile.safe_area.top / profile.height
        bottom = 1.0 - profile.safe_area.bottom / profile.height
        horizontal = {
            BrandZone.LOWER_LEFT: left + (right - left) * 0.19,
            BrandZone.UPPER_LEFT: left + (right - left) * 0.19,
            BrandZone.LOWER_CENTER: (left + right) / 2,
            BrandZone.LOWER_RIGHT: right - (right - left) * 0.19,
            BrandZone.UPPER_RIGHT: right - (right - left) * 0.19,
        }[zone]
        vertical = {
            BrandZone.LOWER_LEFT: bottom - (bottom - top) * 0.075,
            BrandZone.LOWER_CENTER: bottom - (bottom - top) * 0.075,
            BrandZone.LOWER_RIGHT: bottom - (bottom - top) * 0.075,
            BrandZone.UPPER_LEFT: top + (bottom - top) * 0.08,
            BrandZone.UPPER_RIGHT: top + (bottom - top) * 0.08,
        }[zone]
        return round(horizontal, 6), round(vertical, 6)

    @staticmethod
    def _reason(family: EditorialSceneFamily, zone: BrandZone) -> str:
        return {
            EditorialSceneFamily.TRANSFER_SIGNATURE: "keep signature subordinate to verified hero and headline",
            EditorialSceneFamily.RESULT_STATEMENT: "keep signature outside deterministic score and balanced club identities",
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: "keep signature quiet beside verified portrait-led reporting",
            EditorialSceneFamily.TACTICAL_BOARD: "protect deterministic tactical geometry as the primary information surface",
            EditorialSceneFamily.DATA_MONUMENT: "protect exact data hierarchy from brand competition",
            EditorialSceneFamily.EVENT_EDITORIAL: "preserve a single editorial focal hierarchy",
        }[family] + f"; resolved={zone.value}"

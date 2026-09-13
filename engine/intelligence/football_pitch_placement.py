"""Camera-aware deterministic football pitch placement for hybrid visuals.

The pitch is a world-space object rendered by code. This planner defines safe
image-space quadrilaterals for known editorial camera families and validates
custom quadrilaterals before the geometry renderer is allowed to draw.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

Point = tuple[float, float]


class FootballCameraPreset(str, Enum):
    HIGH_WIDE_CENTRAL = "high_wide_central"
    ELEVATED_ENDLINE = "elevated_endline"
    SIDELINE_OBLIQUE = "sideline_oblique"


@dataclass(frozen=True)
class FootballPitchPlacement:
    normalized_corners: tuple[Point, Point, Point, Point]
    preset: FootballCameraPreset
    surface_coverage: float

    def __post_init__(self) -> None:
        if len(self.normalized_corners) != 4:
            raise ValueError("exactly four corners are required")
        for x, y in self.normalized_corners:
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError("normalized corners must be inside 0..1 canvas")
        if not 0.0 < self.surface_coverage < 1.0:
            raise ValueError("surface_coverage must be between 0 and 1")
        _assert_convex(self.normalized_corners)

    def pixels(self, canvas_size: tuple[int, int]) -> tuple[Point, Point, Point, Point]:
        width, height = canvas_size
        if width <= 0 or height <= 0:
            raise ValueError("canvas dimensions must be positive")
        return tuple((x * width, y * height) for x, y in self.normalized_corners)  # type: ignore[return-value]


def _cross(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


def _assert_convex(points: tuple[Point, Point, Point, Point]) -> None:
    signs = []
    for i in range(4):
        value = _cross(points[i], points[(i + 1) % 4], points[(i + 2) % 4])
        if abs(value) < 1e-7:
            raise ValueError("pitch placement contains collinear corners")
        signs.append(value > 0)
    if not all(sign == signs[0] for sign in signs):
        raise ValueError("pitch placement must be a convex quadrilateral")


class FootballPitchPlacementPlanner:
    """Return conservative perspective presets with editorial negative space."""

    _PRESETS = {
        # Source order: near-left, far-left, far-right, near-right in image space
        # mapped consistently to the geometry projector source corners.
        FootballCameraPreset.HIGH_WIDE_CENTRAL: FootballPitchPlacement(
            normalized_corners=((0.08, 0.82), (0.28, 0.39), (0.72, 0.39), (0.92, 0.82)),
            preset=FootballCameraPreset.HIGH_WIDE_CENTRAL,
            surface_coverage=0.43,
        ),
        FootballCameraPreset.ELEVATED_ENDLINE: FootballPitchPlacement(
            normalized_corners=((0.14, 0.88), (0.37, 0.42), (0.63, 0.42), (0.86, 0.88)),
            preset=FootballCameraPreset.ELEVATED_ENDLINE,
            surface_coverage=0.40,
        ),
        FootballCameraPreset.SIDELINE_OBLIQUE: FootballPitchPlacement(
            normalized_corners=((0.03, 0.80), (0.20, 0.45), (0.78, 0.37), (0.96, 0.70)),
            preset=FootballCameraPreset.SIDELINE_OBLIQUE,
            surface_coverage=0.39,
        ),
    }

    def plan(self, preset: FootballCameraPreset = FootballCameraPreset.HIGH_WIDE_CENTRAL) -> FootballPitchPlacement:
        return self._PRESETS[preset]

    def validate_custom(self, corners: tuple[Point, Point, Point, Point], *, preset: FootballCameraPreset = FootballCameraPreset.HIGH_WIDE_CENTRAL) -> FootballPitchPlacement:
        # Coverage is approximate polygon area in normalized canvas space.
        area = 0.0
        for i, (x1, y1) in enumerate(corners):
            x2, y2 = corners[(i + 1) % 4]
            area += x1 * y2 - x2 * y1
        area = abs(area) / 2.0
        if area < 0.12 or area > 0.72:
            raise ValueError("custom pitch placement has implausible canvas coverage")
        return FootballPitchPlacement(corners, preset, area)

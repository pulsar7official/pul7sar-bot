"""Regulation association-football pitch geometry primitives.

This module owns exact world-space geometry for deterministic rendering. It does
not rely on a diffusion model to invent field proportions or markings.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import acos, degrees, isclose


@dataclass(frozen=True)
class LineSegment:
    x1: float
    y1: float
    x2: float
    y2: float
    role: str


@dataclass(frozen=True)
class CircleMark:
    cx: float
    cy: float
    radius: float
    role: str


@dataclass(frozen=True)
class ArcMark:
    cx: float
    cy: float
    radius: float
    start_degrees: float
    end_degrees: float
    role: str


@dataclass(frozen=True)
class PointMark:
    x: float
    y: float
    role: str


@dataclass(frozen=True)
class RectMark:
    x: float
    y: float
    width: float
    height: float
    role: str


@dataclass(frozen=True)
class FootballPitchGeometry:
    """Standard 105m x 68m elite-football reference pitch.

    The Laws of the Game allow dimension ranges. PUL7SAR deliberately uses one
    stable reference geometry for deterministic editorial rendering so generated
    images cannot invent proportions from one story to another.
    """

    length_m: float = 105.0
    width_m: float = 68.0
    centre_circle_radius_m: float = 9.15
    penalty_area_depth_m: float = 16.5
    penalty_area_width_m: float = 40.32
    goal_area_depth_m: float = 5.5
    goal_area_width_m: float = 18.32
    penalty_mark_distance_m: float = 11.0
    penalty_arc_radius_m: float = 9.15
    corner_arc_radius_m: float = 1.0
    goal_width_m: float = 7.32

    def __post_init__(self) -> None:
        if self.length_m <= 0 or self.width_m <= 0:
            raise ValueError("pitch dimensions must be positive")
        if self.length_m <= self.width_m:
            raise ValueError("football pitch length must exceed width")
        if self.penalty_area_width_m >= self.width_m or self.goal_area_width_m >= self.width_m:
            raise ValueError("area widths must fit inside pitch width")
        if self.goal_area_depth_m >= self.penalty_area_depth_m:
            raise ValueError("goal area depth must be smaller than penalty area depth")
        if self.penalty_mark_distance_m >= self.penalty_area_depth_m:
            raise ValueError("penalty mark must lie inside penalty area depth")
        if self.penalty_arc_radius_m <= self.penalty_area_depth_m - self.penalty_mark_distance_m:
            raise ValueError("penalty arc radius must cross the penalty-area boundary")

    @property
    def aspect_ratio(self) -> float:
        return self.length_m / self.width_m

    @property
    def centre(self) -> tuple[float, float]:
        return self.length_m / 2.0, self.width_m / 2.0

    def lines(self) -> tuple[LineSegment, ...]:
        L, W = self.length_m, self.width_m
        cx = L / 2.0
        return (
            LineSegment(0, 0, L, 0, "touchline_top"),
            LineSegment(0, W, L, W, "touchline_bottom"),
            LineSegment(0, 0, 0, W, "goal_line_left"),
            LineSegment(L, 0, L, W, "goal_line_right"),
            LineSegment(cx, 0, cx, W, "halfway_line"),
        )

    def rectangles(self) -> tuple[RectMark, ...]:
        W = self.width_m
        pa_y = (W - self.penalty_area_width_m) / 2.0
        ga_y = (W - self.goal_area_width_m) / 2.0
        return (
            RectMark(0, pa_y, self.penalty_area_depth_m, self.penalty_area_width_m, "penalty_area_left"),
            RectMark(self.length_m - self.penalty_area_depth_m, pa_y, self.penalty_area_depth_m, self.penalty_area_width_m, "penalty_area_right"),
            RectMark(0, ga_y, self.goal_area_depth_m, self.goal_area_width_m, "goal_area_left"),
            RectMark(self.length_m - self.goal_area_depth_m, ga_y, self.goal_area_depth_m, self.goal_area_width_m, "goal_area_right"),
        )

    def circles(self) -> tuple[CircleMark, ...]:
        cx, cy = self.centre
        return (CircleMark(cx, cy, self.centre_circle_radius_m, "centre_circle"),)

    def points(self) -> tuple[PointMark, ...]:
        cx, cy = self.centre
        left, right = self.penalty_marks()
        return (
            PointMark(cx, cy, "centre_mark"),
            PointMark(left[0], left[1], "penalty_mark_left"),
            PointMark(right[0], right[1], "penalty_mark_right"),
        )

    def penalty_marks(self) -> tuple[tuple[float, float], tuple[float, float]]:
        cy = self.width_m / 2.0
        return (
            (self.penalty_mark_distance_m, cy),
            (self.length_m - self.penalty_mark_distance_m, cy),
        )

    def arcs(self) -> tuple[ArcMark, ...]:
        """Return penalty and corner arcs as regulation world-space primitives."""
        L, W = self.length_m, self.width_m
        cy = W / 2.0
        left_x = self.penalty_mark_distance_m
        right_x = L - self.penalty_mark_distance_m

        # Penalty arc is the portion of a 9.15m circle outside the penalty area.
        offset = self.penalty_area_depth_m - self.penalty_mark_distance_m
        theta = degrees(acos(offset / self.penalty_arc_radius_m))
        return (
            ArcMark(left_x, cy, self.penalty_arc_radius_m, -theta, theta, "penalty_arc_left"),
            ArcMark(right_x, cy, self.penalty_arc_radius_m, 180.0 - theta, 180.0 + theta, "penalty_arc_right"),
            ArcMark(0.0, 0.0, self.corner_arc_radius_m, 0.0, 90.0, "corner_arc_top_left"),
            ArcMark(L, 0.0, self.corner_arc_radius_m, 90.0, 180.0, "corner_arc_top_right"),
            ArcMark(L, W, self.corner_arc_radius_m, 180.0, 270.0, "corner_arc_bottom_right"),
            ArcMark(0.0, W, self.corner_arc_radius_m, 270.0, 360.0, "corner_arc_bottom_left"),
        )

    def normalized_point(self, x: float, y: float) -> tuple[float, float]:
        if not 0.0 <= x <= self.length_m or not 0.0 <= y <= self.width_m:
            raise ValueError("point lies outside pitch")
        return x / self.length_m, y / self.width_m

    def integrity_receipt(self) -> dict[str, object]:
        lines = self.lines()
        rects = self.rectangles()
        circles = self.circles()
        points = self.points()
        arcs = self.arcs()
        halfway = [item for item in lines if item.role == "halfway_line"]
        centre = [item for item in circles if item.role == "centre_circle"]
        centre_marks = [item for item in points if item.role == "centre_mark"]
        left_pa = next(item for item in rects if item.role == "penalty_area_left")
        right_pa = next(item for item in rects if item.role == "penalty_area_right")
        symmetric_penalty_areas = (
            isclose(left_pa.width, right_pa.width)
            and isclose(left_pa.height, right_pa.height)
            and isclose(left_pa.y, right_pa.y)
        )
        return {
            "status": "REGULATION_FOOTBALL_GEOMETRY_READY",
            "length_m": self.length_m,
            "width_m": self.width_m,
            "aspect_ratio": round(self.aspect_ratio, 6),
            "halfway_line_count": len(halfway),
            "centre_circle_count": len(centre),
            "centre_mark_count": len(centre_marks),
            "penalty_mark_count": len([item for item in points if item.role.startswith("penalty_mark_")]),
            "penalty_arc_count": len([item for item in arcs if item.role.startswith("penalty_arc_")]),
            "corner_arc_count": len([item for item in arcs if item.role.startswith("corner_arc_")]),
            "penalty_area_count": len([item for item in rects if item.role.startswith("penalty_area_")]),
            "goal_area_count": len([item for item in rects if item.role.startswith("goal_area_")]),
            "symmetric_penalty_areas": symmetric_penalty_areas,
        }

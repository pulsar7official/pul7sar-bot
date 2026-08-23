"""Project regulation football pitch world coordinates into an image quadrilateral.

A four-corner projective transform lets PUL7SAR draw pitch markings with code
instead of asking diffusion to invent perspective geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.intelligence.football_pitch_geometry import FootballPitchGeometry


Point = tuple[float, float]


@dataclass(frozen=True)
class ProjectedPolyline:
    role: str
    points: tuple[Point, ...]
    closed: bool = False


def _solve_linear_system(matrix: list[list[float]], values: list[float]) -> list[float]:
    n = len(values)
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("linear system must be square")
    aug = [list(map(float, row)) + [float(values[i])] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("degenerate projection quadrilateral")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_value = aug[col][col]
        aug[col] = [value / pivot_value for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == 0:
                continue
            aug[row] = [aug[row][i] - factor * aug[col][i] for i in range(n + 1)]
    return [aug[i][-1] for i in range(n)]


@dataclass(frozen=True)
class PerspectiveProjector:
    h: tuple[float, float, float, float, float, float, float, float]

    @classmethod
    def from_quadrilateral(cls, *, source: tuple[Point, Point, Point, Point], destination: tuple[Point, Point, Point, Point]) -> "PerspectiveProjector":
        rows: list[list[float]] = []
        values: list[float] = []
        for (x, y), (u, v) in zip(source, destination):
            rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
            values.append(u)
            rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
            values.append(v)
        solution = _solve_linear_system(rows, values)
        return cls(tuple(solution))

    def project(self, point: Point) -> Point:
        x, y = point
        h11, h12, h13, h21, h22, h23, h31, h32 = self.h
        denominator = h31 * x + h32 * y + 1.0
        if abs(denominator) < 1e-12:
            raise ValueError("point projects to infinity")
        return (
            (h11 * x + h12 * y + h13) / denominator,
            (h21 * x + h22 * y + h23) / denominator,
        )


class FootballPitchProjectionPlanner:
    def __init__(self, geometry: FootballPitchGeometry | None = None) -> None:
        self.geometry = geometry or FootballPitchGeometry()

    def projector(self, destination_corners: tuple[Point, Point, Point, Point]) -> PerspectiveProjector:
        L, W = self.geometry.length_m, self.geometry.width_m
        source = ((0.0, 0.0), (L, 0.0), (L, W), (0.0, W))
        return PerspectiveProjector.from_quadrilateral(source=source, destination=destination_corners)

    @staticmethod
    def _rect_points(x: float, y: float, width: float, height: float) -> tuple[Point, ...]:
        return ((x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y))

    def project_markings(self, destination_corners: tuple[Point, Point, Point, Point], *, circle_samples: int = 72) -> tuple[ProjectedPolyline, ...]:
        if circle_samples < 24:
            raise ValueError("circle_samples must be >= 24")
        import math

        p = self.projector(destination_corners)
        output: list[ProjectedPolyline] = []
        for line in self.geometry.lines():
            output.append(ProjectedPolyline(line.role, (p.project((line.x1, line.y1)), p.project((line.x2, line.y2)))))
        for rect in self.geometry.rectangles():
            points = tuple(p.project(point) for point in self._rect_points(rect.x, rect.y, rect.width, rect.height))
            output.append(ProjectedPolyline(rect.role, points, closed=True))
        for circle in self.geometry.circles():
            world = tuple(
                (
                    circle.cx + circle.radius * math.cos(2 * math.pi * i / circle_samples),
                    circle.cy + circle.radius * math.sin(2 * math.pi * i / circle_samples),
                )
                for i in range(circle_samples)
            )
            points = tuple(p.project(point) for point in world) + (p.project(world[0]),)
            output.append(ProjectedPolyline(circle.role, points, closed=True))
        return tuple(output)

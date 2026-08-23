"""Pillow renderer for deterministic regulation football-pitch overlays.

The renderer consumes projective world geometry; it never asks a generative
model to draw lines, circles, penalty/corner arcs or exact pitch proportions.
It may also paint subtle deterministic mowing bands so replacing a malformed
generated pitch still produces a credible editorial surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.intelligence.football_pitch_projection import FootballPitchProjectionPlanner, Point


@dataclass(frozen=True)
class FootballPitchRenderStyle:
    line_rgba: tuple[int, int, int, int] = (245, 245, 245, 235)
    surface_rgba: tuple[int, int, int, int] = (25, 92, 45, 255)
    alternate_surface_rgba: tuple[int, int, int, int] = (29, 102, 49, 255)
    line_width_px: int = 5
    mark_radius_px: int = 4
    fill_surface: bool = True
    mowing_stripes: bool = True
    stripe_count: int = 10

    def __post_init__(self) -> None:
        if self.line_width_px <= 0 or self.mark_radius_px <= 0:
            raise ValueError("line_width_px and mark_radius_px must be positive")
        if self.stripe_count < 2:
            raise ValueError("stripe_count must be >= 2")
        for name in ("line_rgba", "surface_rgba", "alternate_surface_rgba"):
            value = getattr(self, name)
            if len(value) != 4 or any(not isinstance(ch, int) or not 0 <= ch <= 255 for ch in value):
                raise ValueError(f"{name} must be four 0..255 integers")


class PillowFootballPitchRenderer:
    def __init__(self, planner: FootballPitchProjectionPlanner | None = None) -> None:
        self._planner = planner or FootballPitchProjectionPlanner()

    def _paint_surface(self, draw, *, destination_corners, style: FootballPitchRenderStyle) -> None:
        if not style.fill_surface:
            return
        draw.polygon(destination_corners, fill=style.surface_rgba)
        if not style.mowing_stripes:
            return

        geometry = self._planner.geometry
        projector = self._planner.projector(destination_corners)
        strip = geometry.length_m / style.stripe_count
        for index in range(style.stripe_count):
            if index % 2 == 0:
                continue
            x1 = index * strip
            x2 = (index + 1) * strip
            world = ((x1, 0.0), (x2, 0.0), (x2, geometry.width_m), (x1, geometry.width_m))
            polygon = tuple(projector.project(point) for point in world)
            draw.polygon(polygon, fill=style.alternate_surface_rgba)

    def render_overlay(
        self,
        *,
        canvas_size: tuple[int, int],
        destination_corners: tuple[Point, Point, Point, Point],
        style: FootballPitchRenderStyle | None = None,
        output_path: str | None = None,
    ):
        try:
            from PIL import Image, ImageDraw
        except ImportError as exc:
            raise RuntimeError("Pillow is required for deterministic pitch rendering") from exc

        width, height = canvas_size
        if width <= 0 or height <= 0:
            raise ValueError("canvas_size must be positive")
        render_style = style or FootballPitchRenderStyle()
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        self._paint_surface(draw, destination_corners=destination_corners, style=render_style)

        markings = self._planner.project_all_markings(destination_corners)
        for marking in markings.polylines:
            draw.line(marking.points, fill=render_style.line_rgba, width=render_style.line_width_px, joint="curve")
        r = render_style.mark_radius_px
        for mark in markings.points:
            x, y = mark.point
            draw.ellipse((x - r, y - r, x + r, y + r), fill=render_style.line_rgba)

        if output_path is not None:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            layer.save(target, format="PNG")
        return layer

    def composite_on(self, base_image, *, destination_corners: tuple[Point, Point, Point, Point], style: FootballPitchRenderStyle | None = None):
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for deterministic pitch rendering") from exc
        if base_image.mode != "RGBA":
            base_image = base_image.convert("RGBA")
        overlay = self.render_overlay(canvas_size=base_image.size, destination_corners=destination_corners, style=style)
        return Image.alpha_composite(base_image, overlay)

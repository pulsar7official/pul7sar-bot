"""Pillow renderer for deterministic regulation football-pitch overlays.

The renderer consumes the projective geometry plan; it never asks a generative
model to draw lines, circles, penalty/corner arcs or exact pitch proportions.
Pillow is imported lazily so CPU-only policy tests do not require image
dependencies at import time.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.intelligence.football_pitch_projection import FootballPitchProjectionPlanner, Point


@dataclass(frozen=True)
class FootballPitchRenderStyle:
    line_rgba: tuple[int, int, int, int] = (245, 245, 245, 235)
    surface_rgba: tuple[int, int, int, int] = (25, 92, 45, 220)
    line_width_px: int = 5
    mark_radius_px: int = 4
    fill_surface: bool = True

    def __post_init__(self) -> None:
        if self.line_width_px <= 0 or self.mark_radius_px <= 0:
            raise ValueError("line_width_px and mark_radius_px must be positive")
        for name in ("line_rgba", "surface_rgba"):
            value = getattr(self, name)
            if len(value) != 4 or any(not isinstance(ch, int) or not 0 <= ch <= 255 for ch in value):
                raise ValueError(f"{name} must be four 0..255 integers")


class PillowFootballPitchRenderer:
    def __init__(self, planner: FootballPitchProjectionPlanner | None = None) -> None:
        self._planner = planner or FootballPitchProjectionPlanner()

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

        if render_style.fill_surface:
            draw.polygon(destination_corners, fill=render_style.surface_rgba)

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

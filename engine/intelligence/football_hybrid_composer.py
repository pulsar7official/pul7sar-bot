"""Deterministic football hybrid compositor.

The generative base owns atmosphere only. This compositor replaces the reserved
pitch region with an opaque, regulation-proportioned surface and exact markings,
so malformed generated field geometry cannot survive into the final image.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from engine.intelligence.football_pitch_placement import FootballCameraPreset, FootballPitchPlacementPlanner
from engine.intelligence.football_pitch_renderer import FootballPitchRenderStyle, PillowFootballPitchRenderer


@dataclass(frozen=True)
class FootballHybridCompositionReceipt:
    status: str
    input_path: str
    output_path: str
    canvas: str
    camera_preset: str
    deterministic_geometry_applied: bool
    generated_pitch_markings_replaced: bool
    surface_opacity: int


class FootballHybridComposer:
    def __init__(self) -> None:
        self._placements = FootballPitchPlacementPlanner()
        self._renderer = PillowFootballPitchRenderer()

    def compose_file(
        self,
        *,
        base_path: str,
        output_path: str,
        camera_preset: FootballCameraPreset = FootballCameraPreset.HIGH_WIDE_CENTRAL,
        line_width_px: int = 5,
        surface_rgb: tuple[int, int, int] = (25, 92, 45),
    ) -> FootballHybridCompositionReceipt:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for football hybrid composition") from exc

        source = Path(base_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(source) as raw:
            base = raw.convert("RGBA")
            placement = self._placements.plan(camera_preset)
            corners = placement.pixels(base.size)
            style = FootballPitchRenderStyle(
                line_rgba=(245, 245, 245, 245),
                surface_rgba=(surface_rgb[0], surface_rgb[1], surface_rgb[2], 255),
                line_width_px=line_width_px,
                mark_radius_px=max(2, line_width_px - 1),
                fill_surface=True,
            )
            composed = self._renderer.composite_on(base, destination_corners=corners, style=style)
            composed.save(target, format="PNG")

        return FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path=str(source),
            output_path=str(target),
            canvas=f"{base.width}x{base.height}",
            camera_preset=camera_preset.value,
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=255,
        )

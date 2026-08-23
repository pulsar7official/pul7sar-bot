"""Deterministic football hybrid compositor.

The generative base owns atmosphere only. This compositor replaces the reserved
pitch region with an opaque, regulation-proportioned surface and exact markings,
so malformed generated field geometry cannot survive into the final image.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

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
    mowing_stripes_applied: bool = True
    input_sha256: str = ""
    output_sha256: str = ""


class FootballHybridComposer:
    def __init__(self) -> None:
        self._placements = FootballPitchPlacementPlanner()
        self._renderer = PillowFootballPitchRenderer()

    @staticmethod
    def _validate_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
        if len(rgb) != 3 or any(not isinstance(value, int) or not 0 <= value <= 255 for value in rgb):
            raise ValueError("surface_rgb must contain three 0..255 integers")
        return rgb

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

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

        surface_rgb = self._validate_rgb(surface_rgb)
        source = Path(base_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        input_sha = self._sha256(source)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(source) as raw:
            base = raw.convert("RGBA")
            placement = self._placements.plan(camera_preset)
            corners = placement.pixels(base.size)
            alternate = tuple(min(255, int(channel * 1.10) + 2) for channel in surface_rgb)
            style = FootballPitchRenderStyle(
                line_rgba=(245, 245, 245, 245),
                surface_rgba=(*surface_rgb, 255),
                alternate_surface_rgba=(*alternate, 255),
                line_width_px=line_width_px,
                mark_radius_px=max(2, line_width_px - 1),
                fill_surface=True,
                mowing_stripes=True,
                stripe_count=10,
            )
            composed = self._renderer.composite_on(base, destination_corners=corners, style=style)
            composed.save(target, format="PNG")
            canvas = f"{base.width}x{base.height}"

        output_sha = self._sha256(target)
        if input_sha == output_sha:
            raise RuntimeError("hybrid composition produced byte-identical output; deterministic replacement was not proven")

        return FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path=str(source),
            output_path=str(target),
            canvas=canvas,
            camera_preset=camera_preset.value,
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=255,
            mowing_stripes_applied=True,
            input_sha256=input_sha,
            output_sha256=output_sha,
        )

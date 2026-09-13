"""Non-destructive football geometry reference artifacts.

This module deliberately separates geometric truth from final pixels.  FLUX owns
photographic atmosphere; regulation football geometry is rendered only to a
transparent diagnostic artifact that can be inspected or consumed by QA.  The
reference is never alpha-composited onto the publication candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.football_pitch_placement import FootballCameraPreset, FootballPitchPlacementPlanner
from engine.intelligence.football_pitch_renderer import FootballPitchRenderStyle, PillowFootballPitchRenderer


@dataclass(frozen=True)
class FootballGeometryReferenceReceipt:
    status: str
    base_path: str
    reference_path: str
    canvas: str
    camera_preset: str
    reference_only: bool
    candidate_pixels_untouched: bool
    surface_fill_applied: bool
    mowing_stripes_applied: bool
    base_sha256: str
    reference_sha256: str
    near_width_px: float
    far_width_px: float
    depth_px: float
    perspective_ratio: float


class FootballGeometryReferenceBuilder:
    """Build an inspectable transparent geometry guide without changing the photo."""

    def __init__(self) -> None:
        self._placements = FootballPitchPlacementPlanner()
        self._renderer = PillowFootballPitchRenderer()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def build(
        self,
        *,
        base_path: str,
        reference_path: str,
        camera_preset: FootballCameraPreset = FootballCameraPreset.HIGH_WIDE_CENTRAL,
        line_width_px: int = 4,
    ) -> FootballGeometryReferenceReceipt:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for football geometry reference generation") from exc

        source = Path(base_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        target = Path(reference_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(source) as raw:
            width, height = raw.size
            if width <= 0 or height <= 0:
                raise ValueError("base image dimensions must be positive")
            placement = self._placements.plan(camera_preset)
            corners = placement.pixels((width, height))
            style = FootballPitchRenderStyle(
                line_rgba=(255, 255, 255, 220),
                surface_rgba=(0, 0, 0, 0),
                alternate_surface_rgba=(0, 0, 0, 0),
                line_width_px=line_width_px,
                mark_radius_px=max(2, line_width_px - 1),
                fill_surface=False,
                mowing_stripes=False,
                stripe_count=10,
            )
            self._renderer.render_overlay(
                canvas_size=(width, height),
                destination_corners=corners,
                style=style,
                output_path=str(target),
            )

        near_left, far_left, far_right, near_right = corners
        near_width = abs(near_right[0] - near_left[0])
        far_width = abs(far_right[0] - far_left[0])
        depth = ((near_left[1] + near_right[1]) / 2.0) - ((far_left[1] + far_right[1]) / 2.0)
        if near_width <= 0 or far_width <= 0 or depth <= 0:
            raise RuntimeError("FOOTBALL_GEOMETRY_REFERENCE_INVALID_PERSPECTIVE")
        perspective_ratio = near_width / far_width
        if not 1.15 <= perspective_ratio <= 3.5:
            raise RuntimeError("FOOTBALL_GEOMETRY_REFERENCE_IMPLAUSIBLE_PERSPECTIVE")

        return FootballGeometryReferenceReceipt(
            status="FOOTBALL_GEOMETRY_REFERENCE_READY",
            base_path=str(source),
            reference_path=str(target),
            canvas=f"{width}x{height}",
            camera_preset=camera_preset.value,
            reference_only=True,
            candidate_pixels_untouched=True,
            surface_fill_applied=False,
            mowing_stripes_applied=False,
            base_sha256=self._sha256(source),
            reference_sha256=self._sha256(target),
            near_width_px=round(near_width, 3),
            far_width_px=round(far_width, 3),
            depth_px=round(depth, 3),
            perspective_ratio=round(perspective_ratio, 4),
        )

"""Deterministic football hybrid compositor.

The generative base owns atmosphere and photographic texture only. Exact pitch
geometry is owned by code. A semantic gate must prove that the base contains no
model-generated exact sport geometry before this compositor runs.

Earlier engineering proofs used an opaque flat-green replacement surface. That
proved geometry but looked like a tactical board pasted into the stadium. The
current compositor keeps the underlying photographic turf visible, adds only a
subtle deterministic colour normalisation with an inward feathered boundary,
then draws regulation markings in projective perspective. Synthetic mowing
stripes are disabled by default so photographed grass detail remains visible.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.football_pitch_placement import FootballCameraPreset, FootballPitchPlacementPlanner
from engine.intelligence.football_pitch_renderer import FootballPitchRenderStyle, PillowFootballPitchRenderer


TEXTURE_PRESERVING_COMPOSITION_MODE = "texture_preserving_pitch_overlay_v1"
DEFAULT_SURFACE_OPACITY = 54
DEFAULT_STRIPE_OPACITY = 0
DEFAULT_SURFACE_FEATHER_PX = 18


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
    mowing_stripes_applied: bool = False
    input_sha256: str = ""
    output_sha256: str = ""
    composition_mode: str = TEXTURE_PRESERVING_COMPOSITION_MODE
    source_texture_preserved: bool = True
    surface_feather_px: int = DEFAULT_SURFACE_FEATHER_PX


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
    def _validate_opacity(value: int, *, name: str, minimum: int, maximum: int) -> int:
        if not isinstance(value, int) or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")
        return value

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
        surface_opacity: int = DEFAULT_SURFACE_OPACITY,
        stripe_opacity: int = DEFAULT_STRIPE_OPACITY,
        surface_feather_px: int = DEFAULT_SURFACE_FEATHER_PX,
    ) -> FootballHybridCompositionReceipt:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for football hybrid composition") from exc

        surface_rgb = self._validate_rgb(surface_rgb)
        surface_opacity = self._validate_opacity(surface_opacity, name="surface_opacity", minimum=24, maximum=96)
        stripe_opacity = self._validate_opacity(stripe_opacity, name="stripe_opacity", minimum=0, maximum=64)
        if not isinstance(surface_feather_px, int) or not 0 <= surface_feather_px <= 64:
            raise ValueError("surface_feather_px must be an integer between 0 and 64")
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
                line_rgba=(245, 245, 245, 235),
                surface_rgba=(*surface_rgb, surface_opacity),
                alternate_surface_rgba=(*alternate, stripe_opacity),
                line_width_px=line_width_px,
                mark_radius_px=max(2, line_width_px - 1),
                fill_surface=True,
                mowing_stripes=stripe_opacity > 0,
                stripe_count=10,
                surface_feather_px=surface_feather_px,
            )
            composed = self._renderer.composite_on(base, destination_corners=corners, style=style)
            composed.save(target, format="PNG")
            canvas = f"{base.width}x{base.height}"

        output_sha = self._sha256(target)
        if input_sha == output_sha:
            raise RuntimeError("hybrid composition produced byte-identical output; deterministic geometry was not proven")

        return FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path=str(source),
            output_path=str(target),
            canvas=canvas,
            camera_preset=camera_preset.value,
            deterministic_geometry_applied=True,
            # Kept for compatibility with existing receipts. Under Hybrid v5 the
            # base semantic gate proves generated exact markings are absent; the
            # visible final markings are therefore wholly deterministic.
            generated_pitch_markings_replaced=True,
            surface_opacity=surface_opacity,
            mowing_stripes_applied=stripe_opacity > 0,
            input_sha256=input_sha,
            output_sha256=output_sha,
            composition_mode=TEXTURE_PRESERVING_COMPOSITION_MODE,
            source_texture_preserved=True,
            surface_feather_px=surface_feather_px,
        )

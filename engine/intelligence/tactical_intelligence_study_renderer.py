"""Deterministic Tactical Intelligence visual renderer for PUL7SAR Phase 18.

The pitch is present only because tactical geometry is the information surface.
Regulation markings are rendered by PillowFootballPitchRenderer, while formation
markers and movement arrows are projected from normalized pitch coordinates.
No generative model owns pitch lines, positions, labels, arrows or branding.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.football_pitch_renderer import FootballPitchRenderStyle, PillowFootballPitchRenderer
from engine.intelligence.football_pitch_projection import FootballPitchProjectionPlanner
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.tactical_intelligence_composition import TacticalIntelligenceComposition


@dataclass(frozen=True)
class TacticalPosition:
    role: str
    x_ratio: float
    y_ratio: float

    def __post_init__(self) -> None:
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("tactical role must be non-empty")
        for name in ("x_ratio", "y_ratio"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class TacticalArrow:
    start_x_ratio: float
    start_y_ratio: float
    end_x_ratio: float
    end_y_ratio: float

    def __post_init__(self) -> None:
        for name in ("start_x_ratio", "start_y_ratio", "end_x_ratio", "end_y_ratio"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class TacticalIntelligenceStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    formation_label: str
    position_count: int
    arrow_count: int
    exact_pitch_geometry_used: bool
    generated_pitch_markings_used: bool
    generated_player_positions_used: bool
    decorative_stadium_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    brand_overlay_contract: str
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-tactical-intelligence-study-renderer-v1"


class TacticalIntelligenceStudyRenderer:
    def __init__(self) -> None:
        self._pitch = PillowFootballPitchRenderer()
        self._projection = FootballPitchProjectionPlanner()

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i+2], 16) for i in (1, 3, 5))

    @staticmethod
    def _box(box: NormalizedBox, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            round(box.x * profile.width),
            round(box.y * profile.height),
            round((box.x + box.width) * profile.width),
            round((box.y + box.height) * profile.height),
        )

    @staticmethod
    def _fit_font(draw, text: str, font_path: str, max_width: int, max_height: int, start: int):
        from PIL import ImageFont
        size = max(10, start)
        while size > 10:
            font = ImageFont.truetype(font_path, size=size)
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            if right-left <= max_width and bottom-top <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=10)

    @staticmethod
    def _centered(draw, text: str, font, x: float, y: float, fill) -> None:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        draw.text((x-(right-left)/2, y-(bottom-top)/2-top), text, font=font, fill=fill)

    @staticmethod
    def _pitch_corners(surface: tuple[int, int, int, int]):
        x0, y0, x1, y1 = surface
        inset_x = round((x1-x0) * 0.025)
        inset_y = round((y1-y0) * 0.035)
        return (
            (x0+inset_x, y0+inset_y),
            (x1-inset_x, y0+inset_y),
            (x1-inset_x, y1-inset_y),
            (x0+inset_x, y1-inset_y),
        )

    def render(
        self,
        composition: TacticalIntelligenceComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        headline: str,
        analysis_text: str,
        formation_label: str,
        positions: tuple[TacticalPosition, ...],
        arrows: tuple[TacticalArrow, ...] = (),
        accent_hex: str,
        opponent_accent_hex: str = "#D2D8DE",
        brand_accent_hex: str,
        font_path: str,
    ) -> TacticalIntelligenceStudyReceipt:
        from PIL import Image, ImageDraw, ImageFilter

        if not isinstance(composition, TacticalIntelligenceComposition):
            raise TypeError("composition must be TacticalIntelligenceComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not headline.strip() or not analysis_text.strip() or not formation_label.strip():
            raise ValueError("headline, analysis_text and formation_label are required")
        if not positions:
            raise ValueError("at least one tactical position is required")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if any(not isinstance(p, TacticalPosition) for p in positions):
            raise TypeError("positions must contain TacticalPosition values")
        if any(not isinstance(a, TacticalArrow) for a in arrows):
            raise TypeError("arrows must contain TacticalArrow values")

        accent = self._rgb(accent_hex)
        opponent_accent = self._rgb(opponent_accent_hex)
        image = Image.new("RGBA", (profile.width, profile.height), (5, 11, 18, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        for y in range(profile.height):
            t = y / max(1, profile.height-1)
            draw.line((0, y, profile.width, y), fill=(round(9-3*t), round(18-5*t), round(27-7*t), 255))

        # Subtle technical glow around the information surface, not a stadium scene.
        surface_box = self._box(composition.tactical_surface_box, profile)
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        sx0, sy0, sx1, sy1 = surface_box
        gd.rounded_rectangle((sx0-18, sy0-18, sx1+18, sy1+18), radius=36, fill=(*accent, 42))
        glow = glow.filter(ImageFilter.GaussianBlur(max(20, round(profile.width*0.035))))
        image.alpha_composite(glow)

        pitch_style = FootballPitchRenderStyle(
            line_rgba=(230, 239, 234, 205),
            surface_rgba=(12, 48, 36, 235),
            alternate_surface_rgba=(13, 55, 40, 235),
            line_width_px=max(2, round(profile.width*0.0025)),
            mark_radius_px=max(2, round(profile.width*0.0028)),
            fill_surface=True,
            mowing_stripes=True,
            stripe_count=10,
            surface_feather_px=5,
        )
        corners = self._pitch_corners(surface_box)
        image = self._pitch.composite_on(image, destination_corners=corners, style=pitch_style)
        draw = ImageDraw.Draw(image, "RGBA")
        projector = self._projection.projector(corners)
        L = self._projection.geometry.length_m
        W = self._projection.geometry.width_m

        # Deterministic movement arrows, projected from exact pitch coordinates.
        import math
        for arrow in arrows:
            start = projector.project((arrow.start_x_ratio*L, arrow.start_y_ratio*W))
            end = projector.project((arrow.end_x_ratio*L, arrow.end_y_ratio*W))
            line_width = max(3, round(profile.width*0.004))
            draw.line((start, end), fill=(*opponent_accent, 170), width=line_width)
            dx, dy = end[0]-start[0], end[1]-start[1]
            length = max(1.0, math.hypot(dx, dy))
            ux, uy = dx/length, dy/length
            size = max(9, round(profile.width*0.012))
            px, py = -uy, ux
            p1 = end
            p2 = (end[0]-ux*size+px*size*0.45, end[1]-uy*size+py*size*0.45)
            p3 = (end[0]-ux*size-px*size*0.45, end[1]-uy*size-py*size*0.45)
            draw.polygon((p1, p2, p3), fill=(*opponent_accent, 205))

        # Formation points are code-owned and equal-sized.
        marker_r = max(14, round(profile.width*0.018))
        role_font = self._fit_font(draw, "CM", font_path, marker_r*2, marker_r*2, max(12, round(marker_r*0.82)))
        for position in positions:
            x, y = projector.project((position.x_ratio*L, position.y_ratio*W))
            draw.ellipse((x-marker_r-4, y-marker_r-4, x+marker_r+4, y+marker_r+4), fill=(1, 7, 12, 180))
            draw.ellipse((x-marker_r, y-marker_r, x+marker_r, y+marker_r), fill=(*accent, 235), outline=(241, 246, 249, 230), width=max(2, marker_r//7))
            self._centered(draw, position.role, role_font, x, y, (248, 250, 252, 255))

        # Headline and analysis stay outside the working pitch surface.
        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = self._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.47))
        self._centered(draw, headline, headline_font, (hx0+hx1)/2, (hy0+hy1)/2, (240, 245, 248, 255))

        ax0, ay0, ax1, ay1 = self._box(composition.analysis_box, profile)
        analysis_font = self._fit_font(draw, analysis_text, font_path, ax1-ax0, ay1-ay0, round((ay1-ay0)*0.30))
        self._centered(draw, analysis_text, analysis_font, (ax0+ax1)/2, (ay0+ay1)/2, (184, 198, 208, 245))

        label_y = sy0 - max(14, round(profile.height*0.018))
        label_font = self._fit_font(draw, formation_label, font_path, sx1-sx0, max(20, sy0-label_y+20), max(16, round(profile.height*0.019)))
        self._centered(draw, formation_label, label_font, (sx0+sx1)/2, label_y, (*accent, 245))

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(prebrand, format="PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand),
            output_path=str(target),
            adaptive=composition.brand,
            profile=profile,
            accent_hex=brand_accent_hex,
        )
        prebrand.unlink(missing_ok=True)

        return TacticalIntelligenceStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            width=profile.width,
            height=profile.height,
            formation_label=formation_label,
            position_count=len(positions),
            arrow_count=len(arrows),
            exact_pitch_geometry_used=True,
            generated_pitch_markings_used=False,
            generated_player_positions_used=False,
            decorative_stadium_used=False,
            brand_zone=brand.zone,
            brand_width=brand.width,
            brand_height=brand.height,
            brand_overlay_contract=brand.contract,
        )

"""Study-only deterministic PUL7SAR identity renderer.

It approximates the approved identity signatures for composition studies while
exact master geometry is unavailable. Every receipt says publication_ready=False.
The renderer must never replace the exact BrandMasterGeometryGate for publishing.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.brand_study_geometry import BrandStudyGeometry


@dataclass(frozen=True)
class BrandStudyPlacement:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("study brand placement must be positive")


@dataclass(frozen=True)
class BrandStudyReceipt:
    output_path: str
    output_sha256: str
    accent_hex: str
    seven_scale: float
    pulse_below_wordmark: bool
    football_near_r: bool
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-study-renderer-v1"


class BrandStudyRenderer:
    """Approximate the identity faithfully enough for visual-direction review."""

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    def render_on_file(
        self,
        *,
        base_path: str,
        output_path: str,
        placement: BrandStudyPlacement,
        geometry: BrandStudyGeometry,
        accent_hex: str,
        font_path: str,
    ) -> BrandStudyReceipt:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter

        if not geometry.study_only or geometry.publication_ready:
            raise ValueError("brand study renderer accepts study-only geometry")
        source = Path(base_path)
        target = Path(output_path)
        fpath = Path(font_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        accent = (*self._rgb(accent_hex), 255)

        with Image.open(source) as raw:
            image = raw.convert("RGBA")
            if placement.x + placement.width > image.width or placement.y + placement.height > image.height:
                raise ValueError("study brand placement exceeds canvas")

            # Work on an isolated transparent brand layer. The approximate study
            # font is intentionally not recorded as an approved master font.
            layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            base_size = max(12, int(placement.height * 0.45))
            font = ImageFont.truetype(str(fpath), base_size)
            seven_font = ImageFont.truetype(str(fpath), max(12, int(base_size * geometry.seven_scale)))

            pul = "PUL"
            sar = "SAR"
            seven = "7"
            pul_w = draw.textlength(pul, font=font)
            seven_w = draw.textlength(seven, font=seven_font)
            sar_w = draw.textlength(sar, font=font)
            total = pul_w + seven_w + sar_w
            scale = min(1.0, placement.width / max(1.0, total))
            if scale < 0.70:
                base_size = max(10, int(base_size * scale))
                font = ImageFont.truetype(str(fpath), base_size)
                seven_font = ImageFont.truetype(str(fpath), max(10, int(base_size * geometry.seven_scale)))
                pul_w = draw.textlength(pul, font=font)
                seven_w = draw.textlength(seven, font=seven_font)
                sar_w = draw.textlength(sar, font=font)
                total = pul_w + seven_w + sar_w

            x = placement.x + max(0, int((placement.width - total) / 2))
            baseline_y = placement.y + int(placement.height * 0.09)
            seven_y = max(placement.y, baseline_y - int(base_size * (geometry.seven_scale - 1.0) * 0.45))

            # Metallic approximation: draw a bright face plus a darker offset.
            shadow = (76, 82, 90, 230)
            silver = (224, 230, 236, 255)
            highlight = (255, 255, 255, 150)
            for text, tx, ty, used_font in (
                (pul, x, baseline_y, font),
                (sar, x + pul_w + seven_w, baseline_y, font),
            ):
                draw.text((tx + 2, ty + 3), text, font=used_font, fill=shadow)
                draw.text((tx, ty), text, font=used_font, fill=silver)
                draw.text((tx, ty - 1), text, font=used_font, fill=highlight)
            seven_x = x + pul_w
            draw.text((seven_x + 2, seven_y + 3), seven, font=seven_font, fill=(*accent[:3], 110))
            draw.text((seven_x, seven_y), seven, font=seven_font, fill=accent)

            # Pulse lives in the lower band, never through the wordmark.
            pulse_y = placement.y + int(placement.height * geometry.pulse_band_start)
            pulse_h = max(8, int(placement.height * 0.20))
            pulse = (
                (placement.x + int(placement.width * 0.08), pulse_y + int(pulse_h * 0.55)),
                (placement.x + int(placement.width * 0.34), pulse_y + int(pulse_h * 0.55)),
                (placement.x + int(placement.width * 0.42), pulse_y + int(pulse_h * 0.18)),
                (placement.x + int(placement.width * 0.49), pulse_y + int(pulse_h * 0.90)),
                (placement.x + int(placement.width * 0.57), pulse_y + int(pulse_h * 0.38)),
                (placement.x + int(placement.width * 0.64), pulse_y + int(pulse_h * 0.55)),
                (placement.x + int(placement.width * 0.88), pulse_y + int(pulse_h * 0.55)),
            )
            glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_draw.line(pulse, fill=(*accent[:3], 135), width=max(5, int(placement.height * 0.025)), joint="curve")
            glow = glow.filter(ImageFilter.GaussianBlur(max(2, int(placement.height * 0.018))))
            layer.alpha_composite(glow)
            draw = ImageDraw.Draw(layer)
            draw.line(pulse, fill=accent, width=max(2, int(placement.height * 0.009)), joint="curve")

            # Small deterministic football signature near the R side.
            cx = placement.x + int(placement.width * geometry.football_center_x)
            cy = placement.y + int(placement.height * geometry.football_center_y)
            radius = max(4, int(placement.width * geometry.football_radius))
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(240, 240, 240, 255), outline=(40, 40, 40, 255), width=max(1, radius // 5))
            inner = max(2, radius // 3)
            draw.regular_polygon((cx, cy, inner), n_sides=5, rotation=-18, fill=(30, 30, 30, 255))
            for angle in (18, 90, 162, 234, 306):
                import math
                px = cx + int(radius * 0.64 * math.cos(math.radians(angle)))
                py = cy + int(radius * 0.64 * math.sin(math.radians(angle)))
                draw.ellipse((px-inner//2, py-inner//2, px+inner//2, py+inner//2), fill=(40, 40, 40, 255))

            image.alpha_composite(layer)
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target, format="PNG")

        return BrandStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            accent_hex=accent_hex.upper(),
            seven_scale=geometry.seven_scale,
            pulse_below_wordmark=True,
            football_near_r=True,
        )

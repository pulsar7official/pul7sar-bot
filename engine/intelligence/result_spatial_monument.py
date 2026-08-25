"""Deterministic spatial result monument for Phase 18 visual benchmarking.

The generated model owns atmosphere and environment only. This compositor creates
an exact factual score object as a perspective-aware editorial surface inside the
scene, rather than a flat lower-third pasted over it. It remains study-only and
never invents club identity or PUL7SAR branding.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


@dataclass(frozen=True)
class SpatialResultSpec:
    headline: str
    home: str
    away: str
    score: str
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def validate(self) -> None:
        if not self.score.strip():
            raise ValueError("SPATIAL_RESULT_SCORE_REQUIRED")
        if not self.home.strip() or not self.away.strip():
            raise ValueError("SPATIAL_RESULT_TEAM_LABELS_REQUIRED")


class SpatialResultMonument:
    CONTRACT = "pul7sar-spatial-result-monument-v1"

    @staticmethod
    def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(path, max(12, size))

    @staticmethod
    def _fit(draw: ImageDraw.ImageDraw, text: str, path: str, max_width: int, start: int, minimum: int) -> ImageFont.FreeTypeFont:
        size = start
        while size >= minimum:
            font = ImageFont.truetype(path, size)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= max_width:
                return font
            size -= 2
        return ImageFont.truetype(path, minimum)

    @classmethod
    def compose(cls, base_path: str, output_path: str, spec: SpatialResultSpec) -> str:
        spec.validate()
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)

        canvas = Image.open(base).convert("RGBA")
        w, h = canvas.size

        # Localized cinematic integration: darken only behind/under the monument,
        # leaving the upper generated world readable and visibly original.
        atmosphere = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ad = ImageDraw.Draw(atmosphere, "RGBA")
        ad.ellipse(
            (int(w * .08), int(h * .43), int(w * .95), int(h * .94)),
            fill=(0, 0, 0, 86),
        )
        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(max(18, w // 24)))
        canvas.alpha_composite(atmosphere)

        # Perspective trapezoid: slightly narrower at the rear edge. A factual
        # object appears to sit in scene depth rather than behaving like UI chrome.
        x0, x1 = int(w * .10), int(w * .90)
        y_top, y_bottom = int(h * .55), int(h * .82)
        inset = int(w * .055)
        polygon = [
            (x0 + inset, y_top),
            (x1 - inset, y_top),
            (x1, y_bottom),
            (x0, y_bottom),
        ]

        # Ground contact shadow gives the object weight.
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow, "RGBA")
        shadow_poly = [(x + int(w*.012), y + int(h*.018)) for x, y in polygon]
        sd.polygon(shadow_poly, fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(10, w // 36)))
        canvas.alpha_composite(shadow)

        plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.polygon(polygon, fill=(5, 9, 14, 205))
        # Rear rim / stadium-light catch. Neutral white: no fabricated team brand.
        pd.line(polygon[:2], fill=(245, 248, 252, 110), width=max(2, w // 210))
        pd.line([polygon[0], polygon[3]], fill=(230, 234, 240, 45), width=max(1, w // 320))
        pd.line([polygon[1], polygon[2]], fill=(230, 234, 240, 45), width=max(1, w // 320))
        canvas.alpha_composite(plate)

        draw = ImageDraw.Draw(canvas, "RGBA")
        center_x = w // 2

        # Headline floats just above the physical score object, like an editorial
        # kicker integrated with the same light field rather than a top UI bar.
        headline = spec.headline.upper().strip()
        if headline:
            hf = cls._fit(draw, headline, spec.font_path, int(w*.55), int(w*.041), 18)
            draw.text((center_x, int(h*.515)), headline, font=hf, fill=(239,243,248,220), anchor="mm")

        score_font = cls._fit(draw, spec.score, spec.font_path, int(w*.38), int(w*.19), 58)
        team_text = max((spec.home.upper(), spec.away.upper()), key=len)
        team_font = cls._fit(draw, team_text, spec.font_path, int(w*.27), int(w*.032), 16)

        score_y = int(h * .655)
        draw.text((center_x, score_y), spec.score, font=score_font, fill=(250,251,252,255), anchor="mm")

        label_y = int(h * .747)
        draw.text((int(w*.255), label_y), spec.home.upper(), font=team_font, fill=(236,240,244,235), anchor="mm")
        draw.text((int(w*.745), label_y), spec.away.upper(), font=team_font, fill=(236,240,244,235), anchor="mm")

        # Fine perspective guide lines terminate into the monument itself and make
        # the exact score feel architected, not simply typeset over a photograph.
        guide = Image.new("RGBA", (w, h), (0,0,0,0))
        gd = ImageDraw.Draw(guide, "RGBA")
        gd.line((int(w*.39), int(h*.715), int(w*.34), int(h*.79)), fill=(245,248,250,38), width=max(1,w//360))
        gd.line((int(w*.61), int(h*.715), int(w*.66), int(h*.79)), fill=(245,248,250,38), width=max(1,w//360))
        canvas.alpha_composite(guide)

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out, quality=96)
        return str(out)

"""Sculpted art-direction layer for the premium-hybrid Result benchmark.

V3 keeps all v2 factual and provenance guarantees while increasing perceived
production value through deterministic dimensional typography, optical separation
and stronger neutral identity monuments. No new semantic content is invented.
"""
from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from engine.intelligence.premium_hybrid_result_runtime import (
    PremiumHybridResultStudyReceipt,
    PremiumHybridResultStudyRenderer as _V2Runtime,
)
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer


class PremiumHybridResultStudyRenderer(_V2Runtime):
    """V3 visual treatment; inherits the proven v2 factual render contract."""

    @classmethod
    def _draw_metallic_text(
        cls,
        image: Image.Image,
        *,
        text: str,
        font,
        center_x: float,
        center_y: float,
        accent: tuple[int, int, int],
        outline_px: int,
        glow_radius: int,
    ) -> None:
        mask = cls._text_mask(image.size, text=text, font=font, center_x=center_x, center_y=center_y)

        # Wide optical halo separates the score from photographic detail.
        halo_mask = mask.filter(ImageFilter.GaussianBlur(max(12, glow_radius * 2)))
        halo = Image.new("RGBA", image.size, (*accent, 0))
        halo.putalpha(halo_mask.point(lambda p: round(p * 0.16)))
        image.alpha_composite(halo)

        # Eight-step bevel/extrusion. Dark lower-right depth plus a thin accent rim
        # gives the digits the physical 'score monument' weight missing in flat text.
        for depth in range(9, 0, -1):
            shifted = Image.new("L", image.size, 0)
            shifted.paste(mask, (depth, depth + 2))
            shade = 20 + depth * 2
            extrusion = Image.new("RGBA", image.size, (shade, shade + 4, shade + 10, 0))
            extrusion.putalpha(shifted.point(lambda p, d=depth: round(p * (0.52 + d * 0.018))))
            image.alpha_composite(extrusion)

        expanded = mask.filter(ImageFilter.MaxFilter(max(3, outline_px * 2 + 3)))
        rim_mask = ImageChops.subtract(expanded, mask)
        rim = Image.new("RGBA", image.size, (*accent, 0))
        rim.putalpha(rim_mask.point(lambda p: round(p * 0.62)))
        image.alpha_composite(rim)

        # Bright steel face from the inherited multi-stop material.
        metal = cls._metallic_fill(image.size)
        metal.putalpha(mask)
        image.alpha_composite(metal)

        # Specular highlight shifted upward-left, clipped to the glyph.
        highlight_source = Image.new("L", image.size, 0)
        highlight_source.paste(mask, (-max(1, outline_px), -max(2, outline_px * 2)))
        highlight_mask = ImageChops.multiply(mask, highlight_source)
        highlight_mask = highlight_mask.filter(ImageFilter.GaussianBlur(max(1, outline_px // 2)))
        highlight = Image.new("RGBA", image.size, (255, 255, 255, 0))
        highlight.putalpha(highlight_mask.point(lambda p: round(p * 0.23)))
        image.alpha_composite(highlight)

        # Tight bottom shadow restores edge definition after the glow.
        shadow_mask = Image.new("L", image.size, 0)
        shadow_mask.paste(mask, (0, max(3, outline_px * 3)))
        shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(max(3, outline_px)))
        shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        shadow.putalpha(shadow_mask.point(lambda p: round(p * 0.22)))
        image.alpha_composite(shadow)

    @classmethod
    def _draw_identity_monument(
        cls,
        image: Image.Image,
        *,
        box: tuple[int, int, int, int],
        name: str,
        accent: tuple[int, int, int],
        font_path: str,
        winner: bool,
    ) -> None:
        base = ResultStatementStudyRenderer
        x0, y0, x1, y1 = box
        width, height = x1 - x0, y1 - y0
        cx = (x0 + x1) / 2
        shield_w = min(round(width * 0.38), round(height * 0.50), 88)
        shield_h = round(shield_w * 1.18)
        cy = y0 + round(height * 0.30)
        pts = [
            (cx-shield_w/2, cy-shield_h*0.36),
            (cx, cy-shield_h*0.52),
            (cx+shield_w/2, cy-shield_h*0.36),
            (cx+shield_w*0.46, cy+shield_h*0.17),
            (cx, cy+shield_h*0.52),
            (cx-shield_w*0.46, cy+shield_h*0.17),
        ]

        # Three optical layers create depth while remaining unmistakably a neutral
        # placeholder rather than a fabricated club crest.
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo, "RGBA")
        hd.polygon(pts, fill=(*accent, 72 if winner else 48))
        halo = halo.filter(ImageFilter.GaussianBlur(max(12, shield_w // 3)))
        image.alpha_composite(halo)

        draw = ImageDraw.Draw(image, "RGBA")
        shadow_pts = [(px+5, py+7) for px, py in pts]
        draw.polygon(shadow_pts, fill=(0, 0, 0, 105))
        draw.polygon(pts, fill=(4, 10, 18, 220), outline=(*accent, 245))
        inner = [(cx + (px-cx)*0.76, cy + (py-cy)*0.76) for px, py in pts]
        draw.line(inner + [inner[0]], fill=(239, 245, 249, 135), width=2, joint="curve")
        core = [(cx + (px-cx)*0.48, cy + (py-cy)*0.48) for px, py in pts]
        draw.line(core + [core[0]], fill=(*accent, 145), width=1, joint="curve")
        dot = max(4, shield_w // 12)
        draw.ellipse((cx-dot, cy-dot, cx+dot, cy+dot), fill=(*accent, 255))
        draw.ellipse((cx-dot//2, cy-dot//2, cx+dot//2, cy+dot//2), fill=(244, 248, 251, 205))

        name_y = y0 + round(height * 0.77)
        name_font = base._fit_font(
            draw, name, font_path,
            max(20, round(width * 0.98)), max(18, round(height * 0.22)),
            max(18, round(height * 0.18)),
        )
        bbox = draw.textbbox((0, 0), name, font=name_font)
        tx = cx - (bbox[2]-bbox[0])/2
        ty = name_y - (bbox[3]-bbox[1])/2 - bbox[1]
        draw.text((tx+1, ty+3), name, font=name_font, fill=(0, 0, 0, 115))
        draw.text((tx, ty), name, font=name_font, fill=(242, 247, 250, 255))

        line_w = round(width * (0.60 if winner else 0.42))
        line_y = y1 - max(4, round(height * 0.018))
        draw.rounded_rectangle(
            (cx-line_w/2, line_y-2, cx+line_w/2, line_y+2),
            radius=2,
            fill=(*accent, 235 if winner else 145),
        )
        draw.line(
            (cx-line_w/2, line_y-5, cx+line_w/2, line_y-5),
            fill=(239, 245, 249, 40), width=1,
        )


__all__ = ["PremiumHybridResultStudyReceipt", "PremiumHybridResultStudyRenderer"]

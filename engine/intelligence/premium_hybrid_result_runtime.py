"""Runtime-hardening wrapper for the premium hybrid Result v2 renderer.

The visual renderer remains unchanged; this wrapper fixes the optical falloff
normalization so non-integer canvas fractions can never create a negative base
for the fractional exponent. It intentionally overrides only the deterministic
atmosphere integration method.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.premium_hybrid_result_study_renderer import (
    PremiumHybridResultStudyReceipt,
    PremiumHybridResultStudyRenderer as _PremiumHybridResultStudyRenderer,
)


class PremiumHybridResultStudyRenderer(_PremiumHybridResultStudyRenderer):
    @staticmethod
    def _cinematic_integration(
        image: Image.Image,
        *,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> None:
        """Build optical depth with normalized, finite falloff math."""
        width, height = image.size

        lower = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lower, "RGBA")
        start_y = round(height * 0.27)
        span = max(1, height - start_y - 1)
        for y in range(start_y, height):
            t = max(0.0, min(1.0, (y - start_y) / span))
            alpha = round(18 + 165 * (t ** 1.62))
            ld.line((0, y, width, y), fill=(1, 5, 11, min(196, alpha)))
        image.alpha_composite(lower)

        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        r = round(max(width, height) * 0.38)
        cy = round(height * 0.56)
        gd.ellipse((-round(r * 0.70), cy-r, round(r * 1.30), cy+r), fill=(*home_accent, 76))
        gd.ellipse((width-round(r * 1.30), cy-r, width+round(r * 0.70), cy+r), fill=(*away_accent, 72))
        glow = glow.filter(ImageFilter.GaussianBlur(max(34, round(width * 0.085))))
        image.alpha_composite(glow)

        lights = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(lights, "RGBA")
        for cx in (round(width * 0.10), round(width * 0.90)):
            cy2 = round(height * 0.14)
            rr = round(width * 0.20)
            ldraw.ellipse((cx-rr, cy2-rr, cx+rr, cy2+rr), fill=(226, 239, 248, 31))
        lights = lights.filter(ImageFilter.GaussianBlur(max(36, round(width * 0.09))))
        image.alpha_composite(lights)

        shaft = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shaft, "RGBA")
        cx = width // 2
        top = round(height * 0.09)
        bottom = round(height * 0.70)
        half_top = round(width * 0.025)
        half_bottom = round(width * 0.20)
        sd.polygon(
            ((cx-half_top, top), (cx+half_top, top), (cx+half_bottom, bottom), (cx-half_bottom, bottom)),
            fill=(235, 243, 249, 18),
        )
        shaft = shaft.filter(ImageFilter.GaussianBlur(max(22, round(width * 0.05))))
        image.alpha_composite(shaft)

        rails = Image.new("RGBA", image.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rails, "RGBA")
        horizon = round(height * 0.61)
        bottom_y = round(height * 0.93)
        for x in (round(width*0.08), round(width*0.24), round(width*0.76), round(width*0.92)):
            rd.line((width//2, horizon, x, bottom_y), fill=(228, 238, 245, 16), width=1)
        rd.arc((round(width*.18), round(height*.70), round(width*.82), round(height*1.06)), 190, 350, fill=(228, 238, 245, 14), width=1)
        rails = rails.filter(ImageFilter.GaussianBlur(0.5))
        image.alpha_composite(rails)

        edge = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ed = ImageDraw.Draw(edge, "RGBA")
        side = round(width * 0.08)
        ed.rectangle((0, 0, side, height), fill=(0, 0, 0, 102))
        ed.rectangle((width-side, 0, width, height), fill=(0, 0, 0, 102))
        ed.rectangle((0, 0, width, round(height * 0.05)), fill=(0, 0, 0, 48))
        edge = edge.filter(ImageFilter.GaussianBlur(max(24, round(width * 0.05))))
        image.alpha_composite(edge)


__all__ = ["PremiumHybridResultStudyReceipt", "PremiumHybridResultStudyRenderer"]

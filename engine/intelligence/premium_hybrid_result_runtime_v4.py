"""Editorial-steel art direction for the premium-hybrid Result benchmark.

V4 deliberately removes the game-like coloured digit rim from v3. Club colour
moves back into light and hierarchy while the exact score becomes a restrained
steel object with neutral bevels, photographic separation and soft volumetric
shadow. This remains a deterministic study layer only.
"""
from __future__ import annotations

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from engine.intelligence.premium_hybrid_result_runtime_v3 import (
    PremiumHybridResultStudyReceipt,
    PremiumHybridResultStudyRenderer as _V3Runtime,
)


class PremiumHybridResultStudyRenderer(_V3Runtime):
    @staticmethod
    def _cinematic_integration(
        image: Image.Image,
        *,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> None:
        _V3Runtime._cinematic_integration(
            image,
            home_accent=home_accent,
            away_accent=away_accent,
        )
        width, height = image.size

        # Central oval veil suppresses photographic clutter exactly where the score
        # lives while remaining borderless and organically blended into the scene.
        veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
        vd = ImageDraw.Draw(veil, "RGBA")
        cx, cy = width // 2, round(height * 0.43)
        rx, ry = round(width * 0.34), round(height * 0.22)
        vd.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=(1, 5, 12, 86))
        veil = veil.filter(ImageFilter.GaussianBlur(max(36, round(width * 0.09))))
        image.alpha_composite(veil)

        # Thin photographic bloom at the score horizon. It reads as light rather
        # than a graphic rule and ties the foreground to the stadium floodlights.
        bloom = Image.new("RGBA", image.size, (0, 0, 0, 0))
        bd = ImageDraw.Draw(bloom, "RGBA")
        y = round(height * 0.49)
        bd.rectangle((round(width*0.27), y-2, round(width*0.73), y+2), fill=(236, 243, 248, 35))
        bloom = bloom.filter(ImageFilter.GaussianBlur(max(8, round(width * 0.018))))
        image.alpha_composite(bloom)

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

        # Club colour exists only as a soft atmospheric aura.
        aura = mask.filter(ImageFilter.GaussianBlur(max(18, glow_radius * 2)))
        glow = Image.new("RGBA", image.size, (*accent, 0))
        glow.putalpha(aura.point(lambda p: round(p * 0.13)))
        image.alpha_composite(glow)

        # Deep neutral extrusion creates physical mass without a coloured cartoon rim.
        for depth in range(10, 0, -1):
            shifted = Image.new("L", image.size, 0)
            shifted.paste(mask, (depth, depth + 3))
            tone = max(8, 31 - depth * 2)
            layer = Image.new("RGBA", image.size, (tone, tone + 5, tone + 11, 0))
            layer.putalpha(shifted.point(lambda p, d=depth: round(p * (0.42 + d * 0.025))))
            image.alpha_composite(layer)

        # Neutral outer bevel then a narrow charcoal inner rim.
        outer = mask.filter(ImageFilter.MaxFilter(max(3, outline_px * 2 + 5)))
        outer_ring = ImageChops.subtract(outer, mask)
        silver = Image.new("RGBA", image.size, (166, 177, 187, 0))
        silver.putalpha(outer_ring.point(lambda p: round(p * 0.72)))
        image.alpha_composite(silver)

        near = mask.filter(ImageFilter.MaxFilter(max(3, outline_px * 2 + 1)))
        near_ring = ImageChops.subtract(near, mask)
        charcoal = Image.new("RGBA", image.size, (37, 45, 56, 0))
        charcoal.putalpha(near_ring.point(lambda p: round(p * 0.83)))
        image.alpha_composite(charcoal)

        # Steel face.
        metal = cls._metallic_fill(image.size)
        metal.putalpha(mask)
        image.alpha_composite(metal)

        # Top-left specular strip and lower-face shade simulate a bevelled plate.
        top_mask = Image.new("L", image.size, 0)
        top_mask.paste(mask, (-max(1, outline_px), -max(2, outline_px * 2)))
        top_mask = ImageChops.multiply(mask, top_mask).filter(ImageFilter.GaussianBlur(1.2))
        spec = Image.new("RGBA", image.size, (255, 255, 255, 0))
        spec.putalpha(top_mask.point(lambda p: round(p * 0.24)))
        image.alpha_composite(spec)

        bottom_mask = Image.new("L", image.size, 0)
        bottom_mask.paste(mask, (0, max(3, outline_px * 3)))
        bottom_mask = ImageChops.multiply(mask, bottom_mask).filter(ImageFilter.GaussianBlur(1.5))
        shade = Image.new("RGBA", image.size, (12, 20, 29, 0))
        shade.putalpha(bottom_mask.point(lambda p: round(p * 0.20)))
        image.alpha_composite(shade)


__all__ = ["PremiumHybridResultStudyReceipt", "PremiumHybridResultStudyRenderer"]

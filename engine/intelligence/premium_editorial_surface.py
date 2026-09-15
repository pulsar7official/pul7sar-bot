"""Deterministic premium editorial surface primitives for PUL7SAR Phase 18.

This module owns atmosphere only: depth, restrained light, texture and glass-like
surfaces. It never owns facts, readable copy, real identity, club marks, score,
sport geometry or the PUL7SAR brand. The intent is to close the visual-quality
gap between correct engineering studies and premium editorial art direction
without introducing a paid/network dependency into the core renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter


@dataclass(frozen=True)
class EditorialSurfaceStyle:
    base_top: tuple[int, int, int] = (8, 16, 27)
    base_bottom: tuple[int, int, int] = (2, 7, 13)
    accent: tuple[int, int, int] = (199, 25, 37)
    secondary_accent: tuple[int, int, int] | None = None
    glow_strength: int = 80
    grain_strength: int = 13
    vignette_strength: int = 118
    light_beams: bool = True
    glass_depth: bool = True

    def __post_init__(self) -> None:
        for name in ("base_top", "base_bottom", "accent"):
            value = getattr(self, name)
            if len(value) != 3 or any(not isinstance(ch, int) or not 0 <= ch <= 255 for ch in value):
                raise ValueError(f"{name} must be RGB")
        if self.secondary_accent is not None and (
            len(self.secondary_accent) != 3 or any(not isinstance(ch, int) or not 0 <= ch <= 255 for ch in self.secondary_accent)
        ):
            raise ValueError("secondary_accent must be RGB or None")
        for name in ("glow_strength", "grain_strength", "vignette_strength"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 255:
                raise ValueError(f"{name} must be 0..255")


class PremiumEditorialSurface:
    CONTRACT = "pul7sar-premium-editorial-surface-v1"

    @staticmethod
    def _seed(seed_key: str) -> int:
        if not isinstance(seed_key, str) or not seed_key.strip():
            raise ValueError("seed_key is required")
        return int(sha256(seed_key.encode("utf-8")).hexdigest()[:16], 16)

    @staticmethod
    def _vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
        width, height = size
        image = Image.new("RGBA", size, (*top, 255))
        draw = ImageDraw.Draw(image)
        for y in range(height):
            t = y / max(1, height - 1)
            rgb = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            draw.line((0, y, width, y), fill=(*rgb, 255))
        return image

    @staticmethod
    def _radial_glow(size: tuple[int, int], *, center: tuple[float, float], color: tuple[int, int, int], alpha: int, radius_ratio: float) -> Image.Image:
        width, height = size
        radius = max(1, round(max(width, height) * radius_ratio))
        cx = round(center[0] * width)
        cy = round(center[1] * height)
        small = Image.new("L", (radius * 2, radius * 2), 0)
        sd = ImageDraw.Draw(small)
        for r in range(radius, 0, -max(1, radius // 90)):
            t = 1 - (r / radius)
            value = round(alpha * (t ** 1.65))
            sd.ellipse((radius - r, radius - r, radius + r, radius + r), fill=value)
        glow = Image.new("RGBA", size, (0, 0, 0, 0))
        tint = Image.new("RGBA", small.size, (*color, 255))
        tint.putalpha(small.filter(ImageFilter.GaussianBlur(max(2, radius // 18))))
        glow.alpha_composite(tint, (cx - radius, cy - radius))
        return glow

    @staticmethod
    def _beams(size: tuple[int, int], *, accent: tuple[int, int, int], seed: int) -> Image.Image:
        width, height = size
        rng = random.Random(seed)
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")
        horizon = round(height * 0.17)
        for _ in range(4):
            origin_x = rng.randint(round(width * 0.12), round(width * 0.88))
            spread = rng.randint(round(width * 0.09), round(width * 0.22))
            bottom_x = origin_x + rng.randint(-round(width * 0.18), round(width * 0.18))
            alpha = rng.randint(9, 20)
            draw.polygon(
                ((origin_x - 4, horizon), (origin_x + 4, horizon), (bottom_x + spread, height), (bottom_x - spread, height)),
                fill=(*accent, alpha),
            )
        return layer.filter(ImageFilter.GaussianBlur(max(8, round(width * 0.025))))

    @staticmethod
    def _grain(size: tuple[int, int], *, seed: int, strength: int) -> Image.Image:
        if strength == 0:
            return Image.new("RGBA", size, (0, 0, 0, 0))
        width, height = size
        # Generate at quarter resolution and upscale; this creates film-like texture
        # without expensive per-pixel full-canvas Python loops.
        sw, sh = max(1, width // 4), max(1, height // 4)
        rng = random.Random(seed ^ 0xA5A5A5)
        noise = Image.new("L", (sw, sh))
        noise.putdata([rng.randint(max(0, 128 - strength), min(255, 128 + strength)) for _ in range(sw * sh)])
        noise = noise.resize(size, Image.Resampling.BILINEAR)
        alpha = Image.new("L", size, max(3, min(22, strength)))
        rgba = Image.merge("RGBA", (noise, noise, noise, alpha))
        return rgba

    @staticmethod
    def _vignette(size: tuple[int, int], strength: int) -> Image.Image:
        width, height = size
        mask = Image.new("L", size, 255)
        draw = ImageDraw.Draw(mask)
        inset_x = round(width * 0.08)
        inset_y = round(height * 0.06)
        draw.ellipse((-inset_x, -inset_y, width + inset_x, height + inset_y), fill=0)
        mask = mask.filter(ImageFilter.GaussianBlur(max(20, round(min(width, height) * 0.16))))
        mask = mask.point(lambda value: round(value * strength / 255))
        layer = Image.new("RGBA", size, (0, 0, 0, 255))
        layer.putalpha(mask)
        return layer

    @staticmethod
    def glass_panel(base: Image.Image, box: tuple[int, int, int, int], *, radius: int = 28, opacity: int = 74, border_alpha: int = 38) -> None:
        if base.mode != "RGBA":
            raise ValueError("glass_panel requires RGBA base")
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0:
            raise ValueError("glass panel box must be positive")
        panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(panel, "RGBA")
        draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=(7, 15, 25, opacity), outline=(255, 255, 255, border_alpha), width=1)
        # Soft edge halo gives separation without a heavy card border.
        halo = panel.getchannel("A").filter(ImageFilter.GaussianBlur(max(4, radius // 4)))
        halo_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        halo_tint = Image.new("RGBA", base.size, (125, 165, 195, 20))
        halo_tint.putalpha(halo.point(lambda v: min(34, v // 6)))
        halo_layer = Image.alpha_composite(halo_layer, halo_tint)
        base.alpha_composite(halo_layer)
        base.alpha_composite(panel)

    def render(self, *, size: tuple[int, int], style: EditorialSurfaceStyle, seed_key: str) -> Image.Image:
        width, height = size
        if width <= 0 or height <= 0:
            raise ValueError("size must be positive")
        if not isinstance(style, EditorialSurfaceStyle):
            raise TypeError("style must be EditorialSurfaceStyle")
        seed = self._seed(seed_key)
        image = self._vertical_gradient(size, style.base_top, style.base_bottom)

        # Primary accent remains off-centre so focal elements can own the middle.
        image = Image.alpha_composite(
            image,
            self._radial_glow(size, center=(0.18, 0.38), color=style.accent, alpha=style.glow_strength, radius_ratio=0.58),
        )
        secondary = style.secondary_accent or tuple(min(255, round(ch * 0.72 + 35)) for ch in style.accent)
        image = Image.alpha_composite(
            image,
            self._radial_glow(size, center=(0.86, 0.62), color=secondary, alpha=max(24, style.glow_strength // 2), radius_ratio=0.50),
        )
        if style.light_beams:
            image = Image.alpha_composite(image, self._beams(size, accent=style.accent, seed=seed))

        # Fine horizon and architectural traces create editorial depth without
        # pretending that a specific stadium or venue is present.
        draw = ImageDraw.Draw(image, "RGBA")
        rng = random.Random(seed ^ 0xC0FFEE)
        horizon_y = round(height * 0.72)
        draw.line((0, horizon_y, width, horizon_y), fill=(255, 255, 255, 10), width=1)
        for _ in range(14):
            x = rng.randint(0, width)
            h = rng.randint(round(height * 0.02), round(height * 0.13))
            draw.line((x, horizon_y, x, horizon_y - h), fill=(190, 214, 232, rng.randint(4, 11)), width=1)

        image = Image.alpha_composite(image, self._grain(size, seed=seed, strength=style.grain_strength))
        image = Image.alpha_composite(image, self._vignette(size, style.vignette_strength))
        return image

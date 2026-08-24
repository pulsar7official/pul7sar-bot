"""Premium deterministic Event Editorial renderer for PUL7SAR Phase 18.

General event stories receive one symbolic editorial anchor and cinematic depth,
without forcing a person, football pitch, stadium, trophy or decorative stats.
When a rights-verified photographic context is explicitly supplied for the story,
it may own the photographic atmosphere only. Facts, readable copy, identity,
brand geometry and the editorial anchor remain deterministic/code-owned.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.event_editorial_composition import EventEditorialComposition
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.premium_editorial_surface import EditorialSurfaceStyle, PremiumEditorialSurface
from engine.intelligence.verified_context_surface import (
    VerifiedContextAsset,
    VerifiedContextSurfaceRenderer,
)


class EventAnchorKind(str, Enum):
    ANNOUNCEMENT = "announcement"
    CALENDAR = "calendar"
    GOVERNANCE = "governance"
    BROADCAST = "broadcast"
    GENERIC_EVENT = "generic_event"


@dataclass(frozen=True)
class EventEditorialStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    anchor_kind: str
    single_anchor_used: bool
    person_used: bool
    full_pitch_used: bool
    decorative_stats_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    atmosphere_contract: str
    photographic_context_used: bool = False
    context_contract: str | None = None
    context_source_reference: str | None = None
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-event-editorial-study-renderer-v1-premium-anchor"


class EventEditorialStudyRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith('#'):
            raise ValueError('accent must be #RRGGBB')
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _box(box, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            round(box.x * profile.width), round(box.y * profile.height),
            round((box.x + box.width) * profile.width), round((box.y + box.height) * profile.height),
        )

    @staticmethod
    def _fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_width: int, max_height: int, start: int) -> ImageFont.FreeTypeFont:
        size = max(12, start)
        while size >= 12:
            font = ImageFont.truetype(font_path, size=size)
            b = draw.textbbox((0, 0), text, font=font)
            if b[2]-b[0] <= max_width and b[3]-b[1] <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=12)

    @staticmethod
    def _finish_photographic_context(canvas: Image.Image, *, accent: tuple[int, int, int]) -> Image.Image:
        """Build premium depth without fabricating semantic scene content."""
        width, height = canvas.size
        image = canvas.convert('RGBA')

        # Copy-side shadow gives typography a clean editorial lane while retaining
        # recognisable photographic texture rather than hiding the source image.
        shade = Image.new('RGBA', image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade, 'RGBA')
        for i in range(18):
            x = round(width * (0.43 + i * 0.035))
            alpha = min(165, 28 + i * 8)
            sd.rectangle((x, 0, width, height), fill=(2, 6, 12, alpha))
        shade = shade.filter(ImageFilter.GaussianBlur(max(18, width // 42)))
        image = Image.alpha_composite(image, shade)

        # Two restrained optical accents create lens depth, not fake objects.
        optics = Image.new('RGBA', image.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(optics, 'RGBA')
        od.ellipse(
            (-round(width*.18), round(height*.18), round(width*.42), round(height*.78)),
            fill=(*accent, 34),
        )
        od.ellipse(
            (round(width*.50), -round(height*.10), round(width*1.05), round(height*.45)),
            fill=(220, 237, 248, 15),
        )
        optics = optics.filter(ImageFilter.GaussianBlur(max(26, width // 20)))
        return Image.alpha_composite(image, optics)

    @staticmethod
    def _draw_anchor(canvas: Image.Image, box: tuple[int, int, int, int], *, accent: tuple[int, int, int], kind: EventAnchorKind) -> None:
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            raise ValueError('anchor box must be positive')
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, 'RGBA')
        cx, cy = x0 + w // 2, y0 + h // 2

        halo = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo, 'RGBA')
        for step in range(8, 0, -1):
            inset = round(min(w, h) * 0.035 * step)
            alpha = max(3, 15 - step)
            hd.rounded_rectangle((x0 + inset, y0 + inset, x1 - inset, y1 - inset), radius=max(12, round(w * 0.04)), outline=(*accent, alpha), width=max(1, round(w * 0.006)))
        halo = halo.filter(ImageFilter.GaussianBlur(max(10, round(w * 0.03))))
        canvas.alpha_composite(halo)

        top_w = round(w * (0.38 if kind is EventAnchorKind.GOVERNANCE else 0.46))
        bottom_w = round(w * 0.64)
        top_y = y0 + round(h * 0.13)
        bottom_y = y1 - round(h * 0.10)
        points = (
            (cx - top_w // 2, top_y),
            (cx + top_w // 2, top_y),
            (cx + bottom_w // 2, bottom_y),
            (cx - bottom_w // 2, bottom_y),
        )
        draw.polygon(points, fill=(7, 17, 29, 110), outline=(*accent, 130))

        band_count = {
            EventAnchorKind.ANNOUNCEMENT: 3,
            EventAnchorKind.CALENDAR: 4,
            EventAnchorKind.GOVERNANCE: 2,
            EventAnchorKind.BROADCAST: 5,
            EventAnchorKind.GENERIC_EVENT: 3,
        }[kind]
        for i in range(1, band_count + 1):
            t = i / (band_count + 1)
            y = round(top_y * (1-t) + bottom_y * t)
            half = round((top_w * (1-t) + bottom_w * t) / 2)
            draw.line((cx-half, y, cx+half, y), fill=(226, 238, 246, 24 + i * 6), width=max(1, round(w * 0.003)))

        core_w = round(w * 0.24)
        core_y = cy
        draw.line((cx-core_w, core_y, cx-round(core_w*0.35), core_y), fill=(*accent, 165), width=max(2, round(w*0.007)))
        draw.line((cx-round(core_w*0.35), core_y, cx-round(core_w*0.15), core_y-round(h*0.055), cx+round(core_w*0.03), core_y+round(h*0.07), cx+round(core_w*0.19), core_y-round(h*0.025), cx+round(core_w*0.36), core_y), fill=(*accent, 210), width=max(2, round(w*0.007)), joint='curve')
        draw.line((cx+round(core_w*0.36), core_y, cx+core_w, core_y), fill=(*accent, 165), width=max(2, round(w*0.007)))
        canvas.alpha_composite(layer)

    def render(
        self,
        composition: EventEditorialComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        headline: str,
        kicker: str,
        anchor_kind: EventAnchorKind,
        accent_hex: str,
        font_path: str,
        seed_key: str = 'event-editorial',
        context_asset: VerifiedContextAsset | None = None,
    ) -> EventEditorialStudyReceipt:
        if not isinstance(composition, EventEditorialComposition):
            raise TypeError('composition must be EventEditorialComposition')
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError('profile must be PlatformImageProfile')
        if not isinstance(anchor_kind, EventAnchorKind):
            raise TypeError('anchor_kind must be EventAnchorKind')
        if not headline.strip() or not kicker.strip():
            raise ValueError('headline and kicker are required')
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if context_asset is not None and not isinstance(context_asset, VerifiedContextAsset):
            raise TypeError('context_asset must be VerifiedContextAsset or None')

        accent = self._rgb(accent_hex)
        context_receipt = None
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if context_asset is None:
            surface = PremiumEditorialSurface()
            canvas = surface.render(
                size=(profile.width, profile.height),
                style=EditorialSurfaceStyle(
                    base_top=(7, 13, 24), base_bottom=(2, 6, 12), accent=accent,
                    secondary_accent=(36, 91, 126), glow_strength=94,
                    grain_strength=12, vignette_strength=112,
                ),
                seed_key=seed_key,
            )
            atmosphere_contract = PremiumEditorialSurface.CONTRACT
        else:
            context_base = target.with_name(target.stem + '.context.png')
            context_receipt = VerifiedContextSurfaceRenderer().render(
                asset=context_asset,
                output_path=str(context_base),
                canvas_size=(profile.width, profile.height),
                accent_hex=accent_hex,
                focal_x_ratio=0.43,
                focal_y_ratio=0.50,
            )
            with Image.open(context_base) as loaded:
                canvas = self._finish_photographic_context(loaded.convert('RGBA'), accent=accent)
            context_base.unlink(missing_ok=True)
            atmosphere_contract = context_receipt.contract

        self._draw_anchor(canvas, self._box(composition.anchor_box, profile), accent=accent, kind=anchor_kind)
        draw = ImageDraw.Draw(canvas, 'RGBA')

        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = self._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.59))
        hb = draw.textbbox((0, 0), headline, font=headline_font)
        tx = profile.width/2 - (hb[2]-hb[0])/2
        # restrained text shadow makes the type feel embedded in the scene
        draw.text((tx+2, hy0+3), headline, font=headline_font, fill=(0, 0, 0, 150))
        draw.text((tx, hy0), headline, font=headline_font, fill=(242, 247, 250, 255))

        ax0, ay0, ax1, _ = self._box(composition.anchor_box, profile)
        kicker_font = self._fit_font(draw, kicker, font_path, round((ax1-ax0)*0.58), round(profile.height*0.05), round(profile.height*0.025))
        kb = draw.textbbox((0, 0), kicker, font=kicker_font)
        kx = profile.width/2-(kb[2]-kb[0])/2
        ky = ay0-round(profile.height*0.055)
        draw.text((kx+1, ky+2), kicker, font=kicker_font, fill=(0, 0, 0, 135))
        draw.text((kx, ky), kicker, font=kicker_font, fill=(180, 199, 214, 245))

        prebrand = target.with_name(target.stem + '.prebrand.png')
        canvas.convert('RGB').save(prebrand, format='PNG')
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=accent_hex,
        )
        prebrand.unlink(missing_ok=True)
        return EventEditorialStudyReceipt(
            output_path=str(target), output_sha256=self._sha(target), width=profile.width, height=profile.height,
            anchor_kind=anchor_kind.value, single_anchor_used=True, person_used=False,
            full_pitch_used=False, decorative_stats_used=False, brand_zone=brand.zone,
            brand_width=brand.width, brand_height=brand.height,
            atmosphere_contract=atmosphere_contract,
            photographic_context_used=context_receipt is not None,
            context_contract=context_receipt.contract if context_receipt else None,
            context_source_reference=context_receipt.source_reference if context_receipt else None,
        )

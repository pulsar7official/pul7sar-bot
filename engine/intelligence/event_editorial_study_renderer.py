"""Premium deterministic Event Editorial renderer for PUL7SAR Phase 18.

A verified photographic context, when available, is allowed to be the visual
anchor itself. The renderer must not stack a decorative portal/card over real
photographic texture. When no verified context exists, one minimal code-owned
symbolic anchor is permitted. Facts, copy, identity and PUL7SAR remain exact.
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
from engine.intelligence.verified_context_surface import VerifiedContextAsset, VerifiedContextSurfaceRenderer


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
        width, height = canvas.size
        image = canvas.convert('RGBA')
        shade = Image.new('RGBA', image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade, 'RGBA')
        for i in range(18):
            x = min(width, round(width * (0.43 + i * 0.035)))
            alpha = min(165, 28 + i * 8)
            sd.rectangle((x, 0, width, height), fill=(2, 6, 12, alpha))
        shade = shade.filter(ImageFilter.GaussianBlur(max(18, width // 42)))
        image = Image.alpha_composite(image, shade)
        optics = Image.new('RGBA', image.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(optics, 'RGBA')
        od.ellipse((-round(width*.18), round(height*.18), round(width*.42), round(height*.78)), fill=(*accent, 34))
        od.ellipse((round(width*.50), -round(height*.10), round(width*1.05), round(height*.45)), fill=(220, 237, 248, 15))
        optics = optics.filter(ImageFilter.GaussianBlur(max(26, width // 20)))
        return Image.alpha_composite(image, optics)

    @staticmethod
    def _draw_anchor(canvas: Image.Image, box: tuple[int, int, int, int], *, accent: tuple[int, int, int], kind: EventAnchorKind) -> None:
        # Legacy study hook. Runtime v2 overrides this with a pulse-free aperture.
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            raise ValueError('anchor box must be positive')
        layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, 'RGBA')
        cx, cy = x0 + w // 2, y0 + h // 2
        radius = min(w, h) * 0.22
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=(*accent, 66), width=max(1, round(w*0.003)))
        layer = layer.filter(ImageFilter.GaussianBlur(max(3, round(w*0.008))))
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
            self._draw_anchor(canvas, self._box(composition.anchor_box, profile), accent=accent, kind=anchor_kind)
            single_anchor_used = True
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
            # The verified photograph is the visual anchor. Do not place a graphic
            # portal, card, waveform or symbol over it just to fill the composition.
            single_anchor_used = False

        draw = ImageDraw.Draw(canvas, 'RGBA')
        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = self._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.59))
        hb = draw.textbbox((0, 0), headline, font=headline_font)
        tx = profile.width/2 - (hb[2]-hb[0])/2
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
            anchor_kind=anchor_kind.value, single_anchor_used=single_anchor_used, person_used=False,
            full_pitch_used=False, decorative_stats_used=False, brand_zone=brand.zone,
            brand_width=brand.width, brand_height=brand.height,
            atmosphere_contract=atmosphere_contract,
            photographic_context_used=context_receipt is not None,
            context_contract=context_receipt.contract if context_receipt else None,
            context_source_reference=context_receipt.source_reference if context_receipt else None,
        )

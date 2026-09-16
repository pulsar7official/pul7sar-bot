"""Verified detail-led editorial renderer for story-specific premium concepts.

This renderer is for cases where a real, rights-cleared object/detail photograph is
more truthful than fabricating a person: signing object, shirt detail, document,
equipment, press object or another verified story detail. The source photograph is
primary; text and PUL7SAR remain deterministic overlays.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.verified_story_moment import (
    StoryMomentKind,
    VerifiedStoryMomentAsset,
    VerifiedStoryMomentGate,
)


class DetailEditorialMode(str, Enum):
    SYMBOLIC_SIGNING = "symbolic_signing"
    VERIFIED_EVIDENCE = "verified_evidence"


@dataclass(frozen=True)
class VerifiedDetailEditorialReceipt:
    output_path: str
    output_sha256: str
    mode: str
    source_asset_id: str
    source_sha256: str
    source_reference: str
    source_moment_kind: str
    photograph_is_primary: bool
    person_fabricated: bool
    decorative_pulse_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-verified-detail-editorial-renderer-v1"

    def __post_init__(self) -> None:
        if not self.photograph_is_primary:
            raise ValueError("VERIFIED_DETAIL_PHOTOGRAPH_MUST_BE_PRIMARY")
        if self.person_fabricated or self.decorative_pulse_used:
            raise ValueError("VERIFIED_DETAIL_RENDERER_MAY_NOT_FABRICATE_PERSON_OR_PULSE")
        if self.generator_used or self.network_used or not self.study_only or self.publication_ready:
            raise ValueError("VERIFIED_DETAIL_STUDY_CONTRACT_INVALID")


class VerifiedDetailEditorialRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith('#'):
            raise ValueError('accent must be #RRGGBB')
        return tuple(int(text[i:i+2], 16) for i in (1,3,5))

    @staticmethod
    def _fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_width: int, max_height: int, start: int) -> ImageFont.FreeTypeFont:
        size = max(14, start)
        while size >= 14:
            font = ImageFont.truetype(font_path, size=size)
            box = draw.textbbox((0,0), text, font=font)
            if box[2]-box[0] <= max_width and box[3]-box[1] <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=14)

    @staticmethod
    def _cover(source: Image.Image, width: int, height: int, focal_x: float, focal_y: float) -> Image.Image:
        rgb = source.convert('RGB')
        scale = max(width/rgb.width, height/rgb.height)
        resized = rgb.resize((max(width,round(rgb.width*scale)), max(height,round(rgb.height*scale))), Image.Resampling.LANCZOS)
        ox, oy = resized.width-width, resized.height-height
        left = max(0,min(ox,round(ox*focal_x)))
        top = max(0,min(oy,round(oy*focal_y)))
        return resized.crop((left,top,left+width,top+height)).convert('RGBA')

    @classmethod
    def _grade(cls, image: Image.Image, *, accent: tuple[int,int,int]) -> Image.Image:
        image = ImageEnhance.Color(image.convert('RGB')).enhance(0.78)
        image = ImageEnhance.Contrast(image).enhance(1.14)
        image = ImageEnhance.Brightness(image).enhance(0.79).convert('RGBA')
        width,height = image.size
        lane = Image.new('RGBA', image.size, (0,0,0,0))
        ld = ImageDraw.Draw(lane,'RGBA')
        # Organic left-to-right darkening for copy, not a rectangular card.
        for x in range(width):
            t = x/max(1,width-1)
            alpha = round(150 * max(0.0, 1.0 - t/0.62) ** 2.2)
            if alpha:
                ld.line((x,0,x,height), fill=(1,5,11,alpha))
        image.alpha_composite(lane)
        glow = Image.new('RGBA',image.size,(0,0,0,0))
        gd=ImageDraw.Draw(glow,'RGBA')
        r=round(max(width,height)*0.28)
        gd.ellipse((width-r,round(height*.48)-r,width+r,round(height*.48)+r),fill=(*accent,40))
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(max(28,round(width*.07)))))
        return image

    def render(
        self,
        *,
        profile: PlatformImageProfile,
        adaptive_brand: AdaptiveBrandPlacement,
        output_path: str,
        asset: VerifiedStoryMomentAsset,
        mode: DetailEditorialMode,
        headline: str,
        kicker: str,
        accent_hex: str,
        font_path: str,
        focal_x_ratio: float = 0.58,
        focal_y_ratio: float = 0.48,
    ) -> VerifiedDetailEditorialReceipt:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError('profile must be PlatformImageProfile')
        if not isinstance(adaptive_brand, AdaptiveBrandPlacement):
            raise TypeError('adaptive_brand must be AdaptiveBrandPlacement')
        if not isinstance(asset, VerifiedStoryMomentAsset):
            raise TypeError('asset must be VerifiedStoryMomentAsset')
        if not isinstance(mode, DetailEditorialMode):
            raise TypeError('mode must be DetailEditorialMode')
        if not headline.strip() or not kicker.strip():
            raise ValueError('headline and kicker are required')
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if asset.contains_people:
            raise ValueError('DETAIL_EDITORIAL_ASSET_MUST_NOT_CONTAIN_PEOPLE')
        allowed = {
            DetailEditorialMode.SYMBOLIC_SIGNING: {StoryMomentKind.ARRIVAL, StoryMomentKind.VERIFIED_OBJECT_DETAIL, StoryMomentKind.PRESS_MOMENT},
            DetailEditorialMode.VERIFIED_EVIDENCE: {StoryMomentKind.VERIFIED_OBJECT_DETAIL, StoryMomentKind.PRESS_MOMENT},
        }[mode]
        if asset.moment_kind not in allowed:
            raise ValueError('DETAIL_EDITORIAL_MOMENT_KIND_NOT_ALLOWED_FOR_MODE')
        admission = VerifiedStoryMomentGate().admit(asset)
        accent=self._rgb(accent_hex)
        with Image.open(asset.path) as raw:
            canvas=self._cover(raw,profile.width,profile.height,focal_x_ratio,focal_y_ratio)
        canvas=self._grade(canvas,accent=accent)
        draw=ImageDraw.Draw(canvas,'RGBA')
        max_w=round(profile.width*.53)
        headline_font=self._fit_font(draw,headline,font_path,max_w,round(profile.height*.13),round(profile.height*.075))
        kicker_font=self._fit_font(draw,kicker,font_path,max_w,round(profile.height*.05),round(profile.height*.027))
        x=round(profile.width*.075); y=round(profile.height*.17)
        draw.text((x+2,y+3),headline,font=headline_font,fill=(0,0,0,145))
        draw.text((x,y),headline,font=headline_font,fill=(242,247,250,255))
        hb=draw.textbbox((x,y),headline,font=headline_font)
        ky=hb[3]+round(profile.height*.018)
        draw.text((x,ky),kicker,font=kicker_font,fill=(183,201,216,240))
        target=Path(output_path); target.parent.mkdir(parents=True,exist_ok=True)
        pre=target.with_name(target.stem+'.prebrand.png')
        canvas.convert('RGB').save(pre,format='PNG')
        brand=AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(pre),output_path=str(target),adaptive=adaptive_brand,profile=profile,accent_hex=accent_hex,
        )
        pre.unlink(missing_ok=True)
        return VerifiedDetailEditorialReceipt(
            output_path=str(target),output_sha256=self._sha(target),mode=mode.value,
            source_asset_id=admission.asset_id,source_sha256=admission.source_sha256,
            source_reference=admission.source_reference,source_moment_kind=admission.moment_kind,
            photograph_is_primary=True,person_fabricated=False,decorative_pulse_used=False,
            brand_zone=brand.zone,brand_width=brand.width,brand_height=brand.height,
        )

"""Moment-led Result renderer for premium PUL7SAR coverage.

When a verified decisive-action or celebration photograph exists, the photograph
is the story hero. The exact score and club text become restrained factual layers
instead of forcing every result into a scoreboard/monument composition.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposition
from engine.intelligence.verified_story_moment import (
    StoryMomentKind,
    VerifiedStoryMomentAsset,
    VerifiedStoryMomentGate,
)


@dataclass(frozen=True)
class MomentLedResultReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    moment_asset_id: str
    moment_kind: str
    source_sha256: str
    source_reference: str
    verified_identity_ids: tuple[str, ...]
    score_text: str
    home_name: str
    away_name: str
    score_is_secondary: bool
    photograph_is_primary: bool
    club_identity_scale_equal: bool
    loser_treatment: str
    brand_zone: str
    brand_width: int
    brand_height: int
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-moment-led-result-renderer-v1"

    def __post_init__(self) -> None:
        if self.moment_kind not in {StoryMomentKind.DECISIVE_ACTION.value, StoryMomentKind.CELEBRATION.value}:
            raise ValueError("MOMENT_LED_RESULT_REQUIRES_ACTION_OR_CELEBRATION")
        if not self.score_is_secondary or not self.photograph_is_primary:
            raise ValueError("MOMENT_LED_RESULT_HIERARCHY_INVALID")
        if not self.club_identity_scale_equal:
            raise ValueError("RESULT_CLUB_IDENTITY_SCALE_MUST_REMAIN_EQUAL")
        if self.loser_treatment != "neutral_no_humiliation":
            raise ValueError("RESULT_LOSER_TREATMENT_MUST_REMAIN_NEUTRAL")
        if self.generator_used or self.network_used or self.publication_ready or not self.study_only:
            raise ValueError("MOMENT_LED_STUDY_CONTRACT_INVALID")


class MomentLedResultRenderer:
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
    def _fit_font(draw: ImageDraw.ImageDraw, text: str, font_path: str, max_width: int, max_height: int, start: int) -> ImageFont.FreeTypeFont:
        size = max(14, start)
        while size >= 14:
            font = ImageFont.truetype(font_path, size=size)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2]-box[0] <= max_width and box[3]-box[1] <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=14)

    @staticmethod
    def _cover_crop(source: Image.Image, width: int, height: int, focal_x: float, focal_y: float) -> Image.Image:
        rgb = source.convert("RGB")
        scale = max(width / rgb.width, height / rgb.height)
        resized = rgb.resize((max(width, round(rgb.width*scale)), max(height, round(rgb.height*scale))), Image.Resampling.LANCZOS)
        overflow_x = resized.width - width
        overflow_y = resized.height - height
        left = max(0, min(overflow_x, round(overflow_x*focal_x)))
        top = max(0, min(overflow_y, round(overflow_y*focal_y)))
        return resized.crop((left, top, left+width, top+height))

    @classmethod
    def _grade(cls, image: Image.Image, *, home_accent: tuple[int, int, int], away_accent: tuple[int, int, int]) -> Image.Image:
        image = ImageEnhance.Color(image).enhance(0.86)
        image = ImageEnhance.Contrast(image).enhance(1.12)
        image = ImageEnhance.Brightness(image).enhance(0.82).convert("RGBA")
        width, height = image.size

        # Preserve the photographic moment. The overlays create readable edge lanes
        # without turning the centre into a panel/card.
        falloff = Image.new("RGBA", image.size, (0,0,0,0))
        fd = ImageDraw.Draw(falloff, "RGBA")
        for y in range(round(height*0.58), height):
            t = (y-height*0.58)/(height*0.42)
            fd.line((0,y,width,y), fill=(2,6,12,round(20+165*t*t)))
        image.alpha_composite(falloff)

        # Equal restrained club-light contamination on opposite edges.
        glow = Image.new("RGBA", image.size, (0,0,0,0))
        gd = ImageDraw.Draw(glow, "RGBA")
        r = round(max(width,height)*0.30)
        cy = round(height*0.63)
        gd.ellipse((-r,cy-r,r,cy+r), fill=(*home_accent,42))
        gd.ellipse((width-r,cy-r,width+r,cy+r), fill=(*away_accent,38))
        glow = glow.filter(ImageFilter.GaussianBlur(max(28,round(width*0.07))))
        image.alpha_composite(glow)
        return image

    @staticmethod
    def _centered(draw: ImageDraw.ImageDraw, text: str, font, x: float, y: float, fill) -> None:
        box = draw.textbbox((0,0), text, font=font)
        draw.text((x-(box[2]-box[0])/2-box[0], y-(box[3]-box[1])/2-box[1]), text, font=font, fill=fill)

    def render(
        self,
        composition: ResultStatementComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        moment_asset: VerifiedStoryMomentAsset,
        home_name: str,
        away_name: str,
        home_score: int,
        away_score: int,
        home_accent_hex: str,
        away_accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
        focal_x_ratio: float = 0.50,
        focal_y_ratio: float = 0.42,
    ) -> MomentLedResultReceipt:
        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not isinstance(moment_asset, VerifiedStoryMomentAsset):
            raise TypeError("moment_asset must be VerifiedStoryMomentAsset")
        if moment_asset.moment_kind not in {StoryMomentKind.DECISIVE_ACTION, StoryMomentKind.CELEBRATION}:
            raise ValueError("MOMENT_LED_RESULT_REQUIRES_ACTION_OR_CELEBRATION")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if home_score < 0 or away_score < 0:
            raise ValueError("scores must be non-negative")
        if not home_name.strip() or not away_name.strip():
            raise ValueError("club names are required")
        if not 0.0 <= focal_x_ratio <= 1.0 or not 0.0 <= focal_y_ratio <= 1.0:
            raise ValueError("focal ratios must be within 0..1")

        admission = VerifiedStoryMomentGate().admit(moment_asset)
        source = Path(moment_asset.path)
        with Image.open(source) as raw:
            base = self._cover_crop(raw, profile.width, profile.height, focal_x_ratio, focal_y_ratio)
        home_accent = self._rgb(home_accent_hex)
        away_accent = self._rgb(away_accent_hex)
        canvas = self._grade(base, home_accent=home_accent, away_accent=away_accent)
        draw = ImageDraw.Draw(canvas, "RGBA")

        score_text = f"{home_score}  –  {away_score}"
        score_font = self._fit_font(draw, score_text, font_path, round(profile.width*0.32), round(profile.height*0.065), round(profile.height*0.055))
        name_font = self._fit_font(draw, max((home_name,away_name), key=len), font_path, round(profile.width*0.28), round(profile.height*0.04), round(profile.height*0.025))

        # Score is factual but deliberately subordinate to the photographic moment.
        score_y = round(profile.height*0.115)
        self._centered(draw, score_text, score_font, profile.width/2+2, score_y+3, (0,0,0,145))
        self._centered(draw, score_text, score_font, profile.width/2, score_y, (239,244,248,242))

        # Equal club naming lanes at the lower edge. No winner badge, loser fade or
        # humiliating asymmetry: the photograph carries emotion, facts remain neutral.
        name_y = round(profile.height*0.835)
        self._centered(draw, home_name.upper(), name_font, profile.width*0.27, name_y, (235,241,246,235))
        self._centered(draw, away_name.upper(), name_font, profile.width*0.73, name_y, (235,241,246,235))
        dot_r = max(3, round(profile.width*0.005))
        for cx, accent in ((round(profile.width*0.27), home_accent), (round(profile.width*0.73), away_accent)):
            draw.ellipse((cx-dot_r, name_y+round(profile.height*0.035)-dot_r, cx+dot_r, name_y+round(profile.height*0.035)+dot_r), fill=(*accent,220))

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem+".prebrand.png")
        canvas.convert("RGB").save(prebrand, format="PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        prebrand.unlink(missing_ok=True)

        return MomentLedResultReceipt(
            output_path=str(target), output_sha256=self._sha(target), width=profile.width, height=profile.height,
            moment_asset_id=admission.asset_id, moment_kind=admission.moment_kind,
            source_sha256=admission.source_sha256, source_reference=admission.source_reference,
            verified_identity_ids=admission.verified_identity_ids, score_text=score_text,
            home_name=home_name, away_name=away_name, score_is_secondary=True,
            photograph_is_primary=True, club_identity_scale_equal=True,
            loser_treatment="neutral_no_humiliation", brand_zone=brand.zone,
            brand_width=brand.width, brand_height=brand.height,
        )

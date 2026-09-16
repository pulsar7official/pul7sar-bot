"""Asset-first Verified Subject News study renderer for PUL7SAR Phase 18.

The renderer owns atmosphere, deterministic copy and adaptive PUL7SAR branding.
The real subject is owned exclusively by VerifiedSubjectCompositor, which requires
a VERIFIED depiction-allowed IdentityPlan plus checksum-locked source pixels.
No pose, expression, injury state or identity is generated or redrawn here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.models import IdentityPlan
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.verified_subject_compositor import (
    SubjectPlacement,
    VerifiedSubjectAsset,
    VerifiedSubjectCompositor,
)
from engine.intelligence.verified_subject_news_composition import VerifiedSubjectNewsComposition


@dataclass(frozen=True)
class VerifiedSubjectNewsStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    subject_asset_id: str
    subject_sha256: str
    subject_entity_name: str
    identity_confidence: float
    identity_verified: bool
    subject_placeholder_used: bool
    fabricated_pose_used: bool
    fabricated_expression_used: bool
    fantasy_medical_scene_used: bool
    subject_text_overlap_used: bool
    brand_subject_overlap_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    brand_overlay_contract: str
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-verified-subject-news-study-renderer-v1-asset-first"


class VerifiedSubjectNewsStudyRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _box(box: NormalizedBox, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            round(box.x * profile.width),
            round(box.y * profile.height),
            round((box.x + box.width) * profile.width),
            round((box.y + box.height) * profile.height),
        )

    @staticmethod
    def _intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    @staticmethod
    def _fit_font(draw, text: str, font_path: str, max_width: int, max_height: int, start: int):
        from PIL import ImageFont

        size = max(10, start)
        while size > 10:
            font = ImageFont.truetype(font_path, size=size)
            left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font, spacing=max(2, size // 7))
            if right - left <= max_width and bottom - top <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=10)

    @staticmethod
    def _wrap(draw, text: str, font_path: str, max_width: int, max_height: int, start: int, max_lines: int):
        """Deterministic whitespace wrap; production Arabic stays owned by typography pipeline."""
        words = text.strip().split()
        if not words:
            raise ValueError("text must be non-empty")
        from PIL import ImageFont

        size = max(10, start)
        while size > 10:
            font = ImageFont.truetype(font_path, size=size)
            lines: list[str] = []
            current = ""
            for word in words:
                candidate = word if not current else current + " " + word
                box = draw.textbbox((0, 0), candidate, font=font)
                if box[2] - box[0] <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            if len(lines) <= max_lines:
                spacing = max(2, size // 6)
                bbox = draw.multiline_textbbox((0, 0), "\n".join(lines), font=font, spacing=spacing)
                if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
                    return "\n".join(lines), font, spacing
            size -= 2
        font = ImageFont.truetype(font_path, size=10)
        return text, font, 2

    @classmethod
    def _build_base(cls, *, profile: PlatformImageProfile, accent: tuple[int, int, int], output: Path) -> None:
        from PIL import Image, ImageDraw, ImageFilter

        image = Image.new("RGBA", (profile.width, profile.height), (5, 11, 18, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        for y in range(profile.height):
            t = y / max(1, profile.height - 1)
            draw.line(
                (0, y, profile.width, y),
                fill=(round(10 - 4*t), round(18 - 5*t), round(28 - 8*t), 255),
            )

        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse(
            (-round(profile.width * 0.23), round(profile.height * 0.08), round(profile.width * 0.63), round(profile.height * 0.88)),
            fill=(*accent, 70),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(max(28, round(profile.width * 0.08))))
        image.alpha_composite(glow)

        draw = ImageDraw.Draw(image, "RGBA")
        # Editorial depth only; no fabricated medical symbols or injury imagery.
        for ratio in (0.18, 0.34, 0.50, 0.66):
            x = round(profile.width * ratio)
            draw.line((x, round(profile.height * 0.12), x + round(profile.width * 0.08), round(profile.height * 0.88)), fill=(235, 242, 247, 10), width=1)
        draw.line(
            (round(profile.width * 0.54), round(profile.height * 0.16), round(profile.width * 0.54), round(profile.height * 0.70)),
            fill=(235, 242, 247, 26),
            width=1,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output, format="PNG")

    def render(
        self,
        composition: VerifiedSubjectNewsComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        subject: VerifiedSubjectAsset,
        identity: IdentityPlan,
        headline: str,
        context_text: str,
        accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
    ) -> VerifiedSubjectNewsStudyReceipt:
        from PIL import Image, ImageDraw

        if not isinstance(composition, VerifiedSubjectNewsComposition):
            raise TypeError("composition must be VerifiedSubjectNewsComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not headline.strip() or not context_text.strip():
            raise ValueError("headline and context_text are required")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        accent = self._rgb(accent_hex)

        subject_box = self._box(composition.subject_box, profile)
        headline_box = self._box(composition.headline_box, profile)
        context_box = self._box(composition.context_box, profile)
        if self._intersects(subject_box, headline_box) or self._intersects(subject_box, context_box):
            raise ValueError("VERIFIED_SUBJECT_TEXT_ZONE_OVERLAP")

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        base = target.with_name(target.stem + ".base.png")
        subject_stage = target.with_name(target.stem + ".subject.png")
        text_stage = target.with_name(target.stem + ".text.png")
        self._build_base(profile=profile, accent=accent, output=base)

        sx0, sy0, sx1, sy1 = subject_box
        subject_receipt = VerifiedSubjectCompositor().compose(
            base_path=str(base),
            output_path=str(subject_stage),
            subject=subject,
            identity=identity,
            placement=SubjectPlacement(x=sx0, y=sy0, width=sx1-sx0, height=sy1-sy0),
            accent_hex=accent_hex,
        )

        with Image.open(subject_stage) as raw:
            image = raw.convert("RGBA")
        draw = ImageDraw.Draw(image, "RGBA")

        hx0, hy0, hx1, hy1 = headline_box
        wrapped, headline_font, headline_spacing = self._wrap(
            draw,
            headline,
            font_path,
            hx1-hx0,
            hy1-hy0,
            round((hy1-hy0) * 0.37),
            max_lines=3,
        )
        draw.multiline_text(
            (hx0, hy0),
            wrapped,
            font=headline_font,
            spacing=headline_spacing,
            fill=(242, 246, 249, 255),
        )
        rule_y = hy1 + max(5, round(profile.height * 0.009))
        draw.rounded_rectangle(
            (hx0, rule_y, hx0 + round((hx1-hx0)*0.34), rule_y + 3),
            radius=2,
            fill=(*accent, 220),
        )

        cx0, cy0, cx1, cy1 = context_box
        context_wrapped, context_font, context_spacing = self._wrap(
            draw,
            context_text,
            font_path,
            cx1-cx0,
            cy1-cy0,
            round((cy1-cy0) * 0.26),
            max_lines=3,
        )
        draw.multiline_text(
            (cx0, cy0),
            context_wrapped,
            font=context_font,
            spacing=context_spacing,
            fill=(185, 198, 209, 235),
        )
        image.convert("RGB").save(text_stage, format="PNG")

        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(text_stage),
            output_path=str(target),
            adaptive=composition.brand,
            profile=profile,
            accent_hex=brand_accent_hex,
        )

        brand_box = (brand.x, brand.y, brand.x + brand.width, brand.y + brand.height)
        if self._intersects(brand_box, subject_box):
            raise ValueError("VERIFIED_SUBJECT_BRAND_ZONE_OVERLAP")

        base.unlink(missing_ok=True)
        subject_stage.unlink(missing_ok=True)
        text_stage.unlink(missing_ok=True)

        return VerifiedSubjectNewsStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            width=profile.width,
            height=profile.height,
            subject_asset_id=subject_receipt.subject_asset_id,
            subject_sha256=subject_receipt.subject_sha256,
            subject_entity_name=subject_receipt.entity_name,
            identity_confidence=subject_receipt.identity_confidence,
            identity_verified=subject_receipt.identity_verified,
            subject_placeholder_used=subject_receipt.subject_placeholder_used,
            fabricated_pose_used=False,
            fabricated_expression_used=False,
            fantasy_medical_scene_used=False,
            subject_text_overlap_used=False,
            brand_subject_overlap_used=False,
            brand_zone=brand.zone,
            brand_width=brand.width,
            brand_height=brand.height,
            brand_overlay_contract=brand.contract,
        )

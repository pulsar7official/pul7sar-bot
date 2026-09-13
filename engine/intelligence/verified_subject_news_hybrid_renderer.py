"""Production-shaped verified-subject hybrid renderer.

Layer order is immutable: semantically admitted cinematic base -> checksum-locked
verified subject pixels -> deterministic editorial copy -> adaptive PUL7SAR brand.
The image model never owns recognizable identity, pose, expression or exact copy.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmission
from engine.intelligence.models import IdentityPlan
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.verified_subject_compositor import SubjectPlacement, VerifiedSubjectAsset, VerifiedSubjectCompositor
from engine.intelligence.verified_subject_news_composition import VerifiedSubjectNewsComposition
from engine.intelligence.verified_subject_news_study_renderer import VerifiedSubjectNewsStudyRenderer


@dataclass(frozen=True)
class VerifiedSubjectNewsHybridReceipt:
    output_path: str
    output_sha256: str
    base_scene_sha256: str
    base_quality_tier: str
    subject_asset_id: str
    subject_sha256: str
    subject_entity_name: str
    identity_confidence: float
    generator_owns_identity: bool
    generator_owns_readable_text: bool
    generator_owns_brand: bool
    fabricated_pose_used: bool
    fabricated_expression_used: bool
    subject_text_overlap_used: bool
    brand_subject_overlap_used: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    publication_ready: bool = False
    contract: str = "pul7sar-verified-subject-news-hybrid-renderer-v1-cinematic-asset-first"

    def __post_init__(self) -> None:
        if self.generator_owns_identity or self.generator_owns_readable_text or self.generator_owns_brand:
            raise ValueError("VERIFIED_SUBJECT_HYBRID_PROTECTED_LAYER_OWNERSHIP_VIOLATION")
        if self.fabricated_pose_used or self.fabricated_expression_used:
            raise ValueError("VERIFIED_SUBJECT_HYBRID_MAY_NOT_FABRICATE_SUBJECT_STATE")
        if self.subject_text_overlap_used or self.brand_subject_overlap_used:
            raise ValueError("VERIFIED_SUBJECT_HYBRID_ZONE_COLLISION")
        if self.publication_ready:
            raise ValueError("HYBRID_RENDERER_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class VerifiedSubjectNewsHybridRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _soft_copy_field(image: Image.Image, box: tuple[int, int, int, int]) -> None:
        x0, y0, x1, y1 = box
        veil = Image.new("RGBA", image.size, (0,0,0,0))
        draw = ImageDraw.Draw(veil, "RGBA")
        px, py = round(image.width*0.035), round(image.height*0.025)
        draw.rounded_rectangle((max(0,x0-px), max(0,y0-py), min(image.width,x1+px), min(image.height,y1+py)), radius=max(20,round(image.width*0.035)), fill=(2,7,12,96))
        veil = veil.filter(ImageFilter.GaussianBlur(max(14, round(image.width*0.028))))
        image.alpha_composite(veil)

    def render(
        self,
        composition: VerifiedSubjectNewsComposition,
        *,
        admission: BaseSceneCompositionAdmission,
        profile: PlatformImageProfile,
        output_path: str,
        subject: VerifiedSubjectAsset,
        identity: IdentityPlan,
        headline: str,
        context_text: str,
        accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
    ) -> VerifiedSubjectNewsHybridReceipt:
        if not isinstance(composition, VerifiedSubjectNewsComposition):
            raise TypeError("composition must be VerifiedSubjectNewsComposition")
        if not isinstance(admission, BaseSceneCompositionAdmission):
            raise TypeError("admission must be BaseSceneCompositionAdmission")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not headline.strip() or not context_text.strip():
            raise ValueError("headline and context_text are required")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        admission.assert_bytes_unchanged()
        if (admission.provenance.width, admission.provenance.height) != (profile.width, profile.height):
            raise ValueError("admitted base scene does not match platform profile")

        helper = VerifiedSubjectNewsStudyRenderer
        subject_box = helper._box(composition.subject_box, profile)
        headline_box = helper._box(composition.headline_box, profile)
        context_box = helper._box(composition.context_box, profile)
        if helper._intersects(subject_box, headline_box) or helper._intersects(subject_box, context_box):
            raise ValueError("VERIFIED_SUBJECT_TEXT_ZONE_OVERLAP")

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        subject_stage = target.with_name(target.stem + ".subject.png")
        text_stage = target.with_name(target.stem + ".text.png")
        sx0, sy0, sx1, sy1 = subject_box
        subject_receipt = VerifiedSubjectCompositor().compose(
            base_path=admission.png_path,
            output_path=str(subject_stage),
            subject=subject,
            identity=identity,
            placement=SubjectPlacement(sx0, sy0, sx1-sx0, sy1-sy0),
            accent_hex=accent_hex,
        )

        with Image.open(subject_stage) as raw:
            image = raw.convert("RGBA")
        self._soft_copy_field(image, headline_box)
        draw = ImageDraw.Draw(image, "RGBA")
        hx0, hy0, hx1, hy1 = headline_box
        wrapped, headline_font, spacing = helper._wrap(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.37), 3)
        draw.multiline_text((hx0, hy0), wrapped, font=headline_font, spacing=spacing, fill=(244,247,250,255))
        accent = helper._rgb(accent_hex)
        rule_y = hy1 + max(5, round(profile.height*0.009))
        draw.rounded_rectangle((hx0, rule_y, hx0+round((hx1-hx0)*0.34), rule_y+3), radius=2, fill=(*accent,220))

        cx0, cy0, cx1, cy1 = context_box
        context_wrapped, context_font, context_spacing = helper._wrap(draw, context_text, font_path, cx1-cx0, cy1-cy0, round((cy1-cy0)*0.26), 3)
        draw.multiline_text((cx0,cy0), context_wrapped, font=context_font, spacing=context_spacing, fill=(188,201,211,240))
        image.convert("RGB").save(text_stage, format="PNG")

        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(text_stage), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        brand_box = (brand.x, brand.y, brand.x+brand.width, brand.y+brand.height)
        if helper._intersects(brand_box, subject_box):
            raise ValueError("VERIFIED_SUBJECT_BRAND_ZONE_OVERLAP")
        subject_stage.unlink(missing_ok=True)
        text_stage.unlink(missing_ok=True)
        return VerifiedSubjectNewsHybridReceipt(
            output_path=str(target), output_sha256=self._sha(target),
            base_scene_sha256=admission.png_sha256, base_quality_tier=admission.quality_tier.value,
            subject_asset_id=subject_receipt.subject_asset_id, subject_sha256=subject_receipt.subject_sha256,
            subject_entity_name=subject_receipt.entity_name, identity_confidence=subject_receipt.identity_confidence,
            generator_owns_identity=False, generator_owns_readable_text=False, generator_owns_brand=False,
            fabricated_pose_used=False, fabricated_expression_used=False,
            subject_text_overlap_used=False, brand_subject_overlap_used=False,
            brand_zone=brand.zone, brand_width=brand.width, brand_height=brand.height,
        )

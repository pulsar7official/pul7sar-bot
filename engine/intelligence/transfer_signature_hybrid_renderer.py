"""Production-shaped cinematic Transfer Signature hybrid renderer for PUL7SAR."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.assets import AssetRole
from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmission
from engine.intelligence.exact_raster_asset import ExactRasterAsset, ExactRasterAssetCompositor
from engine.intelligence.models import IdentityPlan
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.transfer_signature_composition import TransferSignatureComposition
from engine.intelligence.verified_subject_compositor import SubjectPlacement, VerifiedSubjectAsset, VerifiedSubjectCompositor
from engine.intelligence.verified_subject_news_study_renderer import VerifiedSubjectNewsStudyRenderer


@dataclass(frozen=True)
class TransferSignatureHybridReceipt:
    output_path: str
    output_sha256: str
    base_scene_sha256: str
    base_quality_tier: str
    hero_asset_id: str
    hero_sha256: str
    hero_entity_name: str
    identity_confidence: float
    destination_crest_sha256: str
    generator_owns_identity: bool
    generator_owns_crest: bool
    generator_owns_readable_text: bool
    generator_owns_brand: bool
    full_pitch_used: bool
    hero_text_overlap: bool
    hero_brand_overlap: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    publication_ready: bool = False
    contract: str = "pul7sar-transfer-signature-hybrid-renderer-v1-cinematic-exact"

    def __post_init__(self) -> None:
        if any((self.generator_owns_identity, self.generator_owns_crest, self.generator_owns_readable_text, self.generator_owns_brand)):
            raise ValueError("TRANSFER_HYBRID_PROTECTED_LAYER_OWNERSHIP_VIOLATION")
        if self.full_pitch_used:
            raise ValueError("TRANSFER_HYBRID_MAY_NOT_FORCE_FULL_PITCH")
        if self.hero_text_overlap or self.hero_brand_overlap:
            raise ValueError("TRANSFER_HYBRID_PROTECTED_HERO_COLLISION")
        if self.publication_ready:
            raise ValueError("HYBRID_RENDERER_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class TransferSignatureHybridRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _box(box, profile: PlatformImageProfile) -> tuple[int,int,int,int]:
        return (
            round(box.x*profile.width), round(box.y*profile.height),
            round((box.x+box.width)*profile.width), round((box.y+box.height)*profile.height),
        )

    @staticmethod
    def _intersects(a: tuple[int,int,int,int], b: tuple[int,int,int,int]) -> bool:
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    @staticmethod
    def _soft_copy_field(image: Image.Image, box: tuple[int,int,int,int]) -> None:
        x0,y0,x1,y1 = box
        veil = Image.new('RGBA', image.size, (0,0,0,0))
        d = ImageDraw.Draw(veil, 'RGBA')
        px, py = round(image.width*0.028), round(image.height*0.02)
        d.rounded_rectangle((max(0,x0-px),max(0,y0-py),min(image.width,x1+px),min(image.height,y1+py)), radius=max(18,round(image.width*0.03)), fill=(2,6,11,92))
        veil = veil.filter(ImageFilter.GaussianBlur(max(12,round(image.width*0.025))))
        image.alpha_composite(veil)

    def render(
        self,
        composition: TransferSignatureComposition,
        *,
        admission: BaseSceneCompositionAdmission,
        profile: PlatformImageProfile,
        output_path: str,
        hero: VerifiedSubjectAsset,
        identity: IdentityPlan,
        destination_crest: ExactRasterAsset,
        headline: str,
        destination_name: str,
        accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
    ) -> TransferSignatureHybridReceipt:
        if not isinstance(composition, TransferSignatureComposition):
            raise TypeError('composition must be TransferSignatureComposition')
        if not isinstance(admission, BaseSceneCompositionAdmission):
            raise TypeError('admission must be BaseSceneCompositionAdmission')
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError('profile must be PlatformImageProfile')
        if destination_crest.reference.role is not AssetRole.TEAM_CREST:
            raise ValueError('destination_crest must use TEAM_CREST role')
        destination_crest.verified_path()
        if not headline.strip() or not destination_name.strip():
            raise ValueError('headline and destination_name are required')
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        admission.assert_bytes_unchanged()
        if (admission.provenance.width, admission.provenance.height) != (profile.width, profile.height):
            raise ValueError('admitted base scene does not match platform profile')

        hero_box = self._box(composition.hero_box, profile)
        headline_box = self._box(composition.headline_box, profile)
        context_box = self._box(composition.club_context_box, profile)
        if self._intersects(hero_box, headline_box) or self._intersects(hero_box, context_box):
            raise ValueError('TRANSFER_HERO_COPY_ZONE_COLLISION')

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        hero_stage = target.with_name(target.stem+'.hero.png')
        copy_stage = target.with_name(target.stem+'.copy.png')
        hx0,hy0,hx1,hy1 = hero_box
        hero_receipt = VerifiedSubjectCompositor().compose(
            base_path=admission.png_path, output_path=str(hero_stage), subject=hero, identity=identity,
            placement=SubjectPlacement(hx0,hy0,hx1-hx0,hy1-hy0), accent_hex=accent_hex,
        )

        with Image.open(hero_stage) as raw:
            image = raw.convert('RGBA')
        self._soft_copy_field(image, headline_box)
        draw = ImageDraw.Draw(image, 'RGBA')
        helper = VerifiedSubjectNewsStudyRenderer
        tx0,ty0,tx1,ty1 = headline_box
        wrapped, font, spacing = helper._wrap(draw, headline, font_path, tx1-tx0, ty1-ty0, round((ty1-ty0)*0.38), 3)
        draw.multiline_text((tx0,ty0), wrapped, font=font, spacing=spacing, fill=(244,248,250,255))
        accent = helper._rgb(accent_hex)
        rule_y = ty1 + max(5,round(profile.height*0.008))
        draw.rounded_rectangle((tx0,rule_y,tx0+round((tx1-tx0)*0.30),rule_y+3),radius=2,fill=(*accent,230))

        cx0,cy0,cx1,cy1 = context_box
        crest_box = (cx0,cy0,cx0+round((cx1-cx0)*0.34),cy1)
        ExactRasterAssetCompositor.composite(image, asset=destination_crest, box=crest_box, padding_ratio=0.08)
        text_x = crest_box[2] + round((cx1-cx0)*0.05)
        name_w = max(20,cx1-text_x)
        name_font = helper._fit_font(draw, destination_name, font_path, name_w, cy1-cy0, round((cy1-cy0)*0.30))
        nb = draw.textbbox((0,0), destination_name, font=name_font)
        draw.text((text_x, (cy0+cy1)/2-(nb[3]-nb[1])/2-nb[1]), destination_name, font=name_font, fill=(218,229,237,247))
        image.convert('RGB').save(copy_stage,format='PNG')

        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(copy_stage), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        brand_box = (brand.x,brand.y,brand.x+brand.width,brand.y+brand.height)
        hero_brand_overlap = self._intersects(hero_box,brand_box)
        if hero_brand_overlap:
            raise ValueError('TRANSFER_HERO_BRAND_PIXEL_COLLISION')
        hero_stage.unlink(missing_ok=True)
        copy_stage.unlink(missing_ok=True)
        return TransferSignatureHybridReceipt(
            output_path=str(target), output_sha256=self._sha(target),
            base_scene_sha256=admission.png_sha256, base_quality_tier=admission.quality_tier.value,
            hero_asset_id=hero_receipt.subject_asset_id, hero_sha256=hero_receipt.subject_sha256,
            hero_entity_name=hero_receipt.entity_name, identity_confidence=hero_receipt.identity_confidence,
            destination_crest_sha256=destination_crest.sha256,
            generator_owns_identity=False, generator_owns_crest=False,
            generator_owns_readable_text=False, generator_owns_brand=False,
            full_pitch_used=False, hero_text_overlap=False, hero_brand_overlap=False,
            brand_zone=brand.zone, brand_width=brand.width, brand_height=brand.height,
        )

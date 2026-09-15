"""Production-shaped Event Editorial hybrid renderer.

The admitted Elite base scene may own a non-factual symbolic/environmental anchor.
Readable copy and PUL7SAR identity remain deterministic post-composition layers.
No person, score, exact mark or sport geometry is inferred by this renderer.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmission
from engine.intelligence.event_editorial_composition import EventEditorialComposition
from engine.intelligence.event_editorial_study_renderer import EventEditorialStudyRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile


@dataclass(frozen=True)
class EventEditorialHybridReceipt:
    output_path: str
    output_sha256: str
    base_scene_sha256: str
    base_quality_tier: str
    generator_owns_nonfactual_symbolic_anchor: bool
    generator_owns_readable_text: bool
    generator_owns_brand: bool
    person_inserted: bool
    exact_data_inserted: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    publication_ready: bool = False
    contract: str = "pul7sar-event-editorial-hybrid-renderer-v1-cinematic"

    def __post_init__(self) -> None:
        if self.generator_owns_readable_text or self.generator_owns_brand:
            raise ValueError("EVENT_HYBRID_GENERATOR_MAY_NOT_OWN_TEXT_OR_BRAND")
        if self.person_inserted or self.exact_data_inserted:
            raise ValueError("GENERIC_EVENT_HYBRID_MAY_NOT_INVENT_PERSON_OR_EXACT_DATA")
        if self.publication_ready:
            raise ValueError("HYBRID_RENDERER_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class EventEditorialHybridRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _box(box, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return (
            round(box.x * profile.width), round(box.y * profile.height),
            round((box.x + box.width) * profile.width), round((box.y + box.height) * profile.height),
        )

    @staticmethod
    def _copy_readability(image: Image.Image, box: tuple[int, int, int, int]) -> None:
        x0, y0, x1, y1 = box
        width = image.width
        veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(veil, "RGBA")
        px, py = round(width * 0.08), round(image.height * 0.045)
        draw.rounded_rectangle(
            (max(0, x0-px), max(0, y0-py), min(image.width, x1+px), min(image.height, y1+py)),
            radius=max(24, round(width*0.045)), fill=(1, 5, 10, 102),
        )
        veil = veil.filter(ImageFilter.GaussianBlur(max(18, round(width*0.04))))
        image.alpha_composite(veil)

    def render(
        self,
        composition: EventEditorialComposition,
        *,
        admission: BaseSceneCompositionAdmission,
        profile: PlatformImageProfile,
        output_path: str,
        headline: str,
        kicker: str,
        accent_hex: str,
        font_path: str,
    ) -> EventEditorialHybridReceipt:
        if not isinstance(composition, EventEditorialComposition):
            raise TypeError("composition must be EventEditorialComposition")
        if not isinstance(admission, BaseSceneCompositionAdmission):
            raise TypeError("admission must be BaseSceneCompositionAdmission")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not headline.strip() or not kicker.strip():
            raise ValueError("headline and kicker are required")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        admission.assert_bytes_unchanged()
        if (admission.provenance.width, admission.provenance.height) != (profile.width, profile.height):
            raise ValueError("admitted base scene does not match platform profile")
        with Image.open(admission.png_path) as base:
            image = base.convert("RGBA")

        headline_box = self._box(composition.headline_box, profile)
        self._copy_readability(image, headline_box)
        draw = ImageDraw.Draw(image, "RGBA")
        hx0, hy0, hx1, hy1 = headline_box
        font = EventEditorialStudyRenderer._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.60))
        b = draw.textbbox((0, 0), headline, font=font)
        draw.text((profile.width/2-(b[2]-b[0])/2, hy0), headline, font=font, fill=(244, 248, 250, 255))

        ax0, ay0, ax1, _ = self._box(composition.anchor_box, profile)
        kicker_font = EventEditorialStudyRenderer._fit_font(draw, kicker, font_path, round((ax1-ax0)*0.58), round(profile.height*0.05), round(profile.height*0.024))
        kb = draw.textbbox((0, 0), kicker, font=kicker_font)
        kicker_y = max(hy1 + round(profile.height*0.012), ay0-round(profile.height*0.055))
        draw.text((profile.width/2-(kb[2]-kb[0])/2, kicker_y), kicker, font=kicker_font, fill=(176, 194, 207, 242))

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(prebrand, format="PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=accent_hex,
        )
        prebrand.unlink(missing_ok=True)
        return EventEditorialHybridReceipt(
            output_path=str(target), output_sha256=self._sha(target),
            base_scene_sha256=admission.png_sha256, base_quality_tier=admission.quality_tier.value,
            generator_owns_nonfactual_symbolic_anchor=True,
            generator_owns_readable_text=False, generator_owns_brand=False,
            person_inserted=False, exact_data_inserted=False,
            brand_zone=brand.zone, brand_width=brand.width, brand_height=brand.height,
        )

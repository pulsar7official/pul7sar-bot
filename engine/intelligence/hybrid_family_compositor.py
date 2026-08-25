"""Executable hybrid compositor for Phase 18 family-quality candidates.

The compositor accepts an already generated atmosphere image and adds only exact,
caller-supplied editorial facts plus the checksum-locked PUL7SAR reference brand.
It deliberately does not fabricate people, crests, statistics, scores, dates or
competition identity. Missing optional exact assets stay absent; no dot, badge or
crest placeholder is drawn.

Important: this compositor does not pretend it has inspected the generated base.
Base-scene text/identity/geometry leakage stays explicitly unverified until a
separate semantic visual gate supplies evidence. Consequently composition alone
can never make a candidate publication-ready.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from engine.intelligence.brand_reference_renderer import BrandReferencePlacement, BrandReferenceRenderer
from engine.intelligence.hybrid_scene_contract import HybridSceneContractRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class HybridEditorialFacts:
    family: EditorialSceneFamily
    headline: str
    primary: str = ""
    secondary: str = ""
    tertiary: str = ""
    home_name: str = ""
    away_name: str = ""
    home_score: int | None = None
    away_score: int | None = None
    accent_hex: str = "#E10600"


@dataclass(frozen=True)
class HybridCompositionReceipt:
    output_path: str
    output_sha256: str
    family: str
    exact_brand_used: bool
    fabricated_crest_used: bool
    placeholder_used: bool
    compositor_generated_text_used: bool
    deterministic_facts_used: bool
    source_photo_used: bool
    base_scene_semantic_verified: bool = False
    base_scene_text_absence_verified: bool = False
    base_scene_identity_absence_verified: bool = False
    base_scene_geometry_absence_verified: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-hybrid-family-compositor-v2"


class HybridFamilyCompositor:
    CONTRACT = "pul7sar-hybrid-family-compositor-v2"
    SIZE = (1080, 1350)

    @staticmethod
    def _font(size: int, *, condensed: bool = False):
        candidates = []
        if condensed:
            candidates += [
                "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
                "/usr/share/fonts/truetype/liberation2/LiberationSansNarrow-Bold.ttf",
            ]
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
        for path in candidates:
            if Path(path).is_file():
                return ImageFont.truetype(path, size=size)
        return ImageFont.load_default()

    @staticmethod
    def _fit_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
        tw, th = size
        scale = max(tw / im.width, th / im.height)
        nw, nh = round(im.width * scale), round(im.height * scale)
        r = im.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - tw) // 2, (nh - th) // 2
        return r.crop((left, top, left + tw, top + th)).convert("RGBA")

    @staticmethod
    def _hex(text: str) -> tuple[int, int, int]:
        value = text.strip().lstrip("#")
        if len(value) != 6:
            raise ValueError("accent_hex must be #RRGGBB")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _shadow_text(layer: Image.Image, xy, text: str, font, *, fill=(244, 246, 248, 255), anchor=None, stroke=0):
        d = ImageDraw.Draw(layer)
        x, y = xy
        d.text((x + 3, y + 5), text, font=font, fill=(0, 0, 0, 150), anchor=anchor, stroke_width=stroke)
        d.text((x, y), text, font=font, fill=fill, anchor=anchor, stroke_width=stroke)

    @staticmethod
    def _readable_zone(canvas: Image.Image, *, top: int, bottom: int, strength: int = 150, reverse: bool = False):
        w, h = canvas.size
        top = max(0, top)
        bottom = min(h, bottom)
        span = max(1, bottom - top)
        # Build a one-pixel-wide alpha ramp and scale it, avoiding per-pixel Python loops.
        ramp = Image.new("L", (1, span))
        rp = ramp.load()
        for y in range(span):
            t = y / max(1, span - 1)
            rp[0, y] = round(strength * ((1 - t) if reverse else t))
        alpha = ramp.resize((w, span), Image.Resampling.NEAREST)
        zone = Image.new("RGBA", (w, span), (2, 5, 10, 0))
        zone.putalpha(alpha)
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        overlay.alpha_composite(zone, (0, top))
        canvas.alpha_composite(overlay)

    @classmethod
    def _result(cls, canvas: Image.Image, f: HybridEditorialFacts):
        if f.home_score is None or f.away_score is None or not f.home_name or not f.away_name:
            raise ValueError("result family requires exact team names and scores")
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        accent = cls._hex(f.accent_hex)
        cls._readable_zone(canvas, top=650, bottom=1210, strength=185)
        draw = ImageDraw.Draw(layer)
        draw.line((120, 760, 960, 760), fill=(*accent, 155), width=3)
        cls._shadow_text(layer, (540, 700), "FULL TIME", cls._font(31, condensed=True), fill=(220, 224, 229, 235), anchor="mm")
        score = f"{f.home_score}  –  {f.away_score}"
        cls._shadow_text(layer, (540, 865), score, cls._font(155, condensed=True), anchor="mm")
        cls._shadow_text(layer, (130, 1030), f.home_name.upper(), cls._font(43, condensed=True), anchor="lm")
        cls._shadow_text(layer, (950, 1030), f.away_name.upper(), cls._font(43, condensed=True), anchor="rm")
        canvas.alpha_composite(layer)

    @classmethod
    def _transfer(cls, canvas: Image.Image, f: HybridEditorialFacts):
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        accent = cls._hex(f.accent_hex)
        cls._readable_zone(canvas, top=0, bottom=530, strength=175, reverse=True)
        d = ImageDraw.Draw(layer)
        d.line((88, 118, 88, 450), fill=(*accent, 230), width=7)
        cls._shadow_text(layer, (125, 142), "TRANSFER", cls._font(27, condensed=True), fill=(*accent, 255), anchor="la")
        cls._shadow_text(layer, (125, 200), f.headline.upper(), cls._font(66, condensed=True), anchor="la")
        if f.primary:
            cls._shadow_text(layer, (125, 360), f.primary.upper(), cls._font(34, condensed=True), fill=(218, 223, 228, 245), anchor="la")
        if f.secondary:
            cls._shadow_text(layer, (125, 414), f.secondary.upper(), cls._font(26, condensed=True), fill=(178, 186, 196, 240), anchor="la")
        canvas.alpha_composite(layer)

    @classmethod
    def _subject(cls, canvas: Image.Image, f: HybridEditorialFacts):
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        accent = cls._hex(f.accent_hex)
        cls._readable_zone(canvas, top=860, bottom=1350, strength=205)
        d = ImageDraw.Draw(layer)
        d.line((84, 1000, 320, 1000), fill=(*accent, 220), width=5)
        cls._shadow_text(layer, (84, 1032), f.headline.upper(), cls._font(58, condensed=True), anchor="la")
        if f.primary:
            cls._shadow_text(layer, (84, 1165), f.primary.upper(), cls._font(31, condensed=True), fill=(208, 215, 222, 245), anchor="la")
        canvas.alpha_composite(layer)

    @classmethod
    def _data(cls, canvas: Image.Image, f: HybridEditorialFacts):
        if not f.primary:
            raise ValueError("data family requires an exact primary data value")
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        accent = cls._hex(f.accent_hex)
        cls._readable_zone(canvas, top=690, bottom=1290, strength=170)
        cls._shadow_text(layer, (92, 735), f.headline.upper(), cls._font(28, condensed=True), fill=(*accent, 255), anchor="la")
        cls._shadow_text(layer, (92, 800), f.primary, cls._font(188, condensed=True), anchor="la")
        if f.secondary:
            cls._shadow_text(layer, (100, 1025), f.secondary.upper(), cls._font(42, condensed=True), fill=(222, 227, 233, 250), anchor="la")
        if f.tertiary:
            cls._shadow_text(layer, (100, 1100), f.tertiary.upper(), cls._font(27, condensed=True), fill=(173, 183, 193, 240), anchor="la")
        canvas.alpha_composite(layer)

    @classmethod
    def _event(cls, canvas: Image.Image, f: HybridEditorialFacts):
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        accent = cls._hex(f.accent_hex)
        cls._readable_zone(canvas, top=70, bottom=560, strength=180, reverse=True)
        cls._shadow_text(layer, (540, 105), "UP NEXT", cls._font(27, condensed=True), fill=(*accent, 255), anchor="ma")
        cls._shadow_text(layer, (540, 170), f.headline.upper(), cls._font(64, condensed=True), anchor="ma")
        if f.primary:
            cls._shadow_text(layer, (540, 330), f.primary.upper(), cls._font(37, condensed=True), anchor="ma")
        if f.secondary:
            cls._shadow_text(layer, (540, 395), f.secondary.upper(), cls._font(27, condensed=True), fill=(190, 198, 207, 245), anchor="ma")
        canvas.alpha_composite(layer)

    def compose(self, *, base_path: str, output_path: str, facts: HybridEditorialFacts, repository_root: str | Path | None = None) -> HybridCompositionReceipt:
        HybridSceneContractRegistry.get(facts.family)
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base)
        with Image.open(base) as src:
            canvas = self._fit_cover(src.convert("RGB"), self.SIZE)
        canvas.alpha_composite(Image.new("RGBA", self.SIZE, (4, 8, 15, 18)))

        if facts.family is EditorialSceneFamily.RESULT_STATEMENT:
            self._result(canvas, facts)
        elif facts.family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            self._transfer(canvas, facts)
        elif facts.family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            self._subject(canvas, facts)
        elif facts.family is EditorialSceneFamily.DATA_MONUMENT:
            self._data(canvas, facts)
        elif facts.family is EditorialSceneFamily.EVENT_EDITORIAL:
            self._event(canvas, facts)
        else:
            raise ValueError("TACTICAL_BOARD must use deterministic tactical compositor")

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_suffix(".prebrand.png")
        canvas.convert("RGB").save(prebrand, "PNG")
        brand_w = 250
        BrandReferenceRenderer().render_on_file(
            base_path=str(prebrand),
            output_path=str(target),
            placement=BrandReferencePlacement(self.SIZE[0] - brand_w - 58, self.SIZE[1] - 122, brand_w),
            accent_hex=facts.accent_hex,
            repository_root=repository_root,
        )
        prebrand.unlink(missing_ok=True)
        digest = sha256(target.read_bytes()).hexdigest()
        return HybridCompositionReceipt(
            output_path=str(target),
            output_sha256=digest,
            family=facts.family.value,
            exact_brand_used=True,
            fabricated_crest_used=False,
            placeholder_used=False,
            compositor_generated_text_used=False,
            deterministic_facts_used=True,
            source_photo_used=False,
            base_scene_semantic_verified=False,
            base_scene_text_absence_verified=False,
            base_scene_identity_absence_verified=False,
            base_scene_geometry_absence_verified=False,
        )

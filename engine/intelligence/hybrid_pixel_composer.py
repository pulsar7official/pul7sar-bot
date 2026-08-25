"""Pixel-level composition for Phase 18 hybrid publication candidates.

The compositor accepts an already generated, unbranded scene and applies only
explicit deterministic or verified-asset layers. It never fabricates crests,
people, competition marks, readable facts, or the PUL7SAR brand.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.hybrid_final_composer import HybridFinalCompositionPlan
from engine.intelligence.hybrid_scene_composition import LayerOwner
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class VerifiedRasterAsset:
    path: str
    kind: str
    verified: bool
    approved: bool = False

    def require_safe(self) -> Path:
        p = Path(self.path)
        if not self.verified:
            raise ValueError(f"UNVERIFIED_ASSET:{self.kind}")
        if not p.is_file():
            raise FileNotFoundError(self.path)
        return p


@dataclass(frozen=True)
class HybridPixelRequest:
    plan: HybridFinalCompositionPlan
    generated_base_path: str
    output_path: str
    headline: str
    primary_label: str = ""
    secondary_label: str = ""
    primary_value: str = ""
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    brand_master: VerifiedRasterAsset | None = None
    club_crest_a: VerifiedRasterAsset | None = None
    club_crest_b: VerifiedRasterAsset | None = None
    verified_subject: VerifiedRasterAsset | None = None
    generated_base_verified_unbranded: bool = False
    generated_base_verified_no_readable_facts: bool = False


@dataclass(frozen=True)
class HybridPixelReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    generated_base_used: bool
    brand_applied: bool
    verified_assets_applied: tuple[str, ...]
    publication_ready: bool = False
    contract: str = "pul7sar-hybrid-pixel-composer-v1"


class HybridPixelComposer:
    CONTRACT = "pul7sar-hybrid-pixel-composer-v1"

    @staticmethod
    def _asset_required(plan: HybridFinalCompositionPlan, name: str) -> bool:
        return any(layer.name == name and layer.required for layer in plan.layers)

    @staticmethod
    def _fit(draw, text: str, font_path: str, max_width: int, start_size: int, min_size: int = 20):
        from PIL import ImageFont
        size = start_size
        while size >= min_size:
            font = ImageFont.truetype(font_path, size)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= max_width:
                return font
            size -= 2
        return ImageFont.truetype(font_path, min_size)

    @staticmethod
    def _paste_asset(canvas, asset: VerifiedRasterAsset, box: tuple[int, int, int, int], *, require_approved=False):
        from PIL import Image
        p = asset.require_safe()
        if require_approved and not asset.approved:
            raise ValueError(f"UNAPPROVED_ASSET:{asset.kind}")
        layer = Image.open(p).convert("RGBA")
        max_w = max(1, box[2] - box[0]); max_h = max(1, box[3] - box[1])
        layer.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        x = box[0] + (max_w - layer.width) // 2
        y = box[1] + (max_h - layer.height) // 2
        canvas.alpha_composite(layer, (x, y))

    def compose(self, req: HybridPixelRequest) -> HybridPixelReceipt:
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

        req.plan.validate()
        if req.plan.family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_USES_DETERMINISTIC_RENDERER_NOT_HYBRID_PIXEL_COMPOSER")
        if not req.generated_base_verified_unbranded:
            raise ValueError("GENERATED_BASE_NOT_VERIFIED_UNBRANDED")
        if not req.generated_base_verified_no_readable_facts:
            raise ValueError("GENERATED_BASE_NOT_VERIFIED_FACT_FREE")

        base_path = Path(req.generated_base_path)
        if not base_path.is_file():
            raise FileNotFoundError(req.generated_base_path)
        canvas = Image.open(base_path).convert("RGBA")
        w, h = canvas.size

        # Gentle editorial grade only; preserve the synthesized physical world.
        canvas = ImageEnhance.Contrast(canvas).enhance(1.04)
        canvas = ImageEnhance.Color(canvas).enhance(0.94)
        shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade, "RGBA")
        sd.rectangle((0, 0, w, int(h * .24)), fill=(0, 0, 0, 42))
        sd.rectangle((0, int(h * .72), w, h), fill=(0, 0, 0, 54))
        canvas.alpha_composite(shade.filter(ImageFilter.GaussianBlur(max(8, w // 55))))
        draw = ImageDraw.Draw(canvas, "RGBA")

        # Headline is deterministic and deliberately secondary to the scene hero.
        if req.headline.strip():
            hf = self._fit(draw, req.headline.upper(), req.font_path, int(w * .72), max(28, int(w * .055)), 20)
            draw.text((int(w * .08), int(h * .10)), req.headline.upper(), font=hf, fill=(244, 246, 248, 238), anchor="la")

        if req.plan.family is EditorialSceneFamily.RESULT_STATEMENT:
            if not req.primary_value.strip():
                raise ValueError("RESULT_REQUIRES_EXACT_SCORE")
            score_font = self._fit(draw, req.primary_value, req.font_path, int(w * .34), max(64, int(w * .14)), 44)
            score_x = int(w * .66); score_y = int(h * .50)
            # restrained broadcast-like score plate; not a gaming card
            plate = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(plate, "RGBA")
            sb = pd.textbbox((0, 0), req.primary_value, font=score_font)
            sw, sh = sb[2] - sb[0], sb[3] - sb[1]
            pad_x, pad_y = int(w * .035), int(h * .018)
            box = (score_x - sw // 2 - pad_x, score_y - sh // 2 - pad_y, score_x + sw // 2 + pad_x, score_y + sh // 2 + pad_y)
            pd.rounded_rectangle(box, radius=max(10, int(w * .018)), fill=(5, 8, 13, 166), outline=(228, 232, 237, 70), width=max(1, w // 500))
            canvas.alpha_composite(plate.filter(ImageFilter.GaussianBlur(max(1, w // 800))))
            draw = ImageDraw.Draw(canvas, "RGBA")
            draw.text((score_x, score_y), req.primary_value, font=score_font, fill=(245, 247, 249, 248), anchor="mm")
            label_font = self._fit(draw, max(req.primary_label, req.secondary_label, key=len), req.font_path, int(w * .30), max(22, int(w * .035)), 18)
            if req.primary_label:
                draw.text((int(w * .18), int(h * .75)), req.primary_label.upper(), font=label_font, fill=(239, 242, 245, 230), anchor="lm")
            if req.secondary_label:
                draw.text((int(w * .82), int(h * .75)), req.secondary_label.upper(), font=label_font, fill=(239, 242, 245, 230), anchor="rm")

        applied = []
        if req.club_crest_a:
            self._paste_asset(canvas, req.club_crest_a, (int(w*.07), int(h*.57), int(w*.25), int(h*.72)))
            applied.append("club_crest_a")
        elif self._asset_required(req.plan, "club_crest"):
            raise ValueError("REQUIRED_VERIFIED_CREST_MISSING")
        if req.club_crest_b:
            self._paste_asset(canvas, req.club_crest_b, (int(w*.75), int(h*.57), int(w*.93), int(h*.72)))
            applied.append("club_crest_b")

        if req.verified_subject:
            self._paste_asset(canvas, req.verified_subject, (int(w*.45), int(h*.14), int(w*.92), int(h*.92)))
            applied.append("verified_subject")
        elif self._asset_required(req.plan, "verified_subject"):
            raise ValueError("REQUIRED_VERIFIED_SUBJECT_MISSING")

        brand_applied = False
        if req.brand_master:
            self._paste_asset(canvas, req.brand_master, (int(w*.73), int(h*.04), int(w*.94), int(h*.13)), require_approved=True)
            brand_applied = True
            applied.append("pul7sar_brand")
        # Missing approved brand never triggers fallback drawing. Phase 18 remains study-only.

        out = Path(req.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out, quality=96)
        digest = sha256(out.read_bytes()).hexdigest()
        return HybridPixelReceipt(
            output_path=str(out), output_sha256=digest, width=w, height=h,
            generated_base_used=True, brand_applied=brand_applied,
            verified_assets_applied=tuple(applied), publication_ready=False,
        )

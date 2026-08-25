"""Pixel-level composition for Phase 18 hybrid publication candidates.

The compositor accepts an already generated, unbranded scene and applies only
explicit deterministic or verified-asset layers. It never fabricates crests,
people, competition marks, readable facts, or the PUL7SAR brand.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.generated_base_provenance import GeneratedBaseProvenance
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
    generated_base_provenance: GeneratedBaseProvenance | None = None
    study_test_override: bool = False


@dataclass(frozen=True)
class HybridPixelReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    generated_base_used: bool
    provenance_verified: bool
    brand_applied: bool
    verified_assets_applied: tuple[str, ...]
    publication_ready: bool = False
    contract: str = "pul7sar-hybrid-pixel-composer-v3-result-hierarchy"


class HybridPixelComposer:
    CONTRACT = "pul7sar-hybrid-pixel-composer-v3-result-hierarchy"

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

        provenance_verified = False
        if req.generated_base_provenance is not None:
            req.generated_base_provenance.validate_for(family=req.plan.family, image_path=req.generated_base_path)
            provenance_verified = True
        elif not req.study_test_override:
            raise ValueError("GENERATED_BASE_PROVENANCE_REQUIRED")

        base_path = Path(req.generated_base_path)
        if not base_path.is_file():
            raise FileNotFoundError(req.generated_base_path)
        canvas = Image.open(base_path).convert("RGBA")
        w, h = canvas.size

        # Preserve the generated physical world. Only create quiet reading zones.
        canvas = ImageEnhance.Contrast(canvas).enhance(1.035)
        canvas = ImageEnhance.Color(canvas).enhance(0.92)
        shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade, "RGBA")
        sd.rectangle((0, 0, w, int(h * .22)), fill=(0, 0, 0, 38))
        sd.rectangle((0, int(h * .58), w, h), fill=(0, 0, 0, 72))
        canvas.alpha_composite(shade.filter(ImageFilter.GaussianBlur(max(8, w // 55))))
        draw = ImageDraw.Draw(canvas, "RGBA")

        if req.headline.strip():
            hf = self._fit(draw, req.headline.upper(), req.font_path, int(w * .62), max(24, int(w * .045)), 18)
            draw.text((int(w * .075), int(h * .085)), req.headline.upper(), font=hf, fill=(244, 246, 248, 225), anchor="la")

        if req.plan.family is EditorialSceneFamily.RESULT_STATEMENT:
            if not req.primary_value.strip():
                raise ValueError("RESULT_REQUIRES_EXACT_SCORE")

            # Visual-review v3: one coherent lower-third result monument. The
            # previous study scattered team labels across spectator texture and
            # made the score look pasted onto the photograph.
            score_font = self._fit(draw, req.primary_value, req.font_path, int(w * .42), max(76, int(w * .17)), 48)
            label_candidates = tuple(x for x in (req.primary_label, req.secondary_label) if x)
            label_font = self._fit(draw, max(label_candidates, key=len) if label_candidates else "TEAM", req.font_path, int(w * .30), max(20, int(w * .030)), 16)

            plate = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            pd = ImageDraw.Draw(plate, "RGBA")
            left, right = int(w * .07), int(w * .93)
            top, bottom = int(h * .61), int(h * .83)
            radius = max(14, int(w * .028))
            pd.rounded_rectangle((left, top, right, bottom), radius=radius, fill=(4, 7, 11, 176), outline=(235, 238, 242, 48), width=max(1, w // 420))
            # Quiet internal separators create editorial structure without
            # pretending to be a club or competition identity system.
            cx = w // 2
            pd.line((int(w*.34), int(h*.68), int(w*.34), int(h*.78)), fill=(240,240,240,34), width=max(1,w//420))
            pd.line((int(w*.66), int(h*.68), int(w*.66), int(h*.78)), fill=(240,240,240,34), width=max(1,w//420))
            canvas.alpha_composite(plate.filter(ImageFilter.GaussianBlur(max(1, w // 900))))
            draw = ImageDraw.Draw(canvas, "RGBA")

            score_y = int(h * .705)
            draw.text((cx, score_y), req.primary_value, font=score_font, fill=(248, 249, 250, 250), anchor="mm")
            label_y = int(h * .755)
            if req.primary_label:
                draw.text((int(w * .205), label_y), req.primary_label.upper(), font=label_font, fill=(239, 242, 245, 232), anchor="mm")
            if req.secondary_label:
                draw.text((int(w * .795), label_y), req.secondary_label.upper(), font=label_font, fill=(239, 242, 245, 232), anchor="mm")

        applied = []
        if req.club_crest_a:
            self._paste_asset(canvas, req.club_crest_a, (int(w*.10), int(h*.62), int(w*.30), int(h*.73)))
            applied.append("club_crest_a")
        elif self._asset_required(req.plan, "club_crest"):
            raise ValueError("REQUIRED_VERIFIED_CREST_MISSING")
        if req.club_crest_b:
            self._paste_asset(canvas, req.club_crest_b, (int(w*.70), int(h*.62), int(w*.90), int(h*.73)))
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

        out = Path(req.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out, quality=96)
        digest = sha256(out.read_bytes()).hexdigest()
        return HybridPixelReceipt(
            output_path=str(out), output_sha256=digest, width=w, height=h,
            generated_base_used=True, provenance_verified=provenance_verified,
            brand_applied=brand_applied, verified_assets_applied=tuple(applied), publication_ready=False,
        )

"""Adaptive spatial result monument for Phase 18 visual benchmarking.

The exact score object is deterministic, but v2 refuses generated bases that do
not provide a sufficiently safe foreground. Placement width is adapted from
measured scene evidence rather than imposing one trapezoid on every camera view.
The compatibility gate is deliberately study-only: it detects obvious placement
risks and must not be treated as full semantic scene understanding.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


@dataclass(frozen=True)
class SpatialResultSpec:
    headline: str
    home: str
    away: str
    score: str
    font_path: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    def validate(self) -> None:
        if not self.score.strip():
            raise ValueError("SPATIAL_RESULT_SCORE_REQUIRED")
        if not self.home.strip() or not self.away.strip():
            raise ValueError("SPATIAL_RESULT_TEAM_LABELS_REQUIRED")


@dataclass(frozen=True)
class SpatialCompatibilityEvidence:
    compatible: bool
    placement_mode: str
    horizontal_detail: float
    central_obstruction: float
    rejection_reasons: tuple[str, ...]
    study_only: bool = True
    contract: str = "pul7sar-result-spatial-compatibility-v1"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["rejection_reasons"] = list(self.rejection_reasons)
        return data


class SpatialResultMonument:
    CONTRACT = "pul7sar-spatial-result-monument-v2-scene-compatible"
    COMPATIBILITY_CONTRACT = "pul7sar-result-spatial-compatibility-v1"
    DETAIL_LIMIT = 16.0
    OBSTRUCTION_LIMIT = 22.0
    NARROW_DETAIL_LIMIT = 8.5

    @staticmethod
    def _fit(draw: ImageDraw.ImageDraw, text: str, path: str, max_width: int, start: int, minimum: int) -> ImageFont.FreeTypeFont:
        size = start
        while size >= minimum:
            font = ImageFont.truetype(path, size)
            box = draw.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= max_width:
                return font
            size -= 2
        return ImageFont.truetype(path, minimum)

    @staticmethod
    def _mean_row(image: Image.Image, x0: int, x1: int, y: int) -> float:
        px = image.load()
        return sum(px[x, y] for x in range(x0, x1)) / max(1, x1 - x0)

    @classmethod
    def inspect_compatibility(cls, image_path: str) -> SpatialCompatibilityEvidence:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(image_path)
        im = Image.open(path).convert("L").resize((160, 200))
        w, h = im.size

        zone = im.crop((int(w*.15), int(h*.55), int(w*.85), int(h*.90)))
        zp = zone.load(); zw, zh = zone.size
        horizontal_detail = sum(
            abs(zp[x, y] - zp[x-1, y])
            for y in range(zh) for x in range(1, zw)
        ) / max(1, zh * (zw - 1))

        diffs = []
        for y in range(int(h*.48), int(h*.92)):
            center = cls._mean_row(im, int(w*.43), int(w*.57), y)
            left = cls._mean_row(im, int(w*.23), int(w*.37), y)
            right = cls._mean_row(im, int(w*.63), int(w*.77), y)
            diffs.append(abs(center - ((left + right) / 2.0)))
        central_obstruction = sum(diffs) / max(1, len(diffs))

        reasons = []
        if horizontal_detail > cls.DETAIL_LIMIT:
            reasons.append("foreground_too_visually_dense_for_grounded_monument")
        if central_obstruction > cls.OBSTRUCTION_LIMIT:
            reasons.append("central_foreground_obstruction_risk")
        mode = "narrow_aisle" if horizontal_detail < cls.NARROW_DETAIL_LIMIT else "open_ground"
        return SpatialCompatibilityEvidence(
            compatible=not reasons,
            placement_mode=mode,
            horizontal_detail=round(horizontal_detail, 4),
            central_obstruction=round(central_obstruction, 4),
            rejection_reasons=tuple(reasons),
        )

    @classmethod
    def compose(cls, base_path: str, output_path: str, spec: SpatialResultSpec) -> str:
        spec.validate()
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)
        evidence = cls.inspect_compatibility(str(base))
        if not evidence.compatible:
            raise ValueError("SPATIAL_RESULT_BASE_INCOMPATIBLE:" + ",".join(evidence.rejection_reasons))

        canvas = Image.open(base).convert("RGBA")
        w, h = canvas.size
        if evidence.placement_mode == "narrow_aisle":
            x0, x1 = int(w*.22), int(w*.78)
            y_top, y_bottom = int(h*.60), int(h*.83)
            inset = int(w*.045)
        else:
            x0, x1 = int(w*.12), int(w*.88)
            y_top, y_bottom = int(h*.59), int(h*.83)
            inset = int(w*.05)
        polygon = [(x0+inset, y_top), (x1-inset, y_top), (x1, y_bottom), (x0, y_bottom)]

        atmosphere = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ad = ImageDraw.Draw(atmosphere, "RGBA")
        ad.ellipse((x0, int(h*.50), x1, int(h*.90)), fill=(0, 0, 0, 52))
        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(max(14, w//30)))
        canvas.alpha_composite(atmosphere)

        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow, "RGBA")
        shadow_poly = [(x+int(w*.008), y+int(h*.014)) for x, y in polygon]
        sd.polygon(shadow_poly, fill=(0, 0, 0, 145))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(7, w//45)))
        canvas.alpha_composite(shadow)

        plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate, "RGBA")
        pd.polygon(polygon, fill=(5, 9, 14, 210))
        pd.line(polygon[:2], fill=(245,248,252,100), width=max(2,w//220))
        pd.line([polygon[0], polygon[3]], fill=(230,234,240,35), width=max(1,w//320))
        pd.line([polygon[1], polygon[2]], fill=(230,234,240,35), width=max(1,w//320))
        canvas.alpha_composite(plate)

        draw = ImageDraw.Draw(canvas, "RGBA")
        center_x = w//2
        headline = spec.headline.upper().strip()
        if headline:
            hf = cls._fit(draw, headline, spec.font_path, int((x1-x0)*.72), int(w*.038), 18)
            draw.text((center_x, int(h*.625)), headline, font=hf, fill=(239,243,248,230), anchor="mm")
        score_font = cls._fit(draw, spec.score, spec.font_path, int((x1-x0)*.48), int(w*.17), 54)
        team_text = max((spec.home.upper(), spec.away.upper()), key=len)
        team_font = cls._fit(draw, team_text, spec.font_path, int((x1-x0)*.34), int(w*.029), 15)
        draw.text((center_x, int(h*.705)), spec.score, font=score_font, fill=(250,251,252,255), anchor="mm")
        draw.text((int(x0+(x1-x0)*.27), int(h*.78)), spec.home.upper(), font=team_font, fill=(236,240,244,240), anchor="mm")
        draw.text((int(x0+(x1-x0)*.73), int(h*.78)), spec.away.upper(), font=team_font, fill=(236,240,244,240), anchor="mm")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out, quality=96)
        return str(out)

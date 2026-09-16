"""Photographic premium-hybrid Result Statement study renderer.

This visual-quality benchmark fuses a rights-aware context photograph with a
fully deterministic editorial foreground. The photograph owns atmosphere only;
exact score, readable names, identity surfaces and PUL7SAR branding remain code
owned. V2 adds metallic score typography, optical stadium light, equal shield
identity monuments and photographic depth without turning the result into a flat
scoreboard card.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposition
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer
from engine.intelligence.verified_context_surface import (
    ContextSurfaceReceipt,
    VerifiedContextAsset,
    VerifiedContextSurfaceRenderer,
)


@dataclass(frozen=True)
class PremiumHybridResultStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    score_text: str
    home_name: str
    away_name: str
    context_asset_id: str
    context_source_sha256: str
    context_output_sha256: str
    context_source_reference: str
    context_rights_basis: str
    context_role: str
    brand_zone: str
    brand_width: int
    brand_height: int
    verified_context_contract: str
    club_identity_scale_equal: bool = True
    home_identity_placeholder_used: bool = True
    away_identity_placeholder_used: bool = True
    loser_treatment: str = "neutral_equal_identity_scale"
    metallic_score_used: bool = True
    optical_depth_used: bool = True
    generator_used: bool = False
    network_used_by_renderer: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-premium-hybrid-result-study-renderer-v2-metallic-depth"

    def __post_init__(self) -> None:
        if self.context_role != "atmosphere_only_not_event_evidence":
            raise ValueError("PREMIUM_HYBRID_CONTEXT_MAY_ONLY_OWN_ATMOSPHERE")
        if not self.club_identity_scale_equal:
            raise ValueError("RESULT_CLUB_IDENTITY_SCALE_MUST_REMAIN_EQUAL")
        if not self.home_identity_placeholder_used or not self.away_identity_placeholder_used:
            raise ValueError("STUDY_RENDERER_EXPECTS_EXPLICIT_NON_CREST_PLACEHOLDERS")
        if not self.metallic_score_used or not self.optical_depth_used:
            raise ValueError("PREMIUM_HYBRID_V2_REQUIRES_METALLIC_SCORE_AND_OPTICAL_DEPTH")
        if self.generator_used or self.network_used_by_renderer:
            raise ValueError("RENDERER_CORE_MUST_REMAIN_LOCAL_AND_DETERMINISTIC")
        if not self.study_only or self.publication_ready:
            raise ValueError("PREMIUM_HYBRID_STUDY_MAY_NOT_AUTHORIZE_PUBLICATION")


class PremiumHybridResultStudyRenderer:
    """Fuse verified photographic depth with deterministic Result editorial layers."""

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        return ResultStatementStudyRenderer._rgb(value)

    @staticmethod
    def _box(box, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        return ResultStatementStudyRenderer._box(box, profile)

    @staticmethod
    def _cinematic_integration(
        image: Image.Image,
        *,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> None:
        """Build optical depth around the photograph without inventing event facts."""
        width, height = image.size

        # Lower falloff anchors score/identities while leaving stadium architecture
        # visible. It is deliberately curved rather than a rectangular dark panel.
        lower = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lower, "RGBA")
        for y in range(round(height * 0.27), height):
            t = (y - height * 0.27) / (height * 0.73)
            alpha = round(18 + 165 * (t ** 1.62))
            ld.line((0, y, width, y), fill=(1, 5, 11, min(196, alpha)))
        image.alpha_composite(lower)

        # Equal club-side light. Winner receives no larger field of colour; result
        # hierarchy remains score-first and loser treatment stays respectful.
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        r = round(max(width, height) * 0.38)
        cy = round(height * 0.56)
        gd.ellipse((-round(r * 0.70), cy-r, round(r * 1.30), cy+r), fill=(*home_accent, 76))
        gd.ellipse((width-round(r * 1.30), cy-r, width+round(r * 0.70), cy+r), fill=(*away_accent, 72))
        glow = glow.filter(ImageFilter.GaussianBlur(max(34, round(width * 0.085))))
        image.alpha_composite(glow)

        # Stadium/floodlight blooms from the upper corners create premium depth.
        lights = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(lights, "RGBA")
        for cx in (round(width * 0.10), round(width * 0.90)):
            cy2 = round(height * 0.14)
            rr = round(width * 0.20)
            ldraw.ellipse((cx-rr, cy2-rr, cx+rr, cy2+rr), fill=(226, 239, 248, 31))
        lights = lights.filter(ImageFilter.GaussianBlur(max(36, round(width * 0.09))))
        image.alpha_composite(lights)

        # Narrow central shaft gives the score an optical stage, not a card.
        shaft = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shaft, "RGBA")
        cx = width // 2
        top = round(height * 0.09)
        bottom = round(height * 0.70)
        half_top = round(width * 0.025)
        half_bottom = round(width * 0.20)
        sd.polygon(
            ((cx-half_top, top), (cx+half_top, top), (cx+half_bottom, bottom), (cx-half_bottom, bottom)),
            fill=(235, 243, 249, 18),
        )
        shaft = shaft.filter(ImageFilter.GaussianBlur(max(22, round(width * 0.05))))
        image.alpha_composite(shaft)

        # Perspective rails are deliberately non-semantic: they hint at sporting
        # space but are not a factual pitch drawing or tactical geometry.
        rails = Image.new("RGBA", image.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rails, "RGBA")
        horizon = round(height * 0.61)
        bottom_y = round(height * 0.93)
        for x in (round(width*0.08), round(width*0.24), round(width*0.76), round(width*0.92)):
            rd.line((width//2, horizon, x, bottom_y), fill=(228, 238, 245, 16), width=1)
        rd.arc((round(width*.18), round(height*.70), round(width*.82), round(height*1.06)), 190, 350, fill=(228, 238, 245, 14), width=1)
        rails = rails.filter(ImageFilter.GaussianBlur(0.5))
        image.alpha_composite(rails)

        edge = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ed = ImageDraw.Draw(edge, "RGBA")
        side = round(width * 0.08)
        ed.rectangle((0, 0, side, height), fill=(0, 0, 0, 102))
        ed.rectangle((width-side, 0, width, height), fill=(0, 0, 0, 102))
        ed.rectangle((0, 0, width, round(height * 0.05)), fill=(0, 0, 0, 48))
        edge = edge.filter(ImageFilter.GaussianBlur(max(24, round(width * 0.05))))
        image.alpha_composite(edge)

    @staticmethod
    def _text_mask(size: tuple[int, int], *, text: str, font, center_x: float, center_y: float) -> Image.Image:
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        box = draw.textbbox((0, 0), text, font=font)
        x = center_x - (box[2] - box[0]) / 2 - box[0]
        y = center_y - (box[3] - box[1]) / 2 - box[1]
        draw.text((x, y), text, font=font, fill=255)
        return mask

    @staticmethod
    def _metallic_fill(size: tuple[int, int]) -> Image.Image:
        width, height = size
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")
        stops = (
            (0.00, (252, 254, 255)),
            (0.28, (203, 214, 223)),
            (0.50, (255, 255, 255)),
            (0.72, (155, 170, 183)),
            (1.00, (235, 241, 245)),
        )
        for y in range(height):
            t = y / max(1, height - 1)
            for i in range(len(stops) - 1):
                a_t, a = stops[i]
                b_t, b = stops[i + 1]
                if a_t <= t <= b_t:
                    u = (t - a_t) / max(1e-9, b_t - a_t)
                    rgb = tuple(round(a[j] * (1-u) + b[j] * u) for j in range(3))
                    draw.line((0, y, width, y), fill=(*rgb, 255))
                    break
        return layer

    @classmethod
    def _draw_metallic_text(
        cls,
        image: Image.Image,
        *,
        text: str,
        font,
        center_x: float,
        center_y: float,
        accent: tuple[int, int, int],
        outline_px: int,
        glow_radius: int,
    ) -> None:
        mask = cls._text_mask(image.size, text=text, font=font, center_x=center_x, center_y=center_y)
        # Black dimensional shadow offset downwards.
        shadow_mask = Image.new("L", image.size, 0)
        shadow_mask.paste(mask, (0, max(2, outline_px * 2)))
        shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(max(3, outline_px)))
        shadow = Image.new("RGBA", image.size, (0, 0, 0, 170))
        shadow.putalpha(shadow_mask.point(lambda p: round(p * 0.67)))
        image.alpha_composite(shadow)

        # Accent bloom is outside the glyph and remains subtle.
        glow_mask = mask.filter(ImageFilter.GaussianBlur(glow_radius))
        glow = Image.new("RGBA", image.size, (*accent, 0))
        glow.putalpha(glow_mask.point(lambda p: round(p * 0.19)))
        image.alpha_composite(glow)

        expanded = mask.filter(ImageFilter.MaxFilter(max(3, outline_px * 2 + 1)))
        outline_mask = ImageChops.subtract(expanded, mask)
        outline = Image.new("RGBA", image.size, (220, 228, 235, 0))
        outline.putalpha(outline_mask.point(lambda p: round(p * 0.55)))
        image.alpha_composite(outline)

        metal = cls._metallic_fill(image.size)
        metal.putalpha(mask)
        image.alpha_composite(metal)

    @classmethod
    def _draw_score_monument_v2(
        cls,
        image: Image.Image,
        *,
        box: tuple[int, int, int, int],
        home_score: int,
        away_score: int,
        font_path: str,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> str:
        base = ResultStatementStudyRenderer
        draw = ImageDraw.Draw(image, "RGBA")
        x0, y0, x1, y1 = box
        width, height = x1-x0, y1-y0
        cy = (y0+y1)/2
        left_cx = x0 + width*0.30
        right_cx = x0 + width*0.70
        sep_cx = (x0+x1)/2
        sample = max((str(home_score), str(away_score)), key=len)
        font = base._fit_font(draw, sample, font_path, round(width*0.31), round(height*0.84), round(height*0.94))
        sep_font = base._fit_font(draw, "–", font_path, round(width*0.10), round(height*0.25), round(height*0.26))

        cls._draw_metallic_text(image, text=str(home_score), font=font, center_x=left_cx, center_y=cy, accent=home_accent, outline_px=max(2, round(width*0.010)), glow_radius=max(10, round(width*0.025)))
        cls._draw_metallic_text(image, text=str(away_score), font=font, center_x=right_cx, center_y=cy, accent=away_accent, outline_px=max(2, round(width*0.010)), glow_radius=max(10, round(width*0.025)))
        draw = ImageDraw.Draw(image, "RGBA")
        base._centered_text(draw, text="–", font=sep_font, center_x=sep_cx, center_y=cy+1, fill=(205, 214, 222, 220))

        # Floating metallic rails below each number replace flat underlines.
        rail_y = y1 - max(4, round(height*0.025))
        rail_w = round(width*0.18)
        for cx2, accent in ((left_cx, home_accent), (right_cx, away_accent)):
            draw.rounded_rectangle((cx2-rail_w/2, rail_y-2, cx2+rail_w/2, rail_y+2), radius=2, fill=(*accent, 220))
            draw.line((cx2-rail_w/2, rail_y-4, cx2+rail_w/2, rail_y-4), fill=(235, 242, 247, 42), width=1)
        return f"{home_score}  –  {away_score}"

    @classmethod
    def _draw_identity_monument(
        cls,
        image: Image.Image,
        *,
        box: tuple[int, int, int, int],
        name: str,
        accent: tuple[int, int, int],
        font_path: str,
        winner: bool,
    ) -> None:
        base = ResultStatementStudyRenderer
        draw = ImageDraw.Draw(image, "RGBA")
        x0, y0, x1, y1 = box
        width, height = x1-x0, y1-y0
        cx = (x0+x1)/2
        shield_w = min(round(width*0.28), round(height*0.42), 70)
        shield_h = round(shield_w*1.16)
        cy = y0 + round(height*0.28)
        pts = [
            (cx-shield_w/2, cy-shield_h*0.36),
            (cx, cy-shield_h*0.50),
            (cx+shield_w/2, cy-shield_h*0.36),
            (cx+shield_w*0.44, cy+shield_h*0.18),
            (cx, cy+shield_h*0.50),
            (cx-shield_w*0.44, cy+shield_h*0.18),
        ]
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo, "RGBA")
        hd.polygon(pts, fill=(*accent, 48 if winner else 34))
        halo = halo.filter(ImageFilter.GaussianBlur(max(10, shield_w//3)))
        image.alpha_composite(halo)
        draw = ImageDraw.Draw(image, "RGBA")
        draw.polygon(pts, fill=(5, 12, 21, 178), outline=(*accent, 230))
        inner = [(cx+(px-cx)*0.72, cy+(py-cy)*0.72) for px, py in pts]
        draw.line(inner+[inner[0]], fill=(226, 236, 243, 105), width=1, joint="curve")
        dot = max(3, shield_w//13)
        draw.ellipse((cx-dot, cy-dot, cx+dot, cy+dot), fill=(*accent, 242))

        name_y = y0 + round(height*0.75)
        name_font = base._fit_font(draw, name, font_path, max(20, round(width*0.96)), max(18, round(height*0.21)), max(18, round(height*0.17)))
        base._centered_text(draw, text=name, font=name_font, center_x=cx, center_y=name_y, fill=(235, 241, 245, 250))
        if winner:
            line_w = round(width*0.48)
            line_y = y1 - max(4, round(height*0.025))
            draw.rounded_rectangle((cx-line_w/2, line_y-2, cx+line_w/2, line_y+2), radius=2, fill=(*accent, 235))

    def render(
        self,
        composition: ResultStatementComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
        context_asset: VerifiedContextAsset,
        home_name: str,
        away_name: str,
        home_score: int,
        away_score: int,
        headline: str,
        home_accent_hex: str,
        away_accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
        winner: str | None = None,
        focal_x_ratio: float = 0.50,
        focal_y_ratio: float = 0.46,
    ) -> PremiumHybridResultStudyReceipt:
        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not isinstance(context_asset, VerifiedContextAsset):
            raise TypeError("context_asset must be VerifiedContextAsset")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if not home_name.strip() or not away_name.strip() or not headline.strip():
            raise ValueError("team names and headline are required")
        if not isinstance(home_score, int) or isinstance(home_score, bool) or home_score < 0:
            raise ValueError("home_score must be a non-negative integer")
        if not isinstance(away_score, int) or isinstance(away_score, bool) or away_score < 0:
            raise ValueError("away_score must be a non-negative integer")
        if winner not in {None, "home", "away"}:
            raise ValueError("winner must be home, away or None")

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        context_path = target.with_name(target.stem + ".context.png")
        context_receipt: ContextSurfaceReceipt = VerifiedContextSurfaceRenderer().render(
            asset=context_asset,
            output_path=str(context_path),
            canvas_size=(profile.width, profile.height),
            accent_hex=brand_accent_hex,
            focal_x_ratio=focal_x_ratio,
            focal_y_ratio=focal_y_ratio,
        )

        with Image.open(context_path) as raw:
            image = raw.convert("RGBA")
        home_accent = self._rgb(home_accent_hex)
        away_accent = self._rgb(away_accent_hex)
        self._cinematic_integration(image, home_accent=home_accent, away_accent=away_accent)
        draw = ImageDraw.Draw(image, "RGBA")
        base = ResultStatementStudyRenderer

        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = base._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.50))
        hb = draw.textbbox((0, 0), headline, font=headline_font)
        center_x = profile.width/2
        center_y = (hy0+hy1)/2
        # Fine editorial rule and soft shadow rather than a headline box.
        rule_w = min(round((hx1-hx0)*0.40), round(profile.width*0.28))
        draw.line((center_x-rule_w/2, hy0-8, center_x+rule_w/2, hy0-8), fill=(229, 238, 244, 60), width=1)
        draw.text((center_x-(hb[2]-hb[0])/2+1, center_y-(hb[3]-hb[1])/2-hb[1]+3), headline, font=headline_font, fill=(0, 0, 0, 95))
        draw.text((center_x-(hb[2]-hb[0])/2, center_y-(hb[3]-hb[1])/2-hb[1]), headline, font=headline_font, fill=(239, 245, 249, 248))

        score_text = self._draw_score_monument_v2(
            image,
            box=self._box(composition.score_box, profile),
            home_score=home_score,
            away_score=away_score,
            font_path=font_path,
            home_accent=home_accent,
            away_accent=away_accent,
        )
        self._draw_identity_monument(
            image,
            box=self._box(composition.home_identity_box, profile),
            name=home_name,
            accent=home_accent,
            font_path=font_path,
            winner=winner == "home",
        )
        self._draw_identity_monument(
            image,
            box=self._box(composition.away_identity_box, profile),
            name=away_name,
            accent=away_accent,
            font_path=font_path,
            winner=winner == "away",
        )

        prebrand = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(prebrand, format="PNG", optimize=True)
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand),
            output_path=str(target),
            adaptive=composition.brand,
            profile=profile,
            accent_hex=brand_accent_hex,
        )
        prebrand.unlink(missing_ok=True)
        context_path.unlink(missing_ok=True)

        return PremiumHybridResultStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            width=profile.width,
            height=profile.height,
            score_text=score_text,
            home_name=home_name,
            away_name=away_name,
            context_asset_id=context_asset.asset_id,
            context_source_sha256=context_receipt.source_sha256,
            context_output_sha256=context_receipt.output_sha256,
            context_source_reference=context_receipt.source_reference,
            context_rights_basis=context_receipt.rights_basis,
            context_role="atmosphere_only_not_event_evidence",
            brand_zone=brand.zone,
            brand_width=brand.width,
            brand_height=brand.height,
            verified_context_contract=context_receipt.contract,
        )

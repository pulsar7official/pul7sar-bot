"""Photographic premium-hybrid Result Statement study renderer.

This is an additive visual-quality benchmark for the Result family. A rights-aware
verified context photograph may provide atmosphere only; exact score, team names,
identity surfaces and PUL7SAR branding remain deterministic code-owned layers.
The renderer never treats the context image as evidence of the match, venue or
club identity and remains study-only until real fact-locked production assets are
registered.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

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
    generator_used: bool = False
    network_used_by_renderer: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-premium-hybrid-result-study-renderer-v1-photographic-context"

    def __post_init__(self) -> None:
        if self.context_role != "atmosphere_only_not_event_evidence":
            raise ValueError("PREMIUM_HYBRID_CONTEXT_MAY_ONLY_OWN_ATMOSPHERE")
        if not self.club_identity_scale_equal:
            raise ValueError("RESULT_CLUB_IDENTITY_SCALE_MUST_REMAIN_EQUAL")
        if not self.home_identity_placeholder_used or not self.away_identity_placeholder_used:
            raise ValueError("STUDY_RENDERER_EXPECTS_EXPLICIT_NON_CREST_PLACEHOLDERS")
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
        """Add optical depth and club-owned light without replacing photograph facts."""
        width, height = image.size

        # Strong lower optical falloff gives score typography a photographic stage
        # instead of a flat card while preserving visible context in the upper half.
        lower = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lower, "RGBA")
        for y in range(round(height * 0.30), height):
            t = (y - height * 0.30) / (height * 0.70)
            alpha = round(28 + 148 * (t ** 1.55))
            ld.line((0, y, width, y), fill=(2, 6, 12, min(190, alpha)))
        image.alpha_composite(lower)

        # Two restrained optical blooms establish club tension while avoiding large
        # solid halves. Both sides have the same geometry and differ only in color.
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        r = round(max(width, height) * 0.34)
        cy = round(height * 0.58)
        gd.ellipse((-round(r * 0.62), cy-r, round(r * 1.38), cy+r), fill=(*home_accent, 82))
        gd.ellipse((width-round(r * 1.38), cy-r, width+round(r * 0.62), cy+r), fill=(*away_accent, 70))
        glow = glow.filter(ImageFilter.GaussianBlur(max(28, round(width * 0.075))))
        image.alpha_composite(glow)

        # A quiet central shaft pulls the eye toward the score monument. It is an
        # optical device only and conveys no match/event fact.
        shaft = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shaft, "RGBA")
        cx = width // 2
        top = round(height * 0.12)
        bottom = round(height * 0.72)
        half_top = round(width * 0.035)
        half_bottom = round(width * 0.18)
        sd.polygon(
            ((cx-half_top, top), (cx+half_top, top), (cx+half_bottom, bottom), (cx-half_bottom, bottom)),
            fill=(232, 241, 248, 14),
        )
        shaft = shaft.filter(ImageFilter.GaussianBlur(max(18, round(width * 0.04))))
        image.alpha_composite(shaft)

        # Edge vignette is blurred to avoid a template/card appearance.
        edge = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ed = ImageDraw.Draw(edge, "RGBA")
        side = round(width * 0.085)
        ed.rectangle((0, 0, side, height), fill=(0, 0, 0, 95))
        ed.rectangle((width-side, 0, width, height), fill=(0, 0, 0, 95))
        ed.rectangle((0, 0, width, round(height * 0.06)), fill=(0, 0, 0, 40))
        edge = edge.filter(ImageFilter.GaussianBlur(max(22, round(width * 0.045))))
        image.alpha_composite(edge)

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
        headline_font = base._fit_font(
            draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.50)
        )
        base._centered_text(
            draw,
            text=headline,
            font=headline_font,
            center_x=profile.width/2,
            center_y=(hy0+hy1)/2,
            fill=(226, 234, 240, 240),
        )

        score_text = base._draw_score_monument(
            draw,
            box=self._box(composition.score_box, profile),
            home_score=home_score,
            away_score=away_score,
            font_path=font_path,
            home_accent=home_accent,
            away_accent=away_accent,
        )
        base._draw_identity_anchor(
            draw,
            box=self._box(composition.home_identity_box, profile),
            name=home_name,
            accent=home_accent,
            font_path=font_path,
            winner=winner == "home",
        )
        base._draw_identity_anchor(
            draw,
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

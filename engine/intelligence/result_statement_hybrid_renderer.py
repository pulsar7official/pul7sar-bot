"""Production-shaped Result Statement hybrid renderer.

A semantically admitted cinematic base scene provides atmosphere only. Exact club
crests, score, readable text and PUL7SAR branding are deterministic post-layers.
No placeholder identity marks are used in this path.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.assets import AssetRole
from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmission
from engine.intelligence.exact_raster_asset import ExactRasterAsset, ExactRasterAssetCompositor
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposition
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer


@dataclass(frozen=True)
class ResultStatementHybridReceipt:
    output_path: str
    output_sha256: str
    base_scene_sha256: str
    base_quality_tier: str
    home_crest_sha256: str
    away_crest_sha256: str
    score_text: str
    exact_crests_used: bool
    exact_score_used: bool
    generated_score_used: bool
    generated_brand_used: bool
    loser_degraded: bool
    brand_zone: str
    brand_width: int
    brand_height: int
    publication_ready: bool = False
    contract: str = "pul7sar-result-statement-hybrid-renderer-v1-cinematic-exact"

    def __post_init__(self) -> None:
        if not self.exact_crests_used or not self.exact_score_used:
            raise ValueError("RESULT_HYBRID_REQUIRES_EXACT_CRESTS_AND_SCORE")
        if self.generated_score_used or self.generated_brand_used:
            raise ValueError("RESULT_HYBRID_GENERATOR_MAY_NOT_OWN_SCORE_OR_BRAND")
        if self.loser_degraded:
            raise ValueError("RESULT_HYBRID_MAY_NOT_DEGRADE_LOSER")
        if self.publication_ready:
            raise ValueError("HYBRID_RENDERER_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class ResultStatementHybridRenderer:
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
    def _assert_crest(asset: ExactRasterAsset, role_name: str) -> None:
        if asset.reference.role is not AssetRole.TEAM_CREST:
            raise ValueError(f"{role_name} must use TEAM_CREST asset role")
        asset.verified_path()

    @staticmethod
    def _readability_layer(image: Image.Image, *, score_box: tuple[int, int, int, int]) -> None:
        """Add a soft central exposure pocket without covering the cinematic base."""
        x0, y0, x1, y1 = score_box
        width, height = image.size
        veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(veil, "RGBA")
        pad_x = round((x1 - x0) * 0.35)
        pad_y = round((y1 - y0) * 0.70)
        draw.rounded_rectangle(
            (max(0, x0 - pad_x), max(0, y0 - pad_y), min(width, x1 + pad_x), min(height, y1 + pad_y)),
            radius=max(24, round(width * 0.05)),
            fill=(1, 5, 9, 118),
        )
        veil = veil.filter(ImageFilter.GaussianBlur(max(18, round(width * 0.035))))
        image.alpha_composite(veil)

    @classmethod
    def _draw_exact_identity(
        cls,
        image: Image.Image,
        *,
        box: tuple[int, int, int, int],
        crest: ExactRasterAsset,
        name: str,
        accent: tuple[int, int, int],
        font_path: str,
        winner: bool,
    ) -> None:
        x0, y0, x1, y1 = box
        width, height = x1 - x0, y1 - y0
        crest_box = (x0, y0, x1, y0 + round(height * 0.64))
        ExactRasterAssetCompositor.composite(image, asset=crest, box=crest_box, padding_ratio=0.12)
        draw = ImageDraw.Draw(image, "RGBA")
        name_font = ResultStatementStudyRenderer._fit_font(
            draw, name, font_path,
            max(20, round(width * 0.96)), max(18, round(height * 0.22)), max(18, round(height * 0.17)),
        )
        ResultStatementStudyRenderer._centered_text(
            draw, text=name, font=name_font,
            center_x=(x0 + x1) / 2, center_y=y0 + round(height * 0.79),
            fill=(236, 241, 245, 255),
        )
        if winner:
            line_w = round(width * 0.52)
            cy = y1 - max(5, round(height * 0.035))
            cx = (x0 + x1) / 2
            draw.rounded_rectangle((cx-line_w/2, cy-2, cx+line_w/2, cy+2), radius=2, fill=(*accent, 238))

    def render(
        self,
        composition: ResultStatementComposition,
        *,
        admission: BaseSceneCompositionAdmission,
        profile: PlatformImageProfile,
        output_path: str,
        home_crest: ExactRasterAsset,
        away_crest: ExactRasterAsset,
        home_name: str,
        away_name: str,
        home_score: int,
        away_score: int,
        headline: str,
        home_accent_hex: str,
        away_accent_hex: str,
        brand_accent_hex: str,
        font_path: str,
        winner: str | None,
    ) -> ResultStatementHybridReceipt:
        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(admission, BaseSceneCompositionAdmission):
            raise TypeError("admission must be BaseSceneCompositionAdmission")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if winner not in {None, "home", "away"}:
            raise ValueError("winner must be home, away or None")
        for score, label in ((home_score, "home_score"), (away_score, "away_score")):
            if not isinstance(score, int) or isinstance(score, bool) or score < 0:
                raise ValueError(f"{label} must be a non-negative integer")
        if not home_name.strip() or not away_name.strip() or not headline.strip():
            raise ValueError("team names and headline are required")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        self._assert_crest(home_crest, "home_crest")
        self._assert_crest(away_crest, "away_crest")
        admission.assert_bytes_unchanged()
        if (admission.provenance.width, admission.provenance.height) != (profile.width, profile.height):
            raise ValueError("admitted base scene does not match platform profile")

        def rgb(value: str) -> tuple[int, int, int]:
            text = value.strip().upper()
            if len(text) != 7 or not text.startswith("#"):
                raise ValueError("accent must be #RRGGBB")
            return tuple(int(text[i:i+2], 16) for i in (1, 3, 5))

        home_accent, away_accent = rgb(home_accent_hex), rgb(away_accent_hex)
        with Image.open(admission.png_path) as base:
            image = base.convert("RGBA")
        score_box = self._box(composition.score_box, profile)
        self._readability_layer(image, score_box=score_box)
        draw = ImageDraw.Draw(image, "RGBA")

        hx0, hy0, hx1, hy1 = self._box(composition.headline_box, profile)
        headline_font = ResultStatementStudyRenderer._fit_font(draw, headline, font_path, hx1-hx0, hy1-hy0, round((hy1-hy0)*0.50))
        ResultStatementStudyRenderer._centered_text(
            draw, text=headline, font=headline_font,
            center_x=profile.width/2, center_y=(hy0+hy1)/2,
            fill=(235, 241, 246, 244),
        )
        score_text = ResultStatementStudyRenderer._draw_score_monument(
            draw, box=score_box, home_score=home_score, away_score=away_score,
            font_path=font_path, home_accent=home_accent, away_accent=away_accent,
        )
        self._draw_exact_identity(
            image, box=self._box(composition.home_identity_box, profile), crest=home_crest,
            name=home_name, accent=home_accent, font_path=font_path, winner=winner == "home",
        )
        self._draw_exact_identity(
            image, box=self._box(composition.away_identity_box, profile), crest=away_crest,
            name=away_name, accent=away_accent, font_path=font_path, winner=winner == "away",
        )

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(prebrand, format="PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        prebrand.unlink(missing_ok=True)
        return ResultStatementHybridReceipt(
            output_path=str(target), output_sha256=self._sha(target),
            base_scene_sha256=admission.png_sha256, base_quality_tier=admission.quality_tier.value,
            home_crest_sha256=home_crest.sha256, away_crest_sha256=away_crest.sha256,
            score_text=score_text, exact_crests_used=True, exact_score_used=True,
            generated_score_used=False, generated_brand_used=False, loser_degraded=False,
            brand_zone=brand.zone, brand_width=brand.width, brand_height=brand.height,
        )

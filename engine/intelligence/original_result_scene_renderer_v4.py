"""Dynamic original Result Scene V4 for PUL7SAR.

V4 keeps exact club identity stable while the visual composition is selected from
story-driven families with anti-repetition memory. It reuses no source photograph,
performs no network call, never fabricates a crest, and keeps the exact score and
PUL7SAR brand deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.club_identity_layer import ClubIdentity, ClubIdentityLayerRenderer
from engine.intelligence.original_result_scene_renderer import OriginalResultSceneRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposition
from engine.intelligence.result_visual_variation import (
    ResultStorySignals,
    ResultVisualFamily,
    ResultVisualVariation,
    ResultVisualVariationEngine,
)


@dataclass(frozen=True)
class OriginalResultSceneV4Receipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    score_text: str
    visual_family: str
    variation_seed: int
    anti_repetition_applied: bool
    home_crest_used: bool
    away_crest_used: bool
    fabricated_crest_used: bool
    score_scale: float
    scene_origin: str = "100_percent_code_generated_original_pixels_plus_exact_local_assets"
    source_photo_used: bool = False
    generator_used: bool = False
    network_used: bool = False
    container_panel_used: bool = False
    perspective_grid_used: bool = False
    decorative_pulse_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-original-result-scene-renderer-v4-dynamic-club-identity"


class OriginalResultSceneRendererV4(OriginalResultSceneRenderer):
    CONTRACT = "pul7sar-original-result-scene-renderer-v4-dynamic-club-identity"

    @staticmethod
    def _score_font_path(font_path: str) -> str:
        base = Path(font_path)
        candidates = (
            base.with_name("DejaVuSansCondensed-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"),
            base,
        )
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        raise FileNotFoundError(font_path)

    @classmethod
    def _family_world(cls, image, *, variation: ResultVisualVariation, left, right) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer, "RGBA")
        family = variation.family
        density = variation.atmosphere_density

        if family is ResultVisualFamily.CENTRAL_MONUMENT:
            d.ellipse((w*.22, h*.29, w*.78, h*.62), fill=(240, 244, 248, int(22*density)))
            d.rectangle((w*.495, h*.22, w*.505, h*.69), fill=(228, 235, 241, int(10*density)))
        elif family is ResultVisualFamily.OFFSET_DUEL:
            d.polygon([(0, h*.29), (w*.47, h*.43), (w*.36, h*.73), (0, h*.66)], fill=(*left, int(34*density)))
            d.polygon([(w, h*.29), (w*.53, h*.43), (w*.64, h*.73), (w, h*.66)], fill=(*right, int(34*density)))
            d.line((w*.5, h*.29, w*.5, h*.72), fill=(236, 240, 244, int(34*density)), width=2)
        elif family is ResultVisualFamily.VERTICAL_TENSION:
            for x, color in ((w*.35, left), (w*.65, right)):
                d.polygon([(x-w*.055, h*.18), (x+w*.035, h*.18), (x+w*.16, h*.74), (x-w*.14, h*.74)], fill=(*color, int(24*density)))
            d.ellipse((w*.30, h*.23, w*.70, h*.56), fill=(245, 248, 250, int(14*density)))
        elif family is ResultVisualFamily.WIDE_ARENA:
            d.arc((w*.04, h*.32, w*.96, h*.84), 194, 346, fill=(228, 235, 242, int(42*density)), width=3)
            d.arc((w*.10, h*.38, w*.90, h*.80), 198, 342, fill=(*left, int(26*density)), width=2)
            d.arc((w*.10, h*.38, w*.90, h*.80), 18, 162, fill=(*right, int(26*density)), width=2)
        else:  # QUIET_EDITORIAL
            d.ellipse((w*.30, h*.31, w*.70, h*.57), fill=(235, 241, 246, int(13*density)))
            d.line((w*.19, h*.72, w*.81, h*.72), fill=(222, 229, 235, int(18*density)), width=1)

        image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(10, int(w*.022)))))

    @classmethod
    def _dynamic_monument(cls, image, *, home_score: int, away_score: int, font_path: str, left, right, variation: ResultVisualVariation) -> str:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        d = ImageDraw.Draw(image, "RGBA")
        score_font_path = cls._score_font_path(font_path)
        max_w = int(w * .205 * variation.score_scale / .72)
        max_h = int(h * .185 * variation.score_scale / .72)
        start = int(h * .168 * variation.score_scale / .72)
        font = cls._fit_font(d, str(max(home_score, away_score)), score_font_path, max_w, max_h, start)
        dash = cls._fit_font(d, "–", score_font_path, int(w*.055), int(h*.045), int(h*.040))
        cy = h * variation.score_center_y
        bias = w * variation.camera_bias
        left_x = w * (0.5 - variation.score_spread/2) + bias
        right_x = w * (0.5 + variation.score_spread/2) + bias

        halo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        q = ImageDraw.Draw(halo, "RGBA")
        q.ellipse((w*.25+bias, cy-h*.11, w*.75+bias, cy+h*.12), fill=(238, 243, 247, 15))
        image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(max(32, int(w*.065)))))
        cls._metal_text(image, str(home_score), cx=left_x, cy=cy, font=font, accent=left)
        cls._metal_text(image, str(away_score), cx=right_x, cy=cy, font=font, accent=right)
        d = ImageDraw.Draw(image, "RGBA")
        cls._center(d, "–", dash, w/2+bias, cy+2, (174, 185, 196, 190))
        return f"{home_score}–{away_score}"

    @classmethod
    def _dynamic_identity(cls, image, *, headline: str, home: str, away: str, font_path: str, left, right, winner: str | None, variation: ResultVisualVariation) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        d = ImageDraw.Draw(image, "RGBA")
        kicker = cls._fit_font(d, headline, font_path, int(w*.47), int(h*.032), int(h*.025))
        cls._center(d, headline.upper(), kicker, w/2, h*.168, (212, 221, 229, 204))
        label = cls._fit_font(d, "FULL TIME", font_path, int(w*.13), int(h*.020), int(h*.015))
        cls._center(d, "FULL TIME", label, w/2, h*.232, (145, 158, 171, 158))

        cy = h * variation.identity_center_y
        positions = (.285, .715) if variation.family in {ResultVisualFamily.OFFSET_DUEL, ResultVisualFamily.WIDE_ARENA} else (.31, .69)
        name_font = cls._fit_font(d, max(home, away, key=len), font_path, int(w*.27), int(h*.031), int(h*.024))
        for side, x, name, accent in (("home", positions[0], home, left), ("away", positions[1], away, right)):
            if winner == side:
                glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow, "RGBA")
                gd.ellipse((w*x-w*.070, cy-h*.022, w*x+w*.070, cy+h*.022), fill=(*accent, 28))
                image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(max(8, int(w*.016)))))
                d = ImageDraw.Draw(image, "RGBA")
            cls._center(d, name.upper(), name_font, w*x, cy, (226, 233, 239, 226))
            d.ellipse((w*x-3, cy+h*.028-3, w*x+3, cy+h*.028+3), fill=(*accent, 205))

    def render(self, composition: ResultStatementComposition, *, profile: PlatformImageProfile, output_path: str,
               home_name: str, away_name: str, home_score: int, away_score: int, headline: str,
               home_accent_hex: str, away_accent_hex: str, brand_accent_hex: str, font_path: str,
               winner: str | None = None, seed: int = 18001, story_key: str | None = None,
               recent_visual_families: tuple[ResultVisualFamily, ...] = (), derby: bool = False,
               qualification: bool = False, comeback: bool = False, late_winner: bool = False,
               competition_stage: str = "regular", home_crest_path: str | None = None,
               away_crest_path: str | None = None) -> OriginalResultSceneV4Receipt:
        from PIL import Image
        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if winner not in {None, "home", "away"}:
            raise ValueError("winner must be home, away or None")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (home_score, away_score)):
            raise ValueError("scores must be non-negative integers")
        if not home_name.strip() or not away_name.strip() or not headline.strip():
            raise ValueError("team names and headline are required")

        variation = ResultVisualVariationEngine().choose(
            story_key=story_key or f"{home_name}|{away_name}|{home_score}-{away_score}|{headline}",
            signals=ResultStorySignals(
                home_score, away_score, winner,
                competition_stage=competition_stage,
                derby=derby,
                qualification=qualification,
                comeback=comeback,
                late_winner=late_winner,
                recent_visual_families=recent_visual_families,
            ),
            seed=seed,
        )
        left = self._rgb(home_accent_hex)
        right = self._rgb(away_accent_hex)
        image = Image.new("RGBA", (profile.width, profile.height), (7, 12, 20, 255))
        self._base_world(image, left=left, right=right, seed=variation.seed)
        self._family_world(image, variation=variation, left=left, right=right)
        score_text = self._dynamic_monument(image, home_score=home_score, away_score=away_score, font_path=font_path, left=left, right=right, variation=variation)
        crest_evidence = ClubIdentityLayerRenderer.render(
            image,
            home=ClubIdentity(home_name, home_accent_hex, home_crest_path),
            away=ClubIdentity(away_name, away_accent_hex, away_crest_path),
        )
        self._dynamic_identity(image, headline=headline, home=home_name, away=away_name, font_path=font_path, left=left, right=right, winner=winner, variation=variation)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        pre = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(pre, "PNG")
        AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(pre), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        pre.unlink(missing_ok=True)
        return OriginalResultSceneV4Receipt(
            output_path=str(target), output_sha256=self._sha(target), width=profile.width, height=profile.height,
            score_text=score_text, visual_family=variation.family.value, variation_seed=variation.seed,
            anti_repetition_applied=variation.anti_repetition_applied,
            home_crest_used=crest_evidence.home_crest_used, away_crest_used=crest_evidence.away_crest_used,
            fabricated_crest_used=crest_evidence.fabricated_crest_used, score_scale=variation.score_scale,
        )

"""Independent deterministic Result Statement study renderer for PUL7SAR.

This renderer exists to prove that result coverage has its own pixel language.
It does not inherit the Transfer renderer. Exact score, readable text, balanced
club identity surfaces and PUL7SAR branding are deterministic. Benchmark club
identity marks are explicit placeholders and therefore publication is blocked.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox, ResultStatementComposition


@dataclass(frozen=True)
class ResultStatementStudyReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    score_text: str
    home_name: str
    away_name: str
    home_identity_placeholder_used: bool
    away_identity_placeholder_used: bool
    club_identity_scale_equal: bool
    loser_treatment: str
    brand_zone: str
    brand_width: int
    brand_height: int
    brand_overlay_contract: str
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-result-statement-study-renderer-v1"


class ResultStatementStudyRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _box(box: NormalizedBox, profile: PlatformImageProfile) -> tuple[int, int, int, int]:
        x0 = round(box.x * profile.width)
        y0 = round(box.y * profile.height)
        x1 = round((box.x + box.width) * profile.width)
        y1 = round((box.y + box.height) * profile.height)
        return x0, y0, x1, y1

    @staticmethod
    def _fit_font(draw, text: str, font_path: str, max_width: int, max_height: int, start: int):
        from PIL import ImageFont

        size = max(10, start)
        while size > 10:
            font = ImageFont.truetype(font_path, size=size)
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            if right - left <= max_width and bottom - top <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=10)

    @classmethod
    def _draw_identity_placeholder(
        cls,
        draw,
        *,
        box: tuple[int, int, int, int],
        name: str,
        accent: tuple[int, int, int],
        font_path: str,
    ) -> None:
        x0, y0, x1, y1 = box
        width = x1 - x0
        height = y1 - y0
        diameter = max(24, min(width, round(height * 0.54)))
        cx = x0 + width // 2
        cy = y0 + round(height * 0.32)
        r = diameter // 2
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*accent, 46), outline=(*accent, 225), width=max(2, diameter // 24))
        initial = (name.strip()[:1] or "?").upper()
        initial_font = cls._fit_font(draw, initial, font_path, round(diameter * 0.72), round(diameter * 0.72), round(diameter * 0.58))
        ib = draw.textbbox((0, 0), initial, font=initial_font)
        draw.text((cx - (ib[2] - ib[0]) / 2, cy - (ib[3] - ib[1]) / 2 - ib[1]), initial, font=initial_font, fill=(238, 244, 249, 255))

        name_top = cy + r + max(8, round(height * 0.05))
        name_font = cls._fit_font(draw, name, font_path, width, max(18, y1 - name_top), max(16, round(height * 0.16)))
        nb = draw.textbbox((0, 0), name, font=name_font)
        draw.text((cx - (nb[2] - nb[0]) / 2, name_top), name, font=name_font, fill=(228, 235, 241, 255))

    def render(
        self,
        composition: ResultStatementComposition,
        *,
        profile: PlatformImageProfile,
        output_path: str,
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
    ) -> ResultStatementStudyReceipt:
        from PIL import Image, ImageDraw

        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if not isinstance(home_score, int) or isinstance(home_score, bool) or home_score < 0:
            raise ValueError("home_score must be a non-negative integer")
        if not isinstance(away_score, int) or isinstance(away_score, bool) or away_score < 0:
            raise ValueError("away_score must be a non-negative integer")
        if not home_name.strip() or not away_name.strip() or not headline.strip():
            raise ValueError("team names and headline are required")
        if winner not in {None, "home", "away"}:
            raise ValueError("winner must be home, away or None")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)

        home_accent = self._rgb(home_accent_hex)
        away_accent = self._rgb(away_accent_hex)
        image = Image.new("RGBA", (profile.width, profile.height), (3, 10, 17, 255))
        draw = ImageDraw.Draw(image, "RGBA")

        # Restrained sports atmosphere: depth and two club-owned light fields,
        # without forcing a pitch or depicting defeat/humiliation.
        for y in range(profile.height):
            t = y / max(1, profile.height - 1)
            base = round(7 + 9 * (1.0 - t))
            draw.line((0, y, profile.width, y), fill=(base, base + 5, base + 11, 255))
        draw.ellipse(
            (-round(profile.width * 0.35), round(profile.height * 0.12), round(profile.width * 0.58), round(profile.height * 0.88)),
            fill=(*home_accent, 22),
        )
        draw.ellipse(
            (round(profile.width * 0.42), round(profile.height * 0.12), round(profile.width * 1.35), round(profile.height * 0.88)),
            fill=(*away_accent, 22),
        )
        center_x = profile.width // 2
        draw.line((center_x, round(profile.height * 0.27), center_x, round(profile.height * 0.68)), fill=(255, 255, 255, 20), width=1)

        headline_box = self._box(composition.headline_box, profile)
        hx0, hy0, hx1, hy1 = headline_box
        headline_font = self._fit_font(draw, headline, font_path, hx1 - hx0, hy1 - hy0, round((hy1 - hy0) * 0.56))
        hb = draw.textbbox((0, 0), headline, font=headline_font)
        draw.text((profile.width / 2 - (hb[2] - hb[0]) / 2, hy0 + (hy1 - hy0 - (hb[3] - hb[1])) / 2 - hb[1]), headline, font=headline_font, fill=(238, 243, 247, 255))

        home_box = self._box(composition.home_identity_box, profile)
        away_box = self._box(composition.away_identity_box, profile)
        self._draw_identity_placeholder(draw, box=home_box, name=home_name, accent=home_accent, font_path=font_path)
        self._draw_identity_placeholder(draw, box=away_box, name=away_name, accent=away_accent, font_path=font_path)

        score_box = self._box(composition.score_box, profile)
        sx0, sy0, sx1, sy1 = score_box
        score_text = f"{home_score}  –  {away_score}"
        score_font = self._fit_font(draw, score_text, font_path, sx1 - sx0, sy1 - sy0, round((sy1 - sy0) * 0.72))
        sb = draw.textbbox((0, 0), score_text, font=score_font)
        draw.text((profile.width / 2 - (sb[2] - sb[0]) / 2, sy0 + (sy1 - sy0 - (sb[3] - sb[1])) / 2 - sb[1]), score_text, font=score_font, fill=(248, 250, 252, 255))

        # Winner emphasis is a restrained line only; neither identity is reduced,
        # faded, crossed out, tilted or visually degraded.
        if winner is not None:
            chosen_box = home_box if winner == "home" else away_box
            chosen_accent = home_accent if winner == "home" else away_accent
            x0, _, x1, y1 = chosen_box
            draw.rounded_rectangle((x0, y1 - 5, x1, y1), radius=2, fill=(*chosen_accent, 220))

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        prebrand = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(prebrand, format="PNG")

        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(prebrand),
            output_path=str(target),
            adaptive=composition.brand,
            profile=profile,
            accent_hex=brand_accent_hex,
        )
        prebrand.unlink(missing_ok=True)

        return ResultStatementStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            width=profile.width,
            height=profile.height,
            score_text=score_text,
            home_name=home_name,
            away_name=away_name,
            home_identity_placeholder_used=True,
            away_identity_placeholder_used=True,
            club_identity_scale_equal=composition.club_identity_scale_equal,
            loser_treatment=composition.loser_treatment,
            brand_zone=brand.zone,
            brand_width=brand.width,
            brand_height=brand.height,
            brand_overlay_contract=brand.contract,
        )

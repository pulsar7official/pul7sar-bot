"""Independent deterministic Result Statement study renderer for PUL7SAR.

This renderer proves that result coverage has its own pixel language. It does not
inherit the Transfer renderer. Exact score, readable text, balanced club identity
surfaces and PUL7SAR branding are deterministic. Benchmark club identity marks
are neutral placeholders and therefore publication is blocked.

The visual grammar is a score monument, not a scoreboard card: dark editorial
space, restrained club-color light, one dominant score, equal identity anchors
and a quiet adaptive PUL7SAR signature.
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
    visual_grammar: str = "score_monument"
    full_pitch_used: bool = False
    giant_color_panels_used: bool = False
    identity_initial_letters_used: bool = False
    generator_used: bool = False
    network_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-result-statement-study-renderer-v2-score-monument"


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

    @staticmethod
    def _centered_text(draw, *, text: str, font, center_x: float, center_y: float, fill) -> None:
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        draw.text(
            (center_x - (right - left) / 2, center_y - (bottom - top) / 2 - top),
            text,
            font=font,
            fill=fill,
        )

    @classmethod
    def _draw_identity_anchor(
        cls,
        draw,
        *,
        box: tuple[int, int, int, int],
        name: str,
        accent: tuple[int, int, int],
        font_path: str,
        winner: bool,
    ) -> None:
        """Draw equal neutral identity anchors without pretending to be real crests."""
        x0, y0, x1, y1 = box
        width = x1 - x0
        height = y1 - y0
        cx = (x0 + x1) / 2

        mark_d = max(44, min(round(height * 0.46), round(width * 0.34), 82))
        mark_r = mark_d // 2
        mark_cy = y0 + round(height * 0.30)
        stroke = max(2, mark_d // 24)

        # Abstract neutral double ring: deliberately not a fictional club crest.
        draw.ellipse(
            (cx - mark_r, mark_cy - mark_r, cx + mark_r, mark_cy + mark_r),
            fill=(8, 15, 24, 205),
            outline=(*accent, 220),
            width=stroke,
        )
        inner = round(mark_r * 0.58)
        draw.ellipse(
            (cx - inner, mark_cy - inner, cx + inner, mark_cy + inner),
            outline=(232, 239, 245, 105),
            width=max(1, stroke - 1),
        )
        dot = max(3, mark_d // 15)
        draw.ellipse(
            (cx - dot, mark_cy - dot, cx + dot, mark_cy + dot),
            fill=(*accent, 235),
        )

        name_y = y0 + round(height * 0.72)
        name_font = cls._fit_font(
            draw,
            name,
            font_path,
            max(20, round(width * 0.94)),
            max(18, round(height * 0.22)),
            max(18, round(height * 0.18)),
        )
        cls._centered_text(
            draw,
            text=name,
            font=name_font,
            center_x=cx,
            center_y=name_y,
            fill=(225, 232, 238, 255),
        )

        # Winner hierarchy is additive only. Loser receives no visual penalty.
        if winner:
            line_w = round(width * 0.48)
            line_y = y1 - max(4, round(height * 0.035))
            draw.rounded_rectangle(
                (cx - line_w / 2, line_y - 2, cx + line_w / 2, line_y + 2),
                radius=2,
                fill=(*accent, 235),
            )

    @classmethod
    def _draw_atmosphere(
        cls,
        image,
        *,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> None:
        """Create restrained club-owned light without large solid color panels."""
        from PIL import Image, ImageDraw, ImageFilter

        width, height = image.size
        draw = ImageDraw.Draw(image, "RGBA")

        # Deep editorial gradient.
        for y in range(height):
            t = y / max(1, height - 1)
            r = round(11 - 5 * t)
            g = round(18 - 6 * t)
            b = round(27 - 7 * t)
            draw.line((0, y, width, y), fill=(r, g, b, 255))

        # Blurred side light, deliberately narrow enough to preserve dark space.
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse(
            (-round(width * 0.28), round(height * 0.18), round(width * 0.38), round(height * 0.77)),
            fill=(*home_accent, 88),
        )
        gd.ellipse(
            (round(width * 0.62), round(height * 0.18), round(width * 1.28), round(height * 0.77)),
            fill=(*away_accent, 72),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(24, round(width * 0.075))))
        image.alpha_composite(glow)

        draw = ImageDraw.Draw(image, "RGBA")
        # Sparse stadium-light rhythm at the upper horizon, not a literal stadium.
        horizon = round(height * 0.245)
        for i in range(13):
            x = round(width * (0.13 + i * 0.0615))
            alpha = 28 + (i % 3) * 11
            draw.ellipse((x - 2, horizon - 2, x + 2, horizon + 2), fill=(232, 239, 245, alpha))

        # Quiet framing lines and central axis; no card border.
        line_y = round(height * 0.515)
        draw.line((round(width * 0.17), line_y, round(width * 0.83), line_y), fill=(230, 238, 244, 24), width=1)
        center_x = width // 2
        draw.line((center_x, round(height * 0.265), center_x, round(height * 0.535)), fill=(230, 238, 244, 18), width=1)

        # Edge vignette through translucent overlays.
        vignette = Image.new("RGBA", image.size, (0, 0, 0, 0))
        vd = ImageDraw.Draw(vignette, "RGBA")
        side = round(width * 0.10)
        vd.rectangle((0, 0, side, height), fill=(0, 0, 0, 58))
        vd.rectangle((width - side, 0, width, height), fill=(0, 0, 0, 58))
        vd.rectangle((0, 0, width, round(height * 0.07)), fill=(0, 0, 0, 35))
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=max(18, round(width * 0.035))))
        image.alpha_composite(vignette)

    @classmethod
    def _draw_score_monument(
        cls,
        draw,
        *,
        box: tuple[int, int, int, int],
        home_score: int,
        away_score: int,
        font_path: str,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> str:
        x0, y0, x1, y1 = box
        width = x1 - x0
        height = y1 - y0
        cy = (y0 + y1) / 2
        left_cx = x0 + width * 0.30
        right_cx = x0 + width * 0.70
        separator_cx = (x0 + x1) / 2

        left_text = str(home_score)
        right_text = str(away_score)
        digit_max_w = round(width * 0.31)
        digit_font = cls._fit_font(
            draw,
            max((left_text, right_text), key=len),
            font_path,
            digit_max_w,
            round(height * 0.82),
            round(height * 0.90),
        )
        separator_font = cls._fit_font(draw, "–", font_path, round(width * 0.12), round(height * 0.30), round(height * 0.28))

        # Very soft text shadows preserve monument weight without a panel.
        for dx, dy, alpha in ((0, 7, 48), (0, 3, 62)):
            cls._centered_text(draw, text=left_text, font=digit_font, center_x=left_cx + dx, center_y=cy + dy, fill=(0, 0, 0, alpha))
            cls._centered_text(draw, text=right_text, font=digit_font, center_x=right_cx + dx, center_y=cy + dy, fill=(0, 0, 0, alpha))

        cls._centered_text(draw, text=left_text, font=digit_font, center_x=left_cx, center_y=cy, fill=(247, 249, 251, 255))
        cls._centered_text(draw, text=right_text, font=digit_font, center_x=right_cx, center_y=cy, fill=(247, 249, 251, 255))
        cls._centered_text(draw, text="–", font=separator_font, center_x=separator_cx, center_y=cy + 2, fill=(181, 192, 203, 215))

        accent_y = y1 - max(3, round(height * 0.03))
        line_w = round(width * 0.19)
        draw.rounded_rectangle((left_cx - line_w / 2, accent_y - 2, left_cx + line_w / 2, accent_y + 2), radius=2, fill=(*home_accent, 185))
        draw.rounded_rectangle((right_cx - line_w / 2, accent_y - 2, right_cx + line_w / 2, accent_y + 2), radius=2, fill=(*away_accent, 150))
        return f"{home_score}  –  {away_score}"

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
        image = Image.new("RGBA", (profile.width, profile.height), (6, 12, 20, 255))
        self._draw_atmosphere(image, home_accent=home_accent, away_accent=away_accent)
        draw = ImageDraw.Draw(image, "RGBA")

        headline_box = self._box(composition.headline_box, profile)
        hx0, hy0, hx1, hy1 = headline_box
        headline_font = self._fit_font(
            draw,
            headline,
            font_path,
            hx1 - hx0,
            hy1 - hy0,
            round((hy1 - hy0) * 0.52),
        )
        self._centered_text(
            draw,
            text=headline,
            font=headline_font,
            center_x=profile.width / 2,
            center_y=(hy0 + hy1) / 2,
            fill=(215, 223, 230, 235),
        )
        rule_w = round((hx1 - hx0) * 0.20)
        rule_y = hy1 + max(7, round(profile.height * 0.008))
        draw.rounded_rectangle(
            (profile.width / 2 - rule_w / 2, rule_y - 1, profile.width / 2 + rule_w / 2, rule_y + 1),
            radius=1,
            fill=(224, 232, 238, 70),
        )

        score_text = self._draw_score_monument(
            draw,
            box=self._box(composition.score_box, profile),
            home_score=home_score,
            away_score=away_score,
            font_path=font_path,
            home_accent=home_accent,
            away_accent=away_accent,
        )

        home_box = self._box(composition.home_identity_box, profile)
        away_box = self._box(composition.away_identity_box, profile)
        self._draw_identity_anchor(
            draw,
            box=home_box,
            name=home_name,
            accent=home_accent,
            font_path=font_path,
            winner=winner == "home",
        )
        self._draw_identity_anchor(
            draw,
            box=away_box,
            name=away_name,
            accent=away_accent,
            font_path=font_path,
            winner=winner == "away",
        )

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

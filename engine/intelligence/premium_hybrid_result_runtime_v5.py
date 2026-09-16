"""Cinematic editorial art direction for the premium-hybrid Result benchmark.

V5 removes the remaining scoreboard-template cues from V4. The photograph remains
visible and atmospheric; the score becomes a restrained central physical object;
club placeholders become quiet identity signatures instead of large shield cards.
No event fact, crest, readable copy or PUL7SAR brand is generated.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.premium_hybrid_result_runtime_v4 import (
    PremiumHybridResultStudyReceipt,
    PremiumHybridResultStudyRenderer as _V4Runtime,
)
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer


class PremiumHybridResultStudyRenderer(_V4Runtime):
    @staticmethod
    def _cinematic_integration(
        image: Image.Image,
        *,
        home_accent: tuple[int, int, int],
        away_accent: tuple[int, int, int],
    ) -> None:
        width, height = image.size

        # Filmic vertical exposure curve: preserve stadium detail above, build only
        # enough density around the score and lower identity zone for separation.
        exposure = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ed = ImageDraw.Draw(exposure, "RGBA")
        for y in range(height):
            t = y / max(1, height - 1)
            alpha = round(8 + 112 * (t ** 2.15))
            ed.line((0, y, width, y), fill=(1, 5, 11, alpha))
        image.alpha_composite(exposure)

        # A broad central pool replaces the obvious oval/card silhouette from V4.
        pool = Image.new("RGBA", image.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(pool, "RGBA")
        cx, cy = width // 2, round(height * 0.43)
        rx, ry = round(width * 0.43), round(height * 0.28)
        pd.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=(2, 7, 15, 66))
        pool = pool.filter(ImageFilter.GaussianBlur(max(58, round(width * 0.13))))
        image.alpha_composite(pool)

        # Club colour exists as symmetric light contamination only, never as cards.
        colour = Image.new("RGBA", image.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(colour, "RGBA")
        rr = round(max(width, height) * 0.33)
        yy = round(height * 0.56)
        cd.ellipse((-round(rr*.72), yy-rr, round(rr*1.28), yy+rr), fill=(*home_accent, 55))
        cd.ellipse((width-round(rr*1.28), yy-rr, width+round(rr*.72), yy+rr), fill=(*away_accent, 52))
        colour = colour.filter(ImageFilter.GaussianBlur(max(48, round(width * 0.11))))
        image.alpha_composite(colour)

        # One soft overhead shaft links the score to real stadium illumination.
        shaft = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shaft, "RGBA")
        top_y = -round(height * 0.08)
        bottom_y = round(height * 0.66)
        sd.polygon(
            (
                (round(width*.44), top_y),
                (round(width*.56), top_y),
                (round(width*.69), bottom_y),
                (round(width*.31), bottom_y),
            ),
            fill=(235, 243, 248, 17),
        )
        shaft = shaft.filter(ImageFilter.GaussianBlur(max(42, round(width * 0.09))))
        image.alpha_composite(shaft)

        # Natural vignette, deliberately softer than V4 and without perspective rails.
        edge = Image.new("RGBA", image.size, (0, 0, 0, 0))
        xd = ImageDraw.Draw(edge, "RGBA")
        side = round(width * 0.055)
        xd.rectangle((0, 0, side, height), fill=(0, 0, 0, 78))
        xd.rectangle((width-side, 0, width, height), fill=(0, 0, 0, 78))
        xd.rectangle((0, height-round(height*.05), width, height), fill=(0, 0, 0, 58))
        edge = edge.filter(ImageFilter.GaussianBlur(max(30, round(width * 0.065))))
        image.alpha_composite(edge)

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
        cy = (y0+y1)/2 - height*0.025
        left_cx = x0 + width*0.32
        right_cx = x0 + width*0.68
        sep_cx = (x0+x1)/2
        sample = max((str(home_score), str(away_score)), key=len)
        font = base._fit_font(draw, sample, font_path, round(width*0.27), round(height*0.74), round(height*0.82))
        sep_font = base._fit_font(draw, "–", font_path, round(width*0.075), round(height*0.18), round(height*0.19))

        cls._draw_metallic_text(
            image, text=str(home_score), font=font, center_x=left_cx, center_y=cy,
            accent=home_accent, outline_px=max(2, round(width*0.007)), glow_radius=max(9, round(width*0.020)),
        )
        cls._draw_metallic_text(
            image, text=str(away_score), font=font, center_x=right_cx, center_y=cy,
            accent=away_accent, outline_px=max(2, round(width*0.007)), glow_radius=max(9, round(width*0.020)),
        )
        draw = ImageDraw.Draw(image, "RGBA")
        base._centered_text(draw, text="–", font=sep_font, center_x=sep_cx, center_y=cy+1, fill=(213, 221, 228, 206))

        # Tiny accent sparks anchor club colour without underlining the digits.
        spark_y = y1 - max(10, round(height*0.055))
        for cx2, accent in ((left_cx, home_accent), (right_cx, away_accent)):
            r = max(2, round(width*0.005))
            draw.ellipse((cx2-r, spark_y-r, cx2+r, spark_y+r), fill=(*accent, 235))
            draw.ellipse((cx2-r*3, spark_y-r*3, cx2+r*3, spark_y+r*3), outline=(*accent, 62), width=1)
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

        # Placeholder identity is intentionally small and neutral. It proves exact
        # crest ownership is external without pretending to be a real club badge.
        icon_y = y0 + round(height*0.23)
        outer = min(round(width*0.055), round(height*0.09), 18)
        draw.ellipse((cx-outer, icon_y-outer, cx+outer, icon_y+outer), outline=(226, 235, 242, 185), width=max(1, outer//5))
        inner = max(2, round(outer*0.34))
        draw.ellipse((cx-inner, icon_y-inner, cx+inner, icon_y+inner), fill=(*accent, 235))

        name_font = base._fit_font(
            draw, name, font_path,
            round(width*0.84), round(height*0.20), round(height*0.15),
        )
        text_y = y0 + round(height*0.55)
        base._centered_text(draw, text=name, font=name_font, center_x=cx, center_y=text_y, fill=(239, 244, 247, 245))

        # Winner emphasis is limited to a slightly brighter micro-rule; geometry and
        # identity scale remain exactly equal for both clubs.
        rule_w = round(width*0.34)
        alpha = 220 if winner else 155
        rule_y = y0 + round(height*0.73)
        draw.rounded_rectangle((cx-rule_w/2, rule_y, cx+rule_w/2, rule_y+2), radius=1, fill=(*accent, alpha))


__all__ = ["PremiumHybridResultStudyReceipt", "PremiumHybridResultStudyRenderer"]

"""Deterministic premium sports-editorial study renderer for PUL7SAR Phase 18.

Version 2 is deliberately closer to the approved 7/10 visual language: stronger
stadium light, atmospheric depth, restrained tactical texture, two-level Arabic
headline hierarchy and a lower adaptive brand zone. It still uses no generator,
no legacy logo, and can never authorize publication.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import random

from engine.intelligence.brand_study_geometry import APPROVED_BRAND_STUDY_GEOMETRY
from engine.intelligence.brand_study_renderer import BrandStudyPlacement, BrandStudyRenderer
from engine.intelligence.visual_study_handoff import VisualStudyHandoff


@dataclass(frozen=True)
class EditorialSceneStudyReceipt:
    output_path: str
    output_sha256: str
    handoff_sha256: str
    accent_hex: str
    width: int
    height: int
    generator_used: bool = False
    legacy_logo_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-editorial-scene-study-renderer-v2"


class EditorialSceneStudyRenderer:
    WIDTH = 1080
    HEIGHT = 1350

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _display_text(text: str) -> str:
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    @staticmethod
    def _fit_font(draw, text: str, font_path: str, max_width: int, start_size: int, min_size: int = 30):
        from PIL import ImageFont
        for size in range(start_size, min_size - 1, -2):
            font = ImageFont.truetype(font_path, size)
            box = draw.textbbox((0, 0), text, font=font, stroke_width=1)
            if box[2] - box[0] <= max_width:
                return font
        return ImageFont.truetype(font_path, min_size)

    @staticmethod
    def _headline_lines(text: str) -> tuple[str, str | None]:
        words = tuple(word for word in text.strip().split() if word)
        if len(words) <= 3:
            return " ".join(words), None
        split = max(2, len(words) - 2)
        return " ".join(words[:split]), " ".join(words[split:])

    @staticmethod
    def _metallic_text(image, text: str, font, center_x: int, y: int, *, max_width: int):
        from PIL import Image, ImageDraw, ImageFilter
        draw = ImageDraw.Draw(image)
        box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        width, height = box[2] - box[0], box[3] - box[1]
        x = center_x - width // 2

        shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.text((x + 8, y + 10), text, font=font, fill=(0, 0, 0, 220), stroke_width=5, stroke_fill=(0, 0, 0, 220))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3))
        image.alpha_composite(shadow)

        mask = Image.new("L", image.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), text, font=font, fill=255, stroke_width=2, stroke_fill=255)
        gradient = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gradient)
        top = max(0, y)
        bottom = min(image.height, y + height + 20)
        for yy in range(top, bottom):
            t = (yy - top) / max(1, bottom - top - 1)
            if t < 0.32:
                c = int(250 - 55 * (t / 0.32))
            elif t < 0.67:
                c = int(195 + 35 * ((t - 0.32) / 0.35))
            else:
                c = int(230 - 95 * ((t - 0.67) / 0.33))
            gd.line((x - 10, yy, x + min(max_width, width) + 10, yy), fill=(c, c + min(8, 255-c), min(255, c + 14), 255))
        image.alpha_composite(Image.composite(gradient, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask))
        highlight = ImageDraw.Draw(image)
        highlight.text((x, y - 2), text, font=font, fill=(255, 255, 255, 42), stroke_width=1, stroke_fill=(255, 255, 255, 25))

    @staticmethod
    def _accent_text(image, text: str, font, center_x: int, y: int, accent: tuple[int, int, int]):
        from PIL import Image, ImageDraw, ImageFilter
        draw = ImageDraw.Draw(image)
        box = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        width = box[2] - box[0]
        x = center_x - width // 2
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((x, y), text, font=font, fill=(*accent, 230), stroke_width=5, stroke_fill=(*accent, 105))
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        image.alpha_composite(glow)
        d = ImageDraw.Draw(image)
        d.text((x + 5, y + 7), text, font=font, fill=(0, 0, 0, 210), stroke_width=3, stroke_fill=(0, 0, 0, 210))
        d.text((x, y), text, font=font, fill=(*accent, 255), stroke_width=2, stroke_fill=tuple(max(0, c - 50) for c in accent) + (255,))
        d.text((x, y - 2), text, font=font, fill=(255, 255, 255, 55))

    def render(self, handoff: VisualStudyHandoff, *, output_path: str, accent_hex: str, font_path: str, seed: int = 7007) -> EditorialSceneStudyReceipt:
        from PIL import Image, ImageDraw, ImageFilter, ImageFont

        if not isinstance(handoff, VisualStudyHandoff):
            raise TypeError("handoff must be VisualStudyHandoff")
        if not handoff.human_review_allowed or handoff.publication_ready:
            raise ValueError("handoff is not a human visual-study contract")
        if handoff.metadata.get("legacy_repo_logo_allowed") is not False:
            raise ValueError("legacy logo policy must be false")
        fpath = Path(font_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        accent = self._rgb(accent_hex)
        rng = random.Random(seed)

        # Base premium charcoal/navy atmosphere.
        image = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (3, 7, 13, 255))
        draw = ImageDraw.Draw(image)
        for y in range(self.HEIGHT):
            horizon = 1.0 - min(1.0, abs(y - 620) / 780)
            lower = max(0.0, (y - 760) / 590)
            base = (3 + int(6*horizon), 7 + int(10*horizon), 13 + int(16*horizon))
            tint = tuple(int(v * (0.032*horizon + 0.018*lower)) for v in accent)
            draw.line((0, y, self.WIDTH, y), fill=tuple(min(255, base[i] + tint[i]) for i in range(3)) + (255,))

        # Large atmospheric glows and diagonal editorial depth.
        atmosphere = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ad = ImageDraw.Draw(atmosphere)
        ad.ellipse((-280, 80, 520, 900), fill=(*accent, 24))
        ad.ellipse((650, 40, 1320, 760), fill=(210, 225, 245, 13))
        ad.polygon([(0, 250), (500, 80), (360, 1060), (0, 1140)], fill=(6, 17, 31, 115))
        ad.polygon([(1080, 160), (735, 250), (850, 1030), (1080, 910)], fill=(*accent, 14))
        atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(35))
        image = Image.alpha_composite(image, atmosphere)

        # Stadium floodlight banks with visible lamps and wide haze beams.
        lights = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lights)
        for side in (0, 1):
            bank_x = 90 if side == 0 else self.WIDTH - 90
            for row in range(3):
                for col in range(6):
                    cx = bank_x + (col - 2.5) * 22
                    cy = 105 + row * 22
                    ld.ellipse((cx-7, cy-7, cx+7, cy+7), fill=(245, 250, 255, 245))
            if side == 0:
                ld.polygon([(35, 145), (230, 160), (570, 865), (145, 640)], fill=(205, 225, 255, 23))
                ld.polygon([(65, 145), (165, 155), (390, 650), (190, 550)], fill=(*accent, 21))
            else:
                ld.polygon([(1045, 145), (850, 160), (510, 865), (935, 640)], fill=(205, 225, 255, 23))
                ld.polygon([(1015, 145), (915, 155), (690, 650), (890, 550)], fill=(*accent, 21))
        blurred = lights.filter(ImageFilter.GaussianBlur(20))
        image = Image.alpha_composite(image, blurred)
        image = Image.alpha_composite(image, lights)

        # Stadium/turf horizon only as atmosphere — not a full pitch requirement.
        ground = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(ground)
        gd.polygon([(0, 845), (1080, 845), (1080, 1350), (0, 1350)], fill=(3, 14, 20, 145))
        for i in range(9):
            x_top = 540 + (i - 4) * 45
            x_bottom = 540 + (i - 4) * 175
            gd.line((x_top, 850, x_bottom, 1350), fill=(*accent, 18), width=2)
        for yy in (910, 1000, 1105, 1230):
            gd.line((130, yy, 950, yy), fill=(170, 205, 225, 14), width=2)
        ground = ground.filter(ImageFilter.GaussianBlur(1))
        image = Image.alpha_composite(image, ground)

        # Tactical overlay: prominent enough to feel football-specific, quiet enough not to dominate.
        tactical = Image.new("RGBA", image.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tactical)
        line = (*accent, 88)
        td.arc((55, 330, 390, 665), 205, 40, fill=line, width=3)
        td.ellipse((135, 435, 245, 545), outline=line, width=3)
        td.line((185, 490, 410, 365), fill=line, width=3)
        td.line((410, 365, 500, 420), fill=line, width=3)
        for px, py in ((185,490),(410,365),(500,420)):
            td.ellipse((px-10,py-10,px+10,py+10), outline=line, width=3)
        td.arc((735, 360, 1050, 675), 140, 325, fill=line, width=3)
        for (x1,y1,x2,y2) in ((870,445,770,580),(770,580,915,655)):
            td.line((x1,y1,x2,y2), fill=line, width=3)
        for px,py in ((870,445),(770,580),(915,655)):
            td.line((px-9,py-9,px+9,py+9), fill=line, width=3)
            td.line((px+9,py-9,px-9,py+9), fill=line, width=3)
        tactical = tactical.filter(ImageFilter.GaussianBlur(0.35))
        image = Image.alpha_composite(image, tactical)

        # Fine particles, mostly near light beams and ground.
        particles = Image.new("RGBA", image.size, (0,0,0,0))
        pd = ImageDraw.Draw(particles)
        for _ in range(115):
            x = rng.randrange(20, self.WIDTH-20)
            y = rng.randrange(150, 1160)
            r = rng.choice((1,1,1,2,2))
            alpha = rng.randrange(28, 105)
            color = accent if rng.random() < 0.65 else (210,225,240)
            pd.ellipse((x-r,y-r,x+r,y+r), fill=(*color,alpha))
        image = Image.alpha_composite(image, particles)

        # Upper-right compact editorial badge, based on the approved guide language.
        badge = Image.new("RGBA", image.size, (0,0,0,0))
        bd = ImageDraw.Draw(badge)
        bd.polygon([(675, 205), (1005, 205), (1028, 238), (1005, 274), (675, 274), (650, 239)], fill=(6,18,30,205), outline=(*accent,190))
        badge_font = ImageFont.truetype(str(fpath), 23)
        badge_text = self._display_text("أخبار • تحليلات • نبض كرة القدم")
        bb = bd.textbbox((0,0), badge_text, font=badge_font)
        bw = bb[2]-bb[0]
        bd.text((835-bw//2, 224), badge_text, font=badge_font, fill=(226,234,242,240))
        image = Image.alpha_composite(image, badge)

        # Small contextual kicker, no duplicate PUL7SAR wordmark at the top.
        draw = ImageDraw.Draw(image)
        kicker_font = ImageFont.truetype(str(fpath), 27)
        kicker = self._display_text("هوية رياضية • خبر واحد • تركيز واحد")
        kb = draw.textbbox((0,0), kicker, font=kicker_font)
        draw.text((76, 285), kicker, font=kicker_font, fill=(190,202,214,215))
        draw.line((76, 326, 345, 326), fill=(*accent,225), width=4)

        first, second = self._headline_lines(handoff.headline)
        first_display = self._display_text(first)
        second_display = self._display_text(second) if second else None
        first_font = self._fit_font(draw, first_display, str(fpath), 900, 118, 54)
        if second_display:
            second_font = self._fit_font(draw, second_display, str(fpath), 820, 124, 58)
            first_y, second_y = 515, 655
        else:
            second_font = None
            first_y, second_y = 590, 0
        self._metallic_text(image, first_display, first_font, self.WIDTH//2, first_y, max_width=900)
        if second_display and second_font:
            self._accent_text(image, second_display, second_font, self.WIDTH//2, second_y, accent)

        draw = ImageDraw.Draw(image)
        if handoff.supporting_copy:
            support = self._display_text(handoff.supporting_copy)
            sf = self._fit_font(draw, support, str(fpath), 760, 36, 24)
            sb = draw.textbbox((0,0), support, font=sf)
            sw = sb[2]-sb[0]
            draw.text(((self.WIDTH-sw)//2, 815), support, font=sf, fill=(185,197,209,225))

        # Accent flare and lower brand stage separation.
        flare = Image.new("RGBA", image.size, (0,0,0,0))
        fd = ImageDraw.Draw(flare)
        fd.line((260, 875, 820, 875), fill=(*accent,105), width=2)
        fd.line((430, 875, 650, 875), fill=(*accent,255), width=5)
        fd.ellipse((500, 858, 580, 892), fill=(*accent,38))
        flare = flare.filter(ImageFilter.GaussianBlur(9))
        image = Image.alpha_composite(image, flare)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.stem + ".scene-stage.png")
        image.convert("RGB").save(stage, format="PNG")
        BrandStudyRenderer().render_on_file(
            base_path=str(stage),
            output_path=str(target),
            placement=BrandStudyPlacement(150, 1030, 780, 245),
            geometry=APPROVED_BRAND_STUDY_GEOMETRY,
            accent_hex=accent_hex,
            font_path=str(fpath),
        )
        stage.unlink(missing_ok=True)

        payload = target.read_bytes()
        return EditorialSceneStudyReceipt(
            output_path=str(target), output_sha256=sha256(payload).hexdigest(),
            handoff_sha256=handoff.payload_sha256, accent_hex=accent_hex.upper(),
            width=self.WIDTH, height=self.HEIGHT,
        )

"""Deterministic premium sports-editorial study renderer for PUL7SAR Phase 18.

Version 3 fixes the v2 Arabic bidi/shaping defect by relying on Pillow RAQM with
raw Arabic text. It also adds a clearly non-identity central footballer
composition placeholder so visual hierarchy can be reviewed before any verified
player asset is supplied. This module is study-only, zero-cost, uses no image
provider, no legacy logo, and can never authorize publication.
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
    verified_player_asset_used: bool = False
    subject_placeholder_used: bool = True
    arabic_raqm_used: bool = True
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-editorial-scene-study-renderer-v3"


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
    def _contains_arabic(text: str) -> bool:
        return any(
            0x0600 <= ord(char) <= 0x06FF
            or 0x0750 <= ord(char) <= 0x077F
            or 0x08A0 <= ord(char) <= 0x08FF
            or 0xFB50 <= ord(char) <= 0xFDFF
            or 0xFE70 <= ord(char) <= 0xFEFF
            for char in text
        )

    @staticmethod
    def _require_raqm() -> None:
        from PIL import features
        if not features.check("raqm"):
            raise RuntimeError("PUL7SAR Arabic visual study requires Pillow libraqm")

    @classmethod
    def _font(cls, font_path: str, size: int):
        from PIL import ImageFont
        cls._require_raqm()
        return ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)

    @classmethod
    def _direction(cls, text: str) -> str | None:
        return "rtl" if cls._contains_arabic(text) else None

    @classmethod
    def _fit_font(cls, draw, text: str, font_path: str, max_width: int, start_size: int, min_size: int = 28):
        direction = cls._direction(text)
        for size in range(start_size, min_size - 1, -2):
            font = cls._font(font_path, size)
            box = draw.textbbox((0, 0), text, font=font, direction=direction, stroke_width=1)
            if box[2] - box[0] <= max_width:
                return font
        return cls._font(font_path, min_size)

    @classmethod
    def _center_text(cls, draw, text: str, font, center_x: int, y: int, *, fill, stroke_width: int = 0, stroke_fill=None):
        direction = cls._direction(text)
        box = draw.textbbox((0, 0), text, font=font, direction=direction, stroke_width=stroke_width)
        width = box[2] - box[0]
        x = center_x - width // 2
        draw.text(
            (x, y), text, font=font, fill=fill, direction=direction,
            stroke_width=stroke_width, stroke_fill=stroke_fill,
        )
        return x, width

    @classmethod
    def _metallic_headline(cls, image, text: str, font, center_x: int, y: int):
        from PIL import Image, ImageDraw, ImageFilter
        direction = cls._direction(text)
        draw = ImageDraw.Draw(image)
        box = draw.textbbox((0, 0), text, font=font, direction=direction, stroke_width=2)
        width, height = box[2] - box[0], box[3] - box[1]
        x = center_x - width // 2

        shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.text((x + 8, y + 10), text, font=font, direction=direction,
                fill=(0, 0, 0, 220), stroke_width=5, stroke_fill=(0, 0, 0, 220))
        image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))

        mask = Image.new("L", image.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), text, font=font, direction=direction, fill=255, stroke_width=2, stroke_fill=255)
        gradient = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gradient)
        top, bottom = max(0, y), min(image.height, y + height + 20)
        for yy in range(top, bottom):
            t = (yy - top) / max(1, bottom - top - 1)
            if t < 0.28:
                c = int(252 - 50 * (t / 0.28))
            elif t < 0.62:
                c = int(202 - 52 * ((t - 0.28) / 0.34))
            else:
                c = int(150 + 80 * ((t - 0.62) / 0.38))
            gd.line((x - 8, yy, x + width + 8, yy), fill=(c, min(255, c + 6), min(255, c + 14), 255))
        image.alpha_composite(Image.composite(gradient, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask))
        ImageDraw.Draw(image).text((x, y - 2), text, font=font, direction=direction,
                                   fill=(255, 255, 255, 48), stroke_width=1, stroke_fill=(255, 255, 255, 24))

    @staticmethod
    def _draw_subject_placeholder(image, accent: tuple[int, int, int]):
        """Draw a non-identity footballer silhouette used only for composition review."""
        from PIL import Image, ImageDraw, ImageFilter
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        cx = 540

        # Wide rim glow behind the subject gives a premium hero silhouette without a face.
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse((285, 250, 795, 980), fill=(*accent, 32))
        image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(55)))

        # Head deliberately has no facial detail: this may not be mistaken for a real person.
        draw.ellipse((cx - 70, 330, cx + 70, 470), fill=(11, 15, 22, 252), outline=(*accent, 150), width=3)
        # Neck and torso/jersey.
        draw.rounded_rectangle((cx - 54, 446, cx + 54, 520), radius=22, fill=(10, 14, 21, 255))
        torso = [(cx - 205, 500), (cx - 105, 455), (cx, 500), (cx + 105, 455), (cx + 205, 500),
                 (cx + 155, 900), (cx, 965), (cx - 155, 900)]
        draw.polygon(torso, fill=(8, 13, 21, 252), outline=(*accent, 175))
        # Shoulder/arm silhouettes.
        draw.polygon([(cx - 205, 505), (cx - 300, 600), (cx - 255, 790), (cx - 150, 660)], fill=(7, 11, 18, 246))
        draw.polygon([(cx + 205, 505), (cx + 300, 600), (cx + 255, 790), (cx + 150, 660)], fill=(7, 11, 18, 246))

        # Jersey seam language and a soft accent center stripe, but no crest or invented mark.
        draw.line((cx, 505, cx, 920), fill=(*accent, 115), width=3)
        draw.arc((cx - 105, 475, cx + 105, 585), 10, 170, fill=(210, 220, 232, 70), width=3)
        draw.line((cx - 140, 545, cx - 175, 870), fill=(220, 230, 240, 28), width=2)
        draw.line((cx + 140, 545, cx + 175, 870), fill=(220, 230, 240, 28), width=2)

        # Rim-light accents on silhouette edges.
        rim = Image.new("RGBA", image.size, (0, 0, 0, 0))
        rd = ImageDraw.Draw(rim)
        rd.arc((cx - 75, 326, cx + 75, 474), 120, 300, fill=(*accent, 230), width=5)
        rd.line((cx - 205, 500, cx - 300, 600), fill=(*accent, 180), width=5)
        rd.line((cx + 205, 500, cx + 300, 600), fill=(*accent, 180), width=5)
        image.alpha_composite(rim.filter(ImageFilter.GaussianBlur(2)))
        image.alpha_composite(layer)

    def render(self, handoff: VisualStudyHandoff, *, output_path: str, accent_hex: str, font_path: str, seed: int = 7007) -> EditorialSceneStudyReceipt:
        from PIL import Image, ImageDraw, ImageFilter

        if not isinstance(handoff, VisualStudyHandoff):
            raise TypeError("handoff must be VisualStudyHandoff")
        if not handoff.human_review_allowed or handoff.publication_ready:
            raise ValueError("handoff is not a human visual-study contract")
        if handoff.metadata.get("legacy_repo_logo_allowed") is not False:
            raise ValueError("legacy logo policy must be false")
        fpath = Path(font_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        self._require_raqm()
        accent = self._rgb(accent_hex)
        rng = random.Random(seed)

        image = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (2, 7, 14, 255))
        draw = ImageDraw.Draw(image)
        # Deep navy/charcoal gradient with restrained club tint.
        for y in range(self.HEIGHT):
            horizon = max(0.0, 1.0 - abs(y - 600) / 760)
            base = (2 + int(5 * horizon), 7 + int(9 * horizon), 14 + int(14 * horizon))
            tint = tuple(int(v * 0.035 * horizon) for v in accent)
            draw.line((0, y, self.WIDTH, y), fill=tuple(base[i] + tint[i] for i in range(3)) + (255,))

        # Stadium floodlights and beams; contextual atmosphere, not a full pitch dependency.
        lights = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lights)
        for side in (0, 1):
            bank_x = 95 if side == 0 else self.WIDTH - 95
            for row in range(3):
                for col in range(6):
                    cx = int(bank_x + (col - 2.5) * 22)
                    cy = 92 + row * 22
                    ld.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(245, 250, 255, 242))
            if side == 0:
                ld.polygon([(25, 140), (215, 150), (470, 850), (110, 700)], fill=(225, 238, 255, 22))
                ld.polygon([(65, 145), (145, 155), (345, 720), (170, 630)], fill=(*accent, 22))
            else:
                ld.polygon([(1055, 140), (865, 150), (610, 850), (970, 700)], fill=(225, 238, 255, 22))
                ld.polygon([(1015, 145), (935, 155), (735, 720), (910, 630)], fill=(*accent, 22))
        image = Image.alpha_composite(image, lights.filter(ImageFilter.GaussianBlur(22)))
        image = Image.alpha_composite(image, lights)

        # Sparse tactical geometry on the outer thirds only.
        tactical = Image.new("RGBA", image.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tactical)
        line = (*accent, 78)
        td.arc((60, 330, 330, 600), 205, 35, fill=line, width=3)
        td.ellipse((125, 425, 215, 515), outline=line, width=3)
        td.line((170, 470, 360, 365), fill=line, width=3)
        td.line((360, 365, 430, 410), fill=line, width=3)
        for px, py in ((170, 470), (360, 365), (430, 410)):
            td.ellipse((px - 8, py - 8, px + 8, py + 8), outline=line, width=3)
        td.arc((750, 350, 1020, 620), 145, 325, fill=line, width=3)
        td.line((875, 440, 785, 570), fill=line, width=3)
        td.line((785, 570, 910, 625), fill=line, width=3)
        image = Image.alpha_composite(image, tactical.filter(ImageFilter.GaussianBlur(0.4)))

        # Ground perspective and controlled particles create depth without a literal full pitch.
        ground = Image.new("RGBA", image.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(ground)
        gd.polygon([(0, 870), (1080, 870), (1080, 1350), (0, 1350)], fill=(2, 13, 19, 150))
        for i in range(9):
            gd.line((540 + (i - 4) * 36, 875, 540 + (i - 4) * 180, 1350), fill=(*accent, 18), width=2)
        for yy in (930, 1030, 1145, 1270):
            gd.line((115, yy, 965, yy), fill=(180, 205, 225, 18), width=2)
        image = Image.alpha_composite(image, ground)
        particles = Image.new("RGBA", image.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(particles)
        for _ in range(90):
            x = rng.randrange(25, self.WIDTH - 25)
            y = rng.randrange(160, 1110)
            r = rng.choice((1, 1, 1, 2))
            c = accent if rng.random() < 0.6 else (210, 225, 240)
            pd.ellipse((x - r, y - r, x + r, y + r), fill=(*c, rng.randrange(28, 90)))
        image = Image.alpha_composite(image, particles)

        # Composition-only subject placeholder. Never used as identity evidence.
        self._draw_subject_placeholder(image, accent)

        # Top micro-labels, rendered with real RAQM RTL instead of reshaper/bidi output.
        draw = ImageDraw.Draw(image)
        small = self._font(str(fpath), 23)
        badge = "أخبار • تحليلات • نبض كرة القدم"
        bx, bw = self._center_text(draw, badge, small, 830, 225, fill=(228, 235, 242, 235))
        draw.rounded_rectangle((bx - 22, 212, bx + bw + 22, 270), radius=16, outline=(*accent, 175), fill=(5, 16, 28, 170), width=2)
        # redraw text over badge after rectangle
        self._center_text(draw, badge, small, 830, 225, fill=(228, 235, 242, 235))
        kicker = "دراسة تركيب بصري • ليست خبراً للنشر"
        kicker_font = self._font(str(fpath), 24)
        self._center_text(draw, kicker, kicker_font, 300, 292, fill=(181, 195, 210, 205))
        draw.line((95, 334, 355, 334), fill=(*accent, 215), width=4)

        # Headline is intentionally short and placed across the subject at chest level.
        headline = handoff.headline.strip()
        headline_font = self._fit_font(draw, headline, str(fpath), 820, 112, 58)
        self._metallic_headline(image, headline, headline_font, self.WIDTH // 2, 690)

        if handoff.supporting_copy:
            support = handoff.supporting_copy.strip()
            support_font = self._fit_font(draw, support, str(fpath), 700, 34, 24)
            self._center_text(ImageDraw.Draw(image), support, support_font, self.WIDTH // 2, 825, fill=(190, 202, 214, 225))

        # Small transfer cue—not an exact club crest, contract, score or factual data.
        cue = Image.new("RGBA", image.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(cue)
        cd.rounded_rectangle((390, 900, 690, 955), radius=18, fill=(5, 17, 29, 205), outline=(*accent, 190), width=2)
        cue_text = "TRANSFER VISUAL STUDY"
        cue_font = self._font(str(fpath), 20)
        self._center_text(cd, cue_text, cue_font, 540, 916, fill=(220, 229, 238, 235))
        image = Image.alpha_composite(image, cue)

        # Separate lower identity stage preserves the approved hybrid-adaptive semantics.
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.stem + ".scene-stage.png")
        image.convert("RGB").save(stage, format="PNG")
        BrandStudyRenderer().render_on_file(
            base_path=str(stage), output_path=str(target),
            placement=BrandStudyPlacement(175, 1040, 730, 230),
            geometry=APPROVED_BRAND_STUDY_GEOMETRY,
            accent_hex=accent_hex, font_path=str(fpath),
        )
        stage.unlink(missing_ok=True)

        payload = target.read_bytes()
        return EditorialSceneStudyReceipt(
            output_path=str(target), output_sha256=sha256(payload).hexdigest(),
            handoff_sha256=handoff.payload_sha256, accent_hex=accent_hex.upper(),
            width=self.WIDTH, height=self.HEIGHT,
        )

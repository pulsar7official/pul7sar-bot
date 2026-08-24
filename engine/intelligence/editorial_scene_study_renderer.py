"""Deterministic premium sports-editorial study renderer for PUL7SAR Phase 18.

This renderer creates pixels entirely in code for human visual-direction review.
It is not a production news renderer and cannot authorize publication. It uses no
legacy logo and no image-generation provider; the study-only adaptive brand is
composited by BrandStudyRenderer after the scene is built.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import math
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
    contract: str = "pul7sar-editorial-scene-study-renderer-v1"


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
    def _fit_font(draw, text: str, font_path: str, max_width: int, start_size: int, min_size: int = 28):
        from PIL import ImageFont
        for size in range(start_size, min_size - 1, -2):
            font = ImageFont.truetype(font_path, size)
            bbox = draw.textbbox((0, 0), text, font=font)
            if bbox[2] - bbox[0] <= max_width:
                return font
        return ImageFont.truetype(font_path, min_size)

    def render(
        self,
        handoff: VisualStudyHandoff,
        *,
        output_path: str,
        accent_hex: str,
        font_path: str,
        seed: int = 7007,
    ) -> EditorialSceneStudyReceipt:
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
        accent = self._rgb(accent_hex)
        randomizer = random.Random(seed)

        image = Image.new("RGB", (self.WIDTH, self.HEIGHT), (4, 8, 15))
        draw = ImageDraw.Draw(image)

        # Deep vertical gradient: charcoal/navy with a restrained club/story tint.
        for y in range(self.HEIGHT):
            t = y / max(1, self.HEIGHT - 1)
            glow = max(0.0, 1.0 - abs(t - 0.42) * 1.75)
            base = (4 + int(5 * glow), 8 + int(8 * glow), 15 + int(12 * glow))
            tint = tuple(int(channel * 0.055 * glow) for channel in accent)
            draw.line((0, y, self.WIDTH, y), fill=tuple(min(255, base[i] + tint[i]) for i in range(3)))

        # Vignette and diagonal editorial panels create depth without becoming a card.
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.polygon([(0, 210), (590, 80), (370, 1050), (0, 1160)], fill=(10, 18, 28, 105))
        od.polygon([(1080, 120), (690, 260), (830, 1040), (1080, 930)], fill=(*accent, 16))
        for x in range(0, self.WIDTH, 18):
            alpha = int(60 * abs(x - self.WIDTH / 2) / (self.WIDTH / 2))
            od.rectangle((x, 0, x + 18, self.HEIGHT), fill=(0, 0, 0, alpha // 4))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)

        # Stadium-style light banks are contextual atmosphere, not a forced pitch.
        light_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(light_layer)
        for side in (0, 1):
            origin_x = 65 if side == 0 else self.WIDTH - 65
            for row in range(3):
                for col in range(5):
                    cx = origin_x + ((col - 2) * 21 if side == 0 else (col - 2) * 21)
                    cy = 105 + row * 22
                    ld.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=(235, 245, 255, 220))
            beam_x = 310 if side == 0 else self.WIDTH - 310
            ld.polygon([(origin_x, 140), (beam_x - 100, 700), (beam_x + 120, 700)], fill=(*accent, 18))
        light_layer = light_layer.filter(ImageFilter.GaussianBlur(9))
        image = Image.alpha_composite(image, light_layer)
        draw = ImageDraw.Draw(image)

        # Subtle tactical language. It remains texture; the story/headline stays hero.
        line = (*accent, 72)
        tactical = Image.new("RGBA", image.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(tactical)
        td.arc((75, 395, 390, 710), 205, 35, fill=line, width=3)
        td.ellipse((150, 485, 260, 595), outline=line, width=3)
        td.line((185, 540, 430, 420), fill=line, width=3)
        td.line((430, 420, 515, 465), fill=line, width=3)
        for px, py in ((185, 540), (430, 420), (515, 465)):
            td.ellipse((px-10, py-10, px+10, py+10), outline=line, width=3)
        td.arc((720, 430, 1015, 725), 145, 325, fill=line, width=3)
        td.line((860, 500, 770, 630), fill=line, width=3)
        td.line((770, 630, 905, 685), fill=line, width=3)
        for px, py in ((860, 500), (770, 630), (905, 685)):
            td.line((px-8, py-8, px+8, py+8), fill=line, width=3)
            td.line((px+8, py-8, px-8, py+8), fill=line, width=3)
        image = Image.alpha_composite(image, tactical)
        draw = ImageDraw.Draw(image)

        # Controlled particles: enough motion for sports energy, not visual noise.
        for _ in range(75):
            x = randomizer.randrange(30, self.WIDTH - 30)
            y = randomizer.randrange(180, 1050)
            r = randomizer.choice((1, 1, 1, 2))
            alpha = randomizer.randrange(35, 105)
            draw.ellipse((x-r, y-r, x+r, y+r), fill=(*accent, alpha))

        # Small editorial kicker establishes hierarchy without a dense info band.
        from PIL import ImageFont
        kicker_font = ImageFont.truetype(str(fpath), 25)
        kicker = "PUL7SAR  •  FOOTBALL EDITORIAL STUDY"
        draw.text((74, 255), kicker, font=kicker_font, fill=(215, 222, 230, 205))
        draw.line((74, 300, 330, 300), fill=(*accent, 220), width=4)

        headline = self._display_text(handoff.headline)
        headline_font = self._fit_font(draw, headline, str(fpath), 900, 112, 48)
        bbox = draw.textbbox((0, 0), headline, font=headline_font)
        tw = bbox[2] - bbox[0]
        tx = (self.WIDTH - tw) // 2
        ty = 545
        # Metallic headline approximation with deep extrusion and crisp face.
        for offset, fill in ((8, (0, 0, 0, 190)), (4, (75, 83, 94, 255))):
            draw.text((tx + offset, ty + offset), headline, font=headline_font, fill=fill)
        draw.text((tx, ty), headline, font=headline_font, fill=(225, 230, 235, 255))
        draw.text((tx, ty - 2), headline, font=headline_font, fill=(255, 255, 255, 120))

        if handoff.supporting_copy:
            support = self._display_text(handoff.supporting_copy)
            support_font = self._fit_font(draw, support, str(fpath), 760, 38, 24)
            sb = draw.textbbox((0, 0), support, font=support_font)
            sw = sb[2] - sb[0]
            draw.text(((self.WIDTH - sw)//2, 735), support, font=support_font, fill=(190, 199, 209, 230))

        # A restrained accent flare anchors the headline instead of flooding the canvas.
        draw.line((260, 820, 820, 820), fill=(*accent, 120), width=2)
        draw.line((430, 820, 650, 820), fill=(*accent, 255), width=5)

        # Temporary file lets the separate brand renderer remain independently testable.
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.stem + ".scene-stage.png")
        image.convert("RGB").save(stage, format="PNG")
        brand = BrandStudyRenderer().render_on_file(
            base_path=str(stage),
            output_path=str(target),
            placement=BrandStudyPlacement(165, 1040, 750, 230),
            geometry=APPROVED_BRAND_STUDY_GEOMETRY,
            accent_hex=accent_hex,
            font_path=str(fpath),
        )
        stage.unlink(missing_ok=True)

        payload = target.read_bytes()
        return EditorialSceneStudyReceipt(
            output_path=str(target),
            output_sha256=sha256(payload).hexdigest(),
            handoff_sha256=handoff.payload_sha256,
            accent_hex=accent_hex.upper(),
            width=self.WIDTH,
            height=self.HEIGHT,
        )

"""Fully original procedural Result Scene benchmark for PUL7SAR.

V2 removes the scoreboard/card container entirely. The exact score itself becomes
the monument inside a code-created cinematic sports world: volumetric light,
atmospheric color contamination, haze, crowd-scale bokeh, reflective depth and
foreground particles. No source photograph, venue photo, match photo, diffusion
model, network call, fabricated crest or external final canvas is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from random import Random

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposition


@dataclass(frozen=True)
class OriginalResultSceneReceipt:
    output_path: str
    output_sha256: str
    width: int
    height: int
    score_text: str
    scene_origin: str
    source_photo_used: bool
    generator_used: bool
    network_used: bool
    fabricated_crest_used: bool
    brand_overlay_contract: str
    visual_language: str = "frameless_cinematic_score_monument"
    container_panel_used: bool = False
    perspective_grid_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-original-result-scene-renderer-v2-frameless"


class OriginalResultSceneRenderer:
    CONTRACT = "pul7sar-original-result-scene-renderer-v2-frameless"

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _fit_font(draw, text: str, font_path: str, max_width: int, max_height: int, start: int):
        from PIL import ImageFont
        size = start
        while size >= 12:
            font = ImageFont.truetype(font_path, size=size)
            l, t, r, b = draw.textbbox((0, 0), text, font=font, stroke_width=1)
            if r - l <= max_width and b - t <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=12)

    @staticmethod
    def _center(draw, text: str, font, cx: float, cy: float, fill, *, stroke_width: int = 0, stroke_fill=None) -> None:
        l, t, r, b = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        draw.text(
            (cx - (r-l)/2, cy - (b-t)/2 - t), text, font=font, fill=fill,
            stroke_width=stroke_width, stroke_fill=stroke_fill,
        )

    @classmethod
    def _base_world(cls, image, *, left: tuple[int,int,int], right: tuple[int,int,int], seed: int) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        rng = Random(seed)
        d = ImageDraw.Draw(image, "RGBA")

        # Deep near-black editorial world with a subtle blue-black lower falloff.
        for y in range(h):
            t = y / max(1, h-1)
            r = int(7 - 2*t)
            g = int(13 - 4*t)
            b = int(24 - 5*t)
            d.line((0, y, w, y), fill=(r, g, b, 255))

        # Team colors contaminate the air, never divide the canvas into panels.
        color_air = Image.new("RGBA", (w, h), (0,0,0,0))
        cd = ImageDraw.Draw(color_air, "RGBA")
        cd.ellipse((-w*0.55, h*0.12, w*0.56, h*0.88), fill=(*left, 112))
        cd.ellipse((w*0.44, h*0.12, w*1.55, h*0.88), fill=(*right, 96))
        cd.ellipse((w*0.22, h*0.24, w*0.78, h*0.72), fill=(225,232,240,24))
        color_air = color_air.filter(ImageFilter.GaussianBlur(radius=max(60, int(w*0.15))))
        image.alpha_composite(color_air)

        # Overhead arena-light impression without identifying or drawing a venue.
        rig = Image.new("RGBA", (w,h), (0,0,0,0))
        rd = ImageDraw.Draw(rig, "RGBA")
        for i in range(11):
            x = int(w*(0.12 + i*0.076))
            power = 75 if i in {3,4,5,6,7} else 45
            rr = 3 if i % 2 == 0 else 2
            rd.ellipse((x-rr, h*0.145-rr, x+rr, h*0.145+rr), fill=(242,247,250,power))
        for x, alpha, spread in ((0.28,26,0.16),(0.40,20,0.11),(0.60,20,0.11),(0.72,26,0.16)):
            tx = int(w*x)
            rd.polygon([(tx-4, int(h*0.15)), (tx+4, int(h*0.15)),
                        (tx+int(w*spread), int(h*0.73)), (tx-int(w*spread), int(h*0.73))],
                       fill=(238,244,248,alpha))
        rig = rig.filter(ImageFilter.GaussianBlur(radius=max(16,int(w*0.03))))
        image.alpha_composite(rig)

        # Crowd-scale bokeh in a curved horizon. No literal seats or stadium copy.
        crowd = Image.new("RGBA", (w,h), (0,0,0,0))
        qd = ImageDraw.Draw(crowd, "RGBA")
        for _ in range(180):
            x = rng.randint(int(w*0.04), int(w*0.96))
            nx = (x-w/2)/(w/2)
            base_y = h*(0.655 + 0.035*(nx*nx))
            y = int(base_y + rng.uniform(-h*0.035, h*0.035))
            radius = rng.choice((1,1,1,2,2,3))
            alpha = rng.randint(15,68)
            if x < w/2 and rng.random() < 0.14:
                color = (*left, min(70,alpha+10))
            elif x >= w/2 and rng.random() < 0.14:
                color = (*right, min(70,alpha+10))
            else:
                color = (225,232,238,alpha)
            qd.ellipse((x-radius,y-radius,x+radius,y+radius), fill=color)
        crowd = crowd.filter(ImageFilter.GaussianBlur(radius=1.6))
        image.alpha_composite(crowd)

        # Reflective stage/floor: only soft elliptical pools, no perspective grid.
        floor = Image.new("RGBA", (w,h), (0,0,0,0))
        fd = ImageDraw.Draw(floor, "RGBA")
        fd.ellipse((w*0.10,h*0.66,w*0.90,h*1.12), fill=(6,10,17,170), outline=(226,235,242,18), width=1)
        fd.ellipse((w*0.22,h*0.71,w*0.78,h*0.98), outline=(226,235,242,14), width=1)
        fd.ellipse((w*0.30,h*0.73,w*0.70,h*0.91), fill=(220,230,238,12))
        floor = floor.filter(ImageFilter.GaussianBlur(radius=max(5,int(w*0.012))))
        image.alpha_composite(floor)

        # Central haze gives the numerals environmental depth.
        haze = Image.new("RGBA", (w,h), (0,0,0,0))
        hd = ImageDraw.Draw(haze, "RGBA")
        hd.ellipse((w*0.18,h*0.25,w*0.82,h*0.69), fill=(222,231,239,31))
        hd.ellipse((w*0.29,h*0.33,w*0.71,h*0.61), fill=(244,248,250,19))
        haze = haze.filter(ImageFilter.GaussianBlur(radius=max(45,int(w*0.115))))
        image.alpha_composite(haze)

        # Foreground dust / lens particles create near-camera depth.
        dust = Image.new("RGBA", (w,h), (0,0,0,0))
        dd = ImageDraw.Draw(dust, "RGBA")
        for _ in range(55):
            x = rng.randint(int(w*0.07), int(w*0.93))
            y = rng.randint(int(h*0.48), int(h*0.88))
            r = rng.choice((1,1,2,2,3,4))
            a = rng.randint(10,42)
            dd.ellipse((x-r,y-r,x+r,y+r), fill=(235,241,245,a))
        dust = dust.filter(ImageFilter.GaussianBlur(radius=1.1))
        image.alpha_composite(dust)

        # Cinematic vignette.
        vig = Image.new("RGBA", (w,h), (0,0,0,0))
        vd = ImageDraw.Draw(vig, "RGBA")
        edge = int(w*0.12)
        vd.rectangle((0,0,edge,h), fill=(0,0,0,88))
        vd.rectangle((w-edge,0,w,h), fill=(0,0,0,88))
        vd.rectangle((0,0,w,int(h*0.09)), fill=(0,0,0,72))
        vd.rectangle((0,int(h*0.90),w,h), fill=(0,0,0,88))
        vig = vig.filter(ImageFilter.GaussianBlur(radius=max(30,int(w*0.05))))
        image.alpha_composite(vig)

    @classmethod
    def _score_face(cls, image, text: str, *, cx: float, cy: float, font, accent: tuple[int,int,int]) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w,h = image.size

        # Colored aura is environmental, not a graphic underline.
        aura = Image.new("RGBA", (w,h), (0,0,0,0))
        ad = ImageDraw.Draw(aura, "RGBA")
        ad.ellipse((cx-w*0.13, cy-h*0.12, cx+w*0.13, cy+h*0.12), fill=(*accent,78))
        aura = aura.filter(ImageFilter.GaussianBlur(radius=max(28,int(w*0.055))))
        image.alpha_composite(aura)

        d = ImageDraw.Draw(image, "RGBA")
        # Extruded dark-metal depth. Multiple offsets make numerals physical.
        for offset in range(16, 1, -2):
            shade = max(10, 38-offset)
            cls._center(d, text, font, cx+offset*0.30, cy+offset*0.72, (shade,shade+2,shade+6,235), stroke_width=2, stroke_fill=(0,0,0,210))
        # Edge metal and white-silver face.
        cls._center(d, text, font, cx, cy, (244,247,250,255), stroke_width=4, stroke_fill=(104,113,124,255))
        cls._center(d, text, font, cx, cy-2, (249,250,252,255), stroke_width=1, stroke_fill=(255,255,255,180))

    @classmethod
    def _monument(cls, image, *, home_score: int, away_score: int, font_path: str, left, right) -> str:
        from PIL import Image, ImageDraw, ImageFilter
        w,h = image.size
        d = ImageDraw.Draw(image, "RGBA")
        font = cls._fit_font(d, str(max(home_score,away_score)), font_path, int(w*0.25), int(h*0.23), int(h*0.205))
        dash_font = cls._fit_font(d, "–", font_path, int(w*0.08), int(h*0.07), int(h*0.060))
        cy = h*0.425

        # One subtle halo spanning both numerals binds the score into the scene.
        halo = Image.new("RGBA", (w,h), (0,0,0,0))
        hd = ImageDraw.Draw(halo, "RGBA")
        hd.ellipse((w*0.22,h*0.30,w*0.78,h*0.57), fill=(231,238,244,22))
        halo = halo.filter(ImageFilter.GaussianBlur(radius=max(35,int(w*0.075))))
        image.alpha_composite(halo)

        cls._score_face(image, str(home_score), cx=w*0.36, cy=cy, font=font, accent=left)
        cls._score_face(image, str(away_score), cx=w*0.64, cy=cy, font=font, accent=right)
        d = ImageDraw.Draw(image, "RGBA")
        cls._center(d, "–", dash_font, w/2, cy+3, (180,190,201,210))

        # Reflection ghost below the numerals, heavily blurred and low-opacity.
        reflection = Image.new("RGBA", (w,h), (0,0,0,0))
        rd = ImageDraw.Draw(reflection, "RGBA")
        cls._center(rd, str(home_score), font, w*0.36, h*0.58, (220,226,232,24))
        cls._center(rd, str(away_score), font, w*0.64, h*0.58, (220,226,232,24))
        reflection = reflection.filter(ImageFilter.GaussianBlur(radius=max(8,int(w*0.018))))
        image.alpha_composite(reflection)
        return f"{home_score}–{away_score}"

    @classmethod
    def _copy_and_identity(cls, image, *, headline: str, home: str, away: str, font_path: str, left, right, winner: str | None) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w,h = image.size
        d = ImageDraw.Draw(image, "RGBA")

        # Editorial headline is deliberately subordinate to the score.
        head_font = cls._fit_font(d, headline, font_path, int(w*0.58), int(h*0.05), int(h*0.034))
        cls._center(d, headline.upper(), head_font, w/2, h*0.185, (218,225,231,222))
        label_font = cls._fit_font(d, "FULL TIME", font_path, int(w*0.16), int(h*0.025), int(h*0.017))
        cls._center(d, "FULL TIME", label_font, w/2, h*0.262, (156,168,180,175))

        # Team identities remain equal; no fake crest shapes. Color is a restrained
        # light signature. Winner receives additive aura only.
        name_font = cls._fit_font(d, max(home,away,key=len), font_path, int(w*0.31), int(h*0.045), int(h*0.031))
        for side, x, name, accent in (("home",0.30,home,left),("away",0.70,away,right)):
            if winner == side:
                glow = Image.new("RGBA", (w,h), (0,0,0,0))
                gd = ImageDraw.Draw(glow, "RGBA")
                gd.ellipse((w*x-w*0.07,h*0.586-h*0.025,w*x+w*0.07,h*0.586+h*0.025), fill=(*accent,42))
                glow = glow.filter(ImageFilter.GaussianBlur(radius=max(10,int(w*0.018))))
                image.alpha_composite(glow)
                d = ImageDraw.Draw(image, "RGBA")
            cls._center(d, name.upper(), name_font, w*x, h*0.625, (230,236,241,238))
            bar_w = w*0.055
            y = h*0.582
            d.rounded_rectangle((w*x-bar_w/2,y-2,w*x+bar_w/2,y+2), radius=2, fill=(*accent,210))

    def render(self, composition: ResultStatementComposition, *, profile: PlatformImageProfile, output_path: str,
               home_name: str, away_name: str, home_score: int, away_score: int, headline: str,
               home_accent_hex: str, away_accent_hex: str, brand_accent_hex: str, font_path: str,
               winner: str | None = None, seed: int = 18001) -> OriginalResultSceneReceipt:
        from PIL import Image
        if not isinstance(composition, ResultStatementComposition):
            raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        if winner not in {None,"home","away"}:
            raise ValueError("winner must be home, away or None")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if isinstance(home_score, bool) or isinstance(away_score, bool) or not isinstance(home_score,int) or not isinstance(away_score,int) or home_score < 0 or away_score < 0:
            raise ValueError("scores must be non-negative integers")
        if not home_name.strip() or not away_name.strip() or not headline.strip():
            raise ValueError("team names and headline are required")

        left = self._rgb(home_accent_hex)
        right = self._rgb(away_accent_hex)
        image = Image.new("RGBA", (profile.width, profile.height), (7,12,20,255))
        self._base_world(image, left=left, right=right, seed=seed)
        score_text = self._monument(image, home_score=home_score, away_score=away_score, font_path=font_path, left=left, right=right)
        self._copy_and_identity(image, headline=headline, home=home_name, away=away_name, font_path=font_path, left=left, right=right, winner=winner)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        pre = target.with_name(target.stem + ".prebrand.png")
        image.convert("RGB").save(pre, "PNG")
        brand = AdaptiveBrandOverlayRenderer().render_on_file(
            base_path=str(pre), output_path=str(target), adaptive=composition.brand,
            profile=profile, accent_hex=brand_accent_hex,
        )
        pre.unlink(missing_ok=True)
        return OriginalResultSceneReceipt(
            output_path=str(target), output_sha256=self._sha(target), width=profile.width, height=profile.height,
            score_text=score_text, scene_origin="100_percent_code_generated_original_pixels", source_photo_used=False,
            generator_used=False, network_used=False, fabricated_crest_used=False,
            brand_overlay_contract=brand.contract,
        )

"""Fully original procedural Result Scene benchmark for PUL7SAR.

No source photograph, venue photo, match photo, diffusion model, network call or
external visual canvas is used. The renderer creates an editorial sports world
from code-owned light, depth, atmosphere, typography and exact score layers, then
adds the embedded PUL7SAR brand through AdaptiveBrandOverlayRenderer.

This is a visual benchmark, not publication authorization. Club crests are not
fabricated; benchmark identity uses names and color light only.
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
    visual_language: str = "original_cinematic_score_monument"
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-original-result-scene-renderer-v1"


class OriginalResultSceneRenderer:
    CONTRACT = "pul7sar-original-result-scene-renderer-v1"

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
            l, t, r, b = draw.textbbox((0, 0), text, font=font)
            if r - l <= max_width and b - t <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=12)

    @staticmethod
    def _center(draw, text: str, font, cx: float, cy: float, fill) -> None:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
        draw.text((cx - (r-l)/2, cy - (b-t)/2 - t), text, font=font, fill=fill)

    @classmethod
    def _base_world(cls, image, *, left: tuple[int,int,int], right: tuple[int,int,int], seed: int) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        rng = Random(seed)
        d = ImageDraw.Draw(image, "RGBA")

        # Deep cinematic vertical gradient.
        for y in range(h):
            t = y / max(1, h-1)
            r = int(8 + 2*(1-t))
            g = int(13 + 5*(1-t))
            b = int(22 + 11*(1-t))
            d.line((0, y, w, y), fill=(r, g, b, 255))

        # Atmospheric club-color contamination, not panels.
        glow = Image.new("RGBA", (w, h), (0,0,0,0))
        gd = ImageDraw.Draw(glow, "RGBA")
        gd.ellipse((-w*0.38, h*0.10, w*0.53, h*0.95), fill=(*left, 105))
        gd.ellipse((w*0.47, h*0.10, w*1.38, h*0.95), fill=(*right, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(40, int(w*0.12))))
        image.alpha_composite(glow)

        # Volumetric beams from an unseen upper rig.
        beams = Image.new("RGBA", (w, h), (0,0,0,0))
        bd = ImageDraw.Draw(beams, "RGBA")
        for i, x in enumerate((0.19, 0.34, 0.66, 0.81)):
            topx = int(w*x)
            spread = int(w*(0.07 + 0.01*(i%2)))
            bd.polygon([(topx-5, 0), (topx+5, 0), (topx+spread, int(h*0.72)), (topx-spread, int(h*0.72))], fill=(235,242,248,20))
        beams = beams.filter(ImageFilter.GaussianBlur(radius=max(18, int(w*0.035))))
        image.alpha_composite(beams)

        # Abstract crowd/horizon bokeh. It reads as sports atmosphere without
        # claiming a real stadium or copying one.
        bokeh = Image.new("RGBA", (w,h), (0,0,0,0))
        bkd = ImageDraw.Draw(bokeh, "RGBA")
        horizon = int(h*0.69)
        for _ in range(125):
            x = rng.randint(int(w*0.05), int(w*0.95))
            y = rng.randint(horizon-int(h*0.07), horizon+int(h*0.05))
            rad = rng.randint(1,4)
            alpha = rng.randint(18,72)
            bkd.ellipse((x-rad,y-rad,x+rad,y+rad), fill=(232,238,244,alpha))
        bokeh = bokeh.filter(ImageFilter.GaussianBlur(radius=2.2))
        image.alpha_composite(bokeh)

        # Perspective terraces and ground reflections establish physical depth.
        d = ImageDraw.Draw(image, "RGBA")
        vanish_y = int(h*0.61)
        for n, alpha in ((0.08,28),(0.14,22),(0.22,17),(0.31,13)):
            y = int(h*(0.68+n))
            d.line((int(w*0.08), y, int(w*0.92), y), fill=(225,235,242,alpha), width=1)
        for x in (0.18,0.32,0.68,0.82):
            d.line((int(w*0.50), vanish_y, int(w*x), h), fill=(225,235,242,12), width=1)

        # Central mist prevents the score from feeling pasted on.
        mist = Image.new("RGBA", (w,h), (0,0,0,0))
        md = ImageDraw.Draw(mist, "RGBA")
        md.ellipse((w*0.17,h*0.22,w*0.83,h*0.72), fill=(218,228,237,30))
        mist = mist.filter(ImageFilter.GaussianBlur(radius=max(55,int(w*0.13))))
        image.alpha_composite(mist)

        # Vignette.
        vig = Image.new("RGBA", (w,h), (0,0,0,0))
        vd = ImageDraw.Draw(vig, "RGBA")
        edge = int(w*0.12)
        vd.rectangle((0,0,edge,h), fill=(0,0,0,78))
        vd.rectangle((w-edge,0,w,h), fill=(0,0,0,78))
        vd.rectangle((0,0,w,int(h*0.10)), fill=(0,0,0,58))
        vd.rectangle((0,int(h*0.88),w,h), fill=(0,0,0,72))
        vig = vig.filter(ImageFilter.GaussianBlur(radius=max(25,int(w*0.045))))
        image.alpha_composite(vig)

    @classmethod
    def _monument(cls, image, *, home_score: int, away_score: int, font_path: str, left, right) -> str:
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size
        cx = w/2
        cy = h*0.43

        # A single floating physical slab, not a scoreboard card.
        slab = Image.new("RGBA", (w,h), (0,0,0,0))
        sd = ImageDraw.Draw(slab, "RGBA")
        x0,x1 = int(w*0.245), int(w*0.755)
        y0,y1 = int(h*0.315), int(h*0.545)
        radius = int(w*0.028)
        sd.rounded_rectangle((x0,y0,x1,y1), radius=radius, fill=(8,14,22,150), outline=(224,233,240,40), width=2)
        sd.rounded_rectangle((x0+6,y0+6,x1-6,y1-6), radius=max(2,radius-6), outline=(255,255,255,16), width=1)
        # metallic top rim
        sd.rounded_rectangle((x0+18,y0+16,x1-18,y0+19), radius=2, fill=(238,244,248,54))
        slab = slab.filter(ImageFilter.GaussianBlur(radius=0.35))
        image.alpha_composite(slab)

        d = ImageDraw.Draw(image, "RGBA")
        score_left = str(home_score)
        score_right = str(away_score)
        font = cls._fit_font(d, max(score_left,score_right,key=len), font_path, int(w*0.17), int(h*0.16), int(h*0.145))
        dash_font = cls._fit_font(d, "–", font_path, int(w*0.07), int(h*0.06), int(h*0.055))

        # soft projected shadows + bright front face
        for dx,dy,a in ((0,10,62),(0,4,72)):
            cls._center(d, score_left, font, w*0.37+dx, cy+dy, (0,0,0,a))
            cls._center(d, score_right, font, w*0.63+dx, cy+dy, (0,0,0,a))
        cls._center(d, score_left, font, w*0.37, cy, (248,250,252,255))
        cls._center(d, score_right, font, w*0.63, cy, (248,250,252,255))
        cls._center(d, "–", dash_font, cx, cy+2, (188,198,208,218))

        # light integrated beneath score, no graphic underline panels
        light = Image.new("RGBA", (w,h), (0,0,0,0))
        ld = ImageDraw.Draw(light, "RGBA")
        ld.ellipse((w*0.28,h*0.50,w*0.46,h*0.555), fill=(*left,80))
        ld.ellipse((w*0.54,h*0.50,w*0.72,h*0.555), fill=(*right,70))
        light = light.filter(ImageFilter.GaussianBlur(radius=max(15,int(w*0.025))))
        image.alpha_composite(light)
        return f"{home_score}–{away_score}"

    @classmethod
    def _copy_and_identity(cls, image, *, headline: str, home: str, away: str, font_path: str, left, right, winner: str | None) -> None:
        from PIL import ImageDraw
        w,h = image.size
        d = ImageDraw.Draw(image, "RGBA")
        head_font = cls._fit_font(d, headline, font_path, int(w*0.70), int(h*0.07), int(h*0.044))
        cls._center(d, headline.upper(), head_font, w/2, h*0.19, (222,229,235,238))

        name_font = cls._fit_font(d, max(home,away,key=len), font_path, int(w*0.30), int(h*0.05), int(h*0.034))
        cls._center(d, home.upper(), name_font, w*0.30, h*0.63, (232,237,242,244))
        cls._center(d, away.upper(), name_font, w*0.70, h*0.63, (232,237,242,244))

        # Equal identity light cores. Winner gets additive glow only.
        for side, x, accent in (("home",0.30,left),("away",0.70,right)):
            r = int(w*0.012)
            d.ellipse((w*x-r,h*0.575-r,w*x+r,h*0.575+r), fill=(*accent,230))
            if winner == side:
                rr = int(w*0.027)
                d.ellipse((w*x-rr,h*0.575-rr,w*x+rr,h*0.575+rr), outline=(*accent,100), width=2)

        # Small factual label keeps hierarchy editorial rather than template-like.
        label_font = cls._fit_font(d, "FULL TIME", font_path, int(w*0.18), int(h*0.035), int(h*0.020))
        cls._center(d, "FULL TIME", label_font, w/2, h*0.272, (171,181,192,180))

    def render(self, composition: ResultStatementComposition, *, profile: PlatformImageProfile, output_path: str,
               home_name: str, away_name: str, home_score: int, away_score: int, headline: str,
               home_accent_hex: str, away_accent_hex: str, brand_accent_hex: str, font_path: str,
               winner: str | None = None, seed: int = 18001) -> OriginalResultSceneReceipt:
        from PIL import Image
        if winner not in {None,"home","away"}:
            raise ValueError("winner must be home, away or None")
        if not Path(font_path).is_file():
            raise FileNotFoundError(font_path)
        if home_score < 0 or away_score < 0:
            raise ValueError("scores must be non-negative")
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
        brand = AdaptiveBrandOverlayRenderer().render_on_file(base_path=str(pre), output_path=str(target), adaptive=composition.brand, profile=profile, accent_hex=brand_accent_hex)
        pre.unlink(missing_ok=True)
        return OriginalResultSceneReceipt(
            output_path=str(target), output_sha256=self._sha(target), width=profile.width, height=profile.height,
            score_text=score_text, scene_origin="100_percent_code_generated_original_pixels", source_photo_used=False,
            generator_used=False, network_used=False, fabricated_crest_used=False, brand_overlay_contract=brand.contract,
        )

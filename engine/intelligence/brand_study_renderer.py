"""Study-only deterministic PUL7SAR identity renderer.

Version 2 better approximates the approved identity signatures for composition
review: metallic PUL/SAR, a visibly enlarged accent 7, pulse below the wordmark,
and the small football signature near R. It remains approximation-only and may
never replace the exact BrandMasterGeometryGate for publishing.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import math

from engine.intelligence.brand_study_geometry import BrandStudyGeometry


@dataclass(frozen=True)
class BrandStudyPlacement:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("study brand placement must be positive")


@dataclass(frozen=True)
class BrandStudyReceipt:
    output_path: str
    output_sha256: str
    accent_hex: str
    seven_scale: float
    pulse_below_wordmark: bool
    football_near_r: bool
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-study-renderer-v2"


class BrandStudyRenderer:
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
    def _metallic_word(layer, text: str, font, x: int, y: int):
        from PIL import Image, ImageDraw, ImageFilter
        draw = ImageDraw.Draw(layer)
        box = draw.textbbox((x, y), text, font=font, stroke_width=1)
        mask = Image.new("L", layer.size, 0)
        md = ImageDraw.Draw(mask)
        md.text((x, y), text, font=font, fill=255, stroke_width=1, stroke_fill=255)

        shadow = Image.new("RGBA", layer.size, (0,0,0,0))
        sd = ImageDraw.Draw(shadow)
        sd.text((x+4, y+6), text, font=font, fill=(0,0,0,210), stroke_width=3, stroke_fill=(0,0,0,210))
        shadow = shadow.filter(ImageFilter.GaussianBlur(2))
        layer.alpha_composite(shadow)

        gradient = Image.new("RGBA", layer.size, (0,0,0,0))
        gd = ImageDraw.Draw(gradient)
        top, bottom = box[1], max(box[1]+1, box[3])
        for yy in range(max(0,top), min(layer.height,bottom+3)):
            t = (yy-top)/max(1,bottom-top)
            if t < 0.22:
                c = 247-int(35*t/0.22)
            elif t < 0.50:
                c = 212-int(62*(t-0.22)/0.28)
            elif t < 0.72:
                c = 150+int(90*(t-0.50)/0.22)
            else:
                c = 240-int(90*(t-0.72)/0.28)
            gd.line((box[0]-6,yy,box[2]+6,yy), fill=(c,min(255,c+5),min(255,c+12),255))
        layer.alpha_composite(Image.composite(gradient, Image.new("RGBA", layer.size,(0,0,0,0)), mask))
        hi = ImageDraw.Draw(layer)
        hi.text((x, y-1), text, font=font, fill=(255,255,255,48), stroke_width=1, stroke_fill=(255,255,255,28))

    def render_on_file(self, *, base_path: str, output_path: str, placement: BrandStudyPlacement, geometry: BrandStudyGeometry, accent_hex: str, font_path: str) -> BrandStudyReceipt:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter

        if not geometry.study_only or geometry.publication_ready:
            raise ValueError("brand study renderer accepts study-only geometry")
        source, target, fpath = Path(base_path), Path(output_path), Path(font_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        accent_rgb = self._rgb(accent_hex)
        accent = (*accent_rgb,255)

        with Image.open(source) as raw:
            image = raw.convert("RGBA")
            if placement.x+placement.width > image.width or placement.y+placement.height > image.height:
                raise ValueError("study brand placement exceeds canvas")
            layer = Image.new("RGBA", image.size, (0,0,0,0))
            draw = ImageDraw.Draw(layer)

            base_size = max(24, int(placement.height*0.43))
            font = ImageFont.truetype(str(fpath), base_size)
            seven_font = ImageFont.truetype(str(fpath), max(28,int(base_size*geometry.seven_scale)))
            pul, seven, sar = "PUL", "7", "SAR"
            pul_w = draw.textlength(pul,font=font)
            seven_w = draw.textlength(seven,font=seven_font)
            sar_w = draw.textlength(sar,font=font)
            gap = max(2,int(base_size*0.015))
            total = pul_w+seven_w+sar_w+gap*2
            if total > placement.width*0.90:
                factor = placement.width*0.90/total
                base_size = max(20,int(base_size*factor))
                font = ImageFont.truetype(str(fpath),base_size)
                seven_font = ImageFont.truetype(str(fpath),max(24,int(base_size*geometry.seven_scale)))
                pul_w = draw.textlength(pul,font=font); seven_w = draw.textlength(seven,font=seven_font); sar_w = draw.textlength(sar,font=font)
                total = pul_w+seven_w+sar_w+gap*2

            x = placement.x + int((placement.width-total)/2)
            y = placement.y + int(placement.height*0.08)
            seven_y = max(placement.y, y-int(base_size*(geometry.seven_scale-1.0)*0.42))
            self._metallic_word(layer,pul,font,x,y)
            seven_x = x+pul_w+gap
            sar_x = seven_x+seven_w+gap
            self._metallic_word(layer,sar,font,sar_x,y)

            # Accent 7 with a tight glow and bevel-like face.
            glow = Image.new("RGBA", image.size,(0,0,0,0))
            gdraw = ImageDraw.Draw(glow)
            gdraw.text((seven_x,seven_y),seven,font=seven_font,fill=(*accent_rgb,220),stroke_width=5,stroke_fill=(*accent_rgb,90))
            glow = glow.filter(ImageFilter.GaussianBlur(max(4,int(base_size*0.08))))
            layer.alpha_composite(glow)
            draw = ImageDraw.Draw(layer)
            dark_accent = tuple(max(0,c-70) for c in accent_rgb)+(255,)
            draw.text((seven_x+3,seven_y+5),seven,font=seven_font,fill=(0,0,0,190),stroke_width=2,stroke_fill=(0,0,0,190))
            draw.text((seven_x,seven_y),seven,font=seven_font,fill=accent,stroke_width=2,stroke_fill=dark_accent)
            draw.text((seven_x,seven_y-2),seven,font=seven_font,fill=(255,255,255,52))

            # Pulse below the wordmark, wider and more identity-like than v1.
            pulse_y = placement.y+int(placement.height*geometry.pulse_band_start)
            pulse_h = max(10,int(placement.height*0.22))
            points = (
                (placement.x+int(placement.width*0.06), pulse_y+int(pulse_h*0.55)),
                (placement.x+int(placement.width*0.31), pulse_y+int(pulse_h*0.55)),
                (placement.x+int(placement.width*0.38), pulse_y+int(pulse_h*0.42)),
                (placement.x+int(placement.width*0.44), pulse_y+int(pulse_h*0.10)),
                (placement.x+int(placement.width*0.51), pulse_y+int(pulse_h*0.88)),
                (placement.x+int(placement.width*0.58), pulse_y+int(pulse_h*0.34)),
                (placement.x+int(placement.width*0.65), pulse_y+int(pulse_h*0.55)),
                (placement.x+int(placement.width*0.90), pulse_y+int(pulse_h*0.55)),
            )
            pglow = Image.new("RGBA",image.size,(0,0,0,0)); pg=ImageDraw.Draw(pglow)
            pg.line(points,fill=(*accent_rgb,150),width=max(7,int(placement.height*0.03)),joint="curve")
            pglow=pglow.filter(ImageFilter.GaussianBlur(max(4,int(placement.height*0.02))))
            layer.alpha_composite(pglow)
            draw=ImageDraw.Draw(layer)
            draw.line(points,fill=accent,width=max(2,int(placement.height*0.008)),joint="curve")

            # Football signature near R, small enough to remain punctuation-like.
            cx=placement.x+int(placement.width*geometry.football_center_x)
            cy=placement.y+int(placement.height*geometry.football_center_y)
            radius=max(7,int(placement.width*geometry.football_radius))
            ball_glow=Image.new("RGBA",image.size,(0,0,0,0)); bg=ImageDraw.Draw(ball_glow)
            bg.ellipse((cx-radius-4,cy-radius-4,cx+radius+4,cy+radius+4),fill=(230,240,250,80))
            ball_glow=ball_glow.filter(ImageFilter.GaussianBlur(5)); layer.alpha_composite(ball_glow)
            draw=ImageDraw.Draw(layer)
            draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(235,238,240,255),outline=(75,78,82,255),width=max(1,radius//6))
            inner=max(2,radius//3)
            pts=[]
            for i in range(5):
                a=math.radians(-90+i*72)
                pts.append((cx+inner*math.cos(a),cy+inner*math.sin(a)))
            draw.polygon(pts,fill=(28,30,33,255))
            for angle in (18,90,162,234,306):
                px=cx+int(radius*0.66*math.cos(math.radians(angle))); py=cy+int(radius*0.66*math.sin(math.radians(angle)))
                draw.ellipse((px-inner//2,py-inner//2,px+inner//2,py+inner//2),fill=(45,47,50,255))

            image.alpha_composite(layer)
            target.parent.mkdir(parents=True,exist_ok=True)
            image.save(target,format="PNG")

        return BrandStudyReceipt(output_path=str(target),output_sha256=self._sha(target),accent_hex=accent_hex.upper(),seven_scale=geometry.seven_scale,pulse_below_wordmark=True,football_near_r=True)

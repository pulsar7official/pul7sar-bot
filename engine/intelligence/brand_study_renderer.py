"""Study-only deterministic PUL7SAR identity renderer.

Version 4 preserves metallic PUL/SAR, enlarged accent 7, football near R, and
renders the compact user-confirmed pulse signature around the 7 instead of a
full-width underline. It remains study-only until exact master geometry exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import math

from engine.intelligence.brand_study_geometry import BrandStudyGeometry, REFERENCE_PULSE_WAVEFORM_V2


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
    pulse_waveform_id: str
    pulse_full_wordmark_underline: bool
    pulse_left_extent: float
    pulse_right_extent: float
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-study-renderer-v4"


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
        layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
        gradient = Image.new("RGBA", layer.size, (0,0,0,0))
        gd = ImageDraw.Draw(gradient)
        top, bottom = box[1], max(box[1]+1, box[3])
        for yy in range(max(0,top), min(layer.height,bottom+3)):
            t = (yy-top)/max(1,bottom-top)
            c = int(246 - 92*t + 70*abs(0.52-t))
            c = max(130,min(250,c))
            gd.line((box[0]-6,yy,box[2]+6,yy), fill=(c,min(255,c+5),min(255,c+12),255))
        layer.alpha_composite(Image.composite(gradient, Image.new("RGBA", layer.size,(0,0,0,0)), mask))

    @staticmethod
    def _pulse_points(placement: BrandStudyPlacement, geometry: BrandStudyGeometry):
        band_y = placement.y + int(placement.height * geometry.pulse_band_start)
        band_h = max(12, int(placement.height * geometry.pulse_band_height))
        return tuple(
            (
                placement.x + int(placement.width * nx),
                band_y + int(band_h * ny),
            )
            for nx, ny in REFERENCE_PULSE_WAVEFORM_V2
        )

    def render_on_file(self, *, base_path: str, output_path: str, placement: BrandStudyPlacement, geometry: BrandStudyGeometry, accent_hex: str, font_path: str) -> BrandStudyReceipt:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        if not geometry.study_only or geometry.publication_ready:
            raise ValueError("brand study renderer accepts study-only geometry")
        if geometry.pulse_waveform_id != "reference-pulse-v2-compact" or not geometry.pulse_visual_link_to_seven:
            raise ValueError("brand study renderer requires approved compact pulse reference")
        if geometry.pulse_full_wordmark_underline:
            raise ValueError("brand study renderer forbids full-wordmark pulse underline")
        source, target, fpath = Path(base_path), Path(output_path), Path(font_path)
        if not source.is_file(): raise FileNotFoundError(base_path)
        if not fpath.is_file(): raise FileNotFoundError(font_path)
        accent_rgb = self._rgb(accent_hex); accent = (*accent_rgb,255)

        with Image.open(source) as raw:
            image = raw.convert("RGBA")
            if placement.x+placement.width > image.width or placement.y+placement.height > image.height:
                raise ValueError("study brand placement exceeds canvas")
            layer = Image.new("RGBA", image.size, (0,0,0,0)); draw = ImageDraw.Draw(layer)
            base_size = max(24, int(placement.height*0.40))
            font = ImageFont.truetype(str(fpath), base_size)
            seven_font = ImageFont.truetype(str(fpath), max(28,int(base_size*geometry.seven_scale)))
            pul, seven, sar = "PUL", "7", "SAR"
            pul_w=draw.textlength(pul,font=font); seven_w=draw.textlength(seven,font=seven_font); sar_w=draw.textlength(sar,font=font)
            gap=max(2,int(base_size*0.015)); total=pul_w+seven_w+sar_w+gap*2
            if total > placement.width*0.90:
                factor=placement.width*0.90/total; base_size=max(20,int(base_size*factor))
                font=ImageFont.truetype(str(fpath),base_size); seven_font=ImageFont.truetype(str(fpath),max(24,int(base_size*geometry.seven_scale)))
                pul_w=draw.textlength(pul,font=font); seven_w=draw.textlength(seven,font=seven_font); sar_w=draw.textlength(sar,font=font); total=pul_w+seven_w+sar_w+gap*2
            x=placement.x+int((placement.width-total)/2); y=placement.y+int(placement.height*0.06)
            seven_y=max(placement.y,y-int(base_size*(geometry.seven_scale-1.0)*0.44))
            self._metallic_word(layer,pul,font,x,y)
            seven_x=x+pul_w+gap; sar_x=seven_x+seven_w+gap
            self._metallic_word(layer,sar,font,sar_x,y)

            glow=Image.new("RGBA",image.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
            gd.text((seven_x,seven_y),seven,font=seven_font,fill=(*accent_rgb,220),stroke_width=5,stroke_fill=(*accent_rgb,90))
            layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(max(4,int(base_size*0.08)))))
            draw=ImageDraw.Draw(layer); dark=tuple(max(0,c-70) for c in accent_rgb)+(255,)
            draw.text((seven_x+3,seven_y+5),seven,font=seven_font,fill=(0,0,0,190),stroke_width=2,stroke_fill=(0,0,0,190))
            draw.text((seven_x,seven_y),seven,font=seven_font,fill=accent,stroke_width=2,stroke_fill=dark)

            # Compact signature: short horizontal shoulders, concentrated pulse
            # around the enlarged 7, two recovery beats, no full-word underline.
            points=self._pulse_points(placement,geometry)
            pglow=Image.new("RGBA",image.size,(0,0,0,0)); pg=ImageDraw.Draw(pglow)
            pg.line(points,fill=(*accent_rgb,175),width=max(7,int(placement.height*0.032)),joint="curve")
            layer.alpha_composite(pglow.filter(ImageFilter.GaussianBlur(max(4,int(placement.height*0.02)))))
            draw=ImageDraw.Draw(layer)
            draw.line(points,fill=accent,width=max(2,int(placement.height*0.009)),joint="curve")
            core=tuple(min(255,int(c*0.55+140)) for c in accent_rgb)+(235,)
            draw.line(points,fill=core,width=max(1,int(placement.height*0.0035)),joint="curve")

            cx=placement.x+int(placement.width*geometry.football_center_x); cy=placement.y+int(placement.height*geometry.football_center_y)
            radius=max(7,int(placement.width*geometry.football_radius))
            draw.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(235,238,240,255),outline=(75,78,82,255),width=max(1,radius//6))
            inner=max(2,radius//3); pts=[]
            for i in range(5):
                a=math.radians(-90+i*72); pts.append((cx+inner*math.cos(a),cy+inner*math.sin(a)))
            draw.polygon(pts,fill=(28,30,33,255))
            image.alpha_composite(layer); target.parent.mkdir(parents=True,exist_ok=True); image.save(target,format="PNG")

        return BrandStudyReceipt(
            output_path=str(target), output_sha256=self._sha(target), accent_hex=accent_hex.upper(),
            seven_scale=geometry.seven_scale, pulse_below_wordmark=True, football_near_r=True,
            pulse_waveform_id=geometry.pulse_waveform_id,
            pulse_full_wordmark_underline=geometry.pulse_full_wordmark_underline,
            pulse_left_extent=geometry.pulse_left_extent, pulse_right_extent=geometry.pulse_right_extent,
        )

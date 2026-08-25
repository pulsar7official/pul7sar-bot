"""Fully original procedural Result Scene benchmark for PUL7SAR.

V3 is a frameless, source-photo-free result composition. The exact score itself
is the physical visual hero: code-rendered metallic faces, controlled extrusion,
edge light, atmospheric team-color contamination, haze and arena-scale depth.
No source photograph, diffusion model, network call, fabricated crest, pitch,
scoreboard card or decorative PUL7SAR pulse is used.
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
    visual_language: str = "frameless_metallic_cinematic_score_monument"
    container_panel_used: bool = False
    perspective_grid_used: bool = False
    decorative_pulse_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-original-result-scene-renderer-v3-metallic"


class OriginalResultSceneRenderer:
    CONTRACT = "pul7sar-original-result-scene-renderer-v3-metallic"

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
            if r-l <= max_width and b-t <= max_height:
                return font
            size -= 2
        return ImageFont.truetype(font_path, size=12)

    @staticmethod
    def _text_xy(draw, text: str, font, cx: float, cy: float, *, stroke_width: int = 0) -> tuple[float, float]:
        l, t, r, b = draw.textbbox((0,0), text, font=font, stroke_width=stroke_width)
        return cx-(r-l)/2-l, cy-(b-t)/2-t

    @classmethod
    def _center(cls, draw, text: str, font, cx: float, cy: float, fill, *, stroke_width: int = 0, stroke_fill=None) -> None:
        x,y = cls._text_xy(draw, text, font, cx, cy, stroke_width=stroke_width)
        draw.text((x,y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)

    @classmethod
    def _base_world(cls, image, *, left: tuple[int,int,int], right: tuple[int,int,int], seed: int) -> None:
        from PIL import Image, ImageDraw, ImageFilter
        w,h = image.size
        rng = Random(seed)
        d = ImageDraw.Draw(image, "RGBA")

        for y in range(h):
            t = y/max(1,h-1)
            d.line((0,y,w,y), fill=(int(7-2*t), int(13-4*t), int(24-5*t), 255))

        air = Image.new("RGBA",(w,h),(0,0,0,0)); ad = ImageDraw.Draw(air,"RGBA")
        ad.ellipse((-w*.55,h*.10,w*.55,h*.90), fill=(*left,108))
        ad.ellipse((w*.45,h*.10,w*1.55,h*.90), fill=(*right,92))
        ad.ellipse((w*.25,h*.20,w*.75,h*.72), fill=(230,237,243,23))
        image.alpha_composite(air.filter(ImageFilter.GaussianBlur(max(62,int(w*.15)))))

        rig = Image.new("RGBA",(w,h),(0,0,0,0)); rd = ImageDraw.Draw(rig,"RGBA")
        for i in range(13):
            x=int(w*(.09+i*.068)); p=80 if 4<=i<=8 else 42; r=2 if i%3 else 3
            rd.ellipse((x-r,h*.135-r,x+r,h*.135+r), fill=(243,247,250,p))
        for x,a,s in ((.25,23,.15),(.39,18,.11),(.61,18,.11),(.75,23,.15)):
            tx=int(w*x)
            rd.polygon([(tx-3,int(h*.14)),(tx+3,int(h*.14)),(tx+int(w*s),int(h*.67)),(tx-int(w*s),int(h*.67))], fill=(240,245,249,a))
        image.alpha_composite(rig.filter(ImageFilter.GaussianBlur(max(16,int(w*.028)))))

        crowd=Image.new("RGBA",(w,h),(0,0,0,0)); cd=ImageDraw.Draw(crowd,"RGBA")
        for _ in range(210):
            x=rng.randint(int(w*.035),int(w*.965)); nx=(x-w/2)/(w/2)
            y=int(h*(.66+.030*nx*nx)+rng.uniform(-h*.032,h*.034))
            r=rng.choice((1,1,1,2,2,3)); a=rng.randint(14,65)
            if rng.random()<.10: color=(*left,a) if x<w/2 else (*right,a)
            else: color=(226,233,239,a)
            cd.ellipse((x-r,y-r,x+r,y+r),fill=color)
        image.alpha_composite(crowd.filter(ImageFilter.GaussianBlur(1.5)))

        # Soft reflective pool remains behind the score only, never around brand.
        stage=Image.new("RGBA",(w,h),(0,0,0,0)); sd=ImageDraw.Draw(stage,"RGBA")
        sd.ellipse((w*.18,h*.55,w*.82,h*.79), fill=(230,237,242,12))
        sd.ellipse((w*.27,h*.60,w*.73,h*.75), fill=(245,248,250,10))
        image.alpha_composite(stage.filter(ImageFilter.GaussianBlur(max(18,int(w*.035)))))

        haze=Image.new("RGBA",(w,h),(0,0,0,0)); hd=ImageDraw.Draw(haze,"RGBA")
        hd.ellipse((w*.18,h*.24,w*.82,h*.67),fill=(225,233,240,30))
        hd.ellipse((w*.30,h*.31,w*.70,h*.58),fill=(250,251,252,17))
        image.alpha_composite(haze.filter(ImageFilter.GaussianBlur(max(48,int(w*.12)))))

        dust=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(dust,"RGBA")
        for _ in range(48):
            x=rng.randint(int(w*.08),int(w*.92)); y=rng.randint(int(h*.48),int(h*.80)); r=rng.choice((1,1,2,2,3)); a=rng.randint(9,36)
            dd.ellipse((x-r,y-r,x+r,y+r),fill=(238,243,247,a))
        image.alpha_composite(dust.filter(ImageFilter.GaussianBlur(1.0)))

        vig=Image.new("RGBA",(w,h),(0,0,0,0)); vd=ImageDraw.Draw(vig,"RGBA"); edge=int(w*.12)
        vd.rectangle((0,0,edge,h),fill=(0,0,0,90)); vd.rectangle((w-edge,0,w,h),fill=(0,0,0,90))
        vd.rectangle((0,0,w,int(h*.085)),fill=(0,0,0,70)); vd.rectangle((0,int(h*.91),w,h),fill=(0,0,0,92))
        image.alpha_composite(vig.filter(ImageFilter.GaussianBlur(max(30,int(w*.05)))))

    @classmethod
    def _metal_text(cls, image, text: str, *, cx: float, cy: float, font, accent: tuple[int,int,int]) -> None:
        from PIL import Image, ImageChops, ImageDraw, ImageFilter
        w,h=image.size
        probe=ImageDraw.Draw(image,"RGBA")
        x,y=cls._text_xy(probe,text,font,cx,cy,stroke_width=0)

        # Environmental aura behind the numeral.
        aura=Image.new("RGBA",(w,h),(0,0,0,0)); au=ImageDraw.Draw(aura,"RGBA")
        au.ellipse((cx-w*.13,cy-h*.11,cx+w*.13,cy+h*.12),fill=(*accent,75))
        image.alpha_composite(aura.filter(ImageFilter.GaussianBlur(max(28,int(w*.052)))))

        # Extrusion: directional, compact, gunmetal rather than black cartoon shadow.
        ext=Image.new("RGBA",(w,h),(0,0,0,0)); ed=ImageDraw.Draw(ext,"RGBA")
        for off in range(15,0,-1):
            tone=int(35+off*.9)
            ed.text((x+off*.42,y+off*.70),text,font=font,fill=(tone,tone+3,tone+8,250),stroke_width=2,stroke_fill=(8,10,14,245))
        image.alpha_composite(ext)

        # Exact glyph mask.
        mask=Image.new("L",(w,h),0); md=ImageDraw.Draw(mask)
        md.text((x,y),text,font=font,fill=255)

        # Metallic face: high-low-high tonal sweep gives brushed metal depth.
        metal=Image.new("RGBA",(w,h),(0,0,0,0)); gd=ImageDraw.Draw(metal,"RGBA")
        top=max(0,int(cy-h*.12)); bottom=min(h-1,int(cy+h*.13)); span=max(1,bottom-top)
        stops=((0.00,(252,253,254)),(.18,(205,211,217)),(.38,(247,249,250)),(.58,(150,159,169)),(.78,(232,236,239)),(1.0,(188,196,204)))
        def interp(t):
            for i in range(len(stops)-1):
                a,c0=stops[i]; b,c1=stops[i+1]
                if a<=t<=b:
                    q=(t-a)/max(.0001,b-a); return tuple(int(c0[j]+(c1[j]-c0[j])*q) for j in range(3))
            return stops[-1][1]
        for yy in range(top,bottom+1):
            c=interp((yy-top)/span); gd.line((0,yy,w,yy),fill=(*c,255))
        image.alpha_composite(Image.composite(metal,Image.new("RGBA",(w,h),(0,0,0,0)),mask))

        # Crisp steel border + inner specular edge.
        outer=mask.filter(ImageFilter.MaxFilter(7)); border=ImageChops.subtract(outer,mask)
        edge_layer=Image.new("RGBA",(w,h),(98,108,119,0)); edge_layer.putalpha(border.point(lambda p:min(210,p)))
        image.alpha_composite(edge_layer)
        inner=ImageChops.subtract(mask,mask.filter(ImageFilter.MinFilter(3)))
        hi=Image.new("RGBA",(w,h),(255,255,255,0)); hi.putalpha(inner.point(lambda p:min(155,p)))
        image.alpha_composite(hi)

    @classmethod
    def _monument(cls,image,*,home_score:int,away_score:int,font_path:str,left,right)->str:
        from PIL import Image,ImageDraw,ImageFilter
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA")
        font=cls._fit_font(d,str(max(home_score,away_score)),font_path,int(w*.255),int(h*.235),int(h*.215))
        dash=cls._fit_font(d,"–",font_path,int(w*.07),int(h*.055),int(h*.050)); cy=h*.415
        halo=Image.new("RGBA",(w,h),(0,0,0,0)); q=ImageDraw.Draw(halo,"RGBA")
        q.ellipse((w*.23,h*.29,w*.77,h*.57),fill=(235,241,245,19))
        image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(max(38,int(w*.075)))))
        cls._metal_text(image,str(home_score),cx=w*.355,cy=cy,font=font,accent=left)
        cls._metal_text(image,str(away_score),cx=w*.645,cy=cy,font=font,accent=right)
        d=ImageDraw.Draw(image,"RGBA"); cls._center(d,"–",dash,w/2,cy+3,(181,191,202,205))
        return f"{home_score}–{away_score}"

    @classmethod
    def _copy_and_identity(cls,image,*,headline:str,home:str,away:str,font_path:str,left,right,winner:str|None)->None:
        from PIL import Image,ImageDraw,ImageFilter
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA")
        # One restrained factual label; generic benchmark headline becomes a kicker.
        kicker=cls._fit_font(d,headline,font_path,int(w*.50),int(h*.036),int(h*.028))
        cls._center(d,headline.upper(),kicker,w/2,h*.175,(213,221,228,210))
        label=cls._fit_font(d,"FULL TIME",font_path,int(w*.14),int(h*.022),int(h*.016))
        cls._center(d,"FULL TIME",label,w/2,h*.247,(147,160,173,166))

        name_font=cls._fit_font(d,max(home,away,key=len),font_path,int(w*.28),int(h*.036),int(h*.027))
        for side,x,name,accent in (("home",.30,home,left),("away",.70,away,right)):
            if winner==side:
                g=Image.new("RGBA",(w,h),(0,0,0,0)); gd=ImageDraw.Draw(g,"RGBA")
                gd.ellipse((w*x-w*.065,h*.575-h*.018,w*x+w*.065,h*.575+h*.018),fill=(*accent,34))
                image.alpha_composite(g.filter(ImageFilter.GaussianBlur(max(9,int(w*.017))))); d=ImageDraw.Draw(image,"RGBA")
            cls._center(d,name.upper(),name_font,w*x,h*.605,(225,232,238,225))
            bw=w*.043; yy=h*.565
            d.rounded_rectangle((w*x-bw/2,yy-1.5,w*x+bw/2,yy+1.5),radius=2,fill=(*accent,195))

    def render(self,composition:ResultStatementComposition,*,profile:PlatformImageProfile,output_path:str,
               home_name:str,away_name:str,home_score:int,away_score:int,headline:str,
               home_accent_hex:str,away_accent_hex:str,brand_accent_hex:str,font_path:str,
               winner:str|None=None,seed:int=18001)->OriginalResultSceneReceipt:
        from PIL import Image
        if not isinstance(composition,ResultStatementComposition): raise TypeError("composition must be ResultStatementComposition")
        if not isinstance(profile,PlatformImageProfile): raise TypeError("profile must be PlatformImageProfile")
        if winner not in {None,"home","away"}: raise ValueError("winner must be home, away or None")
        if not Path(font_path).is_file(): raise FileNotFoundError(font_path)
        if any(isinstance(v,bool) or not isinstance(v,int) or v<0 for v in (home_score,away_score)): raise ValueError("scores must be non-negative integers")
        if not home_name.strip() or not away_name.strip() or not headline.strip(): raise ValueError("team names and headline are required")
        left=self._rgb(home_accent_hex); right=self._rgb(away_accent_hex)
        image=Image.new("RGBA",(profile.width,profile.height),(7,12,20,255))
        self._base_world(image,left=left,right=right,seed=seed)
        score_text=self._monument(image,home_score=home_score,away_score=away_score,font_path=font_path,left=left,right=right)
        self._copy_and_identity(image,headline=headline,home=home_name,away=away_name,font_path=font_path,left=left,right=right,winner=winner)
        target=Path(output_path); target.parent.mkdir(parents=True,exist_ok=True); pre=target.with_name(target.stem+".prebrand.png")
        image.convert("RGB").save(pre,"PNG")
        brand=AdaptiveBrandOverlayRenderer().render_on_file(base_path=str(pre),output_path=str(target),adaptive=composition.brand,profile=profile,accent_hex=brand_accent_hex)
        pre.unlink(missing_ok=True)
        return OriginalResultSceneReceipt(output_path=str(target),output_sha256=self._sha(target),width=profile.width,height=profile.height,
            score_text=score_text,scene_origin="100_percent_code_generated_original_pixels",source_photo_used=False,generator_used=False,
            network_used=False,fabricated_crest_used=False,brand_overlay_contract=brand.contract)

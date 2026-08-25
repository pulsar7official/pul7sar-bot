"""Original procedural pixel renderer for every PUL7SAR editorial family.

The renderer intentionally uses radically different spatial grammars per archetype.
It creates no real-person likeness and no club crest. Exact crests/subjects may be
added only through verified deterministic asset layers in a later production pass.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import cos, pi, sin
from pathlib import Path
from random import Random

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_scene_blueprint import VisualSceneBlueprint


@dataclass(frozen=True)
class FamilySceneRequest:
    blueprint: VisualSceneBlueprint
    headline: str
    primary_label: str
    secondary_label: str = ""
    primary_value: str = ""
    accent_a: str = "#E30613"
    accent_b: str = "#2878FF"
    brand_accent: str = "#E30613"
    seed: int = 18


@dataclass(frozen=True)
class FamilySceneReceipt:
    output_path: str
    output_sha256: str
    family: str
    archetype_id: str
    width: int
    height: int
    source_photo_used: bool = False
    generator_used: bool = False
    network_used: bool = False
    fabricated_crest_used: bool = False
    placeholder_used: bool = False
    real_person_depicted: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-original-family-scene-renderer-v1"


class OriginalFamilySceneRenderer:
    CONTRACT = "pul7sar-original-family-scene-renderer-v1"

    @staticmethod
    def _rgb(hex_value: str) -> tuple[int, int, int]:
        text = hex_value.strip().lstrip("#")
        if len(text) != 6:
            raise ValueError("color must be RRGGBB")
        return tuple(int(text[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _font(path: str, size: int):
        from PIL import ImageFont
        return ImageFont.truetype(path, max(10, size))

    @classmethod
    def _fit(cls, draw, text: str, path: str, max_w: int, start: int, min_size: int = 16):
        size = start
        while size >= min_size:
            f = cls._font(path, size)
            box = draw.textbbox((0, 0), text, font=f)
            if box[2] - box[0] <= max_w:
                return f
            size -= 2
        return cls._font(path, min_size)

    @staticmethod
    def _center(draw, xy, text, font, fill, *, anchor="mm", stroke_width=0, stroke_fill=None):
        draw.text(xy, text, font=font, fill=fill, anchor=anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)

    @staticmethod
    def _glow_ellipse(image, box, color, alpha=100, blur=60):
        from PIL import Image, ImageDraw, ImageFilter
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer, "RGBA")
        d.ellipse(box, fill=(*color, alpha)); image.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))

    @staticmethod
    def _glow_line(image, points, color, width=4, alpha=150, blur=14):
        from PIL import Image, ImageDraw, ImageFilter
        glow = Image.new("RGBA", image.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow, "RGBA")
        gd.line(points, fill=(*color, alpha), width=width)
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))
        ImageDraw.Draw(image, "RGBA").line(points, fill=(*color, min(235, alpha+55)), width=max(1, width//2))

    @classmethod
    def _base(cls, image, a, b, seed: int, *, energy: float = 1.0):
        from PIL import Image, ImageDraw, ImageFilter
        w, h = image.size; rng = Random(seed); d = ImageDraw.Draw(image, "RGBA")
        for y in range(h):
            t = y / max(1, h-1)
            d.line((0, y, w, y), fill=(int(5+5*(1-t)), int(9+8*(1-t)), int(18+11*(1-t)), 255))
        cls._glow_ellipse(image, (-w*.7, h*.02, w*.48, h*.96), a, int(72*energy), int(w*.15))
        cls._glow_ellipse(image, (w*.52, h*.02, w*1.7, h*.96), b, int(60*energy), int(w*.17))
        haze = Image.new("RGBA", image.size, (0,0,0,0)); hd = ImageDraw.Draw(haze,"RGBA")
        hd.ellipse((w*.18,h*.18,w*.82,h*.82), fill=(225,235,244,int(24*energy)))
        image.alpha_composite(haze.filter(ImageFilter.GaussianBlur(int(w*.12))))
        dust = Image.new("RGBA", image.size, (0,0,0,0)); dd=ImageDraw.Draw(dust,"RGBA")
        for _ in range(int(70*energy)):
            x=rng.randint(int(w*.04),int(w*.96)); y=rng.randint(int(h*.08),int(h*.88)); r=rng.choice((1,1,1,2,2,3)); al=rng.randint(8,30)
            dd.ellipse((x-r,y-r,x+r,y+r), fill=(236,242,247,al))
        image.alpha_composite(dust.filter(ImageFilter.GaussianBlur(.8)))
        vignette=Image.new("RGBA",image.size,(0,0,0,0)); vd=ImageDraw.Draw(vignette,"RGBA")
        vd.rectangle((0,0,w*.09,h),fill=(0,0,0,80)); vd.rectangle((w*.91,0,w,h),fill=(0,0,0,80)); vd.rectangle((0,h*.92,w,h),fill=(0,0,0,95))
        image.alpha_composite(vignette.filter(ImageFilter.GaussianBlur(int(w*.04))))

    @classmethod
    def _metal_text(cls, image, text, cx, cy, font, accent, *, scale_glow=1.0):
        from PIL import Image, ImageChops, ImageDraw, ImageFilter
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); box=d.textbbox((0,0),text,font=font); tw=box[2]-box[0]; th=box[3]-box[1]; x=int(cx-tw/2-box[0]); y=int(cy-th/2-box[1])
        cls._glow_ellipse(image,(cx-tw*.72,cy-th*.8,cx+tw*.72,cy+th*.8),accent,int(70*scale_glow),int(max(22,tw*.18)))
        extr=Image.new("RGBA",image.size,(0,0,0,0)); ed=ImageDraw.Draw(extr,"RGBA")
        for off in range(12,0,-1): ed.text((x+off*.55,y+off*.7),text,font=font,fill=(34+off,38+off,45+off,245),stroke_width=2,stroke_fill=(7,9,13,245))
        image.alpha_composite(extr)
        mask=Image.new("L",image.size,0); ImageDraw.Draw(mask).text((x,y),text,font=font,fill=255)
        face=Image.new("RGBA",image.size,(0,0,0,0)); fd=ImageDraw.Draw(face,"RGBA")
        top=max(0,int(cy-th*.75)); bot=min(h-1,int(cy+th*.75)); span=max(1,bot-top)
        stops=((244,247,250),(160,169,180),(252,253,254),(114,124,136),(226,231,236))
        for yy in range(top,bot+1):
            q=(yy-top)/span*(len(stops)-1); i=min(len(stops)-2,int(q)); z=q-i; c=tuple(int(stops[i][j]*(1-z)+stops[i+1][j]*z) for j in range(3)); fd.line((0,yy,w,yy),fill=(*c,255))
        image.alpha_composite(Image.composite(face,Image.new("RGBA",image.size,(0,0,0,0)),mask))
        outer=mask.filter(ImageFilter.MaxFilter(5)); edge=ImageChops.subtract(outer,mask); el=Image.new("RGBA",image.size,(117,128,140,0)); el.putalpha(edge.point(lambda p:min(205,p))); image.alpha_composite(el)

    @staticmethod
    def _ball(draw, cx, cy, r, *, alpha=220):
        draw.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(228,233,238,alpha), outline=(100,112,124,alpha), width=max(1,int(r*.05)))
        pts=[]
        for i in range(5):
            ang=-pi/2+i*2*pi/5; pts.append((cx+cos(ang)*r*.30,cy+sin(ang)*r*.30))
        draw.polygon(pts,fill=(22,28,35,alpha))
        for x,y in pts: draw.line((x,y,cx+((x-cx)*2.4),cy+((y-cy)*2.4)),fill=(75,84,94,alpha),width=max(1,int(r*.035)))

    def _transfer(self, image, req, font_path, a, b):
        from PIL import Image, ImageDraw, ImageFilter
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id
        if aid=="threshold_arrival":
            for k in range(7):
                x=w*(.12+k*.065); self._glow_line(image,[(x,h*.16),(x+w*.18,h*.80)],a if k<3 else b,width=5,alpha=70,blur=25)
            d.polygon([(w*.57,h*.18),(w*.86,h*.12),(w*.82,h*.80),(w*.55,h*.74)],fill=(8,13,22,190),outline=(*b,130))
            # abstract jersey, explicitly not a person
            d.polygon([(w*.63,h*.36),(w*.70,h*.31),(w*.78,h*.36),(w*.75,h*.64),(w*.66,h*.64)],fill=(220,225,231,36),outline=(235,239,242,130),width=3)
            tx=w*.12
        elif aid=="identity_transition":
            d.polygon([(0,0),(w*.46,0),(w*.60,h),(0,h)],fill=(*a,34)); d.polygon([(w*.54,0),(w,0),(w,h),(w*.40,h)],fill=(*b,30))
            self._glow_line(image,[(w*.47,h*.12),(w*.56,h*.85)],(225,234,242),width=3,alpha=80,blur=16)
            for r in (w*.12,w*.18,w*.25): d.arc((w*.5-r,h*.47-r,w*.5+r,h*.47+r),200,340,fill=(230,236,241,70),width=2)
            tx=w*.50
        elif aid=="signing_object":
            # contract/paper object only for confirmed signing benchmark, no signature
            d.rounded_rectangle((w*.18,h*.28,w*.72,h*.70),radius=24,fill=(221,226,231,28),outline=(231,237,242,120),width=3)
            for i in range(5): d.rounded_rectangle((w*.25,h*(.39+i*.045),w*(.58+i*.012),h*(.39+i*.045)+4),2,fill=(228,234,239,80))
            d.ellipse((w*.66,h*.51,w*.78,h*.63),outline=(*a,150),width=5)
            tx=w*.18
        else:
            d.polygon([(w*.08,h*.70),(w*.30,h*.20),(w*.66,h*.13),(w*.91,h*.72)],fill=(220,229,236,22),outline=(*b,105),width=3)
            for k in range(5): self._glow_line(image,[(w*(.18+k*.13),h*.70),(w*(.34+k*.08),h*.28)],b,width=3,alpha=55,blur=18)
            tx=w*.12
        f=self._fit(d,req.headline,font_path,int(w*.68),54,28); d.text((tx,h*.16 if aid!="identity_transition" else h*.13),req.headline.upper(),font=f,fill=(239,243,247,235),anchor="la")
        sf=self._fit(d,req.primary_label,font_path,int(w*.45),28,18); d.text((tx,h*.22),req.primary_label.upper(),font=sf,fill=(*a,230),anchor="la")

    def _result(self, image, req, font_path, a, b):
        from PIL import ImageDraw
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id; score=req.primary_value or "3–1"
        if aid=="score_monument":
            f=self._fit(d,score,font_path,int(w*.46),180,80); self._metal_text(image,score,w*.50,h*.43,f,a,scale_glow=.75); y=h*.68
        elif aid=="club_duel_space":
            d.polygon([(0,h*.15),(w*.48,h*.28),(w*.40,h*.83),(0,h*.90)],fill=(*a,38)); d.polygon([(w,h*.12),(w*.52,h*.28),(w*.61,h*.84),(w,h*.91)],fill=(*b,34))
            f=self._fit(d,score,font_path,int(w*.32),120,64); self._metal_text(image,score,w*.62,h*.50,f,b,scale_glow=.55); y=h*.73
        elif aid=="aftermath_editorial":
            f=self._fit(d,score,font_path,int(w*.28),100,54); self._metal_text(image,score,w*.27,h*.57,f,a,scale_glow=.35); self._ball(d,w*.76,h*.60,w*.075,alpha=120); y=h*.76
        else:
            # wide arena: score deliberately secondary
            for i in range(9):
                yy=h*(.38+i*.035); d.arc((w*.05,yy,w*.95,yy+h*.26),200,340,fill=(220,228,235,35+i*4),width=2)
            for x in (w*.15,w*.32,w*.68,w*.85): self._glow_line(image,[(x,h*.16),(w*.5,h*.68)],(235,240,245),width=2,alpha=30,blur=12)
            f=self._fit(d,score,font_path,int(w*.25),92,50); self._metal_text(image,score,w*.50,h*.60,f,a,scale_glow=.35); y=h*.77
        hf=self._fit(d,req.headline,font_path,int(w*.64),44,24); d.text((w*.50,h*.16),req.headline.upper(),font=hf,fill=(237,242,246,230),anchor="ma")
        nf=self._fit(d,max(req.primary_label,req.secondary_label,key=len),font_path,int(w*.30),26,16)
        d.text((w*.27,y),req.primary_label.upper(),font=nf,fill=(232,237,241,220),anchor="mm"); d.text((w*.73,y),req.secondary_label.upper(),font=nf,fill=(232,237,241,220),anchor="mm")
        d.line((w*.18,y+h*.035,w*.36,y+h*.035),fill=(*a,150),width=3); d.line((w*.64,y+h*.035,w*.82,y+h*.035),fill=(*b,150),width=3)

    def _subject(self, image, req, font_path, a, b):
        from PIL import ImageDraw
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id
        if aid=="absence_space":
            # empty luminous seat/tunnel: absence without fake person
            d.rounded_rectangle((w*.16,h*.28,w*.46,h*.72),36,fill=(8,13,21,170),outline=(227,234,240,80),width=3)
            d.rounded_rectangle((w*.23,h*.46,w*.39,h*.61),18,fill=(225,232,238,20),outline=(*a,110),width=3)
            self._glow_line(image,[(w*.50,h*.19),(w*.78,h*.70)],a,width=5,alpha=55,blur=24); tx=w*.55
        elif aid=="statement_stage":
            for x in (.27,.39,.51):
                d.line((w*x,h*.43,w*x,h*.67),fill=(218,226,233,90),width=4); d.ellipse((w*x-9,h*.40-9,w*x+9,h*.40+9),fill=(228,235,240,130))
            d.rounded_rectangle((w*.17,h*.67,w*.63,h*.71),8,fill=(223,231,237,55)); tx=w*.66
        elif aid=="subject_detail":
            # abstract equipment detail, no face
            self._ball(d,w*.30,h*.50,w*.15,alpha=170); d.arc((w*.12,h*.25,w*.50,h*.74),20,160,fill=(*a,150),width=6); tx=w*.56
        else:
            # verified-subject slot represented as protected negative silhouette zone, never fake portrait
            d.ellipse((w*.16,h*.25,w*.48,h*.57),fill=(225,232,238,14),outline=(225,233,239,45),width=2); d.rounded_rectangle((w*.12,h*.48,w*.52,h*.84),80,fill=(225,232,238,10)); tx=w*.58
        f=self._fit(d,req.headline,font_path,int(w*(.34 if tx>w*.5 else .48)),52,26); d.text((tx,h*.30),req.headline.upper(),font=f,fill=(239,243,247,235),anchor="la")
        sf=self._fit(d,req.primary_label,font_path,int(w*.32),26,16); d.text((tx,h*.42),req.primary_label.upper(),font=sf,fill=(*a,220),anchor="la")

    def _tactical(self, image, req, font_path, a, b):
        from PIL import ImageDraw
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id
        # exact deterministic geometry; layouts are substantially different
        if aid=="topology_map":
            box=(w*.14,h*.23,w*.86,h*.79); d.rounded_rectangle(box,20,outline=(220,231,238,105),width=3); d.line((w*.50,h*.23,w*.50,h*.79),fill=(220,231,238,75),width=2); d.ellipse((w*.43,h*.45,w*.57,h*.57),outline=(220,231,238,75),width=2)
            pts=[(.26,.36),(.36,.47),(.31,.66),(.50,.37),(.50,.62),(.68,.35),(.64,.52),(.73,.66)]
        elif aid=="phase_corridor":
            d.polygon([(w*.08,h*.30),(w*.86,h*.20),(w*.92,h*.72),(w*.18,h*.80)],fill=(20,45,39,140),outline=(220,231,238,90)); pts=[(.18,.61),(.31,.53),(.45,.47),(.59,.40),(.75,.33)]
        elif aid=="layered_shape":
            pts=[]
            for row,yy in enumerate((.34,.48,.62,.74)):
                xs=(.23,.50,.77) if row in (0,3) else (.17,.38,.62,.83)
                for x in xs: pts.append((x,yy))
                d.line((w*.11,h*yy,w*.89,h*yy),fill=(226,234,240,35),width=2)
        else:
            d.polygon([(w*.08,h*.30),(w*.48,h*.22),(w*.50,h*.78),(w*.12,h*.82)],fill=(*a,28)); d.polygon([(w*.52,h*.22),(w*.92,h*.30),(w*.88,h*.82),(w*.50,h*.78)],fill=(*b,25)); pts=[(.22,.39),(.34,.54),(.27,.69),(.67,.38),(.76,.53),(.69,.69)]
        px=[(w*x,h*y) for x,y in pts]
        for i,(x,y) in enumerate(px):
            c=a if i<len(px)//2 else b; d.ellipse((x-11,y-11,x+11,y+11),fill=(*c,210),outline=(245,248,250,210),width=2)
            if i+1<len(px): d.line((x,y,px[i+1][0],px[i+1][1]),fill=(*c,80),width=3)
        f=self._fit(d,req.headline,font_path,int(w*.55),42,22); d.text((w*.12,h*.12),req.headline.upper(),font=f,fill=(237,242,246,230),anchor="la")

    def _data(self, image, req, font_path, a, b):
        from PIL import ImageDraw
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id; value=req.primary_value or "27"
        if aid=="number_sculpture":
            f=self._fit(d,value,font_path,int(w*.45),210,90); self._metal_text(image,value,w*.36,h*.47,f,a,scale_glow=.7); tx=w*.62
        elif aid=="table_rise":
            tx=w*.12
            for i,(lab,v) in enumerate((("01",.82),("02",.67),("03",.53),("04",.38))):
                y=h*(.34+i*.10); d.text((w*.14,y),lab,font=self._font(font_path,24),fill=(230,236,241,165),anchor="mm"); d.rounded_rectangle((w*.20,y-8,w*(.20+v*.62),y+8),8,fill=(*(a if i==0 else (112,126,141)),170))
            d.polygon([(w*.77,h*.27),(w*.82,h*.18),(w*.87,h*.27)],fill=(*a,190))
        elif aid=="draw_orbit":
            tx=w*.12; cx,cy=w*.62,h*.49
            for r in (w*.11,w*.19,w*.27): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(226,234,240,45),width=2)
            for i in range(8):
                ang=i*2*pi/8+.2; x=cx+cos(ang)*w*.25; y=cy+sin(ang)*w*.25; c=a if i%2==0 else b; d.ellipse((x-12,y-12,x+12,y+12),fill=(*c,190),outline=(242,246,249,190))
        else:
            tx=w*.12; y=h*.53; d.line((w*.15,y,w*.87,y),fill=(220,230,237,90),width=3)
            for i,x in enumerate((.21,.39,.57,.75)):
                d.ellipse((w*x-9,y-9,w*x+9,y+9),fill=(*(a if i==1 else b),190)); d.line((w*x,y-55,w*x,y+55),fill=(230,236,241,45),width=2)
        f=self._fit(d,req.headline,font_path,int(w*(.31 if tx>w*.5 else .55)),46,23); d.text((tx,h*.18),req.headline.upper(),font=f,fill=(238,242,246,230),anchor="la")
        sf=self._fit(d,req.primary_label,font_path,int(w*.42),25,16); d.text((tx,h*.26),req.primary_label.upper(),font=sf,fill=(*a,220),anchor="la")

    def _event(self, image, req, font_path, a, b):
        from PIL import ImageDraw
        w,h=image.size; d=ImageDraw.Draw(image,"RGBA"); aid=req.blueprint.archetype_id
        if aid=="event_horizon":
            for r in range(9): d.arc((w*(.05+r*.015),h*(.36-r*.01),w*(.95-r*.015),h*(.82+r*.012)),190,350,fill=(227,235,241,22+r*5),width=2)
            self._ball(d,w*.70,h*.54,w*.11,alpha=170); tx=w*.12
        elif aid=="object_story":
            self._ball(d,w*.31,h*.49,w*.17,alpha=205); self._glow_ellipse(image,(w*.09,h*.27,w*.53,h*.72),a,75,int(w*.07)); tx=w*.58
        elif aid=="anticipation_tunnel":
            for i in range(7):
                m=w*(.07+i*.045); d.polygon([(m,h*.18+i*h*.015),(w-m,h*.18+i*h*.015),(w*.69-i*w*.025,h*.78-i*h*.018),(w*.31+i*w*.025,h*.78-i*h*.018)],outline=(225,234,240,40+i*9))
            self._glow_ellipse(image,(w*.37,h*.56,w*.63,h*.83),b,80,int(w*.05)); tx=w*.12
        else:
            d.ellipse((w*.22,h*.31,w*.46,h*.55),outline=(*a,155),width=7); d.arc((w*.26,h*.35,w*.42,h*.51),30,320,fill=(232,238,242,95),width=2); tx=w*.53
        f=self._fit(d,req.headline,font_path,int(w*(.38 if tx>w*.5 else .58)),50,25); d.text((tx,h*.23),req.headline.upper(),font=f,fill=(239,243,247,235),anchor="la")
        sf=self._fit(d,req.primary_label,font_path,int(w*.36),25,16); d.text((tx,h*.34),req.primary_label.upper(),font=sf,fill=(*a,220),anchor="la")

    def render(self, request: FamilySceneRequest, *, profile: PlatformImageProfile, output_path: str, font_path: str) -> FamilySceneReceipt:
        from PIL import Image
        if not isinstance(request, FamilySceneRequest): raise TypeError("request must be FamilySceneRequest")
        if not isinstance(profile, PlatformImageProfile): raise TypeError("profile must be PlatformImageProfile")
        if not Path(font_path).is_file(): raise FileNotFoundError(font_path)
        family=EditorialSceneFamily(request.blueprint.family); a=self._rgb(request.accent_a); b=self._rgb(request.accent_b)
        image=Image.new("RGBA",(profile.width,profile.height),(6,10,18,255)); self._base(image,a,b,request.seed,energy=.92)
        if family is EditorialSceneFamily.TRANSFER_SIGNATURE: self._transfer(image,request,font_path,a,b)
        elif family is EditorialSceneFamily.RESULT_STATEMENT: self._result(image,request,font_path,a,b)
        elif family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: self._subject(image,request,font_path,a,b)
        elif family is EditorialSceneFamily.TACTICAL_BOARD: self._tactical(image,request,font_path,a,b)
        elif family is EditorialSceneFamily.DATA_MONUMENT: self._data(image,request,font_path,a,b)
        else: self._event(image,request,font_path,a,b)
        target=Path(output_path); target.parent.mkdir(parents=True,exist_ok=True); pre=target.with_name(target.stem+".prebrand.png"); image.convert("RGB").save(pre,"PNG")
        occupied={
            EditorialSceneFamily.TRANSFER_SIGNATURE:(BrandZone.UPPER_LEFT,), EditorialSceneFamily.RESULT_STATEMENT:(BrandZone.UPPER_LEFT,),
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:(BrandZone.UPPER_LEFT,), EditorialSceneFamily.TACTICAL_BOARD:(BrandZone.UPPER_LEFT,),
            EditorialSceneFamily.DATA_MONUMENT:(BrandZone.UPPER_LEFT,), EditorialSceneFamily.EVENT_EDITORIAL:(BrandZone.UPPER_LEFT,),
        }[family]
        adaptive=AdaptiveBrandPlacementResolver().resolve(family=family,profile=profile,occupied_zones=occupied)
        AdaptiveBrandOverlayRenderer().render_on_file(base_path=str(pre),output_path=str(target),adaptive=adaptive,profile=profile,accent_hex=request.brand_accent)
        pre.unlink(missing_ok=True); digest=sha256(target.read_bytes()).hexdigest()
        return FamilySceneReceipt(str(target),digest,family.value,request.blueprint.archetype_id,profile.width,profile.height)

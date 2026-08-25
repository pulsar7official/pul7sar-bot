"""PUL7SAR Phase 18 editorial cinematic V4 renderer.

V4 does not call the legacy V2 family builders. It reuses only low-level Blender
primitives and constructs each editorial family as a separate visual world. The
base render contains no PUL7SAR wordmark, club crest, readable editorial copy or
real-person likeness; those remain deterministic post-composition layers.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

from engine.intelligence.cinematic_art_direction import CinematicArtDirectionRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
import tools.phase18_blender_family_scene_v2 as B

FAMILIES={f.value:f for f in EditorialSceneFamily}


def parse():
    p=argparse.ArgumentParser(); p.add_argument('--family',required=True,choices=tuple(FAMILIES)); p.add_argument('--variant',choices=('a','b'),default='a')
    p.add_argument('--seed',type=int,default=18); p.add_argument('--accent-a',default='D90E25'); p.add_argument('--accent-b',default='2457D6'); p.add_argument('--output',required=True)
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def look_at(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()


def setup(family,seed,a,b):
    random.seed(seed); bpy.ops.wm.read_factory_settings(use_empty=True); d=CinematicArtDirectionRegistry.get(family)
    s=bpy.context.scene; s.render.engine='BLENDER_EEVEE'; s.render.resolution_x=540; s.render.resolution_y=675; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'
    s.eevee.use_gtao=True; s.eevee.gtao_distance=5; s.eevee.gtao_factor=1.65; s.eevee.use_bloom=True; s.eevee.bloom_intensity=.035; s.eevee.bloom_radius=3
    s.view_settings.look='AgX - Medium High Contrast'; s.view_settings.exposure=-.28; s.world=bpy.data.worlds.new('V4 World'); s.world.color=(.0015,.0025,.006)
    bpy.ops.object.camera_add(location=d.camera_xyz); cam=bpy.context.object; cam.data.lens=d.lens_mm; look_at(cam,d.look_at_xyz); s.camera=cam
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=d.look_at_xyz); focus=bpy.context.object; cam.data.dof.use_dof=True; cam.data.dof.focus_object=focus; cam.data.dof.aperture_fstop=d.aperture_fstop
    floor=B.material('charcoal floor',(.012,.016,.023),metal=.58,rough=.25,bump=.10); B.cube('floor',(0,1,-.18),(9,10,.20),floor,bevel=.04)
    backdrop=B.material('architectural black',(.008,.012,.020),metal=.15,rough=.48,bump=.035)
    B.cube('rear',(1.0,7.7,3.0),(8.2,.34,3.8),backdrop,bevel=.45,rot=(0,0,math.radians(-2)))
    B.area('keyA',(-5.4,-2.5,7.5),a,720,4.0,d.look_at_xyz); B.area('keyB',(5.4,-.8,6.7),b,560,3.5,d.look_at_xyz); B.area('top',(0,2.0,9.5),(.70,.76,.86),390,4.5,d.look_at_xyz)
    B.spot('rim',(1.8,7,7),(.55,.66,.84),610,.45,d.look_at_xyz,.40); B.compositor(s)
    return s


def stadium_depth(a,b):
    dark=B.material('stand dark',(.014,.019,.028),metal=.20,rough=.55); ea=B.material('stand a',a,emission=.65,rough=.30); eb=B.material('stand b',b,emission=.65,rough=.30)
    for row in range(5):
        y=5.7+row*.40; z=1.55+row*.38; B.cube('stand'+str(row),(0,y,z),(6.4-row*.25,.20,.10),dark,bevel=.05)
        for x in (-5.0,-3.6,-2.2,2.2,3.6,5.0): B.sphere('crowd_%d_%s'%(row,x),(x,y-.20,z+.19),.035,ea if x<0 else eb,segments=10)


def score_family(a,b):
    stadium_depth(a,b); metal=B.material('score metal',(.50,.55,.62),metal=.98,rough=.17,bump=.065); glass=B.material('club mass',(.025,.035,.052),metal=.65,rough=.18,bump=.06)
    ea=B.material('score a',a,emission=1.05,rough=.22); eb=B.material('score b',b,emission=1.05,rough=.22)
    B.cube('left mass',(-3.8,2.1,1.05),(1.35,1.65,.78),glass,bevel=.30,rot=(0,0,math.radians(-10))); B.cube('right mass',(3.65,2.65,1.28),(1.32,1.55,.92),glass,bevel=.30,rot=(0,0,math.radians(10)))
    B.cube('left accent',(-3.75,.43,1.72),(1.00,.025,.024),ea,bevel=.008); B.cube('right accent',(3.58,1.08,2.05),(1.00,.025,.024),eb,bevel=.008)
    # Score is important but deliberately not frame-filling.
    B.text3d('3',(-1.22,.05,2.70),1.55,.14,metal); B.text3d('1',(1.28,.20,2.62),1.45,.13,metal); B.text3d('–',(.05,.08,2.64),.48,.07,metal)
    # A restrained sporting object anchors foreground without pretending to be a real match photo.
    ball=B.material('ball metal',(.30,.33,.37),metal=.75,rough=.30,bump=.22); B.sphere('ball',(2.65,-.15,.55),.46,ball,segments=64); B.torus('ball ring',(2.65,-.15,.55),.32,.018,eb,(math.radians(66),0,math.radians(14)))
    B.curve_tube('outcome line',[(-4.8,.30,.20),(-2.4,.52,.18),(0,.40,.16),(2.3,.68,.17),(4.7,1.05,.22)],metal,.014)


def transfer_family(a,b):
    fabric=B.material('tailored shirt',(.055,.060,.070),rough=.70,bump=.34); metal=B.material('hanger metal',(.48,.52,.58),metal=.94,rough=.17,bump=.04); stone=B.material('destination stone',(.028,.034,.046),metal=.42,rough=.31,bump=.10)
    ea=B.material('arrival a',a,emission=.85); eb=B.material('destination b',b,emission=1.05)
    # Tunnel recedes into a destination rather than framing the shirt with neon boxes.
    for i in range(5):
        y=1.1+i*.82; z=.70+i*.36; x=4.75-i*.48
        B.cube('thresholdL'+str(i),(-x,y,z),(.025,.08,.70),ea,bevel=.008); B.cube('thresholdR'+str(i),(x,y,z),(.025,.08,.70),eb,bevel=.008)
    B.jersey_mesh(fabric,(.35,.35,2.60),.93); B.torus('collar',(.35,.20,3.33),.26,.035,metal,(math.radians(90),0,0))
    B.curve_tube('hanger',[(-.66,.28,3.62),(.35,.28,4.05),(1.36,.28,3.62)],metal,.018); B.cyl('hook',(.35,.28,4.22),.018,.38,metal,rot=(math.pi/2,0,0),vertices=24)
    B.cube('destination',(3.25,2.9,.58),(1.35,1.15,.54),stone,bevel=.24,rot=(0,0,math.radians(7))); B.cube('destination light',(3.18,1.72,1.08),(.90,.024,.018),eb,bevel=.006)


def subject_family(a,b):
    steel=B.material('subject steel',(.42,.47,.54),metal=.90,rough=.20,bump=.04); matte=B.material('locker matte',(.024,.030,.040),metal=.18,rough=.62,bump=.13); ea=B.material('subject a',a,emission=.72); eb=B.material('subject b',b,emission=.72)
    # Explicit absence metaphor: open locker + empty bench + hanger. No fake person.
    B.cube('locker shell',(1.65,2.30,2.60),(2.10,1.05,2.58),matte,bevel=.18); B.cube('locker void',(1.65,1.28,2.60),(1.72,.08,2.18),B.material('void',(.004,.006,.010),rough=.9),bevel=.04)
    B.curve_tube('hanger',[(-.08,1.13,3.72),(1.65,1.13,3.07),(3.32,1.13,3.72)],steel,.022); B.cyl('hook',(1.65,1.13,3.95),.022,.50,steel,rot=(math.pi/2,0,0),vertices=20)
    B.cube('bench',(-2.55,.70,.46),(1.55,.72,.22),steel,bevel=.20); B.cube('bench light',(-2.55,-.03,.68),(1.12,.020,.018),ea,bevel=.006)
    B.cube('quiet wall',(4.25,3.5,2.45),(1.05,.12,2.2),matte,bevel=.18); B.cube('quiet practical',(4.18,3.36,2.60),(.022,.04,1.20),eb,bevel=.006)


def tactical_family(a,b):
    pitch=B.material('analysis turf',(.020,.070,.050),rough=.76,bump=.10); white=B.material('geometry white',(.62,.68,.72),metal=.12,rough=.45); ea=B.material('team a',a,emission=.70); eb=B.material('team b',b,emission=.70)
    B.cube('cropped pitch',(0,1.20,.02),(5.60,4.25,.05),pitch,bevel=.05,rot=(0,0,math.radians(-2.4)))
    # partial regulation context, not a decorative full-pitch poster
    for y in (-1.75,0,1.75): B.cube('hline'+str(y),(0,1.2+y,.09),(5.05,.014,.010),white,bevel=.003,rot=(0,0,math.radians(-2.4)))
    for x in (-4.4,-2.2,0,2.2,4.4): B.cube('vline'+str(x),(x,1.2,.095),(.012,3.72,.010),white,bevel=.003,rot=(0,0,math.radians(-2.4)))
    red=[(-3.9,-.9),(-2.4,-.25),(-1.1,.45),(.15,1.15)]; blue=[(1.2,1.65),(2.35,2.25),(3.55,2.80)]
    for i,(x,y) in enumerate(red): B.cyl('ra'+str(i),(x,y+.9,.20),.16,.10,ea,vertices=48)
    for i,(x,y) in enumerate(blue): B.cyl('bl'+str(i),(x,y+.9,.20),.16,.10,eb,vertices=48)
    B.curve_tube('verified mechanism',[(x,y+.9,.30) for x,y in red]+[(x,y+.9,.30) for x,y in blue],ea,.032)


def data_family(a,b):
    metal=B.material('data metal',(.48,.53,.60),metal=.97,rough=.17,bump=.055); stone=B.material('data stone',(.026,.031,.043),metal=.48,rough=.30,bump=.09); ea=B.material('data a',a,emission=.78); eb=B.material('data b',b,emission=.70)
    B.cube('monolith',(-1.25,1.35,.52),(2.35,1.42,.52),stone,bevel=.28,rot=(0,0,math.radians(-4))); B.cube('monolith edge',(-1.32,-.10,1.00),(1.70,.022,.018),ea,bevel=.006)
    B.text3d('27',(-2.25,-.18,2.45),1.55,.13,metal)
    # ranking movement is spatial rather than dashboard cards
    for i in range(5):
        h=.20+i*.26; B.cube('rise'+str(i),(1.65+i*.48,1.55+i*.24,h),( .18,.42,h),stone,bevel=.06); B.cube('riseLight'+str(i),(1.65+i*.48,1.10+i*.24,h*2+.04),(.12,.018,.015),eb if i==4 else metal,bevel=.004)


def event_family(a,b):
    metal=B.material('event alloy',(.42,.48,.56),metal=.91,rough=.19,bump=.055); ea=B.material('event a',a,emission=.70); eb=B.material('event b',b,emission=.70); dark=B.material('event dark',(.018,.024,.035),metal=.36,rough=.38,bump=.09)
    # architectural anticipation passage
    for i in range(6):
        y=.9+i*.82; w=5.1-i*.55; z=.65+i*.40
        B.cube('evL'+str(i),(-w,y,z),(.025,.08,.64),ea,bevel=.008); B.cube('evR'+str(i),(w,y,z),(.025,.08,.64),eb,bevel=.008)
        B.cube('evTop'+str(i),(0,y,z+.66),(w,.06,.025),metal,bevel=.006)
    ball=B.material('event ball',(.35,.38,.42),metal=.68,rough=.32,bump=.24); B.sphere('event object',(.55,2.95,1.65),.68,ball,segments=72); B.torus('event seam',(.55,2.95,1.65),.49,.016,ea,(math.radians(65),0,math.radians(18)))
    B.cube('event pedestal',(.55,3.18,.48),(1.05,.95,.28),dark,bevel=.18); B.cube('event horizon',(0,5.95,3.72),(2.20,.08,.035),metal,bevel=.008)


def render_family(f,a,b):
    {EditorialSceneFamily.RESULT_STATEMENT:score_family,EditorialSceneFamily.TRANSFER_SIGNATURE:transfer_family,EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:subject_family,EditorialSceneFamily.TACTICAL_BOARD:tactical_family,EditorialSceneFamily.DATA_MONUMENT:data_family,EditorialSceneFamily.EVENT_EDITORIAL:event_family}[f](a,b)


def main():
    q=parse(); f=FAMILIES[q.family]; a=B.rgb(q.accent_a); b=B.rgb(q.accent_b); s=setup(f,q.seed,a,b); render_family(f,a,b); out=Path(q.output); out.parent.mkdir(parents=True,exist_ok=True); s.render.filepath=str(out); bpy.ops.render.render(write_still=True)

if __name__=='__main__': main()

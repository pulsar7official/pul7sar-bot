"""Procedural 3D benchmark renderer for PUL7SAR editorial families.

Run with Blender:
  blender -b --python tools/phase18_blender_family_scene.py -- --family result_statement --output out.png --seed 18
No external image pixels, models, fonts, network calls or generated identities are used.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args():
    p=argparse.ArgumentParser()
    p.add_argument('--family',required=True)
    p.add_argument('--variant',default='a')
    p.add_argument('--output',required=True)
    p.add_argument('--seed',type=int,default=18)
    p.add_argument('--accent-a',default='D90E25')
    p.add_argument('--accent-b',default='2457D6')
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))


def mat(name,color,metal=0.0,rough=.4,emit=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emit:
        bs.inputs['Emission'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emit
    return m


def add_cube(name,loc,scale,material,bevel=.08,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('soft bevel','BEVEL'); mod.width=bevel; mod.segments=4
    o.data.materials.append(material); return o


def add_cyl(name,loc,radius,depth,material,rot=(0,0,0),vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(material); return o


def add_text(text,loc,size,depth,material,align='CENTER',rot=(math.pi/2,0,0)):
    bpy.ops.object.text_add(location=loc,rotation=rot); o=bpy.context.object; o.data.body=text; o.data.align_x=align; o.data.align_y='CENTER'; o.data.size=size; o.data.extrude=depth; o.data.bevel_depth=depth*.20; o.data.bevel_resolution=4; o.data.materials.append(material); return o


def look(obj,point):
    direction=Vector(point)-obj.location; obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()


def light(name,loc,color,energy,size=5,point=(0,0,1)):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.color=color; l.data.shape='DISK'; l.data.size=size; look(l,point); return l


def ring(radius,z,material,thick=.025):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=thick,major_segments=96,minor_segments=12,location=(0,0,z)); o=bpy.context.object; o.data.materials.append(material); return o


def setup(seed,a,b):
    random.seed(seed); bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.eevee.use_gtao=True; sc.eevee.gtao_distance=3; sc.eevee.gtao_factor=1.5; sc.eevee.use_bloom=True; sc.eevee.bloom_intensity=.08; sc.eevee.bloom_radius=6
    sc.render.resolution_x=1080; sc.render.resolution_y=1350; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.view_settings.look='Medium High Contrast'; sc.view_settings.exposure=.2
    sc.world.color=(.002,.004,.009)
    # Camera
    bpy.ops.object.camera_add(location=(0,-14,5.8)); cam=bpy.context.object; cam.data.lens=52; look(cam,(0,0,2.4)); sc.camera=cam
    floor=mat('floor',(0.018,.025,.038),metal=.55,rough=.22); add_cube('floor',(0,0,-.18),(8,8,.18),floor,bevel=.02)
    # Low side walls provide arena depth without a literal stadium.
    wall=mat('depth',(0.012,.018,.03),metal=.18,rough=.42)
    add_cube('left_depth',(-6,2,2.3),(1.1,6,2.5),wall,bevel=.2,rot=(0,0,-.06)); add_cube('right_depth',(6,2,2.3),(1.1,6,2.5),wall,bevel=.2,rot=(0,0,.06))
    light('key_a',(-5,-4,7),a,1250,5,(0,0,2)); light('key_b',(5,-2,6),b,1050,5,(0,0,2)); light('top',(0,1,10),(0.85,.9,1),850,4,(0,0,1))
    # Small emissive practicals
    ea=mat('emit_a',a,rough=.2,emit=5); eb=mat('emit_b',b,rough=.2,emit=5)
    for i in range(9):
        x=-5.0+i*1.25; add_cyl(f'practical{i}',(x,4.5,5.4),.055,.4,ea if i<5 else eb,rot=(math.pi/2,0,0),vertices=24)
    return sc,ea,eb


def add_particles(a_mat,b_mat,count=46):
    m=mat('particle',(0.65,.72,.80),metal=.1,rough=.3)
    for i in range(count):
        x=random.uniform(-5.8,5.8); y=random.uniform(-1,5); z=random.uniform(.3,6.5); r=random.uniform(.012,.045)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=(x,y,z)); o=bpy.context.object; o.data.materials.append(a_mat if i%13==0 else b_mat if i%17==0 else m)


def result_scene(a,b,variant):
    steel=mat('steel',(.62,.67,.73),metal=.92,rough=.18); dark=mat('dark',(.035,.045,.06),metal=.55,rough=.27); ea=mat('red_emit',a,emit=3); eb=mat('blue_emit',b,emit=3)
    if variant=='a':
        # Score floats off-axis, while two identity plinths create true depth.
        add_cube('plinthA',(-3.2,1.2,.85),(1.5,1.1,.9),dark,.18,rot=(0,0,-.12)); add_cube('plinthB',(3.0,2.0,1.25),(1.6,1.15,1.25),dark,.18,rot=(0,0,.12))
        add_text('3',(-1.35,.0,3.05),2.45,.20,steel); add_text('1',(1.55,.25,2.75),2.05,.18,steel); add_text('—',(.1,.1,2.80),.72,.10,steel)
        add_cube('redbar',(-3.2,.1,1.83),(1.05,.06,.045),ea,.02); add_cube('bluebar',(3,.65,2.63),(1.1,.06,.045),eb,.02)
    else:
        # Arena outcome: the world is hero, score is restrained in foreground.
        for i,r in enumerate((5.6,4.8,4.0,3.2)):
            o=ring(r,1.0+i*.62,ea if i%2==0 else eb,.035); o.rotation_euler.x=math.radians(78)
        add_text('2–2',(0,-.55,1.25),1.15,.12,steel); add_cube('score_shadow',(0,.15,.75),(1.65,.7,.10),dark,.08)
    add_particles(ea,eb,56)


def transfer_scene(a,b,variant):
    steel=mat('steel',(.55,.60,.67),metal=.82,rough=.2); fabric=mat('fabric',(.10,.12,.16),metal=.05,rough=.68); ea=mat('ea',a,emit=4); eb=mat('eb',b,emit=4)
    if variant=='a':
        # Architectural arrival threshold around an empty jersey object, no person.
        for x,z,s in ((-3.7,2.5,1),(3.4,2.8,1.2),(-2.7,4.5,.8),(2.5,4.8,.8)): add_cube('beam',(x,1,z),(.12,2.8,s),ea if x<0 else eb,.03,rot=(0,math.radians(12 if x<0 else -12),0))
        body=add_cube('jersey_body',(1.0,.3,2.5),(1.15,.16,1.35),fabric,.18); add_cube('left_sleeve',(-.2,.25,3.05),(.55,.14,.46),fabric,.12,rot=(0,0,math.radians(-22))); add_cube('right_sleeve',(2.2,.25,3.05),(.55,.14,.46),fabric,.12,rot=(0,0,math.radians(22)))
        add_text('NEW CHAPTER',(-3.9,-.25,4.8),.62,.035,steel,align='LEFT')
    else:
        # Signing desk object study, no fake signature.
        add_cube('desk',(0,1,.7),(3.8,1.4,.18),steel,.1); paper=mat('paper',(.65,.67,.69),metal=.05,rough=.5); add_cube('document',(-.4,-.15,1.05),(1.75,1.0,.025),paper,.025,rot=(0,0,math.radians(-7)))
        for i in range(5): add_cube('line',( -.55, -.36+i*.25,1.09),(1.05,.025,.01),steel,.005)
        add_cyl('pen',(1.8,-.25,1.16),.045,1.25,ea,rot=(0,math.radians(68),math.radians(8)),vertices=32); add_text('OFFICIAL MOVE',(-3.5,-.25,4.3),.58,.035,steel,align='LEFT')
    add_particles(ea,eb,42)


def subject_scene(a,b,variant):
    steel=mat('steel',(.58,.63,.69),metal=.78,rough=.22); dark=mat('dark',(.025,.032,.045),metal=.3,rough=.42); ea=mat('ea',a,emit=3.5); eb=mat('eb',b,emit=3.5)
    if variant=='a':
        # Empty illuminated locker / absence metaphor.
        add_cube('locker',(1.7,1,2.45),(2.0,1.15,2.65),dark,.14); add_cube('seat',(1.7,-.1,.85),(1.05,.65,.22),steel,.15); add_cube('seatback',(1.7,.42,1.65),(1.05,.18,.8),steel,.14)
        add_cube('absence_light',(1.7,.85,4.85),(1.1,.06,.035),ea,.02); add_text('SIDELINED',(-4.0,-.2,4.2),.76,.045,steel,align='LEFT')
    else:
        # Press/appointment stage using microphones only, no fabricated subject.
        add_cube('podium',(-.4,1,1.35),(1.65,.8,1.35),dark,.15); add_cube('podium_trim',(-.4,.15,2.20),(1.45,.06,.04),eb,.015)
        for i,x in enumerate((-.85,-.35,.15)):
            add_cyl('micstem'+str(i),(x,-.05,2.55),.035,.9,steel,rot=(0,0,0),vertices=24); bpy.context.object.rotation_euler.x=math.radians(-12+i*8)
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.13,location=(x,-.13,3.02)); bpy.context.object.data.materials.append(steel)
        add_text('NEW ERA',(1.9,-.1,4.2),.82,.045,steel,align='LEFT')
    add_particles(ea,eb,30)


def tactical_scene(a,b,variant):
    field=mat('field',(.025,.14,.09),metal=.15,rough=.45); white=mat('lines',(.62,.70,.74),rough=.3,emit=.5); ea=mat('ea',a,emit=3); eb=mat('eb',b,emit=3)
    # camera top/oblique for tactics
    cam=bpy.context.scene.camera; cam.location=(0,-11,9.8); look(cam,(0,1,0)); cam.data.lens=55
    add_cube('pitch',(0,1,.02),(4.6,6,.04),field,.02)
    if variant=='a':
        # Cropped right-side corridor, arrows made from cylinders + cones.
        for x in (-3.5,-1.5,.5,2.5): add_cube('lane',(x,1,.09),(.018,5.5,.015),white,.005)
        pts=[(-2.8,-2),(-1.2,-.5),(.6,.7),(2.5,2.8)]
    else:
        pts=[(-2.5,-2),(-.8,-.3),(-2.0,2.3),(2.5,-2),(1.0,-.2),(2.0,2.4)]
        add_cube('midline',(0,1,.09),(.025,5.5,.015),white,.005)
    for i,(x,y) in enumerate(pts):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.22,location=(x,y+.8,.28)); bpy.context.object.data.materials.append(ea if i<len(pts)//2 else eb)
        if i+1<len(pts):
            p1=Vector((x,y+.8,.25)); x2,y2=pts[i+1]; p2=Vector((x2,y2+.8,.25)); vec=p2-p1; mid=(p1+p2)/2; o=add_cyl('link',mid,.045,vec.length,ea if i<len(pts)//2 else eb,vertices=20); o.rotation_euler=vec.to_track_quat('Z','Y').to_euler()


def data_scene(a,b,variant):
    steel=mat('steel',(.62,.68,.74),metal=.92,rough=.15); dark=mat('dark',(.035,.045,.055),metal=.4,rough=.35); ea=mat('ea',a,emit=3.5); eb=mat('eb',b,emit=3.5)
    if variant=='a':
        add_text('27',(-1.5,.1,2.6),3.0,.24,steel); add_text('CONSECUTIVE WINS',(1.05,-.15,4.65),.48,.03,steel,align='LEFT')
        for i in range(6): add_cube('rank'+str(i),(2.2,1+i*.28,.55+i*.45),(.8,.5,.18),ea if i==5 else dark,.08)
    else:
        # Orbital draw: physical nodes and luminous orbits.
        for r,z in ((1.6,2.1),(2.6,2.4),(3.6,2.7)):
            o=ring(r,z,steel,.025); o.rotation_euler.x=math.radians(74)
        for i in range(8):
            ang=i*2*math.pi/8; x=math.cos(ang)*3.2; y=math.sin(ang)*2.0+1; z=2.7+math.sin(ang)*.4; bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.24,location=(x,y,z)); bpy.context.object.data.materials.append(ea if i%2==0 else eb)
        add_text('THE DRAW',(-3.8,-.3,5.1),.72,.04,steel,align='LEFT')
    add_particles(ea,eb,28)


def event_scene(a,b,variant):
    steel=mat('steel',(.53,.59,.66),metal=.75,rough=.22); ea=mat('ea',a,emit=4); eb=mat('eb',b,emit=4); ball=mat('ball',(.55,.58,.60),metal=.25,rough=.34)
    if variant=='a':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=64,radius=1.45,location=(-1.35,.3,2.25)); s=bpy.context.object; s.data.materials.append(ball)
        # geometric seams, not a copied branded ball
        for r in (1.48,1.50):
            o=ring(r,2.25,ea if r<1.49 else eb,.018); o.location.x=-1.35; o.rotation_euler.x=math.radians(90 if r<1.49 else 56)
        add_text('ONE NIGHT AWAITS',(1.15,-.2,4.7),.56,.035,steel,align='LEFT')
    else:
        # Real 3D anticipation tunnel with nested luminous frames.
        for i in range(8):
            z=.7+i*.55; sc=4.6-i*.35
            add_cube('L'+str(i),(-sc,2.4,z),( .045,1.3,z*.0+.75),ea if i%2==0 else eb,.015)
            add_cube('R'+str(i),(sc,2.4,z),(.045,1.3,.75),ea if i%2==0 else eb,.015)
            add_cube('T'+str(i),(0,2.4,z+.75),(sc,.045,.045),ea if i%2==0 else eb,.015)
        add_text('THE ROAD BEGINS',(-3.7,-.3,4.8),.62,.04,steel,align='LEFT')
    add_particles(ea,eb,48)


def main():
    a0=args(); a=rgb(a0.accent_a); b=rgb(a0.accent_b); sc,ea,eb=setup(a0.seed,a,b)
    fam=a0.family
    if fam=='result_statement': result_scene(a,b,a0.variant)
    elif fam=='transfer_signature': transfer_scene(a,b,a0.variant)
    elif fam=='verified_subject_news': subject_scene(a,b,a0.variant)
    elif fam=='tactical_board': tactical_scene(a,b,a0.variant)
    elif fam=='data_monument': data_scene(a,b,a0.variant)
    elif fam=='event_editorial': event_scene(a,b,a0.variant)
    else: raise SystemExit('unsupported family '+fam)
    out=Path(a0.output); out.parent.mkdir(parents=True,exist_ok=True); sc.render.filepath=str(out); bpy.ops.render.render(write_still=True)

if __name__=='__main__': main()

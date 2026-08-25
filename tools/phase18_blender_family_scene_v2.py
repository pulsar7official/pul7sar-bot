"""Cinematic procedural 3D renderer for PUL7SAR Phase 18.

V2 deliberately renders *scene pixels only*. Editorial copy and the approved
PUL7SAR brand are applied later by deterministic post-composition. No source
photos, downloaded 3D models, club crests, people, or network resources are used.
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--family',required=True)
    p.add_argument('--variant',choices=('a','b'),default='a')
    p.add_argument('--output',required=True)
    p.add_argument('--seed',type=int,default=18)
    p.add_argument('--accent-a',default='D90E25')
    p.add_argument('--accent-b',default='2457D6')
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))


def look_at(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()


def material(name,color,*,metal=.0,rough=.4,emission=0.0,bump=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    ekey='Emission Color' if 'Emission Color' in bs.inputs else 'Emission'
    skey='Emission Strength' if 'Emission Strength' in bs.inputs else None
    if emission:
        bs.inputs[ekey].default_value=(*color,1)
        if skey: bs.inputs[skey].default_value=emission
    if bump:
        tex=nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=9.0 if metal>.5 else 32.0; tex.inputs['Detail'].default_value=5.0; tex.inputs['Roughness'].default_value=.72
        bn=nt.nodes.new('ShaderNodeBump'); bn.inputs['Strength'].default_value=bump; bn.inputs['Distance'].default_value=.08
        nt.links.new(tex.outputs['Fac'],bn.inputs['Height']); nt.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
    return m


def cube(name,loc,scale,mat,*,bevel=.08,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('micro bevel','BEVEL'); mod.width=bevel; mod.segments=5
    o.data.materials.append(mat); return o


def cyl(name,loc,radius,depth,mat,*,rot=(0,0,0),vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o


def sphere(name,loc,radius,mat,segments=64):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=max(16,segments//2),radius=radius,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o


def torus(name,loc,major,minor,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=112,minor_segments=16,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o


def text3d(text,loc,size,depth,mat,*,rot=(math.pi/2,0,0),align='CENTER'):
    bpy.ops.object.text_add(location=loc,rotation=rot); o=bpy.context.object; o.data.body=text; o.data.align_x=align; o.data.align_y='CENTER'; o.data.size=size; o.data.extrude=depth; o.data.bevel_depth=max(.01,depth*.22); o.data.bevel_resolution=5; o.data.materials.append(mat); return o


def area(name,loc,color,energy,size,point):
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=energy; o.data.color=color; o.data.shape='DISK'; o.data.size=size; look_at(o,point); return o


def spot(name,loc,color,energy,size,point,angle=.52):
    bpy.ops.object.light_add(type='SPOT',location=loc); o=bpy.context.object; o.name=name; o.data.energy=energy; o.data.color=color; o.data.shadow_soft_size=size; o.data.spot_size=angle; o.data.spot_blend=.55; look_at(o,point); return o


def curve_tube(name,points,mat,bevel=.045):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=5; spl=cu.splines.new('BEZIER'); spl.bezier_points.add(len(points)-1)
    for bp,p in zip(spl.bezier_points,points): bp.co=p; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); cu.materials.append(mat); return ob


def compositor(scene):
    scene.use_nodes=True; nt=scene.node_tree; nt.nodes.clear()
    rl=nt.nodes.new('CompositorNodeRLayers'); glare=nt.nodes.new('CompositorNodeGlare'); glare.glare_type='FOG_GLOW'; glare.quality='HIGH'; glare.threshold=.9; glare.size=7
    comp=nt.nodes.new('CompositorNodeComposite'); nt.links.new(rl.outputs['Image'],glare.inputs['Image']); nt.links.new(glare.outputs['Image'],comp.inputs['Image'])


def fog_volume():
    m=bpy.data.materials.new('atmosphere_volume'); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); vol=nt.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value=.010; vol.inputs['Anisotropy'].default_value=.32; vol.inputs['Color'].default_value=(.12,.16,.22,1); nt.links.new(vol.outputs['Volume'],out.inputs['Volume'])
    cube('fog',(0,2,3.5),(9,9,5.5),m,bevel=0)


def setup(seed,a,b):
    random.seed(seed); bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1080; sc.render.resolution_y=1350; sc.render.resolution_percentage=100; sc.render.image_settings.file_format='PNG'; sc.render.film_transparent=False
    sc.eevee.use_gtao=True; sc.eevee.gtao_distance=4; sc.eevee.gtao_factor=1.7; sc.eevee.use_bloom=True; sc.eevee.bloom_intensity=.10; sc.eevee.bloom_radius=6
    sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=.35; sc.world=bpy.data.worlds.new('PUL7SAR World'); sc.world.color=(.0015,.003,.008)
    bpy.ops.object.camera_add(location=(0,-14.8,5.5)); cam=bpy.context.object; cam.data.lens=58; look_at(cam,(0,.5,2.45)); sc.camera=cam
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,.7,2.5)); focus=bpy.context.object; cam.data.dof.use_dof=True; cam.data.dof.focus_object=focus; cam.data.dof.aperture_fstop=3.2
    floor=material('obsidian',(0.014,.020,.031),metal=.72,rough=.18,bump=.10); cube('floor',(0,1,-.19),(8.6,9,.20),floor,bevel=.03)
    back=material('back',(0.009,.014,.024),metal=.22,rough=.38); cube('back',(0,7,3.1),(7.4,.30,3.6),back,bevel=.3)
    area('keyA',(-5,-2.5,7.7),a,1500,4.7,(0,.8,2.3)); area('keyB',(5,-1.2,6.8),b,1250,4.3,(0,.8,2.4)); area('softTop',(0,2,10),(0.75,.84,.95),800,4.8,(0,1.2,1.8)); spot('rim',(.2,6.2,7.2),(0.65,.78,1),1350,.7,(0,1.1,2.4),.48)
    fog_volume(); compositor(sc)
    ea=material('emitA',a,rough=.18,emission=5.2); eb=material('emitB',b,rough=.18,emission=5.2)
    for i in range(11):
        x=-5.4+i*1.08; cyl('practical'+str(i),(x,6.52,5.85),.045,.35,ea if i<5 else eb,rot=(math.pi/2,0,0),vertices=24)
    return sc,ea,eb


def particles(ea,eb,count=34):
    dust=material('dust',(.58,.66,.75),metal=.05,rough=.32)
    for i in range(count):
        r=random.uniform(.014,.045); x=random.uniform(-5.6,5.6); y=random.uniform(-.5,5.2); z=random.uniform(.45,6.2); sphere('dust'+str(i),(x,y,z),r,ea if i%15==0 else eb if i%19==0 else dust,segments=12)


def jersey_mesh(mat,loc=(1.1,.4,2.55),scale=1.0):
    # Front-facing jersey silhouette with thickness; no person/identity.
    verts=[(-1.0,0,1.0),(-1.75,0,.55),(-1.42,0,-.05),(-.92,0,.18),(-.78,0,-1.15),(.78,0,-1.15),(.92,0,.18),(1.42,0,-.05),(1.75,0,.55),(1.0,0,1.0),(.46,0,.78),(-.46,0,.78)]
    faces=[tuple(range(len(verts)))]
    mesh=bpy.data.meshes.new('jersey_mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new('jersey',mesh); bpy.context.collection.objects.link(o); o.location=loc; o.scale=(scale,scale,scale); o.data.materials.append(mat)
    sol=o.modifiers.new('fabric thickness','SOLIDIFY'); sol.thickness=.10; bev=o.modifiers.new('soft edges','BEVEL'); bev.width=.06; bev.segments=4
    return o


def build_transfer(a,b,v):
    steel=material('steel',(.53,.58,.65),metal=.93,rough=.15,bump=.06); fabric=material('fabric',(.055,.065,.085),rough=.65,bump=.24); ea=material('ta',a,emission=5); eb=material('tb',b,emission=5)
    if v=='a':
        for i,(x,z) in enumerate(((-4.2,2.0),(-3.1,4.5),(3.0,4.6),(4.1,2.1))): cube('portal'+str(i),(x,1.7,z),(.09,2.8,1.15),ea if x<0 else eb,bevel=.025,rot=(0,math.radians(10 if x<0 else -10),0))
        jersey_mesh(fabric,(1.0,.25,2.65),1.05); curve_tube('hem_light',[(-.65,.17,1.45),(.2,.12,1.34),(1.55,.16,1.48)],ea,.035)
        cube('destination_stone',(2.9,1.5,.65),(1.45,1.25,.62),steel,bevel=.20,rot=(0,0,.11))
    else:
        desk=material('desk',(.07,.08,.105),metal=.75,rough=.20,bump=.08); paper=material('paper',(.52,.55,.58),rough=.48)
        cube('desk',(0,1,.68),(4.0,1.6,.18),desk,bevel=.12); cube('document',(-.45,-.05,1.01),(1.75,1.08,.025),paper,bevel=.025,rot=(0,0,math.radians(-8)))
        for i in range(6): cube('docline'+str(i),(-.55,-.62+i*.21,1.047),(1.05,.015,.008),steel,bevel=.003)
        pen=cyl('pen',(1.72,-.28,1.13),.05,1.35,ea,vertices=40); pen.rotation_euler=(math.radians(82),math.radians(22),math.radians(-20))
        torus('seal',(2.15,.45,1.07),.42,.035,eb,(0,0,0))
    particles(ea,eb,32)


def build_result(a,b,v):
    steel=material('score_steel',(.57,.62,.69),metal=.96,rough=.13,bump=.07); dark=material('plinth',(.025,.032,.045),metal=.72,rough=.22,bump=.08); ea=material('ra',a,emission=4.5); eb=material('rb',b,emission=4.5)
    if v=='a':
        cube('left_mass',(-3.25,1.5,.80),(1.55,1.2,.82),dark,bevel=.24,rot=(0,0,-.14)); cube('right_mass',(3.15,2.15,1.10),(1.55,1.2,1.12),dark,bevel=.24,rot=(0,0,.14))
        text3d('3',(-1.25,-.08,3.10),2.05,.17,steel); text3d('1',(1.35,.22,2.85),1.75,.15,steel); text3d('—',(.05,.05,2.86),.60,.08,steel)
        cube('left_id',(-3.25,.05,1.66),(1.05,.05,.025),ea,bevel=.012); cube('right_id',(3.15,.65,2.28),(1.05,.05,.025),eb,bevel=.012)
        curve_tube('energy',[(-4.4,.3,.55),(-2.5,.7,.42),(0,1.05,.35),(2.5,1.0,.45),(4.5,1.55,.70)],material('energy',(.32,.42,.55),emission=1.8),.025)
    else:
        # Wide arena; exact score is intentionally smaller than the environment.
        for i,r in enumerate((5.3,4.45,3.6,2.75)):
            torus('arena'+str(i),(0,2,1.15+i*.65),r,.028,ea if i%2==0 else eb,(math.radians(78),0,0))
        text3d('2–2',(0,-.45,1.20),1.02,.10,steel); cube('low_stage',(0,.35,.58),(1.55,.75,.10),dark,bevel=.08)
        for x in (-3.7,-2.4,2.4,3.7): spot('beam'+str(x),(x,4.5,5.8),a if x<0 else b,650,.4,(0,.4,1.0),.30)
    particles(ea,eb,42)


def build_subject(a,b,v):
    steel=material('subject_steel',(.52,.58,.64),metal=.82,rough=.18,bump=.05); dark=material('subject_dark',(.020,.026,.038),metal=.44,rough=.34,bump=.10); ea=material('sa',a,emission=4); eb=material('sb',b,emission=4)
    if v=='a':
        # Absence: empty locker, hanger and bench are the factual metaphor.
        cube('locker',(1.55,1.45,2.6),(2.0,1.22,2.6),dark,bevel=.18); cube('locker_back',(1.55,2.55,2.6),(1.72,.06,2.25),material('backplate',(.04,.05,.065),metal=.35,rough=.38),bevel=.04)
        curve_tube('hanger',[($.replace('x','0'))],steel) if False else None
        # Hanger from three tubes.
        curve_tube('hanger',[(-.1,2.35,3.85),(1.55,2.35,3.2),(3.2,2.35,3.85)],steel,.025); cyl('hook',(1.55,2.35,4.02),.025,.55,steel,rot=(math.pi/2,0,0),vertices=20)
        cube('bench',(1.55,-.05,.70),(1.25,.75,.20),steel,bevel=.18); cube('absence_bar',(1.55,2.33,4.62),(1.10,.035,.025),ea,bevel=.01)
        area('locker_light',(1.55,.55,5.5),a,700,2.0,(1.55,1.5,2.4))
    else:
        # Empty press stage: no fabricated face/person, just the context objects.
        cube('podium',(-.25,1.45,1.35),(1.6,.9,1.35),dark,bevel=.18); cube('podium_trim',(-.25,.55,2.20),(1.35,.045,.035),eb,bevel=.012)
        for i,x in enumerate((-.85,-.25,.35)):
            stem=cyl('micstem'+str(i),(x,.35,2.73),.025,.85,steel,vertices=24); stem.rotation_euler.x=math.radians(-10+i*8); sphere('mic'+str(i),(x,.20,3.15),.12,steel,segments=40)
        for x in (-3.3,2.9): spot('press'+str(x),(x,-1,6.5),a if x<0 else b,900,.5,(-.2,1.4,2.3),.36)
    particles(ea,eb,24)


def build_tactical(a,b,v):
    sc=bpy.context.scene; cam=sc.camera; cam.location=(0,-11.2,10.4); look_at(cam,(0,1,.25)); cam.data.lens=58; cam.data.dof.aperture_fstop=5.6
    glass=material('pitch_glass',(.022,.13,.10),metal=.32,rough=.20,bump=.03); line=material('pitch_line',(.60,.72,.76),metal=.10,rough=.25,emission=.45); ea=material('tactA',a,emission=4); eb=material('tactB',b,emission=4)
    cube('pitch',(0,1,.00),(4.65,6,.06),glass,bevel=.05)
    # Edge lighting, not a full decorative stadium.
    for x in (-4.55,4.55): cube('edge'+str(x),(x,1,.095),(.025,5.85,.018),line,bevel=.005)
    if v=='a':
        for x in (-3.1,-1.45,.2,1.85,3.5): cube('corridor'+str(x),(x,1,.10),(.012,5.6,.012),line,bevel=.002)
        pts=[(-3.0,-2.7),(-2.0,-1.0),(-.55,.3),(1.10,1.55),(2.8,3.0)]
        for i,(x,y) in enumerate(pts): sphere('p'+str(i),(x,y+1,.30),.22,ea if i<3 else eb,segments=40)
        curve_tube('progress',[(x,y+1,.32) for x,y in pts],material('path',a,emission=2.5),.055)
        # directional arrow head
        bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.22,depth=.55,location=(3.15,4.35,.34),rotation=(0,math.pi/2,0)); bpy.context.object.data.materials.append(ea)
    else:
        cube('mid',(0,1,.10),(.018,5.7,.012),line,bevel=.003)
        left=[(-2.9,-2.4),(-1.7,-.6),(-2.4,1.7)]; right=[(2.9,-2.3),(1.55,-.35),(2.35,1.8)]
        for group,matx in ((left,ea),(right,eb)):
            for i,(x,y) in enumerate(group): sphere('m'+str(x)+str(y),(x,y+1,.30),.23,matx,segments=40)
            curve_tube('shape'+str(group[0][0]),[(x,y+1,.32) for x,y in group],matx,.055)
        curve_tube('duel',[(-1.7,.4,.35),(0,1.0,.50),(1.55,.65,.35)],material('duel',(0.72,.78,.82),emission=2),.035)


def build_data(a,b,v):
    steel=material('data_steel',(.58,.64,.71),metal=.96,rough=.12,bump=.07); dark=material('data_dark',(.025,.032,.045),metal=.58,rough=.25,bump=.06); ea=material('da',a,emission=4); eb=material('db',b,emission=4)
    if v=='a':
        text3d('27',(-1.55,-.05,2.72),2.72,.22,steel); cube('number_stage',(-1.45,.55,.65),(2.2,1.0,.12),dark,bevel=.10)
        for i in range(7): cube('rank'+str(i),(2.25,1.25+i*.30,.44+i*.38),(.82,.62,.16),ea if i==6 else dark,bevel=.08)
        for i in range(3): area('dataLight'+str(i),(-3+i*3,2,6),a if i<2 else b,600,2.2,(0,1,2))
    else:
        for i,(r,z) in enumerate(((1.5,2.0),(2.35,2.35),(3.25,2.72),(4.15,3.05))): torus('orbit'+str(i),(0,1,z),r,.025,steel,(math.radians(74),0,0))
        for i in range(10):
            ang=i*2*math.pi/10+.16; x=math.cos(ang)*3.55; y=math.sin(ang)*2.15+1; z=2.80+math.sin(ang)*.48; sphere('drawnode'+str(i),(x,y,z),.24,ea if i%2==0 else eb,segments=48)
        sphere('drawcore',(0,.4,2.65),.36,material('core',(.66,.72,.80),metal=.45,rough=.18,emission=1.5),segments=56)
    particles(ea,eb,26)


def build_event(a,b,v):
    steel=material('event_steel',(.52,.58,.65),metal=.82,rough=.17,bump=.05); ea=material('ea2',a,emission=4.5); eb=material('eb2',b,emission=4.5)
    if v=='a':
        ballmat=material('ball',(.55,.58,.61),metal=.18,rough=.30,bump=.08); sphere('sport_ball',(-1.35,.15,2.45),1.42,ballmat,segments=80)
        # Abstract seam network, explicitly non-branded.
        for i,rot in enumerate(((math.pi/2,0,0),(math.radians(54),0,math.radians(25)),(math.radians(72),math.radians(42),0))): torus('seam'+str(i),(-1.35,.15,2.45),1.45,.018,ea if i==0 else eb,rot)
        cube('object_stage',(-1.35,.45,.63),(2.15,1.15,.12),material('stage',(.025,.032,.043),metal=.68,rough=.22),bevel=.10); spot('objectRim',(2.6,1.5,6.8),b,1100,.5,(-1.3,.2,2.3),.38)
    else:
        # Luminous perspective tunnel with depth and an open horizon.
        for i in range(9):
            depth=4.5-i*.47; z=.72+i*.49; x=4.55-i*.33; c=ea if i%2==0 else eb
            cube('tl'+str(i),(-x,depth,z),(.035,.08,.78),c,bevel=.01); cube('tr'+str(i),(x,depth,z),(.035,.08,.78),c,bevel=.01); cube('tt'+str(i),(0,depth,z+.78),(x,.08,.035),c,bevel=.01)
        sphere('horizon',(0,5.0,2.1),.48,material('horizon',(0.64,.72,.82),metal=.25,rough=.18,emission=2),segments=56); spot('horizonbeam',(0,6.3,6.8),(0.72,.82,1),1300,.5,(0,4.8,2.0),.35)
    particles(ea,eb,38)


def main():
    a0=parse_args(); a=rgb(a0.accent_a); b=rgb(a0.accent_b); sc,ea,eb=setup(a0.seed,a,b)
    builders={'transfer_signature':build_transfer,'result_statement':build_result,'verified_subject_news':build_subject,'tactical_board':build_tactical,'data_monument':build_data,'event_editorial':build_event}
    if a0.family not in builders: raise SystemExit('unsupported family')
    builders[a0.family](a,b,a0.variant)
    out=Path(a0.output); out.parent.mkdir(parents=True,exist_ok=True); sc.render.filepath=str(out); bpy.ops.render.render(write_still=True)

if __name__=='__main__': main()

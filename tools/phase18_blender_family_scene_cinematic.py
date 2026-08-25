"""Stable cinematic wrapper around the proven procedural Blender family renderer.

Descriptive headlines are suppressed in the 3D world; exact score/data objects are
kept. Copy and the approved PUL7SAR brand are post-composed deterministically.
No external pixels, models, people or network resources are used.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
import phase18_blender_family_scene as base


def _volume():
    m=bpy.data.materials.new('PUL7SAR atmosphere'); m.use_nodes=True
    nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); vol=nt.nodes.new('ShaderNodeVolumePrincipled')
    vol.inputs['Density'].default_value=.008; vol.inputs['Anisotropy'].default_value=.26; vol.inputs['Color'].default_value=(.10,.14,.20,1)
    nt.links.new(vol.outputs['Volume'],out.inputs['Volume']); return m


def _finish(scene):
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,.8,2.45)); focus=bpy.context.object
    scene.camera.data.dof.use_dof=True; scene.camera.data.dof.focus_object=focus; scene.camera.data.dof.aperture_fstop=3.5
    base.add_cube('atmosphere',(0,2.5,3.4),(8,8,5),_volume(),bevel=0)
    scene.use_nodes=True; nt=scene.node_tree; nt.nodes.clear(); rl=nt.nodes.new('CompositorNodeRLayers'); glow=nt.nodes.new('CompositorNodeGlare'); glow.glare_type='FOG_GLOW'; glow.quality='HIGH'; glow.threshold=.9; glow.size=7; comp=nt.nodes.new('CompositorNodeComposite'); nt.links.new(rl.outputs['Image'],glow.inputs['Image']); nt.links.new(glow.outputs['Image'],comp.inputs['Image'])
    for m in list(bpy.data.materials):
        if not m.use_nodes or m.name=='PUL7SAR atmosphere': continue
        ntm=m.node_tree; bs=ntm.nodes.get('Principled BSDF')
        if bs is None or 'Normal' not in bs.inputs: continue
        strength=bs.inputs['Emission Strength'].default_value if 'Emission Strength' in bs.inputs else 0
        if strength>1: continue
        tex=ntm.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=10; tex.inputs['Detail'].default_value=4; tex.inputs['Roughness'].default_value=.7
        bump=ntm.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.08; bump.inputs['Distance'].default_value=.04
        ntm.links.new(tex.outputs['Fac'],bump.inputs['Height']); ntm.links.new(bump.outputs['Normal'],bs.inputs['Normal'])


def _supplement(family,variant,a,b):
    steel=base.mat('v2steel',(.42,.48,.56),metal=.92,rough=.16); ea=base.mat('v2a',a,rough=.15,emit=3.6); eb=base.mat('v2b',b,rough=.15,emit=3.6)
    if family=='transfer_signature' and variant=='a':
        for i in range(3):
            z=1+i*.9; x=4.7-i*.55; base.add_cube('TL'+str(i),(-x,3.1,z),(.05,.08,.72),ea,.02); base.add_cube('TR'+str(i),(x,3.1,z),(.05,.08,.72),eb,.02); base.add_cube('TT'+str(i),(0,3.1,z+.72),(x,.08,.05),steel,.02)
    elif family=='result_statement' and variant=='a':
        for r,c,z in ((4.6,ea,1.1),(3.7,eb,1.55)): base.ring(r,z,c,.028).rotation_euler.x=math.radians(80)
    elif family=='verified_subject_news' and variant=='a':
        base.add_cube('hangerbar',(1.7,.25,4.0),(1.0,.04,.04),steel,.02); base.add_cube('hangerL',(1.05,.22,3.55),(.035,.04,.70),steel,.015,rot=(0,math.radians(-36),0)); base.add_cube('hangerR',(2.35,.22,3.55),(.035,.04,.70),steel,.015,rot=(0,math.radians(36),0))
    elif family=='tactical_board':
        base.add_cube('glassbase',(0,1,-.02),(4.9,6.2,.055),base.mat('glass',(.07,.18,.17),metal=.28,rough=.18),.04)
    elif family=='data_monument' and variant=='a':
        for i in range(3): base.add_cube('step'+str(i),(1.95,1+i*.38,.40+i*.48),(.85,.65,.15),ea if i==2 else steel,.07)
    elif family=='event_editorial' and variant=='b':
        base.spot('horizon',(0,6.2,6.5),b,1000,.5,(0,4.5,1.8),.34)


def main():
    a0=base.args(); a=base.rgb(a0.accent_a); b=base.rgb(a0.accent_b); scene,_,_=base.setup(a0.seed,a,b)
    allowed={'3','1','—','2–2','27'}; original=base.add_text
    base.add_text=lambda text,*args,**kwargs: original(text,*args,**kwargs) if text in allowed else None
    builders={'result_statement':base.result_scene,'transfer_signature':base.transfer_scene,'verified_subject_news':base.subject_scene,'tactical_board':base.tactical_scene,'data_monument':base.data_scene,'event_editorial':base.event_scene}
    builders[a0.family](a,b,a0.variant); _supplement(a0.family,a0.variant,a,b); _finish(scene)
    out=Path(a0.output); out.parent.mkdir(parents=True,exist_ok=True); scene.render.filepath=str(out); bpy.ops.render.render(write_still=True)

if __name__=='__main__': main()

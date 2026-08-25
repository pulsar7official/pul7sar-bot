"""PUL7SAR Phase 18 cinematic V3 renderer.

V3 keeps scene generation completely original and local while moving beyond one
shared procedural stage. Each editorial family receives its own camera grammar,
world architecture and hero staging. Exact text, scores, crests and PUL7SAR brand
remain deterministic post-composition responsibilities.
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


FAMILIES = {f.value: f for f in EditorialSceneFamily}


def args():
    p=argparse.ArgumentParser()
    p.add_argument('--family',required=True,choices=tuple(FAMILIES))
    p.add_argument('--variant',choices=('a','b'),default='a')
    p.add_argument('--output',required=True)
    p.add_argument('--seed',type=int,default=18)
    p.add_argument('--accent-a',default='D90E25')
    p.add_argument('--accent-b',default='2457D6')
    return p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])


def look_at(obj, point):
    obj.rotation_euler=(Vector(point)-obj.location).to_track_quat('-Z','Y').to_euler()


def setup(family, seed, a, b):
    random.seed(seed); bpy.ops.wm.read_factory_settings(use_empty=True)
    d=CinematicArtDirectionRegistry.get(family)
    sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=540; sc.render.resolution_y=675; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'; sc.render.film_transparent=False
    sc.eevee.use_gtao=True; sc.eevee.gtao_distance=4; sc.eevee.gtao_factor=1.45; sc.eevee.use_bloom=True; sc.eevee.bloom_intensity=.055; sc.eevee.bloom_radius=4
    sc.view_settings.look='AgX - Medium High Contrast'; sc.view_settings.exposure=-.18
    sc.world=bpy.data.worlds.new('PUL7SAR V3 World'); sc.world.color=(.002,.004,.009)
    bpy.ops.object.camera_add(location=d.camera_xyz); cam=bpy.context.object; cam.data.lens=d.lens_mm; look_at(cam,d.look_at_xyz); sc.camera=cam
    bpy.ops.object.empty_add(type='PLAIN_AXES',location=d.look_at_xyz); focus=bpy.context.object
    cam.data.dof.use_dof=True; cam.data.dof.focus_object=focus; cam.data.dof.aperture_fstop=d.aperture_fstop

    obs=B.material('v3_obsidian',(.018,.023,.032),metal=.66,rough=.22,bump=.06)
    wall=B.material('v3_wall',(.012,.017,.027),metal=.20,rough=.42,bump=.04)
    B.cube('floor',(0,1,-.16),(8.8,9.5,.18),obs,bevel=.04)
    # Deep off-axis architecture rather than the old universal flat back wall.
    B.cube('rear_mass',(1.25,7.3,3.0),(7.6,.38,3.7),wall,bevel=.38,rot=(0,0,math.radians(-2.5)))
    B.cube('left_wing',(-6.25,3.6,2.2),(.30,4.3,2.5),wall,bevel=.18,rot=(0,0,math.radians(-4)))

    B.area('keyA',(-5.6,-2.0,7.8),a,850,3.6,d.look_at_xyz)
    B.area('keyB',(5.2,-.2,6.4),b,700,3.1,d.look_at_xyz)
    B.area('softTop',(.8,2.8,9.5),(.72,.78,.88),440,4.2,d.look_at_xyz)
    B.spot('rearRim',(1.4,6.8,6.8),(.62,.72,.88),760,.45,d.look_at_xyz,.42)
    B.compositor(sc)
    return sc,d


def architecture(family,a,b,variant):
    ea=B.material('v3_a',a,rough=.26,emission=1.35); eb=B.material('v3_b',b,rough=.26,emission=1.25)
    steel=B.material('v3_steel',(.48,.53,.60),metal=.94,rough=.20,bump=.045)
    glass=B.material('v3_glass',(.10,.14,.20),metal=.25,rough=.10)
    if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
        # A real threshold language: one side remains dark, destination light opens in depth.
        for i,z in enumerate((.75,1.65,2.55,3.45,4.35)):
            B.cube('arrival_l'+str(i),(-4.5+i*.26,2.0+i*.62,z),(.035,.55,.46),ea,bevel=.012,rot=(0,math.radians(5),0))
        B.cube('destination_plane',(3.35,3.3,2.1),(1.55,.10,2.25),glass,bevel=.16,rot=(0,0,math.radians(5)))
        B.cube('destination_edge',(3.25,3.18,2.15),(.035,.13,1.90),eb,bevel=.01)
    elif family is EditorialSceneFamily.RESULT_STATEMENT:
        # Club energies exist as spatial masses, never as rectangular score cards.
        B.cube('club_mass_a',(-4.1,2.3,1.35),(1.35,2.1,1.15),glass,bevel=.34,rot=(0,0,math.radians(-10)))
        B.cube('club_mass_b',(4.0,3.0,1.55),(1.30,2.0,1.35),glass,bevel=.34,rot=(0,0,math.radians(11)))
        B.cube('club_cut_a',(-4.0,.15,2.35),(.95,.035,.025),ea,bevel=.01)
        B.cube('club_cut_b',(3.85,.62,2.55),(.95,.035,.025),eb,bevel=.01)
        B.curve_tube('outcome_axis',[(-4.8,1,.22),(-2.3,.55,.18),(0,.45,.16),(2.5,.8,.18),(4.8,1.5,.25)],steel,.018)
    elif family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
        # Quiet editorial room with a deliberate empty/subject zone and practical lights.
        B.cube('subject_wall',(3.7,2.8,2.45),(1.7,.18,2.55),glass,bevel=.22,rot=(0,0,math.radians(7)))
        B.cube('subject_practical',(3.55,2.58,3.05),(.035,.10,1.15),eb,bevel=.01)
        B.cube('bench',(-2.55,1.7,.45),(1.25,.52,.22),steel,bevel=.18)
        if variant=='a': B.cube('absence_gap',(-2.55,1.6,1.45),(.55,.10,.78),glass,bevel=.22)
    elif family is EditorialSceneFamily.TACTICAL_BOARD:
        # Only a cropped analytical surface. Geometry is the hero, not stadium decoration.
        pitch=B.material('v3_pitch',(.025,.075,.055),rough=.69,bump=.06)
        B.cube('analysis_surface',(0,1.2,.03),(5.3,4.1,.05),pitch,bevel=.06,rot=(0,0,math.radians(-3)))
        for y in (-1.6,.2,2.0,3.8): B.cube('zone'+str(y),(0,y+1.2,.095),(4.75,.012,.012),steel,bevel=.004,rot=(0,0,math.radians(-3)))
    elif family is EditorialSceneFamily.DATA_MONUMENT:
        # Gallery-like information space with one monolithic data plinth.
        B.cube('data_plinth',(-.85,1.35,.52),(2.35,1.55,.52),glass,bevel=.30,rot=(0,0,math.radians(-4)))
        B.cube('data_edge',(-.9,-.22,1.02),(1.75,.025,.025),ea,bevel=.008)
        B.cube('data_wall',(4.25,3.2,2.4),(1.05,.16,2.1),glass,bevel=.20)
        B.cube('data_wall_light',(4.17,3.02,2.55),(.025,.06,1.35),eb,bevel=.008)
    elif family is EditorialSceneFamily.EVENT_EDITORIAL:
        # Forward perspective and practical event lights, no named venue identity.
        for i in range(5):
            y=1.6+i*.82; w=4.7-i*.48; z=.75+i*.42
            B.cube('event_l'+str(i),(-w,y,z),(.03,.09,.68),ea,bevel=.01)
            B.cube('event_r'+str(i),(w,y,z),(.03,.09,.68),eb,bevel=.01)
        B.cube('horizon_gate',(0,5.55,3.15),(2.45,.10,.06),steel,bevel=.02)
    return ea,eb


def build(family,a,b,variant):
    architecture(family,a,b,variant)
    builders={
        EditorialSceneFamily.TRANSFER_SIGNATURE:B.build_transfer,
        EditorialSceneFamily.RESULT_STATEMENT:B.build_result,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:B.build_subject,
        EditorialSceneFamily.TACTICAL_BOARD:B.build_tactical,
        EditorialSceneFamily.DATA_MONUMENT:B.build_data,
        EditorialSceneFamily.EVENT_EDITORIAL:B.build_event,
    }
    builders[family](a,b,variant)


def main():
    q=args(); family=FAMILIES[q.family]; a=B.rgb(q.accent_a); b=B.rgb(q.accent_b)
    sc,_=setup(family,q.seed,a,b); build(family,a,b,q.variant)
    out=Path(q.output); out.parent.mkdir(parents=True,exist_ok=True); sc.render.filepath=str(out); bpy.ops.render.render(write_still=True)


if __name__=='__main__': main()

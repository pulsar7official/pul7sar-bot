from __future__ import annotations

import json
from pathlib import Path

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualDecision, CrossFamilyVisualSystem
from engine.intelligence.original_family_scene_renderer import FamilySceneRequest, OriginalFamilySceneRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_scene_blueprint import VisualSceneBlueprintCompiler

OUT=Path("artifacts/phase18/cross-family-final")
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

STUDIES=(
    (EditorialSceneFamily.TRANSFER_SIGNATURE,"threshold_arrival","NEW CHAPTER","DESTINATION CONFIRMED","","", "#C90B22","#174EA6",101),
    (EditorialSceneFamily.TRANSFER_SIGNATURE,"signing_object","DEAL COMPLETED","OFFICIAL MOVE","","", "#F1C40F","#121C34",102),
    (EditorialSceneFamily.RESULT_STATEMENT,"club_duel_space","FULL-TIME DRAMA","NORTH CITY","SOUTH UNITED","3–1", "#D90E25","#1D5EFF",201),
    (EditorialSceneFamily.RESULT_STATEMENT,"arena_outcome","THE FINAL WORD","EAST ATHLETIC","WEST CLUB","2–2", "#F4C400","#7A1538",202),
    (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,"absence_space","SIDELINED","SQUAD UPDATE","","", "#E4312B","#164C8C",301),
    (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,"statement_stage","NEW ERA","APPOINTMENT CONFIRMED","","", "#14A06F","#29385B",302),
    (EditorialSceneFamily.TACTICAL_BOARD,"phase_corridor","BREAKING THE PRESS","RIGHT-SIDE PROGRESSION","","", "#E3232A","#2D66D4",401),
    (EditorialSceneFamily.TACTICAL_BOARD,"duel_mechanism","MIDFIELD BATTLE","TWO STRUCTURES COLLIDE","","", "#F0B90B","#A5112B",402),
    (EditorialSceneFamily.DATA_MONUMENT,"number_sculpture","RECORD NIGHT","CONSECUTIVE WINS","","27", "#EF2B2D","#2655C7",501),
    (EditorialSceneFamily.DATA_MONUMENT,"draw_orbit","THE DRAW","ROUND OF 16","","", "#7834E8","#0FA7A0",502),
    (EditorialSceneFamily.EVENT_EDITORIAL,"object_story","ONE NIGHT AWAITS","SEASON OPENER","","", "#E02031","#2457D6",601),
    (EditorialSceneFamily.EVENT_EDITORIAL,"anticipation_tunnel","THE ROAD BEGINS","KICK-OFF APPROACHES","","", "#F2B705","#2255C5",602),
)


def _blueprint(family,aid,seed):
    archetype=next(a for a in CrossFamilyVisualSystem.archetypes(family) if a.id==aid)
    return VisualSceneBlueprintCompiler().compile(CrossFamilyVisualDecision(family,archetype,seed,False))


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    profile=PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    renderer=OriginalFamilySceneRenderer(); images=[]
    for idx,(family,aid,headline,primary,secondary,value,a,b,seed) in enumerate(STUDIES,1):
        path=OUT/f"{idx:02d}-{family.value}-{aid}.png"
        receipt=renderer.render(FamilySceneRequest(blueprint=_blueprint(family,aid,seed),headline=headline,primary_label=primary,secondary_label=secondary,primary_value=value,accent_a=a,accent_b=b,brand_accent=a,seed=seed),profile=profile,output_path=str(path),font_path=FONT)
        images.append({"index":idx,"family":family.value,"archetype":aid,"output_path":receipt.output_path,"sha256":receipt.output_sha256,"width":receipt.width,"height":receipt.height,"source_photo_used":False,"generator_used":False,"network_used":False,"fabricated_crest_used":False,"placeholder_used":False,"real_person_depicted":False,"publication_ready":False})
    payload={"schema":"pul7sar-cross-family-final-benchmark-v1","count":len(images),"families":sorted({i["family"] for i in images}),"images":images}
    (OUT/"manifest.json").write_text(json.dumps(payload,indent=2,sort_keys=True),encoding="utf-8")
    return payload

if __name__=="__main__": print(json.dumps(build(),indent=2,sort_keys=True))

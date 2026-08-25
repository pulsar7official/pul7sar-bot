from __future__ import annotations

import json
from pathlib import Path

from engine.intelligence.original_result_scene_renderer_v4 import OriginalResultSceneRendererV4
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.result_visual_variation import ResultVisualFamily


OUTPUT_DIR = Path("artifacts/phase18/original-result-scene-v4")
MANIFEST_PATH = OUTPUT_DIR / "pul7sar-original-result-scene-v4.json"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def build() -> dict[str, object]:
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = ResultStatementComposer().plan(profile)
    renderer = OriginalResultSceneRendererV4()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    studies = (
        dict(
            key="north-city-match-01",
            filename="pul7sar-result-v4-match-01.png",
            home_name="NORTH CITY", away_name="SOUTH UNITED", home_score=3, away_score=1,
            headline="A NIGHT TO REMEMBER", home_accent_hex="#E30613", away_accent_hex="#1D5EFF",
            winner="home", derby=False, qualification=False, comeback=False, late_winner=False,
        ),
        dict(
            key="north-city-match-02",
            filename="pul7sar-result-v4-match-02.png",
            home_name="NORTH CITY", away_name="EAST ATHLETIC", home_score=2, away_score=0,
            headline="CITY CLAIM THE DERBY", home_accent_hex="#E30613", away_accent_hex="#F4C542",
            winner="home", derby=True, qualification=False, comeback=False, late_winner=False,
        ),
        dict(
            key="north-city-match-03",
            filename="pul7sar-result-v4-match-03.png",
            home_name="NORTH CITY", away_name="WEST ROVERS", home_score=1, away_score=1,
            headline="POINTS SHARED", home_accent_hex="#E30613", away_accent_hex="#25B875",
            winner=None, derby=False, qualification=False, comeback=False, late_winner=False,
        ),
    )

    recent: list[ResultVisualFamily] = []
    outputs: list[dict[str, object]] = []
    for index, item in enumerate(studies, start=1):
        receipt = renderer.render(
            composition,
            profile=profile,
            output_path=str(OUTPUT_DIR / item["filename"]),
            home_name=item["home_name"], away_name=item["away_name"],
            home_score=item["home_score"], away_score=item["away_score"],
            headline=item["headline"], home_accent_hex=item["home_accent_hex"],
            away_accent_hex=item["away_accent_hex"], brand_accent_hex="#E30613",
            font_path=FONT_PATH, winner=item["winner"], seed=18000 + index,
            story_key=item["key"], recent_visual_families=tuple(recent),
            derby=item["derby"], qualification=item["qualification"],
            comeback=item["comeback"], late_winner=item["late_winner"],
        )
        recent.append(ResultVisualFamily(receipt.visual_family))
        outputs.append({
            "output_path": receipt.output_path,
            "output_sha256": receipt.output_sha256,
            "score_text": receipt.score_text,
            "visual_family": receipt.visual_family,
            "variation_seed": receipt.variation_seed,
            "anti_repetition_applied": receipt.anti_repetition_applied,
            "home_crest_used": receipt.home_crest_used,
            "away_crest_used": receipt.away_crest_used,
            "fabricated_crest_used": receipt.fabricated_crest_used,
            "score_scale": receipt.score_scale,
        })

    payload = {
        "schema": "pul7sar-original-result-scene-benchmark-v4-dynamic",
        "renderer_contract": renderer.CONTRACT,
        "width": profile.width,
        "height": profile.height,
        "scene_origin": "100_percent_code_generated_original_pixels_plus_exact_local_assets",
        "source_photo_used": False,
        "generator_used": False,
        "network_used": False,
        "fabricated_crest_used": False,
        "study_only": True,
        "publication_ready": False,
        "same_club_dynamic_composition_demo": True,
        "club_identity_policy": "stable names/colors; crests explicit-local-only; missing crests are never fabricated",
        "outputs": outputs,
    }
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))

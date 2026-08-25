from __future__ import annotations

import json
from pathlib import Path

from engine.intelligence.original_result_scene_renderer import OriginalResultSceneRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer


OUTPUT_DIR = Path("artifacts/phase18/original-result-scene")
PNG_PATH = OUTPUT_DIR / "pul7sar-original-result-scene-v1.png"
MANIFEST_PATH = OUTPUT_DIR / "pul7sar-original-result-scene-v1.json"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def build() -> dict[str, object]:
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = ResultStatementComposer().plan(profile)
    receipt = OriginalResultSceneRenderer().render(
        composition,
        profile=profile,
        output_path=str(PNG_PATH),
        home_name="NORTH CITY",
        away_name="SOUTH UNITED",
        home_score=3,
        away_score=1,
        headline="A NIGHT TO REMEMBER",
        home_accent_hex="#E30613",
        away_accent_hex="#1D5EFF",
        brand_accent_hex="#E30613",
        font_path=FONT_PATH,
        winner="home",
        seed=18001,
    )
    payload = {
        "schema": "pul7sar-original-result-scene-benchmark-v1",
        "renderer_contract": receipt.contract,
        "output_path": receipt.output_path,
        "output_sha256": receipt.output_sha256,
        "width": receipt.width,
        "height": receipt.height,
        "score_text": receipt.score_text,
        "scene_origin": receipt.scene_origin,
        "source_photo_used": receipt.source_photo_used,
        "generator_used": receipt.generator_used,
        "network_used": receipt.network_used,
        "fabricated_crest_used": receipt.fabricated_crest_used,
        "brand_overlay_contract": receipt.brand_overlay_contract,
        "visual_language": receipt.visual_language,
        "study_only": receipt.study_only,
        "publication_ready": receipt.publication_ready,
        "benchmark_identity_note": "fictional club names; no club crest is claimed or fabricated",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))

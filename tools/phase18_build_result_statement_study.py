#!/usr/bin/env python3
"""Build an independent deterministic PUL7SAR Result Statement visual study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.result_statement_study_renderer import ResultStatementStudyRenderer


def _font() -> Path:
    for candidate in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("required CI study font unavailable")


def build(output_dir: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = ResultStatementComposer().plan(profile)

    output = root / "pul7sar-result-statement-study-v1.png"
    receipt = ResultStatementStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        home_name="HOME CLUB",
        away_name="AWAY CLUB",
        home_score=3,
        away_score=1,
        headline="FULL TIME",
        home_accent_hex="#034694",
        away_accent_hex="#B21F2D",
        brand_accent_hex="#034694",
        font_path=str(_font()),
        winner="home",
    )

    manifest = {
        "manifest_version": "pul7sar-result-statement-study-v1",
        "renderer_contract": receipt.contract,
        "composition_contract": composition.contract,
        "brand_overlay_contract": receipt.brand_overlay_contract,
        "family": "result_statement",
        "platform": profile.platform.value,
        "png": output.name,
        "png_sha256": receipt.output_sha256,
        "width": receipt.width,
        "height": receipt.height,
        "headline": "FULL TIME",
        "score_text": receipt.score_text,
        "score_is_deterministic": True,
        "score_is_primary": composition.score_is_primary,
        "home_identity_placeholder_used": receipt.home_identity_placeholder_used,
        "away_identity_placeholder_used": receipt.away_identity_placeholder_used,
        "identity_placeholders_are_crest_evidence": False,
        "club_identity_scale_equal": receipt.club_identity_scale_equal,
        "winner_emphasis_mode": composition.winner_emphasis_mode,
        "loser_treatment": receipt.loser_treatment,
        "loser_identity_reduced_or_degraded": False,
        "inherits_transfer_renderer": False,
        "inherits_transfer_layout": False,
        "full_pitch_required": False,
        "brand_zone": receipt.brand_zone,
        "brand_width": receipt.brand_width,
        "brand_height": receipt.brand_height,
        "brand_max_width_ratio": composition.brand.max_width_ratio,
        "brand_max_height_ratio": composition.brand.max_height_ratio,
        "historic_fixed_brand_width_px": 870,
        "historic_fixed_brand_width_removed": receipt.brand_width != 870,
        "generator_used": receipt.generator_used,
        "network_used": receipt.network_used,
        "study_only": receipt.study_only,
        "publication_ready": receipt.publication_ready,
        "real_club_assets_required_for_publication": True,
        "human_visual_review_required": True,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/phase18_result_statement_study")
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

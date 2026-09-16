#!/usr/bin/env python3
"""Build a deterministic 4-3-3 PUL7SAR Tactical Intelligence study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.tactical_intelligence_composition import TacticalIntelligenceComposer
from engine.intelligence.tactical_intelligence_study_renderer import (
    TacticalArrow,
    TacticalIntelligenceStudyRenderer,
    TacticalPosition,
)


def _font() -> Path:
    for candidate in (
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('required CI study font unavailable')


def _positions() -> tuple[TacticalPosition, ...]:
    # Left-to-right attacking direction on exact pitch world coordinates.
    return (
        TacticalPosition('GK', 0.08, 0.50),
        TacticalPosition('LB', 0.25, 0.15),
        TacticalPosition('CB', 0.23, 0.38),
        TacticalPosition('CB', 0.23, 0.62),
        TacticalPosition('RB', 0.25, 0.85),
        TacticalPosition('DM', 0.43, 0.50),
        TacticalPosition('CM', 0.55, 0.30),
        TacticalPosition('CM', 0.55, 0.70),
        TacticalPosition('LW', 0.78, 0.17),
        TacticalPosition('ST', 0.84, 0.50),
        TacticalPosition('RW', 0.78, 0.83),
    )


def _arrows() -> tuple[TacticalArrow, ...]:
    return (
        TacticalArrow(0.25, 0.15, 0.48, 0.10),
        TacticalArrow(0.25, 0.85, 0.48, 0.90),
        TacticalArrow(0.55, 0.30, 0.69, 0.39),
    )


def build(output_dir: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = TacticalIntelligenceComposer().plan(profile)
    positions = _positions()
    arrows = _arrows()

    output = root / 'pul7sar-tactical-intelligence-study-v1.png'
    receipt = TacticalIntelligenceStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        headline='TACTICAL INTELLIGENCE',
        analysis_text='WIDTH + MIDFIELD CONTROL',
        formation_label='4-3-3  |  POSSESSION SHAPE',
        positions=positions,
        arrows=arrows,
        accent_hex='#17A8FF',
        opponent_accent_hex='#D8E1E8',
        brand_accent_hex='#17A8FF',
        font_path=str(_font()),
    )

    manifest = {
        'manifest_version': 'pul7sar-tactical-intelligence-study-v1',
        'renderer_contract': receipt.contract,
        'composition_contract': composition.contract,
        'brand_overlay_contract': receipt.brand_overlay_contract,
        'family': 'tactical_board',
        'platform': profile.platform.value,
        'png': output.name,
        'png_sha256': receipt.output_sha256,
        'width': receipt.width,
        'height': receipt.height,
        'formation_label': receipt.formation_label,
        'position_count': receipt.position_count,
        'arrow_count': receipt.arrow_count,
        'exact_pitch_geometry_used': receipt.exact_pitch_geometry_used,
        'generated_pitch_markings_used': receipt.generated_pitch_markings_used,
        'generated_player_positions_used': receipt.generated_player_positions_used,
        'decorative_stadium_used': receipt.decorative_stadium_used,
        'pitch_is_information_surface': True,
        'pitch_is_global_news_template': False,
        'inherits_transfer_renderer': False,
        'inherits_result_renderer': False,
        'brand_zone': receipt.brand_zone,
        'brand_width': receipt.brand_width,
        'brand_height': receipt.brand_height,
        'brand_max_width_ratio': composition.brand.max_width_ratio,
        'brand_max_height_ratio': composition.brand.max_height_ratio,
        'generator_used': receipt.generator_used,
        'network_used': receipt.network_used,
        'study_only': receipt.study_only,
        'publication_ready': receipt.publication_ready,
        'human_visual_review_required': True,
    }
    (root/'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding='utf-8',
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='output/phase18_tactical_intelligence_study')
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

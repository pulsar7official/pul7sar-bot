#!/usr/bin/env python3
"""Build premium deterministic Data Monument study artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.data_monument_composition import DataMonumentComposer
from engine.intelligence.data_monument_study_renderer import DataMonumentRow, DataMonumentStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


def _font() -> Path:
    for candidate in (
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('required CI study font unavailable')


def build(output_dir: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = DataMonumentComposer().plan(profile)
    rows = (
        DataMonumentRow(1, 'NORTH CITY', '76 PTS', True),
        DataMonumentRow(2, 'ROYAL ATHLETIC', '72 PTS'),
        DataMonumentRow(3, 'UNITED SPORTING', '69 PTS'),
        DataMonumentRow(4, 'OLYMPIA FC', '64 PTS'),
    )
    output = root / 'pul7sar-data-monument-study-v1-premium.png'
    receipt = DataMonumentStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        headline='TITLE RACE',
        context='AFTER 30 MATCHES',
        rows=rows,
        accent_hex='#C71925',
        font_path=str(_font()),
        seed_key='pul7sar-data-monument-v1',
    )
    manifest = {
        'manifest_version': 'pul7sar-data-monument-study-v1-premium',
        'renderer_contract': receipt.contract,
        'composition_contract': composition.contract,
        'atmosphere_contract': receipt.atmosphere_contract,
        'family': 'data_monument',
        'platform': profile.platform.value,
        'png': output.name,
        'png_sha256': receipt.output_sha256,
        'width': receipt.width,
        'height': receipt.height,
        'row_count': receipt.row_count,
        'dominant_value': receipt.dominant_value,
        'exact_values_code_owned': receipt.exact_values_code_owned,
        'generated_exact_values_allowed': composition.generated_exact_values_allowed,
        'spreadsheet_grid_used': receipt.spreadsheet_grid_used,
        'stadium_used': receipt.stadium_used,
        'unnecessary_stadium_allowed': composition.unnecessary_stadium_allowed,
        'dense_paragraph_allowed': composition.dense_paragraph_allowed,
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
    (root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='output/phase18_data_monument_study')
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

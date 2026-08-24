#!/usr/bin/env python3
"""Build premium deterministic Event Editorial study artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.event_editorial_study_renderer import EventAnchorKind, EventEditorialStudyRenderer
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
    composition = EventEditorialComposer().plan(profile)
    output = root / 'pul7sar-event-editorial-study-v1-premium-anchor.png'
    receipt = EventEditorialStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        headline='NEW ERA',
        kicker='OFFICIAL ANNOUNCEMENT',
        anchor_kind=EventAnchorKind.ANNOUNCEMENT,
        accent_hex='#C71925',
        font_path=str(_font()),
        seed_key='pul7sar-event-editorial-v1',
    )
    manifest = {
        'manifest_version': 'pul7sar-event-editorial-study-v1-premium-anchor',
        'renderer_contract': receipt.contract,
        'composition_contract': composition.contract,
        'atmosphere_contract': receipt.atmosphere_contract,
        'family': 'event_editorial',
        'platform': profile.platform.value,
        'png': output.name,
        'png_sha256': receipt.output_sha256,
        'width': receipt.width,
        'height': receipt.height,
        'anchor_kind': receipt.anchor_kind,
        'single_anchor_used': receipt.single_anchor_used,
        'person_used': receipt.person_used,
        'full_pitch_used': receipt.full_pitch_used,
        'decorative_stats_used': receipt.decorative_stats_used,
        'person_required': composition.person_required,
        'full_pitch_required': composition.full_pitch_required,
        'decorative_stats_required': composition.decorative_stats_required,
        'dense_copy_allowed': composition.dense_copy_allowed,
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
    parser.add_argument('--output-dir', default='output/phase18_event_editorial_study')
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

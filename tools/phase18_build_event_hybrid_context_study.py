#!/usr/bin/env python3
"""Build a premium Event Editorial study from a verified local context image."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.event_editorial_study_renderer import EventAnchorKind, EventEditorialStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.verified_context_surface import ContextRightsBasis, VerifiedContextAsset


def _font() -> Path:
    for candidate in (
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('required CI study font unavailable')


def build(*, output_dir: str, context_image: str, source_reference: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    source = Path(context_image)
    if not source.is_file():
        raise FileNotFoundError(context_image)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    asset = VerifiedContextAsset(
        asset_id='phase18-event-cc0-night-stadium',
        path=str(source),
        sha256=digest,
        source_reference=source_reference,
        rights_basis=ContextRightsBasis.PUBLIC_DOMAIN,
    )
    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = EventEditorialComposer().plan(profile)
    output = root / 'pul7sar-event-editorial-hybrid-context-v1.png'
    receipt = EventEditorialStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        headline='MATCH NIGHT',
        kicker='THE STAGE IS SET',
        anchor_kind=EventAnchorKind.ANNOUNCEMENT,
        accent_hex='#C71925',
        font_path=str(_font()),
        seed_key='pul7sar-event-hybrid-context-v1',
        context_asset=asset,
    )
    manifest = {
        'manifest_version': 'pul7sar-event-editorial-hybrid-context-v1',
        'renderer_contract': receipt.contract,
        'composition_contract': composition.contract,
        'context_contract': receipt.context_contract,
        'atmosphere_contract': receipt.atmosphere_contract,
        'family': 'event_editorial',
        'platform': profile.platform.value,
        'png': output.name,
        'png_sha256': receipt.output_sha256,
        'width': receipt.width,
        'height': receipt.height,
        'anchor_kind': receipt.anchor_kind,
        'single_anchor_used': receipt.single_anchor_used,
        'photographic_context_used': receipt.photographic_context_used,
        'context_asset_sha256': digest,
        'context_source_reference': receipt.context_source_reference,
        'context_rights_basis': asset.rights_basis.value,
        'person_used': receipt.person_used,
        'full_pitch_used': receipt.full_pitch_used,
        'decorative_stats_used': receipt.decorative_stats_used,
        'brand_zone': receipt.brand_zone,
        'brand_width': receipt.brand_width,
        'brand_height': receipt.brand_height,
        'generator_used': receipt.generator_used,
        'network_used_by_renderer': receipt.network_used,
        'study_only': receipt.study_only,
        'publication_ready': receipt.publication_ready,
        'human_visual_review_required': True,
    }
    (root / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding='utf-8',
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='output/phase18_event_hybrid_context_study')
    parser.add_argument('--context-image', required=True)
    parser.add_argument('--source-reference', required=True)
    args = parser.parse_args()
    print(json.dumps(build(
        output_dir=args.output_dir,
        context_image=args.context_image,
        source_reference=args.source_reference,
    ), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a real-photo verified-match Result study from rights-cleared event evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from engine.intelligence.moment_led_result_renderer import MomentLedResultRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.verified_story_moment import StoryMomentKind, StoryMomentRights, VerifiedStoryMomentAsset


def _font() -> Path:
    for candidate in (
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('required study font unavailable')


def build(output_dir: str, source_image: str) -> dict[str, object]:
    root=Path(output_dir); root.mkdir(parents=True,exist_ok=True)
    source=Path(source_image)
    if not source.is_file():
        raise FileNotFoundError(source_image)
    source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
    asset=VerifiedStoryMomentAsset(
        asset_id='orlando-atlas-2025-verified-match-moment',
        path=str(source),
        sha256=source_sha,
        source_reference='https://commons.wikimedia.org/wiki/File:OCSC_10_Atlas_7.jpg',
        moment_kind=StoryMomentKind.MATCH_ACTION,
        rights_basis=StoryMomentRights.PUBLIC_DOMAIN,
        contains_people=True,
        verified_identity_ids=('player:martin-ojeda','player:matias-coccaro'),
        event_evidence=True,
        publication_allowed=True,
    )
    profile=PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition=ResultStatementComposer().plan(profile)
    output=root/'pul7sar-verified-match-result-study-v1.png'
    receipt=MomentLedResultRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        moment_asset=asset,
        home_name='ORLANDO CITY',
        away_name='ATLAS FC',
        home_score=3,
        away_score=1,
        home_accent_hex='#633492',
        away_accent_hex='#D71920',
        brand_accent_hex='#633492',
        font_path=str(_font()),
        focal_x_ratio=0.50,
        focal_y_ratio=0.44,
    )
    manifest={
        'manifest_version':'pul7sar-verified-match-result-study-v1',
        'renderer_contract':receipt.contract,
        'family':'result_statement',
        'visual_concept':'verified_match_moment',
        'platform':profile.platform.value,
        'png':output.name,
        'png_sha256':receipt.output_sha256,
        'source_sha256':receipt.source_sha256,
        'source_reference':receipt.source_reference,
        'source_rights':'CC0 1.0 / public-domain dedication',
        'source_depicts':['Martín Ojeda','Matías Cóccaro'],
        'source_event':'Orlando City SC v Club Atlas, 2 August 2025',
        'result_fact_source':'https://www.orlandocitysc.com/news/match-report-orlando-city-sc-downs-atlas-f-c-3-1',
        'score_text':receipt.score_text,
        'score_is_exact':True,
        'photo_claim':'actual match moment, not claimed as decisive goal',
        'photograph_is_primary':receipt.photograph_is_primary,
        'score_is_secondary':receipt.score_is_secondary,
        'verified_identity_ids':list(receipt.verified_identity_ids),
        'club_identity_scale_equal':receipt.club_identity_scale_equal,
        'loser_treatment':receipt.loser_treatment,
        'brand_width':receipt.brand_width,
        'brand_height':receipt.brand_height,
        'generator_used':receipt.generator_used,
        'network_used_by_renderer':receipt.network_used,
        'study_only':receipt.study_only,
        'publication_ready':receipt.publication_ready,
        'human_visual_review_required':True,
    }
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    return manifest


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',default='output/phase18_verified_match_result_study')
    parser.add_argument('--source-image',required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output_dir,args.source_image),ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

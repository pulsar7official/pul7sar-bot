#!/usr/bin/env python3
"""Build a photographic premium-hybrid Result Statement visual-quality benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.premium_hybrid_result_runtime import PremiumHybridResultStudyRenderer
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.verified_context_surface import ContextRightsBasis, VerifiedContextAsset


def _font() -> Path:
    for candidate in (
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("required CI study font unavailable")


def build(output_dir: str, context_image: str, source_reference: str) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    source = Path(context_image)
    if not source.is_file():
        raise FileNotFoundError(context_image)
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    asset = VerifiedContextAsset(
        asset_id="premium-hybrid-result-context-study",
        path=str(source),
        sha256=source_sha,
        source_reference=source_reference,
        rights_basis=ContextRightsBasis.PUBLIC_DOMAIN,
        contains_verified_person=False,
        publication_allowed=True,
    )

    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    composition = ResultStatementComposer().plan(profile)
    output = root / "pul7sar-premium-hybrid-result-study-v2.png"
    receipt = PremiumHybridResultStudyRenderer().render(
        composition,
        profile=profile,
        output_path=str(output),
        context_asset=asset,
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
        focal_x_ratio=0.50,
        focal_y_ratio=0.44,
    )

    manifest = {
        "manifest_version": "pul7sar-premium-hybrid-result-study-v2",
        "renderer_contract": receipt.contract,
        "composition_contract": composition.contract,
        "verified_context_contract": receipt.verified_context_contract,
        "family": "result_statement",
        "platform": profile.platform.value,
        "png": output.name,
        "png_sha256": receipt.output_sha256,
        "width": receipt.width,
        "height": receipt.height,
        "score_text": receipt.score_text,
        "score_is_deterministic": True,
        "metallic_score_used": receipt.metallic_score_used,
        "optical_depth_used": receipt.optical_depth_used,
        "context_asset_id": receipt.context_asset_id,
        "context_source_sha256": receipt.context_source_sha256,
        "context_output_sha256": receipt.context_output_sha256,
        "context_source_reference": receipt.context_source_reference,
        "context_rights_basis": receipt.context_rights_basis,
        "context_role": receipt.context_role,
        "context_is_match_or_venue_evidence": False,
        "club_identity_scale_equal": receipt.club_identity_scale_equal,
        "home_identity_placeholder_used": receipt.home_identity_placeholder_used,
        "away_identity_placeholder_used": receipt.away_identity_placeholder_used,
        "loser_treatment": receipt.loser_treatment,
        "brand_zone": receipt.brand_zone,
        "brand_width": receipt.brand_width,
        "brand_height": receipt.brand_height,
        "generator_used": receipt.generator_used,
        "network_used_by_renderer": receipt.network_used_by_renderer,
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
    parser.add_argument("--output-dir", default="output/phase18_premium_hybrid_result_study")
    parser.add_argument("--context-image", required=True)
    parser.add_argument("--source-reference", required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir, args.context_image, args.source_reference), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

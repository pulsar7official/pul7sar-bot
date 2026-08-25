from pathlib import Path

import pytest
from PIL import Image

from engine.intelligence.hybrid_final_composer import HybridFinalComposer
from engine.intelligence.hybrid_pixel_composer import (
    HybridPixelComposer,
    HybridPixelRequest,
    VerifiedRasterAsset,
)
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def _base(tmp_path: Path) -> Path:
    p = tmp_path / "generated.png"
    Image.new("RGB", (512, 640), (18, 24, 32)).save(p)
    return p


def _result_plan():
    return HybridFinalComposer.compile(
        family=EditorialSceneFamily.RESULT_STATEMENT,
        story_key="result-hybrid-pixel-test",
        seed=18,
    )


def test_result_composes_generated_base_with_exact_text_only(tmp_path):
    out = tmp_path / "out.jpg"
    receipt = HybridPixelComposer().compose(HybridPixelRequest(
        plan=_result_plan(),
        generated_base_path=str(_base(tmp_path)),
        output_path=str(out),
        headline="FULL TIME",
        primary_label="NORTH CITY",
        secondary_label="SOUTH UNITED",
        primary_value="3-1",
        generated_base_verified_unbranded=True,
        generated_base_verified_no_readable_facts=True,
    ))
    assert out.is_file()
    assert receipt.generated_base_used
    assert receipt.brand_applied is False
    assert receipt.publication_ready is False
    assert receipt.verified_assets_applied == ()


def test_generated_base_must_be_verified_unbranded(tmp_path):
    with pytest.raises(ValueError, match="GENERATED_BASE_NOT_VERIFIED_UNBRANDED"):
        HybridPixelComposer().compose(HybridPixelRequest(
            plan=_result_plan(),
            generated_base_path=str(_base(tmp_path)),
            output_path=str(tmp_path / "out.jpg"),
            headline="FULL TIME",
            primary_value="1-0",
            generated_base_verified_no_readable_facts=True,
        ))


def test_result_requires_exact_score(tmp_path):
    with pytest.raises(ValueError, match="RESULT_REQUIRES_EXACT_SCORE"):
        HybridPixelComposer().compose(HybridPixelRequest(
            plan=_result_plan(),
            generated_base_path=str(_base(tmp_path)),
            output_path=str(tmp_path / "out.jpg"),
            headline="FULL TIME",
            generated_base_verified_unbranded=True,
            generated_base_verified_no_readable_facts=True,
        ))


def test_brand_asset_must_be_explicitly_approved(tmp_path):
    brand = tmp_path / "brand.png"
    Image.new("RGBA", (100, 40), (255, 255, 255, 255)).save(brand)
    with pytest.raises(ValueError, match="UNAPPROVED_ASSET:pul7sar_brand"):
        HybridPixelComposer().compose(HybridPixelRequest(
            plan=_result_plan(),
            generated_base_path=str(_base(tmp_path)),
            output_path=str(tmp_path / "out.jpg"),
            headline="FULL TIME",
            primary_value="2-1",
            brand_master=VerifiedRasterAsset(str(brand), "pul7sar_brand", verified=True, approved=False),
            generated_base_verified_unbranded=True,
            generated_base_verified_no_readable_facts=True,
        ))


def test_verified_subject_family_fails_without_verified_subject(tmp_path):
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
        story_key="subject-required-test",
    )
    with pytest.raises(ValueError, match="REQUIRED_VERIFIED_SUBJECT_MISSING"):
        HybridPixelComposer().compose(HybridPixelRequest(
            plan=plan,
            generated_base_path=str(_base(tmp_path)),
            output_path=str(tmp_path / "out.jpg"),
            headline="SQUAD UPDATE",
            generated_base_verified_unbranded=True,
            generated_base_verified_no_readable_facts=True,
        ))


def test_tactical_is_rejected_by_hybrid_pixel_composer(tmp_path):
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.TACTICAL_BOARD,
        story_key="tactical-test",
    )
    with pytest.raises(ValueError, match="TACTICAL_USES_DETERMINISTIC_RENDERER"):
        HybridPixelComposer().compose(HybridPixelRequest(
            plan=plan,
            generated_base_path=str(_base(tmp_path)),
            output_path=str(tmp_path / "out.jpg"),
            headline="PRESSING MAP",
            generated_base_verified_unbranded=True,
            generated_base_verified_no_readable_facts=True,
        ))

from pathlib import Path

import pytest
from PIL import Image

from engine.intelligence.result_spatial_monument import SpatialResultMonument, SpatialResultSpec


def test_spatial_monument_requires_exact_result_fields(tmp_path: Path):
    base = tmp_path / "base.png"
    Image.new("RGB", (320, 400), (35, 45, 55)).save(base)
    with pytest.raises(ValueError, match="SPATIAL_RESULT_SCORE_REQUIRED"):
        SpatialResultMonument.compose(
            str(base), str(tmp_path / "out.jpg"),
            SpatialResultSpec(headline="FULL TIME", home="A", away="B", score=""),
        )


def test_spatial_monument_renders_without_identity_fabrication(tmp_path: Path):
    base = tmp_path / "base.png"
    out = tmp_path / "out.jpg"
    Image.new("RGB", (320, 400), (48, 58, 68)).save(base)
    SpatialResultMonument.compose(
        str(base), str(out),
        SpatialResultSpec(headline="FULL TIME", home="NORTH CITY", away="SOUTH UNITED", score="3-1"),
    )
    assert out.is_file()
    rendered = Image.open(out)
    assert rendered.size == (320, 400)
    assert rendered.convert("RGB").tobytes() != Image.open(base).convert("RGB").tobytes()


def test_spatial_monument_rejects_missing_team_labels(tmp_path: Path):
    base = tmp_path / "base.png"
    Image.new("RGB", (320, 400), (35, 45, 55)).save(base)
    with pytest.raises(ValueError, match="SPATIAL_RESULT_TEAM_LABELS_REQUIRED"):
        SpatialResultMonument.compose(
            str(base), str(tmp_path / "out.jpg"),
            SpatialResultSpec(headline="FULL TIME", home="", away="B", score="3-1"),
        )

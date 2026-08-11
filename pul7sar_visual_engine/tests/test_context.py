"""Phase 1 tests: RenderContext immutability and contract.

Verifies 02_ARCHITECTURE.md, Section 15, Step 2 / Data Ownership and
04_RENDERING_SPECIFICATION.md, Section 6.
"""

import dataclasses

import pytest

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.context import RenderContext
from engine.fonts.resolver import ResolvedFonts
from engine.validation.validator import ValidatedPayload


def _make_context(**overrides) -> RenderContext:
    defaults = dict(
        validated_payload=ValidatedPayload(data={"headline": "Goal!"}),
        resolved_configuration=ResolvedConfiguration(data={"engine": "pillow"}),
        resolved_assets=ResolvedAssets(data={"logo": "logo.png"}),
        resolved_fonts=ResolvedFonts(data={"headline": "Cairo-Bold.ttf"}),
        render_id="render-0001",
        render_metadata={"source": "test"},
        platform_targets=("telegram",),
        canvas_information={"width": 1280, "height": 720},
        locale_information={"locale": "ar"},
    )
    defaults.update(overrides)
    return RenderContext(**defaults)


def test_render_context_holds_all_required_fields():
    ctx = _make_context()
    assert isinstance(ctx.validated_payload, ValidatedPayload)
    assert isinstance(ctx.resolved_configuration, ResolvedConfiguration)
    assert isinstance(ctx.resolved_assets, ResolvedAssets)
    assert isinstance(ctx.resolved_fonts, ResolvedFonts)
    assert ctx.render_id == "render-0001"
    assert ctx.render_metadata == {"source": "test"}
    assert ctx.platform_targets == ("telegram",)
    assert ctx.canvas_information == {"width": 1280, "height": 720}
    assert ctx.locale_information == {"locale": "ar"}


def test_render_context_is_immutable():
    ctx = _make_context()
    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.render_id = "render-0002"


def test_render_context_nested_mappings_are_immutable():
    ctx = _make_context()
    with pytest.raises(TypeError):
        ctx.render_metadata["source"] = "mutated"
    with pytest.raises(TypeError):
        ctx.canvas_information["width"] = 9999
    with pytest.raises(TypeError):
        ctx.locale_information["locale"] = "en"


def test_render_context_platform_targets_is_a_tuple():
    ctx = _make_context(platform_targets=["telegram", "twitter"])
    assert isinstance(ctx.platform_targets, tuple)
    assert ctx.platform_targets == ("telegram", "twitter")


def test_render_context_rejects_wrong_type_for_validated_payload():
    with pytest.raises(TypeError):
        _make_context(validated_payload={"not": "a ValidatedPayload"})


def test_render_context_rejects_wrong_type_for_resolved_configuration():
    with pytest.raises(TypeError):
        _make_context(resolved_configuration={"not": "a ResolvedConfiguration"})


def test_render_context_rejects_wrong_type_for_resolved_assets():
    with pytest.raises(TypeError):
        _make_context(resolved_assets={"not": "a ResolvedAssets"})


def test_render_context_rejects_wrong_type_for_resolved_fonts():
    with pytest.raises(TypeError):
        _make_context(resolved_fonts={"not": "a ResolvedFonts"})


def test_validated_payload_is_immutable():
    payload = ValidatedPayload(data={"headline": "Goal!"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        payload.data = {"headline": "changed"}
    with pytest.raises(TypeError):
        payload.data["headline"] = "changed"


def test_resolved_configuration_is_immutable():
    cfg = ResolvedConfiguration(data={"engine": "pillow"})
    with pytest.raises(TypeError):
        cfg.data["engine"] = "skia"


def test_resolved_assets_is_immutable():
    assets = ResolvedAssets(data={"logo": "logo.png"})
    with pytest.raises(TypeError):
        assets.data["logo"] = "other.png"


def test_resolved_fonts_is_immutable():
    fonts = ResolvedFonts(data={"headline": "Cairo-Bold.ttf"})
    with pytest.raises(TypeError):
        fonts.data["headline"] = "Other.ttf"

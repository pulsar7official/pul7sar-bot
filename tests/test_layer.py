"""Phase 1 tests: Layer, LayerKind, LayerZone.

Verifies 02_ARCHITECTURE.md, Section 11 (Layer System Specification)
and 04_RENDERING_SPECIFICATION.md, Sections 7-9.
"""

import dataclasses

import pytest

from engine.layers.enums import LayerKind, LayerZone
from engine.layers.layer import Layer

EXPECTED_LAYER_KINDS = {
    "BACKGROUND",
    "IMAGE",
    "TEXT",
    "ICON",
    "SHAPE",
    "GRADIENT",
    "TEXTURE",
    "OVERLAY",
}

EXPECTED_LAYER_ZONES = {"BACKGROUND", "CONTENT", "BRAND", "FOOTER"}


def test_layer_kind_has_exactly_the_eight_frozen_values():
    actual = {member.value for member in LayerKind}
    assert actual == EXPECTED_LAYER_KINDS
    assert len(LayerKind) == 8


def test_layer_zone_has_exactly_the_four_frozen_values():
    actual = {member.value for member in LayerZone}
    assert actual == EXPECTED_LAYER_ZONES
    assert len(LayerZone) == 4


def test_unsupported_layer_kind_is_rejected():
    with pytest.raises(ValueError):
        LayerKind("NOT_A_REAL_KIND")


def test_unsupported_layer_zone_is_rejected():
    with pytest.raises(ValueError):
        LayerZone("NOT_A_REAL_ZONE")


def _make_layer(**overrides) -> Layer:
    defaults = dict(
        kind=LayerKind.TEXT,
        zone=LayerZone.CONTENT,
        z_index=10,
        properties={"text": "Goal!"},
    )
    defaults.update(overrides)
    return Layer(**defaults)


def test_layer_holds_required_fields():
    layer = _make_layer()
    assert layer.kind is LayerKind.TEXT
    assert layer.zone is LayerZone.CONTENT
    assert layer.z_index == 10
    assert layer.properties == {"text": "Goal!"}


def test_layer_is_immutable():
    layer = _make_layer()
    with pytest.raises(dataclasses.FrozenInstanceError):
        layer.z_index = 99


def test_layer_properties_mapping_is_immutable():
    layer = _make_layer()
    with pytest.raises(TypeError):
        layer.properties["text"] = "changed"


def test_layer_rejects_kind_that_is_not_a_layer_kind_enum_member():
    with pytest.raises(TypeError):
        _make_layer(kind="TEXT")  # raw string, not LayerKind.TEXT


def test_layer_rejects_zone_that_is_not_a_layer_zone_enum_member():
    with pytest.raises(TypeError):
        _make_layer(zone="CONTENT")  # raw string, not LayerZone.CONTENT


def test_layer_rejects_non_integer_z_index():
    with pytest.raises(TypeError):
        _make_layer(z_index="10")


def test_layer_is_serializable_to_a_plain_dict():
    layer = _make_layer()
    serialized = layer.to_dict()
    assert serialized == {
        "kind": "TEXT",
        "zone": "CONTENT",
        "z_index": 10,
        "properties": {"text": "Goal!"},
    }
    # Must be plain, JSON-compatible types.
    import json

    json.dumps(serialized)  # raises if not serializable

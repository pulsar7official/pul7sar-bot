"""Tests for the canonical PUL7SAR Layer system.

Canonical source:
    engine.layers.layer

This test file intentionally imports Layer, LayerKind and LayerZone from the
same module so type identity is guaranteed across Templates, Pipeline and
Renderer.
"""

import dataclasses

import pytest

from engine.layers.layer import Layer, LayerKind, LayerZone


EXPECTED_LAYER_KINDS = {
    "background",
    "image",
    "text",
    "icon",
    "shape",
    "gradient",
    "texture",
    "overlay",
}

EXPECTED_LAYER_ZONES = {
    "background",
    "content",
    "brand",
    "footer",
}


def _make_layer(**overrides) -> Layer:
    defaults = dict(
        kind=LayerKind.TEXT,
        zone=LayerZone.CONTENT,
        z_index=10,
        properties={"text": "Goal!"},
    )
    defaults.update(overrides)
    return Layer(**defaults)


def test_layer_kind_has_exactly_the_eight_canonical_values():
    assert {member.value for member in LayerKind} == EXPECTED_LAYER_KINDS
    assert len(LayerKind) == 8


def test_layer_zone_has_exactly_the_four_canonical_values():
    assert {member.value for member in LayerZone} == EXPECTED_LAYER_ZONES
    assert len(LayerZone) == 4


def test_unsupported_layer_kind_is_rejected():
    with pytest.raises(ValueError):
        LayerKind("not-a-real-kind")


def test_unsupported_layer_zone_is_rejected():
    with pytest.raises(ValueError):
        LayerZone("not-a-real-zone")


def test_layer_holds_required_fields():
    layer = _make_layer()

    assert layer.kind is LayerKind.TEXT
    assert layer.zone is LayerZone.CONTENT
    assert layer.z_index == 10
    assert dict(layer.properties) == {"text": "Goal!"}


def test_layer_is_immutable():
    layer = _make_layer()

    with pytest.raises(dataclasses.FrozenInstanceError):
        layer.z_index = 99


def test_layer_properties_mapping_is_immutable():
    layer = _make_layer()

    with pytest.raises(TypeError):
        layer.properties["text"] = "changed"


def test_layer_uses_canonical_layer_kind_identity():
    layer = _make_layer()
    assert layer.kind.__class__ is LayerKind
    assert layer.kind is LayerKind.TEXT

    for member in LayerKind:
        assert member.__class__ is LayerKind


def test_layer_uses_canonical_layer_zone_identity():
    layer = _make_layer()
    assert layer.zone.__class__ is LayerZone
    assert layer.zone is LayerZone.CONTENT

    for member in LayerZone:
        assert member.__class__ is LayerZone


def test_layer_properties_are_defensively_copied():
    source = {"text": "Goal!"}
    layer = _make_layer(properties=source)

    source["text"] = "Changed outside"

    assert layer.properties["text"] == "Goal!"


def test_two_equal_layers_describe_the_same_operation():
    first = _make_layer()
    second = _make_layer()

    assert first == second


def test_layer_has_only_the_canonical_data_contract():
    fields = {field.name for field in dataclasses.fields(Layer)}

    assert fields == {
        "kind",
        "zone",
        "z_index",
        "properties",
    }

"""Tests for Renderer."""

import unittest
from typing import Any, Mapping

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.canvas import Canvas
from engine.core.context import RenderContext
from engine.core.exceptions import RenderingError
from engine.fonts.resolver import ResolvedFonts
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.core.renderer import Renderer
from engine.validation.validator import ValidatedPayload


def make_valid_render_context(render_id: str = "test-001") -> RenderContext:
    return RenderContext(
        validated_payload=ValidatedPayload(data={"template": "test"}),
        resolved_configuration=ResolvedConfiguration(data={"engine": {"backend": "pillow"}}),
        resolved_assets=ResolvedAssets(data={"logo": "logo.png"}),
        resolved_fonts=ResolvedFonts(data={"headline": "DejaVuSans-Bold.ttf"}),
        render_id=render_id,
    )


class MockCanvas(Canvas):
    def __init__(self):
        self.calls = []
        self.result = "rendered_image"

    def draw_image(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_image", properties))

    def draw_text(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_text", properties))

    def draw_shape(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_shape", properties))

    def draw_gradient(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_gradient", properties))

    def draw_texture(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_texture", properties))

    def draw_overlay(self, properties: Mapping[str, Any]) -> None:
        self.calls.append(("draw_overlay", properties))

    def get_result(self) -> Any:
        return self.result


class FailingCanvas(Canvas):
    def __init__(self, fail_on: str = "draw_image"):
        self.fail_on = fail_on
        self.calls = []

    def draw_image(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_image":
            raise RuntimeError("Canvas draw_image failed")
        self.calls.append(("draw_image", properties))

    def draw_text(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_text":
            raise RuntimeError("Canvas draw_text failed")
        self.calls.append(("draw_text", properties))

    def draw_shape(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_shape":
            raise RuntimeError("Canvas draw_shape failed")
        self.calls.append(("draw_shape", properties))

    def draw_gradient(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_gradient":
            raise RuntimeError("Canvas draw_gradient failed")
        self.calls.append(("draw_gradient", properties))

    def draw_texture(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_texture":
            raise RuntimeError("Canvas draw_texture failed")
        self.calls.append(("draw_texture", properties))

    def draw_overlay(self, properties: Mapping[str, Any]) -> None:
        if self.fail_on == "draw_overlay":
            raise RuntimeError("Canvas draw_overlay failed")
        self.calls.append(("draw_overlay", properties))

    def get_result(self) -> Any:
        return "rendered_image"


class FailingGetResultCanvas(Canvas):
    def draw_image(self, properties: Mapping[str, Any]) -> None: pass
    def draw_text(self, properties: Mapping[str, Any]) -> None: pass
    def draw_shape(self, properties: Mapping[str, Any]) -> None: pass
    def draw_gradient(self, properties: Mapping[str, Any]) -> None: pass
    def draw_texture(self, properties: Mapping[str, Any]) -> None: pass
    def draw_overlay(self, properties: Mapping[str, Any]) -> None: pass
    def get_result(self) -> Any:
        raise RuntimeError("get_result failed")


class IncompleteCanvas(Canvas):
    def draw_image(self, properties: Mapping[str, Any]) -> None: pass
    def draw_shape(self, properties: Mapping[str, Any]) -> None: pass
    def draw_gradient(self, properties: Mapping[str, Any]) -> None: pass
    def draw_texture(self, properties: Mapping[str, Any]) -> None: pass
    def draw_overlay(self, properties: Mapping[str, Any]) -> None: pass
    def get_result(self) -> Any: return "result"


class TestRenderer(unittest.TestCase):
    def setUp(self) -> None:
        self.canvas = MockCanvas()
        self.renderer = Renderer(self.canvas)
        self.context = make_valid_render_context("test-001")

    def test_render_maintains_layer_order(self) -> None:
        layers = [
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=2, properties={"text": "B"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=3, properties={"text": "C"}),
        ]
        result = self.renderer.render(self.context, layers)
        self.assertEqual(result, "rendered_image")
        self.assertEqual(self.canvas.calls[0][1]["text"], "A")
        self.assertEqual(self.canvas.calls[1][1]["text"], "B")
        self.assertEqual(self.canvas.calls[2][1]["text"], "C")

    def test_render_does_not_modify_layers(self) -> None:
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        original_properties = dict(layer.properties)
        self.renderer.render(self.context, [layer])
        self.assertEqual(dict(layer.properties), original_properties)
        self.assertEqual(layer.kind, LayerKind.TEXT)
        self.assertEqual(layer.zone, LayerZone.CONTENT)
        self.assertEqual(layer.z_index, 1)

    def test_render_dispatches_all_layer_kinds(self) -> None:
        layers = [
            Layer(kind=LayerKind.BACKGROUND, zone=LayerZone.BACKGROUND, z_index=0, properties={"bg": True}),
            Layer(kind=LayerKind.IMAGE, zone=LayerZone.CONTENT, z_index=1, properties={"img": "test.jpg"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=2, properties={"text": "Hello"}),
            Layer(kind=LayerKind.ICON, zone=LayerZone.CONTENT, z_index=3, properties={"icon": "star"}),
            Layer(kind=LayerKind.SHAPE, zone=LayerZone.CONTENT, z_index=4, properties={"shape": "circle"}),
            Layer(kind=LayerKind.GRADIENT, zone=LayerZone.BACKGROUND, z_index=5, properties={"gradient": "blue"}),
            Layer(kind=LayerKind.TEXTURE, zone=LayerZone.CONTENT, z_index=6, properties={"texture": "grain"}),
            Layer(kind=LayerKind.OVERLAY, zone=LayerZone.CONTENT, z_index=7, properties={"overlay": "glow"}),
        ]
        result = self.renderer.render(self.context, layers)
        self.assertEqual(result, "rendered_image")
        self.assertEqual([c[0] for c in self.canvas.calls], [
            "draw_image", "draw_image", "draw_text", "draw_image",
            "draw_shape", "draw_gradient", "draw_texture", "draw_overlay"
        ])

    def test_render_returns_canvas_result(self) -> None:
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        self.assertEqual(self.renderer.render(self.context, [layer]), "rendered_image")

    def test_render_unknown_layer_kind_raises_rendering_error(self) -> None:
        class UnknownKind:
            value = "UNKNOWN"
        layer = Layer(kind=UnknownKind(), zone=LayerZone.CONTENT, z_index=1, properties={})  # type: ignore
        with self.assertRaises(RenderingError):
            self.renderer.render(self.context, [layer])

    def test_render_no_layers_works(self) -> None:
        self.assertEqual(self.renderer.render(self.context, []), "rendered_image")
        self.assertEqual(len(self.canvas.calls), 0)

    def test_render_does_not_auto_reorder_layers(self) -> None:
        layers = [
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=100, properties={"text": "Z"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=50, properties={"text": "M"}),
        ]
        self.renderer.render(self.context, layers)
        self.assertEqual([c[1]["text"] for c in self.canvas.calls], ["Z", "A", "M"])

    def test_renderer_is_stateless(self) -> None:
        canvas = MockCanvas()
        renderer = Renderer(canvas)
        renderer.render(self.context, [Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"})])
        first = len(canvas.calls)
        renderer.render(self.context, [Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "B"})])
        self.assertEqual(len(canvas.calls), first + 1)

    def test_renderer_does_not_read_render_context(self) -> None:
        ctx = make_valid_render_context("test-002")
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        self.assertEqual(self.renderer.render(ctx, [layer]), "rendered_image")

    def test_renderer_uses_canonical_layer_kind_from_layer_module(self) -> None:
        from engine.layers.layer import LayerKind as RendererLayerKind
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={})
        self.assertIsInstance(layer.kind, RendererLayerKind)
        from engine.core.renderer import _LAYER_KIND_DISPATCH
        for key in _LAYER_KIND_DISPATCH.keys():
            self.assertIsInstance(key, RendererLayerKind)
        self.assertIs(layer.kind.__class__, RendererLayerKind)


class TestRendererCanvasErrors(unittest.TestCase):
    def setUp(self) -> None:
        self.context = make_valid_render_context("test-003")

    def test_canvas_operation_failure_raises_rendering_error(self) -> None:
        canvas = FailingCanvas(fail_on="draw_text")
        renderer = Renderer(canvas)
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        with self.assertRaises(RenderingError):
            renderer.render(self.context, [layer])

    def test_canvas_missing_operation_raises_rendering_error(self) -> None:
        renderer = Renderer(IncompleteCanvas())  # type: ignore
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        with self.assertRaises(RenderingError):
            renderer.render(self.context, [layer])

    def test_canvas_get_result_failure_raises_rendering_error(self) -> None:
        renderer = Renderer(FailingGetResultCanvas())  # type: ignore
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        with self.assertRaises(RenderingError):
            renderer.render(self.context, [layer])


class TestRendererProtocolCompatibility(unittest.TestCase):
    def test_renderer_matches_renderer_protocol(self) -> None:
        canvas = MockCanvas()
        renderer = Renderer(canvas)
        import inspect
        sig = inspect.signature(renderer.render)
        params = list(sig.parameters.keys())
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0], "context")
        self.assertEqual(params[1], "layers")


if __name__ == "__main__":
    unittest.main()

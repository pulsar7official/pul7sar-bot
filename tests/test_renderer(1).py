"""Tests for Renderer.

Tests the concrete Renderer implementation against the contract defined in
02_ARCHITECTURE.md Section 14 and 04_RENDERING_SPECIFICATION.md Section 11.

Scope: Renderer only. Does not test Validator, ConfigurationResolver,
AssetResolver, FontResolver, Template, Pipeline, or Exporter.
"""

import unittest
from typing import Any, Mapping

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.canvas import Canvas
from engine.core.context import RenderContext
from engine.core.exceptions import RenderingError
from engine.fonts.resolver import ResolvedFonts
from engine.layers.enums import LayerKind, LayerZone
from engine.layers.layer import Layer
from engine.core.renderer import Renderer
from engine.validation.validator import ValidatedPayload


# ============================================================================
# Helper: Valid RenderContext factory
# ============================================================================

def make_valid_render_context(render_id: str = "test-001") -> RenderContext:
    """Create a valid RenderContext with real lightweight instances."""
    return RenderContext(
        validated_payload=ValidatedPayload(data={"template": "test"}),
        resolved_configuration=ResolvedConfiguration(data={
            "engine": {"width": 640, "height": 480, "backend": "pillow"}
        }),
        resolved_assets=ResolvedAssets(data={"logo": "logo.png"}),
        resolved_fonts=ResolvedFonts(data={"headline": "DejaVuSans-Bold.ttf"}),
        render_id=render_id,
    )


# ============================================================================
# Mock Canvas
# ============================================================================

class MockCanvas(Canvas):
    """Mock Canvas for testing Renderer."""

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


class MockCanvasProvider:
    """Mock CanvasProvider for testing Renderer.

    Supports two modes:
        1. fixed_canvas mode: returns the same canvas on every create() call
        2. fresh mode (default): returns a new MockCanvas() each time
    """

    def __init__(self, fixed_canvas=None):
        self.fixed_canvas = fixed_canvas
        self.created_canvases = []
        self.should_fail = False
        self._unexpected_error = None

    def create(self, context):
        if self.should_fail:
            raise RenderingError("MockCanvasProvider failed")

        if self._unexpected_error is not None:
            raise self._unexpected_error

        if self.fixed_canvas is not None:
            return self.fixed_canvas

        new_canvas = MockCanvas()
        self.created_canvases.append(new_canvas)
        return new_canvas


# ============================================================================
# Failing Canvas implementations
# ============================================================================

class FailingCanvas(Canvas):
    """Canvas that fails on specific operations."""

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
    """Canvas that fails on get_result()."""

    def draw_image(self, properties: Mapping[str, Any]) -> None:
        pass

    def draw_text(self, properties: Mapping[str, Any]) -> None:
        pass

    def draw_shape(self, properties: Mapping[str, Any]) -> None:
        pass

    def draw_gradient(self, properties: Mapping[str, Any]) -> None:
        pass

    def draw_texture(self, properties: Mapping[str, Any]) -> None:
        pass

    def draw_overlay(self, properties: Mapping[str, Any]) -> None:
        pass

    def get_result(self) -> Any:
        raise RuntimeError("get_result failed")


# ============================================================================
# Tests
# ============================================================================

class TestRenderer(unittest.TestCase):
    """Test Renderer functionality."""

    def setUp(self) -> None:
        self.provider = MockCanvasProvider()
        self.renderer = Renderer(self.provider)
        self.context = make_valid_render_context("test-001")

    def test_render_maintains_layer_order(self) -> None:
        """Renderer should maintain layer order."""
        layers = [
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=2, properties={"text": "B"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=3, properties={"text": "C"}),
        ]

        result = self.renderer.render(self.context, layers)

        self.assertEqual(result, "rendered_image")
        canvas = self.provider.created_canvases[0]
        self.assertEqual(len(canvas.calls), 3)
        self.assertEqual(canvas.calls[0][0], "draw_text")
        self.assertEqual(canvas.calls[0][1]["text"], "A")
        self.assertEqual(canvas.calls[1][1]["text"], "B")
        self.assertEqual(canvas.calls[2][1]["text"], "C")

    def test_render_does_not_modify_layers(self) -> None:
        """Renderer should not modify layers."""
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        original_properties = dict(layer.properties)

        self.renderer.render(self.context, [layer])

        self.assertEqual(dict(layer.properties), original_properties)
        self.assertEqual(layer.kind, LayerKind.TEXT)
        self.assertEqual(layer.zone, LayerZone.CONTENT)
        self.assertEqual(layer.z_index, 1)

    def test_render_dispatches_all_layer_kinds(self) -> None:
        """Renderer should dispatch all supported LayerKind values."""
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
        canvas = self.provider.created_canvases[0]
        self.assertEqual(len(canvas.calls), 8)
        self.assertEqual(canvas.calls[0][0], "draw_image")
        self.assertEqual(canvas.calls[1][0], "draw_image")
        self.assertEqual(canvas.calls[2][0], "draw_text")
        self.assertEqual(canvas.calls[3][0], "draw_image")
        self.assertEqual(canvas.calls[4][0], "draw_shape")
        self.assertEqual(canvas.calls[5][0], "draw_gradient")
        self.assertEqual(canvas.calls[6][0], "draw_texture")
        self.assertEqual(canvas.calls[7][0], "draw_overlay")

    def test_render_returns_canvas_result(self) -> None:
        """Renderer should return the result from canvas.get_result()."""
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        result = self.renderer.render(self.context, [layer])
        self.assertEqual(result, "rendered_image")

    def test_render_unknown_layer_kind_raises_rendering_error(self) -> None:
        """Renderer should raise RenderingError for unknown LayerKind."""

        class UnknownKind:
            value = "UNKNOWN"

        layer = Layer(
            kind=UnknownKind(),  # type: ignore
            zone=LayerZone.CONTENT,
            z_index=1,
            properties={},
        )

        with self.assertRaises(RenderingError) as ctx:
            self.renderer.render(self.context, [layer])
        self.assertIn("Unknown LayerKind", str(ctx.exception))

    def test_render_no_layers_works(self) -> None:
        """Renderer should handle empty layer list."""
        result = self.renderer.render(self.context, [])
        self.assertEqual(result, "rendered_image")
        canvas = self.provider.created_canvases[0]
        self.assertEqual(len(canvas.calls), 0)

    def test_render_does_not_auto_reorder_layers(self) -> None:
        """Renderer should not auto-reorder layers."""
        layers = [
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=100, properties={"text": "Z"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"}),
            Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=50, properties={"text": "M"}),
        ]

        result = self.renderer.render(self.context, layers)

        self.assertEqual(result, "rendered_image")
        canvas = self.provider.created_canvases[0]
        self.assertEqual(canvas.calls[0][1]["text"], "Z")
        self.assertEqual(canvas.calls[1][1]["text"], "A")
        self.assertEqual(canvas.calls[2][1]["text"], "M")

    def test_renderer_is_stateless(self) -> None:
        """Renderer should not hold per-request state."""
        provider = MockCanvasProvider()
        renderer = Renderer(provider)

        # First request
        layer1 = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"})
        renderer.render(self.context, [layer1])
        first_call_count = len(provider.created_canvases[0].calls)

        # Second request (new RenderContext, same Renderer)
        context2 = make_valid_render_context("test-002")
        layer2 = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "B"})
        renderer.render(context2, [layer2])
        second_call_count = len(provider.created_canvases[1].calls)

        # Each render should have its own Canvas with its own calls
        self.assertEqual(first_call_count, 1)
        self.assertEqual(second_call_count, 1)
        # Different Canvas instances
        self.assertIsNot(provider.created_canvases[0], provider.created_canvases[1])

    def test_renderer_does_not_read_render_context(self) -> None:
        """Renderer should not read RenderContext for dispatch decisions."""
        minimal_context = make_valid_render_context("test-002")
        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})
        result = self.renderer.render(minimal_context, [layer])
        self.assertEqual(result, "rendered_image")

    def test_renderer_uses_canonical_layer_kind_from_layer_module(self) -> None:
        """VERIFY: Renderer's LayerKind is the SAME as Layer.kind's LayerKind."""
        from engine.layers.layer import LayerKind as RendererLayerKind

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={})
        self.assertIsInstance(layer.kind, RendererLayerKind)

        from engine.core.renderer import _LAYER_KIND_DISPATCH
        for key in _LAYER_KIND_DISPATCH.keys():
            self.assertIsInstance(key, RendererLayerKind)

        self.assertIs(layer.kind.__class__, RendererLayerKind)

    def test_renderer_creates_fresh_canvas_per_render(self) -> None:
        """Renderer should create a new Canvas for each render call."""
        provider = MockCanvasProvider()
        renderer = Renderer(provider)

        context1 = make_valid_render_context("test-001")
        layer1 = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "A"})
        renderer.render(context1, [layer1])

        context2 = make_valid_render_context("test-002")
        layer2 = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "B"})
        renderer.render(context2, [layer2])

        # provider.create() was called twice
        self.assertEqual(len(provider.created_canvases), 2)
        self.assertIsNot(provider.created_canvases[0], provider.created_canvases[1])

    def test_provider_rendering_error_propagates(self) -> None:
        """Provider raising RenderingError should propagate unchanged."""
        provider = MockCanvasProvider()
        provider.should_fail = True
        renderer = Renderer(provider)

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})

        with self.assertRaises(RenderingError) as ctx:
            renderer.render(self.context, [layer])
        self.assertEqual(str(ctx.exception), "MockCanvasProvider failed")

    def test_provider_unexpected_error_wrapped(self) -> None:
        """Provider raising unexpected error should be wrapped as RenderingError."""
        provider = MockCanvasProvider()
        provider._unexpected_error = RuntimeError("Unexpected provider failure")
        renderer = Renderer(provider)

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})

        with self.assertRaises(RenderingError) as ctx:
            renderer.render(self.context, [layer])
        self.assertIn("CanvasProvider failed to create Canvas", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)


class TestRendererCanvasErrors(unittest.TestCase):
    """Test Renderer error handling when Canvas fails."""

    def setUp(self) -> None:
        self.context = make_valid_render_context("test-003")

    def test_canvas_operation_failure_raises_rendering_error(self) -> None:
        """Renderer should wrap Canvas exceptions as RenderingError."""
        failing_canvas = FailingCanvas(fail_on="draw_text")
        provider = MockCanvasProvider(fixed_canvas=failing_canvas)
        renderer = Renderer(provider)

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})

        with self.assertRaises(RenderingError) as ctx:
            renderer.render(self.context, [layer])
        self.assertIn("failed for layer kind", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_canvas_missing_operation_raises_rendering_error(self) -> None:
        """Renderer should raise RenderingError if Canvas is missing an operation."""
        # Use a duck-typed object that is not a Canvas but has all methods except draw_text
        class IncompleteCanvasLike:
            def draw_image(self, properties): pass
            # draw_text is missing
            def draw_shape(self, properties): pass
            def draw_gradient(self, properties): pass
            def draw_texture(self, properties): pass
            def draw_overlay(self, properties): pass
            def get_result(self): return "result"

        incomplete = IncompleteCanvasLike()
        provider = MockCanvasProvider(fixed_canvas=incomplete)  # type: ignore
        renderer = Renderer(provider)

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})

        with self.assertRaises(RenderingError) as ctx:
            renderer.render(self.context, [layer])
        self.assertIn("does not provide required operation", str(ctx.exception))

    def test_canvas_get_result_failure_raises_rendering_error(self) -> None:
        """Renderer should raise RenderingError if canvas.get_result() fails."""
        failing_canvas = FailingGetResultCanvas()
        provider = MockCanvasProvider(fixed_canvas=failing_canvas)
        renderer = Renderer(provider)

        layer = Layer(kind=LayerKind.TEXT, zone=LayerZone.CONTENT, z_index=1, properties={"text": "test"})

        with self.assertRaises(RenderingError) as ctx:
            renderer.render(self.context, [layer])
        self.assertIn("Canvas failed to produce", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)


class TestRendererProtocolCompatibility(unittest.TestCase):
    """Test Renderer compatibility with RendererProtocol."""

    def test_renderer_matches_renderer_protocol(self) -> None:
        """Renderer should be callable with the protocol signature."""
        from engine.pipeline.pipeline import RendererProtocol

        provider = MockCanvasProvider()
        renderer = Renderer(provider)

        self.assertTrue(hasattr(renderer, "render"))
        self.assertTrue(callable(renderer.render))

        import inspect
        sig = inspect.signature(renderer.render)
        params = list(sig.parameters.keys())
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0], "context")
        self.assertEqual(params[1], "layers")


if __name__ == "__main__":
    unittest.main()

"""
PUL7SAR Visual Engine v2
engine/core/renderer.py

Renderer: transforms an ordered collection of Layer objects into a rendered
image using a backend-independent Canvas implementation.

Implements the Renderer component exactly as defined in:
    - ARCHITECTURE.md, Section 7 ("Renderer")
    - 04_RENDERING_SPECIFICATION.md, Section 11 ("Renderer Specification")

Renderer responsibilities (normative):
    - Receive RenderContext and an ordered Layer collection.
    - Dispatch each Layer to the correct Canvas drawing operation, using the
      fixed LayerKind -> Canvas operation mapping defined in
      04_RENDERING_SPECIFICATION.md, Section 11.
    - Produce a rendered image by calling canvas.get_result() exactly once,
      after all drawing operations have completed.

Renderer explicitly does NOT:
    - Resolve assets or fonts.
    - Validate payloads.
    - Export files.
    - Perform any business logic.
    - Modify Layer objects.
    - Modify RenderContext.

Renderer is stateless: it holds no per-request instance state. The Canvas
implementation is injected at construction time per Architecture Section 14.
Every call to render() performs one independent, deterministic rendering pass.
"""

from typing import Sequence

from engine.core.canvas import Canvas
from engine.core.context import RenderContext
from engine.core.exceptions import RenderingError
from engine.layers.layer import Layer, LayerKind


_LAYER_KIND_DISPATCH = {
    LayerKind.BACKGROUND: "draw_image",
    LayerKind.IMAGE: "draw_image",
    LayerKind.TEXT: "draw_text",
    LayerKind.ICON: "draw_image",
    LayerKind.SHAPE: "draw_shape",
    LayerKind.GRADIENT: "draw_gradient",
    LayerKind.TEXTURE: "draw_texture",
    LayerKind.OVERLAY: "draw_overlay",
}


class Renderer:
    """Transforms ordered Layers into pixels using a Canvas implementation."""

    def __init__(self, canvas: Canvas):
        self._canvas = canvas

    def render(
        self,
        context: RenderContext,
        layers: Sequence[Layer],
    ):
        for layer in layers:
            self._dispatch(layer)

        try:
            return self._canvas.get_result()
        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(
                f"Canvas failed to produce a render result: {exc}"
            ) from exc

    def _dispatch(self, layer: Layer):
        operation_name = _LAYER_KIND_DISPATCH.get(layer.kind)

        if operation_name is None:
            raise RenderingError(
                f"Unknown LayerKind: {layer.kind!r}. Renderer cannot "
                "dispatch this layer to a Canvas operation."
            )

        operation = getattr(self._canvas, operation_name, None)

        if operation is None:
            raise RenderingError(
                f"Canvas implementation does not provide required "
                f"operation '{operation_name}' for LayerKind "
                f"{layer.kind!r}."
            )

        try:
            operation(layer.properties)
        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(
                f"Canvas operation '{operation_name}' failed for layer "
                f"kind {layer.kind!r}: {exc}"
            ) from exc

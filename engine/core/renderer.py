"""
PUL7SAR Visual Engine v2
engine/core/renderer.py

Renderer: transforms an ordered collection of Layer objects into a rendered
image using a backend-independent Canvas implementation.

Implements the Renderer component exactly as defined in:
    - ARCHITECTURE.md, Section 7 ("Renderer")
    - 04_RENDERING_SPECIFICATION.md, Section 11 ("Renderer Specification")

Renderer responsibilities (normative):
    - Receive RenderContext, an ordered Layer collection, and a Canvas
      implementation.
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

Renderer is stateless: it holds no instance state, and every call to
render() performs one independent, deterministic rendering pass.
"""

from typing import List

from engine.core.canvas import Canvas
from engine.core.context import RenderContext
from engine.core.exceptions import RenderingError
from engine.core.layer import Layer, LayerKind


# Normative LayerKind -> Canvas operation dispatch mapping.
# Source: 04_RENDERING_SPECIFICATION.md, Section 11 ("LayerKind Dispatch").
# This mapping is fixed. It must not be extended or altered without first
# updating the Rendering Specification.
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
    """
    Transforms ordered Layers into pixels using a Canvas implementation.

    Renderer holds no state. It never resolves assets or fonts, never
    validates payloads, never exports files, and never performs business
    logic. Its only responsibility is dispatching Layers to Canvas
    operations and retrieving the final rendered result.
    """

    def render(
        self,
        context: RenderContext,
        layers: List[Layer],
        canvas: Canvas,
    ):
        """
        Perform one deterministic rendering pass.

        Args:
            context: RenderContext. Immutable render request state, as
                defined in 04_RENDERING_SPECIFICATION.md, Section 6. Never
                read for dispatch decisions and never modified.
            layers: An ordered collection of Layer instances to render, in
                the order they must be drawn. Never modified.
            canvas: A Canvas implementation exposing the drawing operations
                defined in 04_RENDERING_SPECIFICATION.md, Section 10
                (draw_image, draw_text, draw_shape, draw_gradient,
                draw_texture, draw_overlay, get_result).

        Returns:
            The rendered image, as returned by canvas.get_result().

        Raises:
            RenderingError: If any Layer has an unknown LayerKind, if a
                required Canvas operation is unavailable, or if rendering
                fails for any other reason.
        """
        for layer in layers:
            self._dispatch(layer, canvas)

        try:
            return canvas.get_result()
        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(
                f"Canvas failed to produce a render result: {exc}"
            ) from exc

    def _dispatch(self, layer: Layer, canvas: Canvas):
        """
        Dispatch a single Layer to its corresponding Canvas operation.

        Uses the fixed LayerKind -> Canvas operation mapping. Canvas
        receives only layer.properties, per
        04_RENDERING_SPECIFICATION.md, Section 11 ("Canvas must receive
        only layer.properties").

        Raises:
            RenderingError: If the Layer's kind is unknown, if the Canvas
                implementation does not provide the required operation, or
                if the operation itself raises.
        """
        operation_name = _LAYER_KIND_DISPATCH.get(layer.kind)

        if operation_name is None:
            raise RenderingError(
                f"Unknown LayerKind: {layer.kind!r}. Renderer cannot "
                "dispatch this layer to a Canvas operation."
            )

        operation = getattr(canvas, operation_name, None)

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

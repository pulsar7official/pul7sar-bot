"""DefaultTemplate — A minimal real template for production E2E rendering.

This template produces a simple visual composition:
    - A BACKGROUND layer (solid dark color)
    - A SHAPE layer (brand-colored rectangle)

The template is intentionally minimal. Its purpose is to prove the
complete rendering pipeline works end-to-end, not to produce production
visual designs.

The template uses only Layer properties supported by PillowCanvas Phase 9:
    - BACKGROUND: image (PillowCanvas expects preloaded image)
    - SHAPE: shape_type, x, y, width, height, color, outline_color
"""

from typing import Sequence

from engine.core.context import RenderContext
from engine.core.exceptions import TemplateError
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.base import BaseTemplate


class DefaultTemplate(BaseTemplate):
    """Minimal real template for E2E infrastructure validation.

    Produces:
        1. BACKGROUND layer — solid dark rectangle
        2. SHAPE layer — brand-colored rounded rectangle

    This template does NOT use external assets or fonts.
    """

    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        """Generate Layers for the DefaultTemplate.

        Args:
            render_context: Immutable rendering request state.

        Returns:
            Sequence[Layer]: Ordered layers for rendering.

        Raises:
            TemplateError: If the template cannot be executed.
        """
        try:
            # Get dimensions from RenderContext to size the background
            width, height = self._get_dimensions(render_context)

            # Layer 1: BACKGROUND — dark solid color
            # Using IMAGE with a preloaded image is not practical for E2E without assets.
            # PillowCanvas draws BACKGROUND via draw_image which expects an image.
            # For Phase 9 PillowCanvas, BACKGROUND maps to draw_image.
            # Since we don't have a preloaded background image, use SHAPE for background.
            # The canvas background is set at Canvas construction (transparent by default).
            # So we draw a shape to fill the entire canvas as the background.

            background_layer = Layer(
                kind=LayerKind.SHAPE,
                zone=LayerZone.BACKGROUND,
                z_index=0,
                properties={
                    "shape_type": "rectangle",
                    "x": 0,
                    "y": 0,
                    "width": width,
                    "height": height,
                    "color": (20, 30, 50, 255),  # Dark blue-black
                },
            )

            # Layer 2: SHAPE — brand-colored rectangle overlay
            accent_layer = Layer(
                kind=LayerKind.SHAPE,
                zone=LayerZone.CONTENT,
                z_index=1,
                properties={
                    "shape_type": "rectangle",
                    "x": int(width * 0.1),
                    "y": int(height * 0.6),
                    "width": int(width * 0.8),
                    "height": int(height * 0.25),
                    "color": (0, 112, 255, 255),  # Electric Blue (#0070FF)
                    "outline_color": (255, 215, 0, 200),  # Gold outline
                    "outline_width": 3,
                },
            )

            return [background_layer, accent_layer]

        except Exception as exc:
            raise TemplateError(
                f"DefaultTemplate execution failed: {exc}"
            ) from exc

    @staticmethod
    def _get_dimensions(render_context: RenderContext) -> tuple[int, int]:
        """Extract dimensions from RenderContext.

        Priority order:
            1. render_context.canvas_information["width"/"height"]
            2. render_context.resolved_configuration.data["engine"]["width"/"height"]

        Returns:
            tuple[int, int]: (width, height)

        Raises:
            TemplateError: If valid dimensions cannot be obtained.
        """
        # Try canvas_information
        canvas_info = dict(render_context.canvas_information)
        if "width" in canvas_info and "height" in canvas_info:
            try:
                width = int(canvas_info["width"])
                height = int(canvas_info["height"])
                if width > 0 and height > 0:
                    return width, height
            except (ValueError, TypeError):
                pass

        # Fallback to resolved_configuration
        config_data = dict(render_context.resolved_configuration.data)
        engine_config = config_data.get("engine", {})
        if isinstance(engine_config, dict):
            try:
                width = int(engine_config.get("width", 0))
                height = int(engine_config.get("height", 0))
                if width > 0 and height > 0:
                    return width, height
            except (ValueError, TypeError):
                pass

        raise TemplateError(
            "Cannot determine canvas dimensions for DefaultTemplate"
        )

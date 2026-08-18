"""CanvasProvider — Creates fresh Canvas instances per render.

Per Phase 12 architecture:
    - Canvas is PER-RENDER (fresh for each render() call)
    - Dimensions come from RenderContext (single source of truth)
    - Provider is application-scoped, creates request-scoped Canvas

The provider does NOT resolve assets, fonts, or business logic.
It only creates Canvas instances with the correct dimensions.
"""

from engine.canvas.pillow import PillowCanvas
from engine.core.canvas import Canvas
from engine.core.context import RenderContext
from engine.core.exceptions import RenderingError


class CanvasProvider:
    """Creates Canvas instances for rendering."""

    def create(self, render_context: RenderContext) -> Canvas:
        """Create a fresh Canvas for the given render context.

        Args:
            render_context: Immutable rendering request state.

        Returns:
            Canvas: A fresh Canvas instance ready for drawing.

        Raises:
            RenderingError: If dimensions cannot be determined.
        """
        raise NotImplementedError


class PillowCanvasProvider(CanvasProvider):
    """Concrete CanvasProvider using PillowCanvas.

    Dimensions are derived from RenderContext:
        1. Primary: render_context.canvas_information["width"/"height"]
        2. Fallback: render_context.resolved_configuration.data["engine"]["width"/"height"]

    Every call to create() returns a NEW PillowCanvas instance.
    This prevents pixel state from leaking between renders.
    """

    def create(self, render_context: RenderContext) -> PillowCanvas:
        """Create a fresh PillowCanvas for the given render context.

        Args:
            render_context: Immutable rendering request state.

        Returns:
            PillowCanvas: A fresh PillowCanvas instance.

        Raises:
            RenderingError: If valid dimensions cannot be obtained.
        """
        width, height = self._get_dimensions(render_context)

        if width <= 0 or height <= 0:
            raise RenderingError(
                f"Invalid canvas dimensions: {width}x{height}"
            )

        try:
            return PillowCanvas(width, height)
        except Exception as exc:
            raise RenderingError(
                f"Failed to create PillowCanvas: {exc}"
            ) from exc

    @staticmethod
    def _get_dimensions(render_context: RenderContext) -> tuple[int, int]:
        """Extract dimensions from RenderContext.

        Priority order:
            1. render_context.canvas_information["width"/"height"]
               (if both are positive ints)
            2. render_context.resolved_configuration.data["engine"]["width"/"height"]
               (if both are positive ints)

        Returns:
            tuple[int, int]: (width, height)

        Raises:
            RenderingError: If valid dimensions cannot be obtained.
        """
        # Try canvas_information first
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

        raise RenderingError(
            "Cannot determine canvas dimensions: no valid width/height found "
            "in canvas_information or resolved_configuration.engine"
        )

"""QualityVerifier — Structural/output integrity verification.

Per 02_ARCHITECTURE.md, Section 15, Step 6 and 04_RENDERING_SPECIFICATION.md,
Section 12:

    QualityVerifier
        Receives:  RenderContext, Rendered Image
        Verifies:  - rendered result exists
                   - dimensions match resolved Canvas information
                   - image is structurally valid and decodable
                   - image format/mode is compatible
        Success:   Returns the EXACT SAME image object unchanged
        Failure:   Raises QualityVerificationError

QualityVerifier is structurally equivalent in status to Renderer and
Exporter. It is independent from Renderer, Canvas, Exporter, and Pipeline.

This implementation is Phase 10. It performs structural checks only.
No aesthetic, branding, content, or AI evaluation is performed.
"""

from __future__ import annotations

from typing import Any

from PIL import Image

from engine.core.context import RenderContext
from engine.core.exceptions import QualityVerificationError


class QualityVerifier:
    """Concrete QualityVerifier implementation.

    Verifies structural/output integrity of rendered images.

    Stateless: holds no per-request state. Every call to verify()
    performs one independent verification pass.

    Does NOT:
        - render pixels
        - draw anything
        - access Canvas
        - modify the rendered image
        - modify RenderContext
        - resolve assets or fonts
        - execute Templates
        - export files
        - validate raw requests
        - evaluate aesthetics, branding, or content
    """

    def verify(self, render_context: RenderContext, rendered_image: Any) -> Any:
        """Verify structural integrity of the rendered image.

        Args:
            render_context: Immutable rendering request state.
            rendered_image: The image produced by Renderer.

        Returns:
            The exact same rendered image object, unchanged.

        Raises:
            QualityVerificationError: If any structural verification fails.
        """
        # 1. Verify rendered result exists
        if rendered_image is None:
            raise QualityVerificationError(
                "Rendered result is None: no image was produced"
            )

        # 2. Verify rendered result is a PIL Image
        if not isinstance(rendered_image, Image.Image):
            raise QualityVerificationError(
                f"Rendered result must be a PIL.Image.Image, got {type(rendered_image).__name__}"
            )

        # 3. Verify image has valid dimensions
        #    Accessing .size on an already-created in-memory PIL Image
        #    is sufficient structural verification for Phase 10.
        try:
            width, height = rendered_image.size
        except Exception as exc:
            raise QualityVerificationError(
                f"Rendered image is not structurally valid: {exc}"
            ) from exc

        if width <= 0 or height <= 0:
            raise QualityVerificationError(
                f"Rendered image has invalid dimensions: {width}x{height}"
            )

        # 4. Verify dimensions match expected dimensions from configuration
        expected_width, expected_height = self._get_expected_dimensions(render_context)
        if expected_width is not None and expected_height is not None:
            if width != expected_width or height != expected_height:
                raise QualityVerificationError(
                    f"Rendered image dimensions {width}x{height} do not match "
                    f"expected dimensions {expected_width}x{expected_height}"
                )

        # 5. Verify image mode is a recognized Pillow mode
        mode = rendered_image.mode
        if mode not in Image.MODES:
            raise QualityVerificationError(
                f"Rendered image has invalid mode: {mode}"
            )

        # 6. Return the exact same image object unchanged
        return rendered_image

    @staticmethod
    def _get_expected_dimensions(render_context: RenderContext) -> tuple[int | None, int | None]:
        """Extract expected dimensions from RenderContext.

        Priority order:
            1. render_context.canvas_information["width"/"height"]
               (if both are positive ints)
            2. render_context.resolved_configuration.data["engine"]["width"/"height"]
               (if both are positive ints)
            3. None, None (no expectation)

        Returns:
            tuple[int | None, int | None]: (expected_width, expected_height)
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
                # Malformed values: treat as unavailable
                pass

        # Try resolved_configuration
        config_data = dict(render_context.resolved_configuration.data)
        engine_config = config_data.get("engine", {})
        if isinstance(engine_config, dict):
            try:
                width = int(engine_config.get("width", 0))
                height = int(engine_config.get("height", 0))
                if width > 0 and height > 0:
                    return width, height
            except (ValueError, TypeError):
                # Malformed values: treat as unavailable
                pass

        return None, None

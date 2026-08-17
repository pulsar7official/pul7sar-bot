"""PillowCanvas — Concrete Canvas implementation using Pillow.

Implements the Canvas abstraction defined in engine/core/canvas.py
using the Python Imaging Library (Pillow).

Per 04_RENDERING_SPECIFICATION.md, Sections 10-11:
    - Canvas exposes six primitive drawing operations
    - Canvas is backend-independent
    - Canvas never knows templates, sports, or branding
    - Canvas raises RenderingError on failure
    - Backend-specific exceptions never escape the Canvas boundary

Per 02_ARCHITECTURE.md, Section 13:
    - Canvas is only an abstraction
    - Concrete implementations are backend adapters
    - Canvas never contains business logic
    - Canvas never knows football or branding rules

CRITICAL: This implementation DOES NOT resolve assets, fonts, or files.
All images, textures, and fonts must be pre-resolved by the appropriate
resolver subsystems (AssetResolver, FontResolver) and passed as
preloaded objects in Layer properties.
"""

from __future__ import annotations

from typing import Any, Mapping, Tuple

from PIL import Image, ImageDraw, ImageFont

from engine.core.canvas import Canvas
from engine.core.exceptions import RenderingError


# Try to import BaseImageFont for proper type checking, but don't require it
try:
    from PIL.ImageFont import BaseImageFont
except ImportError:
    BaseImageFont = None


class PillowCanvas(Canvas):
    """Pillow-based Canvas implementation.

    Creates and manages an in-memory RGBA image. Each drawing operation
    modifies the internal image. get_result() returns the completed image.

    The Canvas holds internal rendering state (the image). This is
    acceptable per Architecture Section 13: "Canvas implementations may
    maintain internal rendering state."
    """

    def __init__(self, width: int, height: int, background_color: Tuple[int, int, int, int] = (0, 0, 0, 0)):
        """Initialize a PillowCanvas with the given dimensions.

        Args:
            width: Canvas width in pixels.
            height: Canvas height in pixels.
            background_color: RGBA tuple for the background (default: transparent black).

        Raises:
            RenderingError: If the canvas cannot be created.
        """
        try:
            self._image = Image.new("RGBA", (width, height), background_color)
            self._draw = ImageDraw.Draw(self._image)
            self._width = width
            self._height = height
            self._background_color = background_color
        except Exception as exc:
            raise RenderingError(f"Failed to create PillowCanvas: {exc}") from exc

    def get_result(self) -> Image.Image:
        """Return the completed rendered image.

        Returns:
            PIL.Image.Image: The in-memory RGBA image.

        Raises:
            RenderingError: If the image is not available.
        """
        if self._image is None:
            raise RenderingError("PillowCanvas has no rendered image to return")
        return self._image

    # =========================================================================
    # Drawing Operations
    # =========================================================================

    def draw_image(self, properties: Mapping[str, Any]) -> None:
        """Draw an image onto the canvas.

        Supported properties:
            - image (PIL.Image.Image): Preloaded RGBA image. REQUIRED.
            - x (int): X position (default: 0).
            - y (int): Y position (default: 0).
            - width (int): Target width (optional, maintains aspect ratio).
            - height (int): Target height (optional, maintains aspect ratio).
            - opacity (float): Opacity from 0.0 to 1.0 (default: 1.0).

        Raises:
            RenderingError: If the image cannot be drawn.
        """
        try:
            img = properties.get("image")
            if img is None:
                raise RenderingError("draw_image requires 'image' (PIL.Image.Image) in properties")

            if not isinstance(img, Image.Image):
                raise RenderingError(f"draw_image 'image' must be a PIL.Image.Image, got {type(img)}")

            img = img.convert("RGBA")

            x = properties.get("x", 0)
            y = properties.get("y", 0)
            width = properties.get("width")
            height = properties.get("height")
            opacity = properties.get("opacity", 1.0)

            # Validate opacity
            if opacity < 0.0 or opacity > 1.0:
                raise RenderingError(
                    f"draw_image 'opacity' must be between 0.0 and 1.0, got {opacity}"
                )

            # Resize if dimensions provided
            if width is not None and height is not None:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            elif width is not None:
                ratio = width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            elif height is not None:
                ratio = height / img.height
                new_width = int(img.width * ratio)
                img = img.resize((new_width, height), Image.Resampling.LANCZOS)

            # Apply opacity
            if opacity < 1.0:
                alpha = img.getchannel("A")
                alpha = alpha.point(lambda a: int(a * opacity))
                img.putalpha(alpha)

            # Composite onto canvas
            self._image.alpha_composite(img, (x, y))

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_image failed: {exc}") from exc

    def draw_text(self, properties: Mapping[str, Any]) -> None:
        """Draw text onto the canvas.

        Supported properties:
            - text (str): The text to draw. REQUIRED.
            - x (int): X position (default: 0).
            - y (int): Y position (default: 0).
            - font (ImageFont.Font): Preloaded Pillow font object. REQUIRED.
            - color (tuple): RGBA text color (default: (255, 255, 255, 255)).

        The font object must be a valid Pillow font type (e.g., FreeTypeFont,
        ImageFont, or any object compatible with ImageDraw.text()).

        Raises:
            RenderingError: If the text cannot be drawn.
        """
        try:
            text = properties.get("text")
            if text is None:
                raise RenderingError("draw_text requires 'text' in properties")

            font = properties.get("font")
            if font is None:
                raise RenderingError("draw_text requires 'font' (PIL ImageFont object) in properties")

            # Validate font is a valid Pillow font object.
            # Uses capability-based checking: valid fonts have getmask().
            if not self._is_valid_pillow_font(font):
                raise RenderingError(
                    f"draw_text 'font' must be a valid PIL ImageFont object, got {type(font)}"
                )

            x = properties.get("x", 0)
            y = properties.get("y", 0)
            color = properties.get("color", (255, 255, 255, 255))

            draw = ImageDraw.Draw(self._image)
            draw.text((x, y), text, font=font, fill=color)

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_text failed: {exc}") from exc

    def _is_valid_pillow_font(self, font: Any) -> bool:
        """Check if a font object is a valid Pillow font.

        Uses a capability-based check: valid Pillow fonts have getmask()
        (the minimum method required for ImageDraw.text() to function).
        If BaseImageFont is available, use it for a more precise check.
        """
        # If BaseImageFont is available, use it for the check
        if BaseImageFont is not None:
            if isinstance(font, BaseImageFont):
                return True

        # Capability check: valid Pillow font objects have getmask()
        # This is the minimum method required for ImageDraw.text()
        if hasattr(font, "getmask"):
            return True

        return False

    def draw_shape(self, properties: Mapping[str, Any]) -> None:
        """Draw a shape onto the canvas.

        Supported properties:
            - shape_type (str): "rectangle" or "circle". REQUIRED.
            - x (int): X position (default: 0).
            - y (int): Y position (default: 0).
            - width (int): Width of the shape (default: 100).
            - height (int): Height of the shape (default: 100).
            - color (tuple): RGBA fill color.
            - outline_color (tuple): RGBA outline color.
            - outline_width (int): Outline width (default: 1).

        Raises:
            RenderingError: If the shape cannot be drawn.
        """
        try:
            shape_type = properties.get("shape_type")
            if shape_type is None:
                raise RenderingError("draw_shape requires 'shape_type' in properties")

            x = properties.get("x", 0)
            y = properties.get("y", 0)
            width = properties.get("width", 100)
            height = properties.get("height", 100)
            color = properties.get("color")
            outline_color = properties.get("outline_color")
            outline_width = properties.get("outline_width", 1)

            draw = ImageDraw.Draw(self._image)

            if shape_type == "rectangle":
                draw.rectangle(
                    (x, y, x + width, y + height),
                    fill=color,
                    outline=outline_color,
                    width=outline_width,
                )
            elif shape_type == "circle":
                draw.ellipse(
                    (x, y, x + width, y + height),
                    fill=color,
                    outline=outline_color,
                    width=outline_width,
                )
            else:
                raise RenderingError(
                    f"draw_shape unsupported shape_type: {shape_type}. "
                    "Supported: 'rectangle', 'circle'"
                )

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_shape failed: {exc}") from exc

    def draw_gradient(self, properties: Mapping[str, Any]) -> None:
        """Draw a vertical linear gradient onto the canvas.

        Supported properties:
            - color1 (tuple): RGBA start color (top). REQUIRED.
            - color2 (tuple): RGBA end color (bottom). REQUIRED.
            - width (int): Width of gradient area (default: canvas width).
            - height (int): Height of gradient area (default: canvas height).

        Note: Phase 9 supports only vertical linear gradients (top to bottom).
        The first row exactly equals color1. The last row exactly equals color2.

        Raises:
            RenderingError: If the gradient cannot be drawn.
        """
        try:
            color1 = properties.get("color1")
            color2 = properties.get("color2")

            if color1 is None:
                raise RenderingError("draw_gradient requires 'color1' (RGBA tuple)")
            if color2 is None:
                raise RenderingError("draw_gradient requires 'color2' (RGBA tuple)")

            width = properties.get("width", self._width)
            height = properties.get("height", self._height)

            # Validate colors
            for color in (color1, color2):
                if not isinstance(color, tuple) or len(color) < 3:
                    raise RenderingError(f"Gradient colors must be RGBA tuples, got {color}")

            # Convert 3-tuples to RGBA
            c1 = color1 if len(color1) == 4 else (*color1, 255)
            c2 = color2 if len(color2) == 4 else (*color2, 255)

            # Create gradient image
            grad_img = Image.new("RGBA", (width, height))

            if height <= 1:
                # Single row - use color1 only
                for x in range(width):
                    grad_img.putpixel((x, 0), c1)
            else:
                # Vertical linear gradient: t = y / (height - 1)
                # First row: t=0 → color1, Last row: t=1 → color2
                for y in range(height):
                    t = y / (height - 1)
                    r = int(c1[0] + (c2[0] - c1[0]) * t)
                    g = int(c1[1] + (c2[1] - c1[1]) * t)
                    b = int(c1[2] + (c2[2] - c1[2]) * t)
                    a = int(c1[3] + (c2[3] - c1[3]) * t)
                    for x in range(width):
                        grad_img.putpixel((x, y), (r, g, b, a))

            self._image.alpha_composite(grad_img, (0, 0))

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_gradient failed: {exc}") from exc

    def draw_texture(self, properties: Mapping[str, Any]) -> None:
        """Draw a texture onto the canvas.

        Supported properties:
            - texture (PIL.Image.Image): Preloaded RGBA texture image. REQUIRED.
            - x (int): X position (default: 0).
            - y (int): Y position (default: 0).
            - width (int): Target width (optional).
            - height (int): Target height (optional).
            - repeat (bool): Whether to tile the texture (default: False).

        Raises:
            RenderingError: If the texture cannot be drawn.
        """
        try:
            texture = properties.get("texture")
            if texture is None:
                raise RenderingError("draw_texture requires 'texture' (PIL.Image.Image) in properties")

            if not isinstance(texture, Image.Image):
                raise RenderingError(f"draw_texture 'texture' must be a PIL.Image.Image, got {type(texture)}")

            texture = texture.convert("RGBA")

            x = properties.get("x", 0)
            y = properties.get("y", 0)
            width = properties.get("width", texture.width)
            height = properties.get("height", texture.height)
            repeat = properties.get("repeat", False)

            # Resize if needed
            if width != texture.width or height != texture.height:
                texture = texture.resize((width, height), Image.Resampling.LANCZOS)

            if repeat:
                for tx in range(0, self._width, width):
                    for ty in range(0, self._height, height):
                        self._image.alpha_composite(texture, (tx, ty))
            else:
                self._image.alpha_composite(texture, (x, y))

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_texture failed: {exc}") from exc

    def draw_overlay(self, properties: Mapping[str, Any]) -> None:
        """Draw a color overlay onto the canvas.

        Supported properties:
            - overlay_type (str): "color_overlay" only. REQUIRED.
            - x (int): X position (default: 0).
            - y (int): Y position (default: 0).
            - width (int): Width of overlay (default: canvas width).
            - height (int): Height of overlay (default: canvas height).
            - color (tuple): RGBA overlay color. REQUIRED.
            - opacity (float): Opacity from 0.0 to 1.0 (default: 1.0).

        Raises:
            RenderingError: If the overlay cannot be drawn.
        """
        try:
            overlay_type = properties.get("overlay_type")
            if overlay_type is None:
                raise RenderingError("draw_overlay requires 'overlay_type' in properties")

            if overlay_type != "color_overlay":
                raise RenderingError(
                    f"draw_overlay unsupported overlay_type: {overlay_type}. "
                    "Phase 9 supports only 'color_overlay'"
                )

            x = properties.get("x", 0)
            y = properties.get("y", 0)
            width = properties.get("width", self._width)
            height = properties.get("height", self._height)
            color = properties.get("color")
            opacity = properties.get("opacity", 1.0)

            if color is None:
                raise RenderingError("draw_overlay requires 'color' (RGBA tuple)")

            if not isinstance(color, tuple) or len(color) < 3:
                raise RenderingError(f"draw_overlay color must be an RGBA tuple, got {color}")

            if opacity < 0.0 or opacity > 1.0:
                raise RenderingError(
                    f"draw_overlay opacity must be between 0.0 and 1.0, got {opacity}"
                )

            # Convert 3-tuple to RGBA
            overlay_color = color if len(color) == 4 else (*color, 255)

            final_color = (
                overlay_color[0],
                overlay_color[1],
                overlay_color[2],
                int(overlay_color[3] * opacity),
            )

            overlay_img = Image.new("RGBA", (width, height), final_color)
            self._image.alpha_composite(overlay_img, (x, y))

        except RenderingError:
            raise
        except Exception as exc:
            raise RenderingError(f"draw_overlay failed: {exc}") from exc
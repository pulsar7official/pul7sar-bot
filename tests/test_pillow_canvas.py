"""Tests for PillowCanvas.

Tests the concrete PillowCanvas implementation against the Canvas contract.
Verifies that PillowCanvas correctly implements all six Canvas operations
and get_result().
"""

import unittest

from PIL import Image, ImageDraw, ImageFont

from engine.canvas.pillow import PillowCanvas
from engine.core.exceptions import RenderingError


class TestPillowCanvas(unittest.TestCase):
    """Test PillowCanvas functionality."""

    def setUp(self) -> None:
        self.canvas = PillowCanvas(640, 480, (20, 30, 40, 255))

    def test_canvas_construction(self) -> None:
        """Canvas should create an image with correct dimensions."""
        result = self.canvas.get_result()
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (640, 480))
        self.assertEqual(result.mode, "RGBA")
        pixel = result.getpixel((0, 0))
        self.assertEqual(pixel, (20, 30, 40, 255))

    def test_get_result_returns_image(self) -> None:
        """get_result() should return a PIL Image."""
        result = self.canvas.get_result()
        self.assertIsInstance(result, Image.Image)

    def test_get_result_raises_on_failure(self) -> None:
        """get_result() should raise RenderingError if image is None."""
        canvas = PillowCanvas(100, 100)
        canvas._image = None
        with self.assertRaises(RenderingError):
            canvas.get_result()

    def test_draw_image(self) -> None:
        """draw_image() should draw a preloaded image."""
        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        self.canvas.draw_image({"image": img, "x": 10, "y": 10})
        result = self.canvas.get_result()
        pixel = result.getpixel((35, 35))
        self.assertEqual(pixel, (255, 0, 0, 255))

    def test_draw_image_with_resize(self) -> None:
        """draw_image() should resize the image."""
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        self.canvas.draw_image({"image": img, "x": 0, "y": 0, "width": 50, "height": 50})
        result = self.canvas.get_result()
        pixel = result.getpixel((25, 25))
        self.assertEqual(pixel[:3], (255, 0, 0))

    def test_draw_image_with_opacity(self) -> None:
        """draw_image() should apply opacity with correct RGB blending."""
        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        self.canvas.draw_image({"image": img, "x": 10, "y": 10, "opacity": 0.5})

        result = self.canvas.get_result()
        pixel = result.getpixel((35, 35))

        # Over opaque background, result should be opaque (alpha=255)
        self.assertEqual(pixel[3], 255)

        # Expected: 50% blend of (255,0,0) and (20,30,40)
        self.assertAlmostEqual(pixel[0], 138, delta=1)
        self.assertAlmostEqual(pixel[1], 15, delta=1)
        self.assertAlmostEqual(pixel[2], 20, delta=1)

    def test_draw_image_opacity_negative_raises(self) -> None:
        """draw_image() should raise RenderingError for negative opacity."""
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        with self.assertRaises(RenderingError):
            self.canvas.draw_image({"image": img, "opacity": -0.5})

    def test_draw_image_opacity_above_1_raises(self) -> None:
        """draw_image() should raise RenderingError for opacity > 1."""
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        with self.assertRaises(RenderingError):
            self.canvas.draw_image({"image": img, "opacity": 1.5})

    def test_draw_image_missing_image(self) -> None:
        """draw_image() should raise RenderingError if 'image' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_image({"x": 0, "y": 0})

    def test_draw_image_invalid_image_type(self) -> None:
        """draw_image() should raise RenderingError if 'image' is not PIL Image."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_image({"image": "not_an_image", "x": 0, "y": 0})

    def test_draw_text_with_default_font(self) -> None:
        """draw_text() should accept ImageFont.load_default() font."""
        font = ImageFont.load_default()
        self.canvas.draw_text({
            "text": "Hello, World!",
            "x": 100,
            "y": 100,
            "font": font,
            "color": (255, 255, 255, 255),
        })
        result = self.canvas.get_result()
        self.assertIsInstance(result, Image.Image)

    def test_draw_text_font_object_with_getmask_only(self) -> None:
        """draw_text() should accept a font-like object with getmask()."""

        # Create a minimal font-like object that only has getmask()
        class MinimalFont:
            def getmask(self, *args, **kwargs):
                return None

        font = MinimalFont()
        self.canvas.draw_text({
            "text": "Test",
            "x": 10,
            "y": 10,
            "font": font,
            "color": (255, 255, 255, 255),
        })
        # If we get here, the font was accepted.
        # The actual drawing may fail if the object isn't fully compatible,
        # but the validation should accept it based on capability.
        result = self.canvas.get_result()
        self.assertIsInstance(result, Image.Image)

    def test_draw_text_missing_text(self) -> None:
        """draw_text() should raise RenderingError if 'text' is missing."""
        font = ImageFont.load_default()
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({"x": 100, "y": 100, "font": font})

    def test_draw_text_missing_font(self) -> None:
        """draw_text() should raise RenderingError if 'font' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({"text": "Test", "x": 0, "y": 0})

    def test_draw_text_invalid_font_type_string(self) -> None:
        """draw_text() should raise RenderingError if font is a string."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({
                "text": "Test",
                "x": 0,
                "y": 0,
                "font": "not_a_font",
            })

    def test_draw_text_invalid_font_type_int(self) -> None:
        """draw_text() should raise RenderingError if font is an int."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({
                "text": "Test",
                "x": 0,
                "y": 0,
                "font": 12345,
            })

    def test_draw_text_invalid_font_type_dict(self) -> None:
        """draw_text() should raise RenderingError if font is a dict."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({
                "text": "Test",
                "x": 0,
                "y": 0,
                "font": {"not": "a font"},
            })

    def test_draw_text_font_object_without_getmask_rejected(self) -> None:
        """draw_text() should reject objects without getmask()."""

        class InvalidFont:
            def some_other_method(self):
                pass

        font = InvalidFont()
        with self.assertRaises(RenderingError):
            self.canvas.draw_text({
                "text": "Test",
                "x": 0,
                "y": 0,
                "font": font,
            })

    def test_draw_shape_rectangle(self) -> None:
        """draw_shape() should draw a rectangle."""
        self.canvas.draw_shape({
            "shape_type": "rectangle",
            "x": 50,
            "y": 50,
            "width": 100,
            "height": 80,
            "color": (0, 255, 0, 255),
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((75, 75))
        self.assertEqual(pixel, (0, 255, 0, 255))

    def test_draw_shape_circle(self) -> None:
        """draw_shape() should draw a circle."""
        self.canvas.draw_shape({
            "shape_type": "circle",
            "x": 50,
            "y": 50,
            "width": 80,
            "height": 80,
            "color": (0, 0, 255, 255),
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((75, 75))
        self.assertEqual(pixel, (0, 0, 255, 255))

    def test_draw_shape_with_outline(self) -> None:
        """draw_shape() should draw with outline."""
        self.canvas.draw_shape({
            "shape_type": "rectangle",
            "x": 50,
            "y": 50,
            "width": 100,
            "height": 80,
            "color": (0, 255, 0, 255),
            "outline_color": (255, 0, 0, 255),
            "outline_width": 3,
        })
        result = self.canvas.get_result()
        center = result.getpixel((100, 90))
        self.assertEqual(center[:3], (0, 255, 0))
        edge = result.getpixel((50, 50))
        self.assertGreater(edge[0], 0)

    def test_draw_shape_missing_type(self) -> None:
        """draw_shape() should raise RenderingError if 'shape_type' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_shape({"x": 0, "y": 0, "width": 100, "height": 100})

    def test_draw_shape_unsupported(self) -> None:
        """draw_shape() should raise RenderingError for unsupported shapes."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_shape({
                "shape_type": "hexagon",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            })

    def test_draw_gradient_vertical(self) -> None:
        """draw_gradient() should draw a vertical linear gradient with exact endpoints."""
        self.canvas.draw_gradient({
            "color1": (255, 0, 0, 255),
            "color2": (0, 0, 255, 255),
            "width": 200,
            "height": 200,
        })
        result = self.canvas.get_result()

        # First row exactly color1
        top = result.getpixel((100, 0))
        self.assertEqual(top, (255, 0, 0, 255))

        # Last row exactly color2
        bottom = result.getpixel((100, 199))
        self.assertEqual(bottom, (0, 0, 255, 255))

        # Middle is blended
        middle = result.getpixel((100, 100))
        self.assertAlmostEqual(middle[0], 128, delta=5)
        self.assertAlmostEqual(middle[2], 128, delta=5)

    def test_draw_gradient_single_row(self) -> None:
        """draw_gradient() should handle height=1 correctly."""
        self.canvas.draw_gradient({
            "color1": (255, 0, 0, 255),
            "color2": (0, 0, 255, 255),
            "width": 100,
            "height": 1,
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((50, 0))
        self.assertEqual(pixel, (255, 0, 0, 255))

    def test_draw_gradient_missing_color1(self) -> None:
        """draw_gradient() should raise RenderingError if 'color1' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_gradient({"color2": (0, 0, 255, 255)})

    def test_draw_gradient_missing_color2(self) -> None:
        """draw_gradient() should raise RenderingError if 'color2' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_gradient({"color1": (255, 0, 0, 255)})

    def test_draw_gradient_with_3_tuple_colors(self) -> None:
        """draw_gradient() should accept 3-tuple colors (auto-add alpha=255)."""
        self.canvas.draw_gradient({
            "color1": (255, 0, 0),
            "color2": (0, 0, 255),
            "width": 100,
            "height": 100,
        })
        result = self.canvas.get_result()
        top = result.getpixel((50, 0))
        self.assertEqual(top, (255, 0, 0, 255))

    def test_draw_texture_opaque(self) -> None:
        """draw_texture() should draw a fully opaque texture."""
        texture = Image.new("RGBA", (30, 30), (128, 128, 128, 255))
        self.canvas.draw_texture({"texture": texture, "x": 10, "y": 10})
        result = self.canvas.get_result()
        pixel = result.getpixel((25, 25))
        # Fully opaque source over opaque destination → RGB unchanged
        self.assertEqual(pixel, (128, 128, 128, 255))

    def test_draw_texture_with_alpha_blending(self) -> None:
        """draw_texture() should blend semi-transparent textures correctly."""
        texture = Image.new("RGBA", (30, 30), (128, 128, 128, 200))
        self.canvas.draw_texture({"texture": texture, "x": 10, "y": 10})
        result = self.canvas.get_result()
        pixel = result.getpixel((25, 25))

        # Over opaque background (20,30,40) with texture alpha=200 (~78%)
        # Expected RGB: 128*0.78 + 20*0.22 = 104, 128*0.78 + 30*0.22 = 106, 128*0.78 + 40*0.22 = 108
        self.assertAlmostEqual(pixel[0], 104, delta=2)
        self.assertAlmostEqual(pixel[1], 106, delta=2)
        self.assertAlmostEqual(pixel[2], 108, delta=2)
        self.assertEqual(pixel[3], 255)  # Opaque destination

    def test_draw_texture_with_resize(self) -> None:
        """draw_texture() should resize the texture."""
        texture = Image.new("RGBA", (20, 20), (128, 128, 128, 255))
        self.canvas.draw_texture({
            "texture": texture,
            "x": 0,
            "y": 0,
            "width": 40,
            "height": 40,
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((20, 20))
        self.assertEqual(pixel, (128, 128, 128, 255))

    def test_draw_texture_with_repeat(self) -> None:
        """draw_texture() should repeat texture if repeat=True."""
        texture = Image.new("RGBA", (10, 10), (255, 200, 100, 255))
        self.canvas.draw_texture({
            "texture": texture,
            "repeat": True,
            "width": 10,
            "height": 10,
        })
        result = self.canvas.get_result()
        tile1 = result.getpixel((5, 5))
        tile2 = result.getpixel((15, 5))
        self.assertEqual(tile1, tile2)

    def test_draw_texture_missing_texture(self) -> None:
        """draw_texture() should raise RenderingError if 'texture' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_texture({"x": 0, "y": 0})

    def test_draw_texture_invalid_texture_type(self) -> None:
        """draw_texture() should raise RenderingError if texture is not PIL Image."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_texture({"texture": "not_a_texture"})

    def test_draw_overlay_color_overlay(self) -> None:
        """draw_overlay() should draw a color overlay."""
        self.canvas.draw_overlay({
            "overlay_type": "color_overlay",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
            "color": (255, 0, 0, 128),
            "opacity": 0.5,
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((50, 50))

        self.assertEqual(pixel[3], 255)

        # Expected: 25% red overlay on background (alpha=64/255)
        self.assertAlmostEqual(pixel[0], 79, delta=1)
        self.assertAlmostEqual(pixel[1], 23, delta=1)
        self.assertAlmostEqual(pixel[2], 30, delta=1)

    def test_draw_overlay_opacity_negative_raises(self) -> None:
        """draw_overlay() should raise RenderingError for negative opacity."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_overlay({
                "overlay_type": "color_overlay",
                "color": (255, 0, 0, 128),
                "opacity": -0.5,
            })

    def test_draw_overlay_opacity_above_1_raises(self) -> None:
        """draw_overlay() should raise RenderingError for opacity > 1."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_overlay({
                "overlay_type": "color_overlay",
                "color": (255, 0, 0, 128),
                "opacity": 1.5,
            })

    def test_draw_overlay_with_3_tuple_color(self) -> None:
        """draw_overlay() should accept 3-tuple color (auto-add alpha=255)."""
        self.canvas.draw_overlay({
            "overlay_type": "color_overlay",
            "color": (255, 0, 0),
            "opacity": 0.5,
        })
        result = self.canvas.get_result()
        pixel = result.getpixel((50, 50))
        self.assertEqual(pixel[3], 255)

    def test_draw_overlay_missing_color(self) -> None:
        """draw_overlay() should raise RenderingError if 'color' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_overlay({
                "overlay_type": "color_overlay",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
            })

    def test_draw_overlay_unsupported_type(self) -> None:
        """draw_overlay() should raise RenderingError for unsupported types."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_overlay({"overlay_type": "vignette"})

    def test_draw_overlay_missing_type(self) -> None:
        """draw_overlay() should raise RenderingError if 'overlay_type' is missing."""
        with self.assertRaises(RenderingError):
            self.canvas.draw_overlay({"color": (255, 0, 0, 128)})


class TestPillowCanvasWithRenderer(unittest.TestCase):
    """Test PillowCanvas integration with Renderer."""

    def setUp(self) -> None:
        from engine.core.renderer import Renderer
        from engine.layers.layer import Layer, LayerKind, LayerZone

        self.canvas = PillowCanvas(640, 480, (20, 30, 40, 255))
        self.renderer = Renderer(self.canvas)
        self.LayerKind = LayerKind
        self.LayerZone = LayerZone
        self.Layer = Layer

    def test_renderer_with_pillow_canvas_returns_image(self) -> None:
        """Renderer should return a PIL Image when using PillowCanvas."""
        from engine.assets.resolver import ResolvedAssets
        from engine.configuration.resolver import ResolvedConfiguration
        from engine.core.context import RenderContext
        from engine.fonts.resolver import ResolvedFonts
        from engine.validation.validator import ValidatedPayload

        context = RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-001",
        )

        img = Image.new("RGBA", (50, 50), (255, 0, 0, 255))
        font = ImageFont.load_default()

        layers = [
            self.Layer(
                kind=self.LayerKind.SHAPE,
                zone=self.LayerZone.CONTENT,
                z_index=0,
                properties={
                    "shape_type": "rectangle",
                    "x": 50,
                    "y": 50,
                    "width": 540,
                    "height": 380,
                    "color": (40, 50, 60, 200),
                },
            ),
            self.Layer(
                kind=self.LayerKind.IMAGE,
                zone=self.LayerZone.CONTENT,
                z_index=1,
                properties={
                    "image": img,
                    "x": 100,
                    "y": 100,
                    "opacity": 0.8,
                },
            ),
            self.Layer(
                kind=self.LayerKind.TEXT,
                zone=self.LayerZone.CONTENT,
                z_index=2,
                properties={
                    "text": "Hello, Renderer!",
                    "x": 200,
                    "y": 200,
                    "font": font,
                    "color": (255, 255, 255, 255),
                },
            ),
        ]

        result = self.renderer.render(context, layers)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (640, 480))
        self.assertEqual(result.mode, "RGBA")

    def test_renderer_preserves_canvas_state(self) -> None:
        """Renderer should not modify Canvas internals beyond drawing."""
        from engine.assets.resolver import ResolvedAssets
        from engine.configuration.resolver import ResolvedConfiguration
        from engine.core.context import RenderContext
        from engine.fonts.resolver import ResolvedFonts
        from engine.validation.validator import ValidatedPayload

        context = RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-002",
        )

        font = ImageFont.load_default()
        initial_hash = hash(self.canvas.get_result().tobytes())

        layers = [
            self.Layer(
                kind=self.LayerKind.TEXT,
                zone=self.LayerZone.CONTENT,
                z_index=1,
                properties={
                    "text": "Test",
                    "x": 10,
                    "y": 10,
                    "font": font,
                },
            ),
        ]

        result = self.renderer.render(context, layers)
        self.assertIs(result, self.canvas.get_result())
        self.assertNotEqual(initial_hash, hash(result.tobytes()))


if __name__ == "__main__":
    unittest.main()
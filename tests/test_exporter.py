"""Tests for PillowExporter.

Tests the concrete PillowExporter implementation against the contract
defined in 02_ARCHITECTURE.md Section 15 Step 7 and 04_RENDERING_SPECIFICATION.md.

Scope: Exporter only. Does not test Renderer, Canvas, QualityVerifier,
Pipeline, or other subsystems.
"""

import unittest
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from engine.core.exceptions import ExportError
from engine.export.exporter import PillowExporter


def webp_available() -> bool:
    """Check if WEBP encoding is available in the current Pillow build."""
    try:
        dummy = Image.new("RGB", (1, 1), (255, 255, 255))
        buffer = BytesIO()
        dummy.save(buffer, format="WEBP", quality=90)
        return True
    except Exception:
        return False


class TestPillowExporter(unittest.TestCase):
    """Test PillowExporter functionality."""

    def setUp(self) -> None:
        self.image = Image.new("RGBA", (100, 80), (255, 100, 50, 200))

    def _create_image(self, mode: str = "RGBA") -> Image.Image:
        """Create a test image in the specified mode."""
        if mode == "RGBA":
            return Image.new("RGBA", (100, 80), (255, 100, 50, 200))
        elif mode == "RGB":
            return Image.new("RGB", (100, 80), (255, 100, 50))
        elif mode == "LA":
            img = Image.new("L", (100, 80), 128)
            alpha = Image.new("L", (100, 80), 200)
            img.putalpha(alpha)
            return img
        elif mode == "L":
            return Image.new("L", (100, 80), 128)
        elif mode == "P":
            img = Image.new("P", (100, 80))
            palette = [255, 100, 50] * 85 + [0, 0, 0] * 171
            img.putpalette(palette)
            return img
        elif mode == "P_transparent":
            # P-mode with transparency via palette
            img = Image.new("P", (100, 80))
            palette = [255, 100, 50] * 85 + [0, 0, 0] * 171
            img.putpalette(palette)
            # Set transparency index (palette entry 0 = transparent)
            img.info["transparency"] = 0
            # Fill some pixels with transparent index
            pixels = img.load()
            for x in range(50):
                for y in range(80):
                    pixels[x, y] = 0  # transparent
            return img
        elif mode == "CMYK":
            return Image.new("CMYK", (100, 80), (0, 100, 50, 0))
        return Image.new("RGB", (100, 80), (255, 100, 50))

    # =========================================================================
    # PNG Tests
    # =========================================================================

    def test_png_export_succeeds(self) -> None:
        """PNG export should succeed and return bytes."""
        exporter = PillowExporter("PNG")
        result = exporter.export(self.image)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_png_output_is_decodable(self) -> None:
        """PNG output should be decodable as PNG."""
        exporter = PillowExporter("PNG")
        result = exporter.export(self.image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.size, (100, 80))

    def test_png_preserves_alpha(self) -> None:
        """PNG should preserve alpha transparency."""
        exporter = PillowExporter("PNG")
        image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGBA")
        pixel = decoded.getpixel((5, 5))
        self.assertEqual(pixel[3], 128)

    def test_png_ignores_quality(self) -> None:
        """PNG should ignore quality value."""
        exporter = PillowExporter("PNG", quality=999)
        result = exporter.export(self.image)
        self.assertIsInstance(result, bytes)

    # =========================================================================
    # JPEG Mode Handling Tests
    # =========================================================================

    def test_jpeg_rgb_export_succeeds(self) -> None:
        """JPEG RGB export should succeed."""
        exporter = PillowExporter("JPEG", quality=90)
        image = self._create_image("RGB")
        result = exporter.export(image)
        self.assertIsInstance(result, bytes)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))

    def test_jpeg_rgba_export_succeeds(self) -> None:
        """JPEG RGBA export should succeed (flatten to RGB)."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("RGBA")
        original_pixel = image.getpixel((10, 10))
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))
        # Original unchanged
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_jpeg_la_export_succeeds(self) -> None:
        """JPEG LA export should succeed (flatten to RGB)."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("LA")
        original_pixel = image.getpixel((10, 10))
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))
        # Original unchanged
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_jpeg_l_export_succeeds(self) -> None:
        """JPEG L (grayscale) export should succeed (convert to RGB)."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("L")
        original_pixel = image.getpixel((10, 10))
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))
        # Original unchanged
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_jpeg_p_export_succeeds(self) -> None:
        """JPEG P (palette) export should succeed (convert to RGB)."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("P")
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))

    def test_jpeg_p_transparent_export_succeeds(self) -> None:
        """JPEG P with transparency should flatten to RGB with white background."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("P_transparent")
        original_mode = image.mode
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))
        # Original unchanged
        self.assertEqual(image.mode, original_mode)
        # Verify transparent area flattened to white
        # (0, 0) should be white (255, 255, 255) since it was transparent
        pixel = decoded.getpixel((0, 0))
        self.assertEqual(pixel, (255, 255, 255))

    def test_jpeg_cmyk_export_succeeds(self) -> None:
        """JPEG CMYK export should succeed (convert to RGB)."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("CMYK")
        result = exporter.export(image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.mode, "RGB")
        self.assertEqual(decoded.size, (100, 80))

    # =========================================================================
    # JPEG Immutability Tests
    # =========================================================================

    def test_jpeg_rgba_original_not_mutated(self) -> None:
        """JPEG RGBA export should not mutate original."""
        exporter = PillowExporter("JPEG")
        image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
        original_mode = image.mode
        original_pixel = image.getpixel((5, 5))
        exporter.export(image)
        self.assertEqual(image.mode, original_mode)
        self.assertEqual(image.getpixel((5, 5)), original_pixel)

    def test_jpeg_la_original_not_mutated(self) -> None:
        """JPEG LA export should not mutate original."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("LA")
        original_mode = image.mode
        original_pixel = image.getpixel((10, 10))
        exporter.export(image)
        self.assertEqual(image.mode, original_mode)
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_jpeg_l_original_not_mutated(self) -> None:
        """JPEG L export should not mutate original."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("L")
        original_mode = image.mode
        original_pixel = image.getpixel((10, 10))
        exporter.export(image)
        self.assertEqual(image.mode, original_mode)
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_jpeg_p_original_not_mutated(self) -> None:
        """JPEG P export should not mutate original."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("P")
        original_mode = image.mode
        exporter.export(image)
        self.assertEqual(image.mode, original_mode)

    def test_jpeg_p_transparent_original_not_mutated(self) -> None:
        """JPEG P with transparency export should not mutate original."""
        exporter = PillowExporter("JPEG")
        image = self._create_image("P_transparent")
        original_mode = image.mode
        original_info_transparency = image.info.get("transparency")
        exporter.export(image)
        self.assertEqual(image.mode, original_mode)
        self.assertEqual(image.info.get("transparency"), original_info_transparency)

    def test_jpeg_preserves_dimensions(self) -> None:
        """JPEG should preserve dimensions."""
        exporter = PillowExporter("JPEG")
        result = exporter.export(self.image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.size, (100, 80))

    # =========================================================================
    # JPEG Quality Tests
    # =========================================================================

    def test_jpeg_quality_validation_valid(self) -> None:
        """Valid JPEG quality should be accepted."""
        exporter = PillowExporter("JPEG", quality=1)
        self.assertEqual(exporter.quality, 1)
        exporter = PillowExporter("JPEG", quality=100)
        self.assertEqual(exporter.quality, 100)

    def test_jpeg_quality_validation_too_low(self) -> None:
        """Quality below 1 should raise ExportError."""
        with self.assertRaises(ExportError) as ctx:
            PillowExporter("JPEG", quality=0)
        self.assertIn("between 1 and 100", str(ctx.exception))

    def test_jpeg_quality_validation_too_high(self) -> None:
        """Quality above 100 should raise ExportError."""
        with self.assertRaises(ExportError) as ctx:
            PillowExporter("JPEG", quality=101)
        self.assertIn("between 1 and 100", str(ctx.exception))

    def test_jpeg_quality_non_integer(self) -> None:
        """Non-integer quality should raise ExportError."""
        with self.assertRaises(ExportError) as ctx:
            PillowExporter("JPEG", quality=95.5)  # type: ignore
        self.assertIn("integer", str(ctx.exception))

    # =========================================================================
    # WEBP Tests
    # =========================================================================

    @unittest.skipIf(not webp_available(), "WEBP not available in this Pillow build")
    def test_webp_export_succeeds(self) -> None:
        """WEBP export should succeed when available."""
        exporter = PillowExporter("WEBP", quality=90)
        result = exporter.export(self.image)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    @unittest.skipIf(not webp_available(), "WEBP not available in this Pillow build")
    def test_webp_output_decodable(self) -> None:
        """WEBP output should be decodable when available."""
        exporter = PillowExporter("WEBP")
        result = exporter.export(self.image)
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.size, (100, 80))

    def test_webp_unavailable_raises_export_error(self) -> None:
        """If WEBP unavailable, construction should raise ExportError."""
        if not webp_available():
            with self.assertRaises(ExportError) as ctx:
                PillowExporter("WEBP")
            self.assertIn("WEBP export is not available", str(ctx.exception))
        else:
            # If available, just verify construction works
            exporter = PillowExporter("WEBP")
            self.assertEqual(exporter.output_format, "WEBP")

    def test_webp_quality_validation(self) -> None:
        """WEBP quality should be validated."""
        if webp_available():
            with self.assertRaises(ExportError):
                PillowExporter("WEBP", quality=0)
            with self.assertRaises(ExportError):
                PillowExporter("WEBP", quality=101)
        else:
            with self.assertRaises(ExportError):
                PillowExporter("WEBP", quality=90)

    # =========================================================================
    # Format Handling Tests
    # =========================================================================

    def test_format_normalization_aliases(self) -> None:
        """Format aliases should be normalized."""
        exporter = PillowExporter("JPG")
        self.assertEqual(exporter.output_format, "JPEG")
        exporter = PillowExporter("jpg")
        self.assertEqual(exporter.output_format, "JPEG")
        exporter = PillowExporter("png")
        self.assertEqual(exporter.output_format, "PNG")

    def test_unsupported_format_raises_export_error(self) -> None:
        """Unsupported format should raise ExportError."""
        with self.assertRaises(ExportError) as ctx:
            PillowExporter("BMP")
        self.assertIn("Unsupported export format", str(ctx.exception))

    # =========================================================================
    # Input Validation Tests
    # =========================================================================

    def test_none_input_raises_export_error(self) -> None:
        """None input should raise ExportError."""
        exporter = PillowExporter("PNG")
        with self.assertRaises(ExportError) as ctx:
            exporter.export(None)
        self.assertIn("None", str(ctx.exception))

    def test_non_pil_input_raises_export_error(self) -> None:
        """Non-PIL input should raise ExportError."""
        exporter = PillowExporter("PNG")
        with self.assertRaises(ExportError) as ctx:
            exporter.export("not_an_image")
        self.assertIn("expected a PIL.Image.Image", str(ctx.exception))

    # =========================================================================
    # Error Boundary Tests
    # =========================================================================

    def test_export_error_is_used(self) -> None:
        """Exporter should use ExportError for failures."""
        exporter = PillowExporter("PNG")
        with self.assertRaises(ExportError):
            exporter.export(None)

    def test_no_builtin_exception_escapes(self) -> None:
        """No built-in exceptions should escape Exporter."""
        exporter = PillowExporter("PNG")
        try:
            exporter.export(None)
        except ExportError:
            pass
        except Exception as exc:
            self.fail(f"A raw built-in exception escaped Exporter: {exc!r}")

    @patch("PIL.Image.Image.save")
    def test_save_failure_wrapped_as_export_error(self, mock_save) -> None:
        """Pillow save exceptions should be wrapped as ExportError."""
        mock_save.side_effect = OSError("Simulated disk full")
        exporter = PillowExporter("PNG")
        image = Image.new("RGB", (10, 10), (255, 255, 255))

        with self.assertRaises(ExportError) as ctx:
            exporter.export(image)

        self.assertIn("Failed to export image", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, OSError)
        self.assertEqual(str(ctx.exception.__cause__), "Simulated disk full")

        # Verify raw OSError does NOT escape
        try:
            exporter.export(image)
        except ExportError:
            pass
        except OSError:
            self.fail("OSError escaped Exporter boundary")

    @patch("PIL.Image.Image.convert")
    def test_preparation_failure_wrapped_as_export_error(self, mock_convert) -> None:
        """Preparation failures (convert) should be wrapped as ExportError."""
        mock_convert.side_effect = OSError("Simulated preparation failure")

        exporter = PillowExporter("JPEG")
        # Use an L-mode image so _prepare_for_export calls convert("RGB")
        image = Image.new("L", (10, 10), 128)

        with self.assertRaises(ExportError) as ctx:
            exporter.export(image)

        self.assertIn("Failed to export image", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, OSError)
        self.assertEqual(str(ctx.exception.__cause__), "Simulated preparation failure")

        # Verify raw OSError does NOT escape
        try:
            exporter.export(image)
        except ExportError:
            pass
        except OSError:
            self.fail("OSError escaped Exporter boundary")

    @patch("PIL.Image.Image.paste")
    def test_preparation_paste_failure_wrapped(self, mock_paste) -> None:
        """RGBA preparation paste failures should be wrapped as ExportError."""
        mock_paste.side_effect = OSError("Simulated paste failure")

        exporter = PillowExporter("JPEG")
        image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))

        with self.assertRaises(ExportError) as ctx:
            exporter.export(image)

        self.assertIn("Failed to export image", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, OSError)

    # =========================================================================
    # Stateless Test
    # =========================================================================

    def test_exporter_is_stateless_across_calls(self) -> None:
        """Exporter should not hold per-request state."""
        exporter = PillowExporter("PNG")
        image1 = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        image2 = Image.new("RGBA", (20, 20), (0, 255, 0, 255))

        result1 = exporter.export(image1)
        result2 = exporter.export(image2)

        decoded1 = Image.open(BytesIO(result1))
        decoded2 = Image.open(BytesIO(result2))

        self.assertEqual(decoded1.size, (10, 10))
        self.assertEqual(decoded2.size, (20, 20))


if __name__ == "__main__":
    unittest.main()
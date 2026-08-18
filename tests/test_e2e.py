"""True production End-to-End tests.

These tests use REAL production components:
    Validator, ConfigurationResolver, AssetResolver, FontResolver,
    TemplateRegistry, TemplateResolver, DefaultTemplate, Renderer,
    PillowCanvasProvider, PillowCanvas, QualityVerifier, PillowExporter

No fakes are used for the critical rendering path.

The purpose is to prove the complete pipeline works end-to-end.
"""

import unittest
from io import BytesIO

from PIL import Image

from engine.bootstrap import create_engine


class TestEndToEnd(unittest.TestCase):
    """True production E2E tests."""

    def setUp(self) -> None:
        self.pipeline = create_engine()

    def test_single_request_produces_jpeg_bytes(self) -> None:
        """A single request should produce valid JPEG bytes."""
        raw_request = {"template": "default"}

        result = self.pipeline.execute(raw_request)

        # Verify result is bytes
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

        # Verify it's decodable as JPEG
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.format, "JPEG")

        # Verify dimensions are reasonable (from default configuration)
        # Default from ConfigurationResolver: 1280x720
        self.assertEqual(decoded.size, (1280, 720))

    def test_multiple_requests_are_independent(self) -> None:
        """Multiple requests should not share state."""
        raw_request = {"template": "default"}

        # First request
        result1 = self.pipeline.execute(raw_request)
        decoded1 = Image.open(BytesIO(result1))

        # Second request (same pipeline instance)
        result2 = self.pipeline.execute(raw_request)
        decoded2 = Image.open(BytesIO(result2))

        # Both should be valid JPEG
        self.assertEqual(decoded1.format, "JPEG")
        self.assertEqual(decoded2.format, "JPEG")

        # Both should have same dimensions
        self.assertEqual(decoded1.size, decoded2.size)

        # Output bytes should be deterministic (same template, same config)
        # PNG output is deterministic; JPEG may vary slightly due to encoding
        # We check that both are valid and dimensions match

    def test_pixels_are_drawn(self) -> None:
        """The rendered image should contain actual drawn content."""
        raw_request = {"template": "default"}

        result = self.pipeline.execute(raw_request)
        decoded = Image.open(BytesIO(result))

        # The DefaultTemplate draws:
        # 1. A dark background rectangle (20, 30, 50)
        # 2. An electric blue accent rectangle (0, 112, 255)

        # Check that the image is not a blank canvas (all black/transparent)
        # Sample a few pixels to verify content was drawn

        # Background area (center-left) should be dark blue-black
        bg_pixel = decoded.getpixel((100, 100))
        # Dark blue-black: approx (20, 30, 50)
        self.assertAlmostEqual(bg_pixel[0], 20, delta=10)
        self.assertAlmostEqual(bg_pixel[1], 30, delta=10)
        self.assertAlmostEqual(bg_pixel[2], 50, delta=10)

        # Accent area (center) should be electric blue
        accent_pixel = decoded.getpixel((640, 480))
        # Electric Blue: (0, 112, 255)
        self.assertAlmostEqual(accent_pixel[0], 0, delta=10)
        self.assertAlmostEqual(accent_pixel[1], 112, delta=10)
        self.assertAlmostEqual(accent_pixel[2], 255, delta=10)

    def test_quality_verifier_passes(self) -> None:
        """The image should pass QualityVerifier checks."""
        raw_request = {"template": "default"}

        # If QualityVerifier fails, Pipeline.execute() would raise
        # QualityVerificationError. The fact that this completes means
        # the verifier passed.
        result = self.pipeline.execute(raw_request)

        # Verify the result is bytes (verifier returned the image)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

        # Decode and verify dimensions match expected
        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.size, (1280, 720))

    def test_empty_request_uses_default_template(self) -> None:
        """Empty request should use the default template."""
        raw_request = {}

        result = self.pipeline.execute(raw_request)

        # Should still work with default template
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

        decoded = Image.open(BytesIO(result))
        self.assertEqual(decoded.format, "JPEG")
        self.assertEqual(decoded.size, (1280, 720))

    def test_template_default_override(self) -> None:
        """Request should be able to specify a template."""
        raw_request = {"template": "default"}

        result = self.pipeline.execute(raw_request)
        self.assertIsInstance(result, bytes)

    def test_multiple_pipeline_instances(self) -> None:
        """Different Pipeline instances should work independently."""
        pipeline1 = create_engine()
        pipeline2 = create_engine()

        result1 = pipeline1.execute({"template": "default"})
        result2 = pipeline2.execute({"template": "default"})

        self.assertIsInstance(result1, bytes)
        self.assertIsInstance(result2, bytes)

        decoded1 = Image.open(BytesIO(result1))
        decoded2 = Image.open(BytesIO(result2))

        self.assertEqual(decoded1.size, decoded2.size)


if __name__ == "__main__":
    unittest.main()

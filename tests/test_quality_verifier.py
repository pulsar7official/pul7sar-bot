"""Tests for QualityVerifier.

Tests the concrete QualityVerifier implementation against the contract
defined in 02_ARCHITECTURE.md Section 15 Step 6 and
04_RENDERING_SPECIFICATION.md Section 12.

Scope: QualityVerifier only. Does not test Renderer, Canvas, Pipeline,
Exporter, or other subsystems.
"""

import unittest

from PIL import Image

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.context import RenderContext
from engine.core.exceptions import QualityVerificationError
from engine.fonts.resolver import ResolvedFonts
from engine.quality.verifier import QualityVerifier
from engine.validation.validator import ValidatedPayload


class TestQualityVerifier(unittest.TestCase):
    """Test QualityVerifier functionality."""

    def setUp(self) -> None:
        self.verifier = QualityVerifier()

    def _create_context(
        self,
        config_width: int | None = 1280,
        config_height: int | None = 720,
        canvas_width: int | None = None,
        canvas_height: int | None = None,
    ) -> RenderContext:
        """Create a RenderContext for testing."""
        config_data = {}
        if config_width is not None and config_height is not None:
            config_data["engine"] = {"width": config_width, "height": config_height}

        canvas_info = {}
        if canvas_width is not None and canvas_height is not None:
            canvas_info = {"width": canvas_width, "height": canvas_height}

        return RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data=config_data),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-001",
            canvas_information=canvas_info,
        )

    def _create_image(self, width: int = 1280, height: int = 720, mode: str = "RGBA") -> Image.Image:
        """Create a test image."""
        return Image.new(mode, (width, height), (20, 30, 40, 255))

    # =========================================================================
    # SUCCESS CASES
    # =========================================================================

    def test_valid_image_accepted(self) -> None:
        """verify() should accept a valid rendered image."""
        context = self._create_context()
        image = self._create_image()
        result = self.verifier.verify(context, image)

        self.assertIs(result, image)
        self.assertEqual(result.size, (1280, 720))

    def test_returns_exact_same_object(self) -> None:
        """verify() must return the exact same image object."""
        context = self._create_context()
        image = self._create_image()

        result = self.verifier.verify(context, image)

        self.assertIs(result, image)

    def test_dimension_match_passes(self) -> None:
        """Matching dimensions should pass verification."""
        context = self._create_context(config_width=1920, config_height=1080)
        image = self._create_image(width=1920, height=1080)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_canvas_information_takes_precedence(self) -> None:
        """canvas_information should take precedence over configuration."""
        context = self._create_context(
            config_width=640, config_height=480,
            canvas_width=1920, canvas_height=1080,
        )
        image = self._create_image(width=1920, height=1080)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_canvas_information_used_when_present(self) -> None:
        """When canvas_information has dimensions, they should be used."""
        context = self._create_context(
            config_width=1280, config_height=720,
            canvas_width=800, canvas_height=600,
        )
        image = self._create_image(width=800, height=600)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_no_dimension_expectation_passes(self) -> None:
        """When no dimensions exist, dimension check is skipped.

        Uses a small arbitrary size (123x67) to prove verification succeeds
        without dimension comparison, while avoiding large memory allocation.
        """
        context = RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-002",
            canvas_information={},
        )
        image = self._create_image(width=123, height=67)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_all_valid_pil_modes_accepted(self) -> None:
        """All valid PIL modes should be accepted."""
        context = self._create_context(config_width=100, config_height=100)
        valid_modes = ["RGB", "RGBA", "L", "LA", "P", "CMYK"]

        for mode in valid_modes:
            image = Image.new(mode, (100, 100))
            result = self.verifier.verify(context, image)
            self.assertIs(result, image)

    def test_image_not_modified(self) -> None:
        """verify() should not modify the image."""
        context = self._create_context()
        image = self._create_image()
        original_size = image.size
        original_mode = image.mode
        original_pixel = image.getpixel((10, 10))

        self.verifier.verify(context, image)

        self.assertEqual(image.size, original_size)
        self.assertEqual(image.mode, original_mode)
        self.assertEqual(image.getpixel((10, 10)), original_pixel)

    def test_render_context_not_modified(self) -> None:
        """verify() should not modify RenderContext."""
        context = self._create_context()
        image = self._create_image()
        original_config = dict(context.resolved_configuration.data)

        self.verifier.verify(context, image)

        self.assertEqual(dict(context.resolved_configuration.data), original_config)

    def test_quality_verifier_is_stateless(self) -> None:
        """QualityVerifier should not hold per-request state."""
        verifier = QualityVerifier()
        context1 = self._create_context()
        context2 = self._create_context(config_width=800, config_height=600)
        image1 = self._create_image()
        image2 = self._create_image(width=800, height=600)

        result1 = verifier.verify(context1, image1)
        result2 = verifier.verify(context2, image2)

        self.assertIs(result1, image1)
        self.assertIs(result2, image2)

    # =========================================================================
    # FAILURE CASES
    # =========================================================================

    def test_none_image_raises_quality_verification_error(self) -> None:
        """None rendered result should raise QualityVerificationError."""
        context = self._create_context()

        with self.assertRaises(QualityVerificationError) as ctx:
            self.verifier.verify(context, None)

        self.assertIn("None", str(ctx.exception))

    def test_non_pil_image_raises_quality_verification_error(self) -> None:
        """Non-PIL image should raise QualityVerificationError."""
        context = self._create_context()

        with self.assertRaises(QualityVerificationError) as ctx:
            self.verifier.verify(context, "not_an_image")

        self.assertIn("must be a PIL.Image.Image", str(ctx.exception))

    def test_dimension_mismatch_raises_quality_verification_error(self) -> None:
        """Dimension mismatch should raise QualityVerificationError."""
        context = self._create_context(config_width=1920, config_height=1080)
        image = self._create_image(width=1280, height=720)

        with self.assertRaises(QualityVerificationError) as ctx:
            self.verifier.verify(context, image)

        self.assertIn("do not match expected dimensions", str(ctx.exception))

    def test_canvas_information_mismatch_raises_error(self) -> None:
        """Canvas information mismatch should raise QualityVerificationError."""
        context = self._create_context(
            config_width=1280, config_height=720,
            canvas_width=800, canvas_height=600,
        )
        image = self._create_image(width=1920, height=1080)

        with self.assertRaises(QualityVerificationError) as ctx:
            self.verifier.verify(context, image)

        self.assertIn("do not match expected dimensions", str(ctx.exception))

    def test_quality_verification_error_is_used(self) -> None:
        """QualityVerifier should raise QualityVerificationError on failure."""
        context = self._create_context(config_width=1920, config_height=1080)
        image = self._create_image(width=1280, height=720)

        with self.assertRaises(QualityVerificationError):
            self.verifier.verify(context, image)

    def test_no_builtin_exception_escapes(self) -> None:
        """No built-in exceptions should escape QualityVerifier."""
        context = self._create_context()
        image = "not_an_image"

        try:
            self.verifier.verify(context, image)
        except QualityVerificationError:
            pass
        except Exception as exc:
            self.fail(f"A raw built-in exception escaped QualityVerifier: {exc!r}")

    # =========================================================================
    # EDGE CASES
    # =========================================================================

    def test_missing_engine_config_uses_no_expectation(self) -> None:
        """When engine config is missing, dimension check is skipped."""
        context = RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={"other": "value"}),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-003",
            canvas_information={},
        )
        image = self._create_image(width=999, height=999)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_malformed_canvas_information_uses_config(self) -> None:
        """Malformed canvas_information should fall back to config."""
        context = self._create_context(
            config_width=640, config_height=480,
            canvas_width="not_an_int", canvas_height=600,
        )
        image = self._create_image(width=640, height=480)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)

    def test_malformed_engine_config_uses_no_expectation(self) -> None:
        """Malformed engine config should treat as no expectation."""
        context = RenderContext(
            validated_payload=ValidatedPayload(data={}),
            resolved_configuration=ResolvedConfiguration(data={
                "engine": {"width": "not_an_int", "height": 720}
            }),
            resolved_assets=ResolvedAssets(data={}),
            resolved_fonts=ResolvedFonts(data={}),
            render_id="test-004",
            canvas_information={},
        )
        image = self._create_image(width=999, height=999)

        result = self.verifier.verify(context, image)
        self.assertIs(result, image)


if __name__ == "__main__":
    unittest.main()
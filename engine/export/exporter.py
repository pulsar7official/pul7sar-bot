"""PillowExporter — Concrete Exporter using Pillow.

Per 02_ARCHITECTURE.md, Section 15, Step 7 and 04_RENDERING_SPECIFICATION.md,
Section 4:

    Exporter
        Receives:  Completed rendered image (unchanged from QualityVerifier)
        Converts:  To required output format (PNG, JPEG, WEBP)
        Does NOT:  Render, draw, access Canvas, receive RenderContext

Phase 11 implementation. Output format and quality are configured at
construction time. Exporter does not receive RenderContext.
"""

from __future__ import annotations

from io import BytesIO
from typing import Literal

from PIL import Image

from engine.core.exceptions import ExportError


# Supported export formats
SupportedFormat = Literal["PNG", "JPEG", "WEBP"]


class PillowExporter:
    """Concrete Exporter using Pillow encoding.

    Configured at construction time with output format and quality.
    Does NOT receive RenderContext.

    Supported formats:
        - PNG: Lossless, supports alpha
        - JPEG: Lossy, RGB only (all modes converted to RGB for JPEG)
        - WEBP: Lossy or lossless, supports alpha (runtime-dependent)

    Attributes:
        _output_format: Normalized format string (PNG, JPEG, WEBP)
        _quality: JPEG/WEBP quality (1-100), ignored for PNG
    """

    # Supported format names and their PIL save format strings
    _SUPPORTED_FORMATS = {
        "PNG": "PNG",
        "JPEG": "JPEG",
        "WEBP": "WEBP",
    }

    # Format aliases
    _FORMAT_ALIASES = {
        "JPG": "JPEG",
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP",
    }

    # Formats that use quality setting
    _QUALITY_FORMATS = {"JPEG", "WEBP"}

    def __init__(self, output_format: str = "PNG", quality: int = 95):
        """Initialize the PillowExporter.

        Args:
            output_format: Desired output format ("PNG", "JPEG", "WEBP").
                          Aliases like "JPG" are normalized to "JPEG".
            quality: JPEG/WEBP quality from 1 to 100 (default: 95).
                    Ignored for PNG output.

        Raises:
            ExportError: If the output format is unsupported or the
                WEBP format is requested but not available at runtime.
        """
        self._output_format = self._normalize_format(output_format)

        # Validate quality ONLY for formats that use it
        if self._output_format in self._QUALITY_FORMATS:
            self._quality = self._validate_quality(quality)
        else:
            # PNG ignores quality; store as None
            self._quality = None

        # Verify WEBP support at construction time if requested
        if self._output_format == "WEBP":
            self._check_webp_support()

    def export(self, rendered_image: Image.Image) -> bytes:
        """Export the rendered image as encoded bytes.

        Args:
            rendered_image: PIL.Image.Image from QualityVerifier.

        Returns:
            bytes: Encoded image data in the configured format.

        Raises:
            ExportError: If the image is None, not a PIL Image, or
                encoding fails for any reason. All backend/Pillow
                exceptions are wrapped as ExportError.
        """
        try:
            # 1. Validate input
            if rendered_image is None:
                raise ExportError("Exporter received None instead of a rendered image")

            if not isinstance(rendered_image, Image.Image):
                raise ExportError(
                    f"Exporter expected a PIL.Image.Image, got {type(rendered_image).__name__}"
                )

            # 2. Prepare image for export (does NOT mutate original)
            export_image = self._prepare_for_export(rendered_image)

            # 3. Encode to bytes
            buffer = BytesIO()
            save_kwargs = self._get_save_kwargs()
            export_image.save(buffer, format=self._output_format, **save_kwargs)
            return buffer.getvalue()

        except ExportError:
            # Re-raise deliberate ExportError without wrapping
            raise
        except Exception as exc:
            # Wrap any backend/Pillow exception as ExportError
            raise ExportError(
                f"Failed to export image as {self._output_format}: {exc}"
            ) from exc

    def _prepare_for_export(self, image: Image.Image) -> Image.Image:
        """Prepare the image for encoding without mutating the original.

        For JPEG:
            - RGB → direct (no copy needed)
            - RGBA/LA → copy, flatten to RGB with white background
            - L → convert to RGB via copy
            - P → convert to RGB; if transparency exists, flatten onto white background
            - CMYK → convert to RGB via copy
            - Other modes → safe convert to RGB via copy

        For other formats: returns the image unchanged.

        Args:
            image: The original PIL Image.

        Returns:
            Image.Image: Image ready for encoding (may be a copy).
        """
        if self._output_format == "JPEG":
            mode = image.mode

            # RGB: direct (no copy needed, original unchanged)
            if mode == "RGB":
                return image

            # RGBA: flatten alpha to RGB with white background
            if mode == "RGBA":
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(image, (0, 0), image)
                return rgb_image

            # LA: grayscale + alpha → flatten to RGB with white background
            if mode == "LA":
                rgba_image = image.convert("RGBA")
                rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                rgb_image.paste(rgba_image, (0, 0), rgba_image)
                return rgb_image

            # L: grayscale → RGB
            if mode == "L":
                return image.convert("RGB")

            # P: palette. Handle transparency if present.
            if mode == "P":
                return self._prepare_p_for_jpeg(image)

            # CMYK: convert to RGB
            if mode == "CMYK":
                return image.convert("RGB")

            # All other modes: attempt safe conversion
            try:
                return image.convert("RGB")
            except Exception as exc:
                raise ExportError(
                    f"Failed to convert image mode {mode!r} to RGB for JPEG export: {exc}"
                ) from exc

        # No transformation needed for PNG/WEBP
        return image

    def _prepare_p_for_jpeg(self, image: Image.Image) -> Image.Image:
        """Prepare P-mode image for JPEG export.

        If the palette image has transparency, flatten it onto
        white background. Otherwise, convert directly to RGB.

        Args:
            image: Original P-mode PIL Image.

        Returns:
            Image.Image: RGB image ready for JPEG export.
        """
        # Check for transparency in P-mode image
        # PIL stores palette transparency in info["transparency"]
        has_transparency = "transparency" in image.info

        if has_transparency:
            # Convert to RGBA, then flatten onto white background
            rgba_image = image.convert("RGBA")
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(rgba_image, (0, 0), rgba_image)
            return rgb_image

        # No transparency: direct conversion to RGB
        return image.convert("RGB")

    def _get_save_kwargs(self) -> dict:
        """Get format-specific save arguments.

        Returns:
            dict: Keyword arguments for PIL Image.save().
        """
        if self._output_format == "PNG":
            return {"compress_level": 6}

        if self._output_format == "JPEG":
            return {"quality": self._quality, "optimize": True}

        if self._output_format == "WEBP":
            return {"quality": self._quality}

        return {}

    # =========================================================================
    # Validation Helpers
    # =========================================================================

    @classmethod
    def _normalize_format(cls, output_format: str) -> str:
        """Normalize format name and validate it is supported.

        Args:
            output_format: Raw format string.

        Returns:
            str: Normalized format name.

        Raises:
            ExportError: If the format is unsupported.
        """
        # Check alias
        if output_format in cls._FORMAT_ALIASES:
            normalized = cls._FORMAT_ALIASES[output_format]
        else:
            normalized = output_format.upper()

        if normalized not in cls._SUPPORTED_FORMATS:
            supported = ", ".join(cls._SUPPORTED_FORMATS.keys())
            raise ExportError(
                f"Unsupported export format: {output_format!r}. "
                f"Supported formats: {supported}"
            )

        return normalized

    @classmethod
    def _validate_quality(cls, quality: int) -> int:
        """Validate quality value.

        Args:
            quality: Quality value to validate.

        Returns:
            int: Validated quality.

        Raises:
            ExportError: If quality is outside 1-100 or not an integer.
        """
        if not isinstance(quality, int):
            raise ExportError(f"Quality must be an integer, got {type(quality).__name__}")

        if quality < 1 or quality > 100:
            raise ExportError(
                f"Quality must be between 1 and 100, got {quality}"
            )

        return quality

    @classmethod
    def _check_webp_support(cls) -> None:
        """Check if WEBP encoding is available.

        Raises:
            ExportError: If WEBP is not available in the current Pillow build.
        """
        try:
            dummy = Image.new("RGB", (1, 1), (255, 255, 255))
            buffer = BytesIO()
            dummy.save(buffer, format="WEBP", quality=90)
        except Exception:
            raise ExportError(
                "WEBP export is not available in this Pillow build. "
                "Please install Pillow with WEBP support."
            )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def output_format(self) -> str:
        """Get the configured output format."""
        return self._output_format

    @property
    def quality(self) -> int | None:
        """Get the configured quality value (None if not applicable)."""
        return self._quality
"""Exception hierarchy for the PUL7SAR Visual Engine."""

from __future__ import annotations


class VisualEngineError(Exception):
    """Root exception for every error produced by the Visual Engine."""


class ConfigurationError(VisualEngineError):
    """Raised when engine configuration cannot be resolved."""


class AssetError(VisualEngineError):
    """Raised when an asset cannot be found or loaded."""


class FontError(VisualEngineError):
    """Raised when a required font cannot be loaded."""


class TemplateError(VisualEngineError):
    """Raised when a template cannot be resolved or executed."""


class RenderingError(VisualEngineError):
    """Raised when rendering cannot complete successfully."""


class ExportError(VisualEngineError):
    """Raised when final image export fails."""


class ValidationError(VisualEngineError):
    """Raised when a rendering request is invalid."""


class QualityVerificationError(VisualEngineError):
    """Raised when structural output verification fails."""

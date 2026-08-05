"""Exception hierarchy for the PUL7SAR Visual Engine.

Defines the engine-wide exception hierarchy as mandated by the
architecture specification (02_ARCHITECTURE.md, Section 9).

All engine-specific exceptions inherit from :class:`VisualEngineError`.
Python built-in exceptions must never be exposed across subsystem
boundaries; subsystems should raise (or wrap and re-raise) one of the
exceptions defined here instead.

These exception classes carry no rendering logic and no business
logic. They exist solely to communicate what failed and why.
"""

from __future__ import annotations


class VisualEngineError(Exception):
    """Root exception for every error produced by the Visual Engine.

    All other engine exceptions must inherit from this class.
    """


class ConfigurationError(VisualEngineError):
    """Raised when engine configuration cannot be loaded, validated,
    or resolved.

    Examples: missing configuration file, invalid configuration value,
    invalid YAML schema.
    """


class AssetError(VisualEngineError):
    """Raised when an asset cannot be found or loaded.

    Examples: missing logo, missing background, unsupported image
    format, corrupted asset.
    """


class FontError(VisualEngineError):
    """Raised when a required font cannot be loaded.

    Examples: font file missing, invalid font, unsupported font
    format.
    """


class TemplateError(VisualEngineError):
    """Raised when a template cannot be created or executed.

    Examples: unknown template, invalid template implementation,
    missing required layer.
    """


class RenderingError(VisualEngineError):
    """Raised whenever rendering cannot complete successfully.

    Examples: canvas creation failed, drawing operation failed,
    renderer internal failure.
    """


class ExportError(VisualEngineError):
    """Raised when exporting the final image fails.

    Examples: cannot save image, unsupported export format, file
    system write failure.
    """


class ValidationError(VisualEngineError):
    """Raised when validated input data becomes invalid before
    rendering.

    Examples: missing required payload field, invalid render request,
    unsupported platform profile.
    """

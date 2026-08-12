"""Exception hierarchy for the PUL7SAR Visual Engine.

Defined per 02_ARCHITECTURE.md, Section 12 (Exception Hierarchy) and
04_RENDERING_SPECIFICATION.md (Section 13, Pipeline Specification;
Sections 10-11, Error Propagation).

All engine-specific exceptions inherit from VisualEngineError.

Each subclass is owned by exactly one subsystem:

    ValidationError            -> Validator
    ConfigurationError         -> ConfigurationResolver
    AssetError                 -> AssetResolver
    FontError                  -> FontResolver
    TemplateError              -> Template
    RenderingError             -> Canvas / Renderer
    QualityVerificationError   -> QualityVerifier
    ExportError                -> Exporter

QualityVerificationError is a direct child of VisualEngineError and a
sibling of RenderingError and ExportError, not a subtype of either
(Architecture Section 12; Rendering Specification Section 12).

Pipeline never raises any of these directly and never catches and
reinterprets them -- it only propagates them unchanged (Architecture
Section 8, "Pipeline must never"; Rendering Specification Section 13).
"""

from __future__ import annotations


class VisualEngineError(Exception):
    """Root exception for every error produced by the Visual Engine."""


class ValidationError(VisualEngineError):
    """Raised by Validator when the raw incoming rendering request
    fails validation."""


class ConfigurationError(VisualEngineError):
    """Raised by ConfigurationResolver when engine configuration
    cannot be loaded, validated, or resolved."""


class AssetError(VisualEngineError):
    """Raised by AssetResolver when a required asset cannot be found
    or loaded."""


class FontError(VisualEngineError):
    """Raised by FontResolver when a required font cannot be
    loaded."""


class TemplateError(VisualEngineError):
    """Raised when a template cannot be created or executed."""


class RenderingError(VisualEngineError):
    """Raised by Canvas implementations when a drawing operation
    cannot be completed, and by Renderer when an unsupported
    LayerKind is dispatched or a required Canvas operation is
    missing."""


class QualityVerificationError(VisualEngineError):
    """Raised by QualityVerifier when the rendered result fails
    structural/output integrity verification.

    Direct child of VisualEngineError. Sibling of RenderingError and
    ExportError -- not a subtype of either.
    """


class ExportError(VisualEngineError):
    """Raised by Exporter when exporting the final image fails."""

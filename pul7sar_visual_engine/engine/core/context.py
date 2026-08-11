"""RenderContext -- the immutable, shared rendering-request state.

Per 02_ARCHITECTURE.md, Section 15, Step 2 (and Data Ownership) and
04_RENDERING_SPECIFICATION.md, Section 6:

    - Created exactly once, by Pipeline, after Validator ->
      ConfigurationResolver -> AssetResolver -> FontResolver have all
      completed successfully.
    - Immutable after creation.
    - Shared read-only with exactly three subsystems: Template,
      Renderer, QualityVerifier.
    - Never received by Validator, ConfigurationResolver,
      AssetResolver, FontResolver, Canvas, or Exporter.
    - Contains data only -- no rendering logic.

This module defines the RenderContext data structure itself. The
"created exactly once" rule is a behavioral constraint on Pipeline
(implemented in Phase 2/integration, not enforceable by the data
class in isolation) -- a data class cannot police how many times it
is instantiated across the wider application; that responsibility
belongs to Pipeline, which is the only component permitted to
construct one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.fonts.resolver import ResolvedFonts
from engine.validation.validator import ValidatedPayload


@dataclass(frozen=True)
class RenderContext:
    """Immutable, resolved state of one rendering request.

    Fields correspond exactly to the contents list in
    04_RENDERING_SPECIFICATION.md, Section 6:
    ValidatedPayload, ResolvedConfiguration, ResolvedAssets,
    ResolvedFonts, render metadata, render identifier, platform
    targets, canvas information, locale information.
    """

    validated_payload: ValidatedPayload
    resolved_configuration: ResolvedConfiguration
    resolved_assets: ResolvedAssets
    resolved_fonts: ResolvedFonts
    render_id: str
    render_metadata: Mapping[str, Any] = field(default_factory=dict)
    platform_targets: Tuple[str, ...] = field(default_factory=tuple)
    canvas_information: Mapping[str, Any] = field(default_factory=dict)
    locale_information: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name, value in (
            ("validated_payload", self.validated_payload),
            ("resolved_configuration", self.resolved_configuration),
            ("resolved_assets", self.resolved_assets),
            ("resolved_fonts", self.resolved_fonts),
        ):
            self._require_type(field_name, value)

        object.__setattr__(
            self, "render_metadata", MappingProxyType(dict(self.render_metadata))
        )
        object.__setattr__(
            self, "platform_targets", tuple(self.platform_targets)
        )
        object.__setattr__(
            self,
            "canvas_information",
            MappingProxyType(dict(self.canvas_information)),
        )
        object.__setattr__(
            self,
            "locale_information",
            MappingProxyType(dict(self.locale_information)),
        )

    @staticmethod
    def _require_type(field_name: str, value: Any) -> None:
        expected = {
            "validated_payload": ValidatedPayload,
            "resolved_configuration": ResolvedConfiguration,
            "resolved_assets": ResolvedAssets,
            "resolved_fonts": ResolvedFonts,
        }[field_name]
        if not isinstance(value, expected):
            raise TypeError(
                f"RenderContext.{field_name} must be a {expected.__name__}, "
                f"got {type(value)!r}"
            )

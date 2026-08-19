"""Immutable rendering request state."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.content import RenderContent
from engine.entities.model import EntityContext
from engine.fonts.resolver import ResolvedFonts
from engine.themes.model import ResolvedTheme
from engine.validation.validator import ValidatedPayload


@dataclass(frozen=True)
class RenderContext:
    """One immutable resolved rendering request."""

    validated_payload: ValidatedPayload
    resolved_configuration: ResolvedConfiguration
    resolved_assets: ResolvedAssets
    resolved_fonts: ResolvedFonts
    render_id: str

    content: Optional[RenderContent] = None
    entity: Optional[EntityContext] = None
    theme: Optional[ResolvedTheme] = None

    render_metadata: Mapping[str, Any] = field(default_factory=dict)
    platform_targets: tuple[str, ...] = field(default_factory=tuple)
    canvas_information: Mapping[str, Any] = field(default_factory=dict)
    locale_information: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.validated_payload, ValidatedPayload):
            raise TypeError("validated_payload must be ValidatedPayload")
        if not isinstance(self.resolved_configuration, ResolvedConfiguration):
            raise TypeError("resolved_configuration must be ResolvedConfiguration")
        if not isinstance(self.resolved_assets, ResolvedAssets):
            raise TypeError("resolved_assets must be ResolvedAssets")
        if not isinstance(self.resolved_fonts, ResolvedFonts):
            raise TypeError("resolved_fonts must be ResolvedFonts")
        if not isinstance(self.render_id, str) or not self.render_id:
            raise TypeError("render_id must be a non-empty str")

        if self.content is not None and not isinstance(self.content, RenderContent):
            raise TypeError("content must be RenderContent or None")
        if self.entity is not None and not isinstance(self.entity, EntityContext):
            raise TypeError("entity must be EntityContext or None")
        if self.theme is not None and not isinstance(self.theme, ResolvedTheme):
            raise TypeError("theme must be ResolvedTheme or None")

        object.__setattr__(
            self, "render_metadata", MappingProxyType(dict(self.render_metadata))
        )
        object.__setattr__(
            self, "canvas_information", MappingProxyType(dict(self.canvas_information))
        )
        object.__setattr__(
            self, "locale_information", MappingProxyType(dict(self.locale_information))
        )
        object.__setattr__(self, "platform_targets", tuple(self.platform_targets))

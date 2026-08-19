"""Immutable rendering request state."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.content import RenderContent
from engine.fonts.resolver import ResolvedFonts
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
    render_metadata: Mapping[str, Any] = field(default_factory=dict)
    platform_targets: tuple[str, ...] = field(default_factory=tuple)
    canvas_information: Mapping[str, Any] = field(default_factory=dict)
    locale_information: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.validated_payload, ValidatedPayload):
            raise TypeError("validated_payload must be ValidatedPayload")
        if not isinstance(self.resolved_configuration, ResolvedConfiguration):
            raise TypeError(
                "resolved_configuration must be ResolvedConfiguration"
            )
        if not isinstance(self.resolved_assets, ResolvedAssets):
            raise TypeError("resolved_assets must be ResolvedAssets")
        if not isinstance(self.resolved_fonts, ResolvedFonts):
            raise TypeError("resolved_fonts must be ResolvedFonts")
        if not isinstance(self.render_id, str) or not self.render_id:
            raise TypeError("render_id must be a non-empty str")

        object.__setattr__(
            self, "render_metadata",
            MappingProxyType(dict(self.render_metadata))
        )
        object.__setattr__(
            self, "canvas_information",
            MappingProxyType(dict(self.canvas_information))
        )
        object.__setattr__(
            self, "locale_information",
            MappingProxyType(dict(self.locale_information))
        )
        object.__setattr__(
            self, "platform_targets", tuple(self.platform_targets)
        )

        # Phase 14: explicit request["content"] -> RenderContent.
        # Pipeline remains unchanged: RenderContext owns the final immutable
        # representation while business content stays separate from metadata.
        if self.content is None:
            raw_content = dict(self.validated_payload.data).get("content")
            if raw_content is not None:
                if isinstance(raw_content, RenderContent):
                    parsed = raw_content
                else:
                    if not isinstance(raw_content, Mapping):
                        raise TypeError("content must be a mapping or RenderContent")
                    raw = dict(raw_content)
                    parsed = RenderContent(
                        headline=raw.get("headline", ""),
                        summary=raw.get("summary", ""),
                        image=raw.get("image"),
                    )
                object.__setattr__(self, "content", parsed)
        elif not isinstance(self.content, RenderContent):
            raise TypeError("content must be RenderContent or None")

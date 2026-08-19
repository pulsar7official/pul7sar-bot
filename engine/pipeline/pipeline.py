"""Pipeline -- coordinates the complete rendering lifecycle.

Phase 15 adds one injected ThemeResolver collaborator used only during
RenderContext assembly. Theme logic remains outside Pipeline.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any, Optional, Protocol, Sequence, runtime_checkable

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.content import RenderContent
from engine.core.context import RenderContext
from engine.entities.model import EntityContext
from engine.fonts.resolver import ResolvedFonts
from engine.layers.layer import Layer
from engine.themes.model import ResolvedTheme
from engine.validation.validator import ValidatedPayload


@runtime_checkable
class ValidatorProtocol(Protocol):
    def validate(self, raw_request: Any) -> ValidatedPayload: ...


@runtime_checkable
class ConfigurationResolverProtocol(Protocol):
    def resolve(self, validated_payload: ValidatedPayload) -> ResolvedConfiguration: ...


@runtime_checkable
class AssetResolverProtocol(Protocol):
    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedAssets: ...


@runtime_checkable
class FontResolverProtocol(Protocol):
    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedFonts: ...


@runtime_checkable
class TemplateProtocol(Protocol):
    def execute(self, render_context: RenderContext) -> Sequence[Layer]: ...


@runtime_checkable
class TemplateResolverProtocol(Protocol):
    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> TemplateProtocol: ...


@runtime_checkable
class RendererProtocol(Protocol):
    def render(self, render_context: RenderContext, layers: Sequence[Layer]) -> Any: ...


@runtime_checkable
class QualityVerifierProtocol(Protocol):
    def verify(self, render_context: RenderContext, rendered_image: Any) -> Any: ...


@runtime_checkable
class ExporterProtocol(Protocol):
    def export(self, rendered_image: Any) -> Any: ...


@runtime_checkable
class ThemeResolverProtocol(Protocol):
    def resolve(self, entity: Optional[EntityContext]) -> ResolvedTheme: ...


class Pipeline:
    """Orchestrate rendering while delegating subsystem responsibilities."""

    def __init__(
        self,
        *,
        validator: ValidatorProtocol,
        configuration_resolver: ConfigurationResolverProtocol,
        asset_resolver: AssetResolverProtocol,
        font_resolver: FontResolverProtocol,
        template_resolver: TemplateResolverProtocol,
        renderer: RendererProtocol,
        quality_verifier: QualityVerifierProtocol,
        exporter: ExporterProtocol,
        theme_resolver: Optional[ThemeResolverProtocol] = None,
    ) -> None:
        self._validator = validator
        self._configuration_resolver = configuration_resolver
        self._asset_resolver = asset_resolver
        self._font_resolver = font_resolver
        self._template_resolver = template_resolver
        self._renderer = renderer
        self._quality_verifier = quality_verifier
        self._exporter = exporter
        self._theme_resolver = theme_resolver

    def execute(self, raw_request: Any) -> Any:
        validated_payload = self._validator.validate(raw_request)

        resolved_configuration = self._configuration_resolver.resolve(
            validated_payload
        )
        resolved_assets = self._asset_resolver.resolve(
            validated_payload, resolved_configuration
        )
        resolved_fonts = self._font_resolver.resolve(
            validated_payload, resolved_configuration
        )

        render_context = self._assemble_render_context(
            validated_payload=validated_payload,
            resolved_configuration=resolved_configuration,
            resolved_assets=resolved_assets,
            resolved_fonts=resolved_fonts,
        )

        template = self._template_resolver.resolve(
            validated_payload, resolved_configuration
        )
        layers = template.execute(render_context)
        rendered_image = self._renderer.render(render_context, layers)
        verified_image = self._quality_verifier.verify(
            render_context, rendered_image
        )
        return self._exporter.export(verified_image)

    def _assemble_render_context(
        self,
        *,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
        resolved_assets: ResolvedAssets,
        resolved_fonts: ResolvedFonts,
    ) -> RenderContext:
        data = dict(validated_payload.data)

        content = self._parse_content(data.get("content"))
        entity = self._parse_entity(data.get("entity"))
        theme = (
            self._theme_resolver.resolve(entity)
            if self._theme_resolver is not None
            else None
        )

        return RenderContext(
            validated_payload=validated_payload,
            resolved_configuration=resolved_configuration,
            resolved_assets=resolved_assets,
            resolved_fonts=resolved_fonts,
            render_id=str(uuid.uuid4()),
            content=content,
            entity=entity,
            theme=theme,
        )

    @staticmethod
    def _parse_content(raw: Any) -> Optional[RenderContent]:
        if raw is None:
            return None
        if isinstance(raw, RenderContent):
            return raw
        if not isinstance(raw, Mapping):
            raise TypeError("content must be a mapping or RenderContent")
        data = dict(raw)
        return RenderContent(
            headline=data.get("headline", ""),
            summary=data.get("summary", ""),
            image=data.get("image"),
        )

    @staticmethod
    def _parse_entity(raw: Any) -> Optional[EntityContext]:
        if raw is None:
            return None
        if isinstance(raw, EntityContext):
            return raw
        if not isinstance(raw, Mapping):
            raise TypeError("entity must be a mapping or EntityContext")
        data = dict(raw)
        key = data.get("key")
        if key is None:
            return None
        return EntityContext(
            key=key,
            kind=data.get("kind"),
            display_name=data.get("display_name"),
        )

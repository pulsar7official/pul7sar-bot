"""Deterministic EntityContext -> ResolvedTheme resolution."""

from __future__ import annotations

from engine.branding.model import BrandPalette
from engine.entities.model import EntityContext
from engine.themes.contrast import choose_text_color
from engine.themes.model import ResolvedTheme
from engine.themes.registry import ThemeRegistry


class ThemeResolver:
    """Resolve one contextual visual theme with brand fallback."""

    def __init__(self, registry: ThemeRegistry, brand_palette: BrandPalette) -> None:
        self._registry = registry
        self._brand_palette = brand_palette

    def resolve(self, entity: EntityContext | None) -> ResolvedTheme:
        if entity is not None and entity.key:
            contextual = self._registry.get(entity.key)
            if contextual is not None:
                return contextual
        return self._default_theme()

    def _default_theme(self) -> ResolvedTheme:
        brand = self._brand_palette
        return ResolvedTheme(
            primary_color=brand.primary,
            secondary_color=brand.secondary,
            # Headline sits over the lower dark gradient, so contrast is evaluated
            # against the actual overlay background rather than brand primary.
            text_color=choose_text_color(brand.dark),
            overlay_color=brand.dark,
            overlay_opacity=0.72,
            accent_color=brand.primary,
            entity_key=None,
            source="default",
            logo_treatment="master",
        )

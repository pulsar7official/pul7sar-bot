"""Production composition root for the PUL7SAR Visual Engine."""

from __future__ import annotations

import json
from pathlib import Path

from engine.assets.resolver import AssetResolver
from engine.branding.defaults import get_default_brand_palette
from engine.canvas.provider import PillowCanvasProvider
from engine.configuration.resolver import ConfigurationResolver
from engine.core.renderer import Renderer
from engine.export.exporter import PillowExporter
from engine.fonts.resolver import FontResolver
from engine.pipeline.pipeline import Pipeline
from engine.quality.verifier import QualityVerifier
from engine.templates.implementations.default import DefaultTemplate
from engine.templates.implementations.news import NewsTemplate
from engine.templates.registry import TemplateRegistry
from engine.templates.resolver import TemplateResolver
from engine.themes.contrast import choose_text_color
from engine.themes.model import ResolvedTheme
from engine.themes.registry import ThemeRegistry
from engine.themes.resolver import ThemeResolver
from engine.validation.validator import Validator


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid RGB hex color: {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _build_theme_registry() -> ThemeRegistry:
    """Load the small Phase-15 seed dataset once during engine creation."""
    data_path = Path(__file__).resolve().parent / "themes" / "data" / "teams.json"
    registry = ThemeRegistry()

    with data_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    for entity_key, record in records.items():
        primary = _hex_to_rgb(record["primary"])
        secondary = _hex_to_rgb(record["secondary"]) if record.get("secondary") else None
        accent = _hex_to_rgb(record.get("accent", record["primary"]))
        overlay = _hex_to_rgb(record.get("overlay", "#0F172A"))
        overlay_opacity = float(record.get("overlay_opacity", 0.72))

        registry.register(
            entity_key,
            ResolvedTheme(
                primary_color=primary,
                secondary_color=secondary,
                # Headline is rendered over the lower overlay, so text contrast
                # is resolved against the overlay color, not the club primary.
                text_color=choose_text_color(overlay),
                overlay_color=overlay,
                overlay_opacity=overlay_opacity,
                accent_color=accent,
                entity_key=entity_key,
                source=record.get("kind", "club"),
                logo_treatment="contextual",
            ),
        )

    return registry


def create_engine() -> Pipeline:
    """Create a fully wired reusable production Pipeline."""
    validator = Validator()
    configuration_resolver = ConfigurationResolver()
    asset_resolver = AssetResolver()
    font_resolver = FontResolver()
    quality_verifier = QualityVerifier()
    exporter = PillowExporter(output_format="JPEG")

    template_registry = TemplateRegistry()
    template_registry.register("default", DefaultTemplate)
    template_registry.register("news", NewsTemplate)

    template_resolver = TemplateResolver(
        registry=template_registry,
        default_template="default",
    )

    theme_resolver = ThemeResolver(
        registry=_build_theme_registry(),
        brand_palette=get_default_brand_palette(),
    )

    renderer = Renderer(PillowCanvasProvider())

    return Pipeline(
        validator=validator,
        configuration_resolver=configuration_resolver,
        asset_resolver=asset_resolver,
        font_resolver=font_resolver,
        template_resolver=template_resolver,
        renderer=renderer,
        quality_verifier=quality_verifier,
        exporter=exporter,
        theme_resolver=theme_resolver,
    )

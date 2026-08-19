"""Production composition root for the PUL7SAR Visual Engine."""

from engine.assets.resolver import AssetResolver
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
from engine.validation.validator import Validator


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
    )

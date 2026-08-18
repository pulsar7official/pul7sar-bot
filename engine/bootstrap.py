"""PUL7SAR Visual Engine — Production composition root.

This module creates the application-scoped Visual Engine with all real
subsystems wired together.

Per Phase 12 architecture:
    - Pipeline, Renderer, and most components are application-scoped
    - Canvas is per-render (created fresh each render() call)
    - Exporter is application-scoped with static JPEG format
    - No request configuration is resolved at bootstrap time

Usage:
    from engine.bootstrap import create_engine

    pipeline = create_engine()
    result = pipeline.execute(raw_request)  # bytes
"""

from engine.assets.resolver import AssetResolver
from engine.canvas.provider import PillowCanvasProvider
from engine.configuration.resolver import ConfigurationResolver
from engine.core.renderer import Renderer
from engine.export.exporter import PillowExporter
from engine.fonts.resolver import FontResolver
from engine.pipeline.pipeline import Pipeline
from engine.quality.verifier import QualityVerifier
from engine.templates.implementations.default import DefaultTemplate
from engine.templates.registry import TemplateRegistry
from engine.templates.resolver import TemplateResolver
from engine.validation.validator import Validator


def create_engine() -> Pipeline:
    """Create a fully wired production Visual Engine Pipeline.

    Returns:
        Pipeline: A ready-to-use Pipeline instance.

    The Pipeline is application-scoped and can be reused across
    multiple requests. Each render() call will create a fresh
    Canvas with dimensions from the request's RenderContext.
    """
    # ========================================================================
    # 1. Stateless resolvers (application-scoped)
    # ========================================================================
    validator = Validator()
    configuration_resolver = ConfigurationResolver()
    asset_resolver = AssetResolver()
    font_resolver = FontResolver()

    # ========================================================================
    # 2. QualityVerifier (stateless, application-scoped)
    # ========================================================================
    quality_verifier = QualityVerifier()

    # ========================================================================
    # 3. Exporter (application-scoped, static JPEG)
    # ========================================================================
    exporter = PillowExporter(output_format="JPEG")  # quality default 95

    # ========================================================================
    # 4. Template Registry + Resolver
    # ========================================================================
    template_registry = TemplateRegistry()
    template_registry.register("default", DefaultTemplate)

    template_resolver = TemplateResolver(
        registry=template_registry,
        default_template="default",
    )

    # ========================================================================
    # 5. Canvas Provider + Renderer
    # ========================================================================
    canvas_provider = PillowCanvasProvider()
    renderer = Renderer(canvas_provider)

    # ========================================================================
    # 6. Pipeline (application-scoped)
    # ========================================================================
    pipeline = Pipeline(
        validator=validator,
        configuration_resolver=configuration_resolver,
        asset_resolver=asset_resolver,
        font_resolver=font_resolver,
        template_resolver=template_resolver,
        renderer=renderer,
        quality_verifier=quality_verifier,
        exporter=exporter,
    )

    return pipeline

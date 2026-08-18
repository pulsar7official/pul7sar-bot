"""Tests for bootstrap composition root.

Verifies that engine.bootstrap.create_engine() correctly wires
all production components together.
"""

import unittest

from engine.bootstrap import create_engine
from engine.canvas.provider import PillowCanvasProvider
from engine.core.renderer import Renderer
from engine.export.exporter import PillowExporter
from engine.pipeline.pipeline import Pipeline
from engine.quality.verifier import QualityVerifier
from engine.templates.implementations.default import DefaultTemplate
from engine.templates.registry import TemplateRegistry
from engine.templates.resolver import TemplateResolver
from engine.validation.validator import Validator


class TestBootstrap(unittest.TestCase):
    """Test the bootstrap composition root."""

    def test_create_engine_returns_pipeline(self) -> None:
        """create_engine() should return a Pipeline instance."""
        pipeline = create_engine()
        self.assertIsInstance(pipeline, Pipeline)

    def test_pipeline_has_correct_dependencies(self) -> None:
        """Pipeline should have all real components injected."""
        pipeline = create_engine()

        # Pipeline uses private attributes; verify via type checks
        self.assertIsInstance(pipeline._validator, Validator)
        self.assertIsInstance(pipeline._configuration_resolver, object)
        self.assertIsInstance(pipeline._asset_resolver, object)
        self.assertIsInstance(pipeline._font_resolver, object)
        self.assertIsInstance(pipeline._template_resolver, TemplateResolver)
        self.assertIsInstance(pipeline._renderer, Renderer)
        self.assertIsInstance(pipeline._quality_verifier, QualityVerifier)
        self.assertIsInstance(pipeline._exporter, PillowExporter)

    def test_renderer_uses_canvas_provider(self) -> None:
        """Renderer should use a CanvasProvider."""
        pipeline = create_engine()
        renderer = pipeline._renderer
        self.assertTrue(hasattr(renderer, "_canvas_provider"))
        self.assertIsInstance(renderer._canvas_provider, PillowCanvasProvider)

    def test_exporter_format_is_jpeg(self) -> None:
        """Exporter should use JPEG format."""
        pipeline = create_engine()
        exporter = pipeline._exporter
        self.assertEqual(exporter.output_format, "JPEG")

    def test_exporter_quality_is_95(self) -> None:
        """Exporter should use quality 95 (default)."""
        pipeline = create_engine()
        exporter = pipeline._exporter
        self.assertEqual(exporter.quality, 95)

    def test_template_registry_contains_default(self) -> None:
        """TemplateRegistry should have 'default' registered."""
        pipeline = create_engine()
        resolver = pipeline._template_resolver
        registry = resolver._registry
        self.assertTrue(registry.has("default"))
        cls = registry.get("default")
        self.assertEqual(cls, DefaultTemplate)

    def test_template_resolver_has_default(self) -> None:
        """TemplateResolver should use 'default' as fallback."""
        pipeline = create_engine()
        resolver = pipeline._template_resolver
        self.assertEqual(resolver._default_template, "default")

    def test_bootstrap_does_not_resolve_request(self) -> None:
        """Bootstrap should not create Canvas or resolve dimensions."""
        pipeline = create_engine()
        # The provider should exist but no Canvas should be created yet
        renderer = pipeline._renderer
        provider = renderer._canvas_provider
        self.assertIsInstance(provider, PillowCanvasProvider)
        # No Canvas instance stored on renderer
        self.assertFalse(hasattr(renderer, "_canvas"))
        # No Canvas instance stored on provider
        self.assertFalse(hasattr(provider, "_canvas"))


if __name__ == "__main__":
    unittest.main()

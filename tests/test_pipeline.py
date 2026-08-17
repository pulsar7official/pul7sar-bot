"""Pipeline integration tests for PUL7SAR Visual Engine.

Phase 8 scope:
- verify Pipeline orchestration and exact forwarding between collaborators
- verify canonical Layer identity
- verify engine exceptions propagate unchanged
- do not implement production Canvas, QualityVerifier, or Exporter
"""

import unittest
import uuid
from typing import Any, Optional, Sequence

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.context import RenderContext
from engine.core.exceptions import (
    AssetError,
    ConfigurationError,
    ExportError,
    FontError,
    QualityVerificationError,
    RenderingError,
    TemplateError,
    ValidationError,
)
from engine.fonts.resolver import ResolvedFonts
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.pipeline.pipeline import Pipeline
from engine.validation.validator import ValidatedPayload


class CallLog:
    """Shared ordered lifecycle log used by all test doubles."""

    def __init__(self) -> None:
        self.events = []

    def add(self, event: str) -> None:
        self.events.append(event)


class FakeValidator:
    def __init__(
        self,
        log: CallLog,
        payload: Optional[ValidatedPayload] = None,
    ) -> None:
        self.log = log
        self.payload = payload or ValidatedPayload(data={"template": "test"})
        self.calls = []
        self.error: Optional[Exception] = None

    def validate(self, raw_request: Any) -> ValidatedPayload:
        self.log.add("validator")
        self.calls.append(raw_request)
        if self.error is not None:
            raise self.error
        return self.payload


class FakeConfigurationResolver:
    def __init__(
        self,
        log: CallLog,
        config: Optional[ResolvedConfiguration] = None,
    ) -> None:
        self.log = log
        self.config = config or ResolvedConfiguration(
            data={
                "engine": {"backend": "pillow", "width": 1280, "height": 720},
                "template": {"name": "default"},
                "platform": {"name": "telegram"},
            }
        )
        self.calls = []
        self.error: Optional[Exception] = None

    def resolve(
        self,
        validated_payload: ValidatedPayload,
    ) -> ResolvedConfiguration:
        self.log.add("configuration")
        self.calls.append(validated_payload)
        if self.error is not None:
            raise self.error
        return self.config


class FakeAssetResolver:
    def __init__(
        self,
        log: CallLog,
        assets: Optional[ResolvedAssets] = None,
    ) -> None:
        self.log = log
        self.assets = assets or ResolvedAssets(data={"logo": "logo.png"})
        self.calls = []
        self.error: Optional[Exception] = None

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedAssets:
        self.log.add("assets")
        self.calls.append((validated_payload, resolved_configuration))
        if self.error is not None:
            raise self.error
        return self.assets


class FakeFontResolver:
    def __init__(
        self,
        log: CallLog,
        fonts: Optional[ResolvedFonts] = None,
    ) -> None:
        self.log = log
        self.fonts = fonts or ResolvedFonts(
            data={"headline": "DejaVuSans-Bold.ttf"}
        )
        self.calls = []
        self.error: Optional[Exception] = None

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedFonts:
        self.log.add("fonts")
        self.calls.append((validated_payload, resolved_configuration))
        if self.error is not None:
            raise self.error
        return self.fonts


class FakeTemplate:
    def __init__(
        self,
        log: CallLog,
        layers: Optional[Sequence[Layer]] = None,
    ) -> None:
        self.log = log
        self.layers = layers if layers is not None else (
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=1,
                properties={"text": "Test Headline"},
            ),
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=2,
                properties={"text": "Test Body"},
            ),
        )
        self.calls = []
        self.error: Optional[Exception] = None

    def execute(self, render_context: RenderContext) -> Sequence[Layer]:
        self.log.add("template_execute")
        self.calls.append(render_context)
        if self.error is not None:
            raise self.error
        return self.layers


class FakeTemplateResolver:
    def __init__(
        self,
        log: CallLog,
        template: Optional[FakeTemplate] = None,
    ) -> None:
        self.log = log
        self.template = template or FakeTemplate(log)
        self.calls = []
        self.error: Optional[Exception] = None

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> FakeTemplate:
        self.log.add("template_resolve")
        self.calls.append((validated_payload, resolved_configuration))
        if self.error is not None:
            raise self.error
        return self.template


class FakeRenderer:
    def __init__(self, log: CallLog, result: Any = None) -> None:
        self.log = log
        self.result = object() if result is None else result
        self.calls = []
        self.error: Optional[Exception] = None

    def render(
        self,
        render_context: RenderContext,
        layers: Sequence[Layer],
    ) -> Any:
        self.log.add("renderer")
        self.calls.append((render_context, layers))
        if self.error is not None:
            raise self.error
        return self.result


class FakeQualityVerifier:
    def __init__(self, log: CallLog, result: Any = None) -> None:
        self.log = log
        self.result = result
        self.calls = []
        self.error: Optional[Exception] = None

    def verify(
        self,
        render_context: RenderContext,
        rendered_image: Any,
    ) -> Any:
        self.log.add("quality")
        self.calls.append((render_context, rendered_image))
        if self.error is not None:
            raise self.error
        # The real contract returns the same image unchanged unless a custom
        # sentinel is supplied for forwarding tests.
        return rendered_image if self.result is None else self.result


class FakeExporter:
    def __init__(
        self,
        log: CallLog,
        result: Any = "exported_file.png",
    ) -> None:
        self.log = log
        self.result = result
        self.calls = []
        self.error: Optional[Exception] = None

    def export(self, rendered_image: Any) -> Any:
        self.log.add("exporter")
        self.calls.append(rendered_image)
        if self.error is not None:
            raise self.error
        return self.result


class PipelineHarness:
    """Creates one consistent set of collaborators for each test."""

    def __init__(self) -> None:
        self.log = CallLog()
        self.validator = FakeValidator(self.log)
        self.configuration = FakeConfigurationResolver(self.log)
        self.assets = FakeAssetResolver(self.log)
        self.fonts = FakeFontResolver(self.log)
        self.template = FakeTemplate(self.log)
        self.template_resolver = FakeTemplateResolver(self.log, self.template)
        self.renderer = FakeRenderer(self.log)
        self.quality = FakeQualityVerifier(self.log)
        self.exporter = FakeExporter(self.log)
        self.pipeline = Pipeline(
            validator=self.validator,
            configuration_resolver=self.configuration,
            asset_resolver=self.assets,
            font_resolver=self.fonts,
            template_resolver=self.template_resolver,
            renderer=self.renderer,
            quality_verifier=self.quality,
            exporter=self.exporter,
        )


class TestPipelineLifecycle(unittest.TestCase):
    def setUp(self) -> None:
        self.h = PipelineHarness()

    def test_pipeline_executes_stages_in_exact_required_order(self) -> None:
        self.h.pipeline.execute({"sport": "football"})

        self.assertEqual(
            self.h.log.events,
            [
                "validator",
                "configuration",
                "assets",
                "fonts",
                "template_resolve",
                "template_execute",
                "renderer",
                "quality",
                "exporter",
            ],
        )

    def test_validator_receives_raw_request(self) -> None:
        raw_request = {"sport": "football"}
        self.h.pipeline.execute(raw_request)
        self.assertIs(self.h.validator.calls[0], raw_request)

    def test_configuration_receives_exact_validated_payload(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        self.assertIs(self.h.configuration.calls[0], self.h.validator.payload)

    def test_asset_resolver_receives_exact_upstream_objects(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        payload, config = self.h.assets.calls[0]
        self.assertIs(payload, self.h.validator.payload)
        self.assertIs(config, self.h.configuration.config)

    def test_font_resolver_receives_exact_upstream_objects(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        payload, config = self.h.fonts.calls[0]
        self.assertIs(payload, self.h.validator.payload)
        self.assertIs(config, self.h.configuration.config)

    def test_template_resolver_receives_payload_and_configuration(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        payload, config = self.h.template_resolver.calls[0]
        self.assertIs(payload, self.h.validator.payload)
        self.assertIs(config, self.h.configuration.config)

    def test_template_resolver_returns_instance_that_is_executed(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        self.assertEqual(len(self.h.template.calls), 1)

    def test_render_context_contains_exact_four_upstream_objects(self) -> None:
        self.h.pipeline.execute({"sport": "football"})
        context = self.h.template.calls[0]

        self.assertIs(context.validated_payload, self.h.validator.payload)
        self.assertIs(
            context.resolved_configuration,
            self.h.configuration.config,
        )
        self.assertIs(context.resolved_assets, self.h.assets.assets)
        self.assertIs(context.resolved_fonts, self.h.fonts.fonts)

    def test_same_render_context_instance_reaches_template_renderer_and_quality(self) -> None:
        self.h.pipeline.execute({"sport": "football"})

        template_context = self.h.template.calls[0]
        renderer_context = self.h.renderer.calls[0][0]
        quality_context = self.h.quality.calls[0][0]

        self.assertIs(template_context, renderer_context)
        self.assertIs(template_context, quality_context)

    def test_template_layers_are_passed_to_renderer_by_identity(self) -> None:
        custom_layers = (
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=100,
                properties={"text": "Z"},
            ),
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=1,
                properties={"text": "A"},
            ),
        )
        self.h.template.layers = custom_layers

        self.h.pipeline.execute({"sport": "football"})

        passed_layers = self.h.renderer.calls[0][1]
        self.assertIs(passed_layers, custom_layers)
        self.assertIs(passed_layers[0], custom_layers[0])
        self.assertIs(passed_layers[1], custom_layers[1])

    def test_pipeline_does_not_reorder_layers(self) -> None:
        custom_layers = (
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=100,
                properties={"text": "Z"},
            ),
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=1,
                properties={"text": "A"},
            ),
            Layer(
                kind=LayerKind.TEXT,
                zone=LayerZone.CONTENT,
                z_index=50,
                properties={"text": "M"},
            ),
        )
        self.h.template.layers = custom_layers

        self.h.pipeline.execute({"sport": "football"})

        passed_layers = self.h.renderer.calls[0][1]
        self.assertEqual(
            [layer.properties["text"] for layer in passed_layers],
            ["Z", "A", "M"],
        )

    def test_renderer_output_is_passed_to_quality_verifier_by_identity(self) -> None:
        rendered = object()
        self.h.renderer.result = rendered

        self.h.pipeline.execute({"sport": "football"})

        self.assertIs(self.h.quality.calls[0][1], rendered)

    def test_quality_output_is_passed_to_exporter_by_identity(self) -> None:
        verified = object()
        self.h.quality.result = verified

        self.h.pipeline.execute({"sport": "football"})

        self.assertIs(self.h.exporter.calls[0], verified)

    def test_pipeline_returns_exact_exporter_result(self) -> None:
        expected = object()
        self.h.exporter.result = expected
        result = self.h.pipeline.execute({"sport": "football"})
        self.assertIs(result, expected)


class TestPipelineRenderContextCreation(unittest.TestCase):
    def test_render_context_is_assembled_exactly_once_per_execution(self) -> None:
        h = PipelineHarness()
        original = h.pipeline._assemble_render_context
        calls = []

        def counted_assemble(**kwargs):
            calls.append(kwargs)
            return original(**kwargs)

        h.pipeline._assemble_render_context = counted_assemble  # type: ignore[method-assign]
        h.pipeline.execute({"sport": "football"})

        self.assertEqual(len(calls), 1)

    def test_render_id_is_valid_uuid(self) -> None:
        h = PipelineHarness()
        h.pipeline.execute({"sport": "football"})
        render_id = h.template.calls[0].render_id
        self.assertEqual(str(uuid.UUID(render_id)), render_id)

    def test_render_id_is_unique_per_execution(self) -> None:
        h = PipelineHarness()

        h.pipeline.execute({"sport": "football"})
        first_id = h.template.calls[-1].render_id

        h.pipeline.execute({"sport": "basketball"})
        second_id = h.template.calls[-1].render_id

        self.assertNotEqual(first_id, second_id)


class TestPipelineCanonicalLayer(unittest.TestCase):
    def test_pipeline_imports_the_canonical_layer_class(self) -> None:
        from engine.layers.layer import Layer as CanonicalLayer
        from engine.pipeline.pipeline import Layer as PipelineLayer

        self.assertIs(PipelineLayer, CanonicalLayer)

    def test_template_output_contains_canonical_layer_instances(self) -> None:
        h = PipelineHarness()
        h.pipeline.execute({"sport": "football"})

        passed_layers = h.renderer.calls[0][1]
        self.assertTrue(passed_layers)
        for layer in passed_layers:
            self.assertIs(type(layer), Layer)
            self.assertIs(type(layer.kind), LayerKind)
            self.assertIs(type(layer.zone), LayerZone)


class TestPipelineErrorPropagation(unittest.TestCase):
    def _assert_same_exception_propagates(
        self,
        h: PipelineHarness,
        collaborator: Any,
        error: Exception,
    ) -> None:
        collaborator.error = error

        with self.assertRaises(type(error)) as caught:
            h.pipeline.execute({"sport": "football"})

        self.assertIs(caught.exception, error)

    def test_validation_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.validator,
            ValidationError("validation failed"),
        )

    def test_configuration_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.configuration,
            ConfigurationError("configuration failed"),
        )

    def test_asset_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.assets,
            AssetError("asset failed"),
        )

    def test_font_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.fonts,
            FontError("font failed"),
        )

    def test_template_resolution_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.template_resolver,
            TemplateError("template resolution failed"),
        )

    def test_template_execution_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.template,
            TemplateError("template execution failed"),
        )

    def test_rendering_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.renderer,
            RenderingError("rendering failed"),
        )

    def test_quality_verification_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.quality,
            QualityVerificationError("quality verification failed"),
        )

    def test_export_error_propagates_unchanged(self) -> None:
        h = PipelineHarness()
        self._assert_same_exception_propagates(
            h,
            h.exporter,
            ExportError("export failed"),
        )


if __name__ == "__main__":
    unittest.main()

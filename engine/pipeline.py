"""Pipeline -- coordinates the complete rendering lifecycle.

Per 02_ARCHITECTURE.md, Section 15 ("Core Rendering Flow") and
04_RENDERING_SPECIFICATION.md, Section 13 ("Pipeline Specification"):

    Pipeline invokes, in order, passing each stage's output forward as
    the next stage's input:

        1. Validator                 (raises ValidationError)
        2. ConfigurationResolver     (raises ConfigurationError)
        3. AssetResolver             (raises AssetError)
        4. FontResolver              (raises FontError)
        5. Pipeline itself           -- RenderContext assembly
        6. Pipeline itself           -- Template Resolution/Selection
        7. Template                  (execution -> ordered Layers)
        8. Renderer                  (raises RenderingError)
        9. QualityVerifier           (raises QualityVerificationError)
       10. Exporter                  (raises ExportError)

RenderContext assembly and Template Resolution/Selection are the only
two acts Pipeline performs directly (Architecture Section 8, "Pipeline's
sole responsibilities..."). Neither contains validation, resolution,
execution, or rendering logic. Every other stage is delegated to the
subsystem that owns it; Pipeline never implements that subsystem's
responsibility and never catches-and-reinterprets its exceptions --
it only propagates them unchanged (Architecture Section 8, "Pipeline
must never"; Rendering Specification Section 5, "Fail Fast").

Why Protocols instead of concrete collaborators
------------------------------------------------
Validator, ConfigurationResolver, AssetResolver, FontResolver, Template,
Renderer, QualityVerifier, and Exporter are, at the time this module is
written, defined only as Phase 1 data contracts (see the docstrings in
engine/validation/validator.py, engine/configuration/resolver.py,
engine/assets/resolver.py, engine/fonts/resolver.py) -- their concrete
classes belong to later implementation stages and are explicitly out of
scope for this session. Pipeline nonetheless needs a typed contract for
each collaborator to orchestrate against and for tests to construct
fakes against. The ``typing.Protocol`` definitions below are the
"minimal interface... explicitly required by the frozen specification
for Pipeline integration" -- they describe only the single call each
stage owner already makes per the specification (Rendering
Specification Section 4; Architecture Section 15) and add no behavior,
no registry, and no factory of their own. Every concrete implementation
of these subsystems is injected into Pipeline's constructor; Pipeline
never constructs one.

Template Resolution/Selection specifically: Architecture Section 15,
Step 1.5 states the lookup mechanism Pipeline uses to map a request to
a concrete Template "is an implementation detail and is intentionally
unspecified" and that Pipeline "requires no knowledge of any Template's
internal implementation." Rather than inventing that lookup mechanism
(which would mean building the registry/factory this session was
explicitly told not to build), Pipeline delegates the lookup itself to
an injected ``TemplateResolverProtocol`` collaborator and treats
*calling it* as the selection act it is responsible for. This keeps
the actual mechanism outside Pipeline while Pipeline remains the
component that performs selection, per the specification.

Collaborator call shapes (and why RenderContext is withheld from some)
------------------------------------------------------------------------
Per Architecture Section 6 / "Data Ownership" and Rendering
Specification Section 6, RenderContext is shared read-only with
exactly three subsystems -- Template, Renderer, QualityVerifier -- and
is never received by Validator, ConfigurationResolver, AssetResolver,
FontResolver, Canvas, or Exporter (Architecture Step 7, "Exporter
receives the completed rendered image, unchanged from QualityVerifier"
-- RenderContext is not part of that input). The protocol signatures
below reflect that exactly: Exporter's protocol takes only the
rendered image, not RenderContext.

Renderer's Canvas implementation (Architecture Section 14,
"Responsibilities": Renderer receives RenderContext, ordered Layers,
and a Canvas implementation) is not threaded through Pipeline's call:
Canvas construction/selection is Renderer's own concern, resolved when
a concrete Renderer is built, not a value Pipeline owns or forwards --
Pipeline has no Canvas-related responsibility anywhere in the frozen
specifications.
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol, Sequence, runtime_checkable

from engine.assets.resolver import ResolvedAssets
from engine.configuration.resolver import ResolvedConfiguration
from engine.core.context import RenderContext
from engine.fonts.resolver import ResolvedFonts
from engine.layers.layer import Layer
from engine.validation.validator import ValidatedPayload


@runtime_checkable
class ValidatorProtocol(Protocol):
    """Contract for the Validator collaborator (Rendering Specification
    Section 4; Architecture Step 1.1). Validator internals are out of
    scope for this session."""

    def validate(self, raw_request: Any) -> ValidatedPayload: ...


@runtime_checkable
class ConfigurationResolverProtocol(Protocol):
    """Contract for the ConfigurationResolver collaborator (Rendering
    Specification Section 4; Architecture Step 1.2)."""

    def resolve(self, validated_payload: ValidatedPayload) -> ResolvedConfiguration: ...


@runtime_checkable
class AssetResolverProtocol(Protocol):
    """Contract for the AssetResolver collaborator (Rendering
    Specification Section 4; Architecture Step 1.3)."""

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedAssets: ...


@runtime_checkable
class FontResolverProtocol(Protocol):
    """Contract for the FontResolver collaborator (Rendering
    Specification Section 4; Architecture Step 1.4)."""

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> ResolvedFonts: ...


@runtime_checkable
class TemplateProtocol(Protocol):
    """Contract for a resolved Template (Rendering Specification
    Section 4; Architecture Step 3). Template Execution and Layer
    Generation are a single act owned entirely by Template."""

    def execute(self, render_context: RenderContext) -> Sequence[Layer]: ...


@runtime_checkable
class TemplateResolverProtocol(Protocol):
    """Contract Pipeline calls to perform Template Resolution/Selection
    (Architecture Step 1.5; Rendering Specification Section 13, item 6).
    The lookup mechanism itself is intentionally unspecified by the
    frozen specification and is therefore injected, not implemented
    here."""

    def resolve(
        self,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
    ) -> TemplateProtocol: ...


@runtime_checkable
class RendererProtocol(Protocol):
    """Contract for the Renderer collaborator (Rendering Specification
    Section 4; Architecture Step 4). Canvas is Renderer's own internal
    concern, not forwarded by Pipeline (see module docstring)."""

    def render(self, render_context: RenderContext, layers: Sequence[Layer]) -> Any: ...


@runtime_checkable
class QualityVerifierProtocol(Protocol):
    """Contract for the QualityVerifier collaborator (Rendering
    Specification Section 12; Architecture Step 6)."""

    def verify(self, render_context: RenderContext, rendered_image: Any) -> Any: ...


@runtime_checkable
class ExporterProtocol(Protocol):
    """Contract for the Exporter collaborator (Architecture Step 7).
    Receives only the rendered image -- never RenderContext (see
    module docstring)."""

    def export(self, rendered_image: Any) -> Any: ...


class Pipeline:
    """Orchestrates the rendering lifecycle end to end.

    Pipeline is an orchestrator, not a god object: it contains no
    validation, resolution, template-execution, rendering, quality
    -verification, or export logic of its own. Its only direct acts
    are RenderContext assembly and invoking the injected Template
    -Resolution collaborator (Architecture Section 8).
    """

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
    ) -> None:
        self._validator = validator
        self._configuration_resolver = configuration_resolver
        self._asset_resolver = asset_resolver
        self._font_resolver = font_resolver
        self._template_resolver = template_resolver
        self._renderer = renderer
        self._quality_verifier = quality_verifier
        self._exporter = exporter

    def execute(self, raw_request: Any) -> Any:
        """Run one rendering request through the full lifecycle.

        Stage order and forwarding follow Rendering Specification
        Section 3 / Section 13 exactly. Every exception raised by a
        stage propagates unchanged -- Pipeline does not catch, wrap,
        reinterpret, or substitute fallback output for any of them
        (Architecture Section 8; Rendering Specification Section 5,
        "Fail Fast").
        """
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

    @staticmethod
    def _assemble_render_context(
        *,
        validated_payload: ValidatedPayload,
        resolved_configuration: ResolvedConfiguration,
        resolved_assets: ResolvedAssets,
        resolved_fonts: ResolvedFonts,
    ) -> RenderContext:
        """Create the single RenderContext for this execution.

        Assembly only (Architecture Step 2; Rendering Specification
        Section 6, Section 13 item 5) -- no validation or resolution
        logic. ``render_id`` is generated here because RenderContext
        requires one and no upstream stage produces it; every other
        field is left at RenderContext's own defaults, which is the
        smallest assembly that satisfies the data contract without
        inventing metadata the frozen specification does not require.
        """
        return RenderContext(
            validated_payload=validated_payload,
            resolved_configuration=resolved_configuration,
            resolved_assets=resolved_assets,
            resolved_fonts=resolved_fonts,
            render_id=str(uuid.uuid4()),
        )

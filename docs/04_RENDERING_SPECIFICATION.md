# PUL7SAR Rendering Specification

Version: 1.0

Status: Official Engineering Specification

---

# 1. Purpose

This document defines the rendering subsystem of the PUL7SAR Visual Engine.

It specifies every component involved in transforming a validated rendering request into one or more exported visual assets.

This document is normative.

If implementation conflicts with this specification, the specification takes precedence.

---

# 2. Rendering Philosophy

Rendering is a deterministic transformation.

Input:

Validated rendering request.

Output:

Rendered visual assets.

Rendering must never depend on hidden global state.

Rendering must produce identical results for identical inputs.

---

3. Rendering Lifecycle

Every render follows the exact same lifecycle.

Request

↓

Validation — owned by Validator (raises ValidationError)

↓

Configuration Resolution — owned by ConfigurationResolver (raises
ConfigurationError)

↓

Asset Resolution — owned by AssetResolver (raises AssetError)

↓

Font Resolution — owned by FontResolver (raises FontError)

↓

RenderContext Creation — owned by Pipeline (assembly only; no
validation/resolution logic)

↓

Template Resolution / Selection — owned by Pipeline (selects which
Template to invoke; does not execute it)

↓

Template Execution (produces Layer Generation as its direct output) —
owned by Template

↓

Rendering — owned by Renderer (raises RenderingError)

↓

Quality Verification — owned by QualityVerifier (raises
QualityVerificationError)

↓

Export — owned by Exporter (raises ExportError)

↓

Completed Result

No stage may be skipped.

Each stage must receive the outputs required from the preceding stages.

No stage may modify the authoritative outputs of a previous stage.

RenderContext is created only after validation, configuration resolution,
asset resolution, and font resolution have been completed.

Once created, RenderContext represents the resolved and immutable state
of the current rendering request and is shared by the rendering
subsystems that require it.

Pipeline is responsible for coordinating this lifecycle by invoking the
subsystem that owns each stage. Pipeline does not implement any stage's
responsibility itself, with the sole exception of RenderContext
assembly and Template Resolution/Selection, neither of which contains
validation, resolution, execution, or rendering logic of its own.

No other component may reorder, skip, or independently orchestrate
these stages.

# 4. Core Rendering Components

The rendering subsystem consists of the following components.

## Validator

Validates the raw incoming rendering request and produces a
ValidatedPayload. Raises ValidationError. Depends on no other
subsystem. Full contract: Architecture Specification, Section 15, Step
1.1.

---

## ConfigurationResolver

Resolves engine/template/platform configuration for a ValidatedPayload
and produces ResolvedConfiguration. Raises ConfigurationError. Depends
only on ValidatedPayload. Full contract: Architecture Specification,
Section 15, Step 1.2.

---

## AssetResolver

Resolves required visual assets and produces ResolvedAssets. Raises
AssetError. Depends only on ValidatedPayload and ResolvedConfiguration.
Full contract: Architecture Specification, Section 15, Step 1.3.

---

## FontResolver

Resolves required fonts and produces ResolvedFonts. Raises FontError.
Depends only on ValidatedPayload and ResolvedConfiguration. Full
contract: Architecture Specification, Section 15, Step 1.4.

---

## RenderContext

Immutable render request state.

---

## Template

Describes visual composition and produces an ordered list of Layer
objects. Templates never render, never access Canvas, and never
perform drawing.

---

## Layer

Declarative drawing instruction.

---

## Renderer

Transforms Layers into pixels.

---

## Canvas

Backend abstraction responsible for drawing.

---

## QualityVerifier

Verifies the structural/output integrity of the rendered result before
export. Independent from Renderer, Canvas, Exporter, and Pipeline.
Never renders, never modifies the rendered image, Layers, or
RenderContext.

---

## Pipeline

Coordinates the rendering process by invoking the subsystem responsible
for each lifecycle stage. Never implements a stage's responsibility
itself.

---

## Exporter

Produces platform-specific outputs.

---

# 5. Rendering Principles

The following principles are mandatory.

### Deterministic Rendering

Equal input must always generate equal output.

---

### Backend Independence

Templates must never know which rendering backend is used.

---

### Stateless Rendering

Rendering components must not depend on shared mutable state.

---

### Fail Fast

The Visual Engine does not perform fallback substitution or produce
degraded output on failure.

Every failure — recoverable or not — is raised as the appropriate
VisualEngineError subtype (see Architecture Specification, Section 12)
and propagated to the caller of Pipeline unchanged.

No subsystem may catch an error from a stage it does not own and
continue the lifecycle with substitute, default, or partial output.

---

### Platform Independence

Rendering occurs once.

Exporting adapts the result for each platform.

---

# 6. RenderContext

RenderContext represents one immutable rendering request.

It is created once by the Pipeline, after Validation, Configuration
Resolution, Asset Resolution, and Font Resolution have all completed
(see Section 3).

RenderContext is shared read-only with exactly three subsystems:
Template, Renderer, and QualityVerifier.

Validator, ConfigurationResolver, AssetResolver, FontResolver, Canvas,
and Exporter never receive RenderContext.

No subsystem may modify RenderContext.

RenderContext contains:

- ValidatedPayload
- ResolvedConfiguration
- ResolvedAssets
- ResolvedFonts
- render metadata
- render identifier
- platform targets
- canvas information
- locale information

RenderContext contains data only.

It never contains rendering logic.

---

# 7. Layer

Layer represents one declarative drawing instruction.

A Layer never draws itself.

A Layer only describes drawing.

Every Layer contains:

- kind
- zone
- z_index
- properties

Layers are immutable after creation.

Layer ordering (zone order, then z_index, then insertion order) is
authoritatively defined in the Architecture Specification, Section 11
(Layer System Specification).

---
---

# 8. LayerKind Specification

LayerKind defines the semantic type of a Layer.

Every Layer must have exactly one LayerKind.

Allowed values are:

- BACKGROUND
- IMAGE
- TEXT
- ICON
- SHAPE
- GRADIENT
- TEXTURE
- OVERLAY

No additional values may be introduced without updating this specification.

---

## BACKGROUND

Represents the base visual surface.

Examples:

- solid color
- stadium image
- abstract background

---

## IMAGE

Represents raster or vector imagery.

Examples:

- player photo
- club badge
- competition logo

---

## TEXT

Represents textual content.

Examples:

- headline
- subtitle
- statistics
- captions

---

## ICON

Represents lightweight symbolic graphics.

Examples:

- whistle
- football
- warning icon
- trophy icon

---

## SHAPE

Represents geometric primitives.

Examples:

- rectangle
- rounded rectangle
- circle
- line

---

## GRADIENT

Represents color transitions.

Gradients must never contain business logic.

---

## TEXTURE

Represents reusable surface effects.

Examples:

- dust
- grain
- turf
- paper
- motion blur

---

## OVERLAY

Represents reusable visual effects.

Examples:

- lighting
- watermark
- pulse effect
- glow

---

# 9. LayerZone Specification

LayerZone determines where a Layer belongs within the rendering stack.

Allowed values:

- BACKGROUND
- CONTENT
- BRAND
- FOOTER

---

## BACKGROUND

Contains:

- gradients
- background images
- textures
- lighting

Generated only by BaseTemplate.

---

## CONTENT

Contains all template-specific visual elements.

Generated only by template implementations.

---

## BRAND

Contains:

- logo
- pulse mark
- watermark

Generated only by BaseTemplate.

---

## FOOTER

Contains:

- social handle
- copyright
- footer branding

Generated only by BaseTemplate.

---

## 10. Canvas Specification

Canvas is the rendering backend abstraction.

Canvas is responsible only for drawing operations.

Canvas never knows:

- sports
- templates
- branding
- business logic

Canvas exposes drawing capabilities only.

The following six operations are the complete normative drawing interface
of Canvas for the current engine version:

- draw_image
- draw_text
- draw_shape
- draw_gradient
- draw_texture
- draw_overlay

No additional Canvas drawing operation may be introduced without updating
this specification and the Architecture Specification.

Canvas also exposes the following result-retrieval operation:

- get_result

get_result is not a drawing primitive.

It is used only to retrieve the completed rendered image after all Layer
drawing operations have finished.

Renderer MUST call get_result exactly once after dispatching the complete
ordered Layer collection.

Canvas implementations may vary.

The remainder of the system must remain unaware of the chosen backend.

### Error Propagation

Canvas implementations MUST raise RenderingError whenever a drawing
operation cannot be completed.

Backend-specific exceptions (e.g. a Pillow or Skia internal error) MUST
NOT escape the Canvas boundary. Canvas implementations MUST catch and
re-raise such failures as RenderingError.

---

# 11. Renderer Specification

Renderer transforms ordered Layers into pixels.

Renderer receives:

- RenderContext
- ordered Layer collection
- Canvas implementation

Renderer produces:

- rendered image

Renderer never:

- resolves assets
- resolves fonts
- validates payloads
- exports files

Renderer only renders.
LayerKind Dispatch

The Renderer shall dispatch LayerKind values to Canvas operations using
the following fixed mapping:

BACKGROUND -> draw_image
IMAGE -> draw_image
TEXT -> draw_text
ICON -> draw_image
SHAPE -> draw_shape
GRADIENT -> draw_gradient
TEXTURE -> draw_texture
OVERLAY -> draw_overlay

This mapping is normative.

Renderer implementations must not introduce additional Canvas operations
without updating this specification.

### Error Propagation

A LayerKind with no entry in the normative dispatch table above MUST
cause Renderer to raise RenderingError.

A Canvas implementation missing a required operation MUST cause
Renderer to raise RenderingError when that operation is requested.

Renderer MUST NOT expose raw backend-specific exceptions surfaced by
Canvas; any exception received from Canvas is already RenderingError
(see Section 10, Error Propagation) and Renderer propagates it
unchanged — it does not catch and reinterpret it.

---

# 12. QualityVerifier Specification

QualityVerifier is a dedicated subsystem, architecturally equivalent in
status to Renderer and Exporter. It is independent from Renderer,
Canvas, Exporter, and Pipeline.

Purpose:

Verify the structural/output integrity of the rendered result before
it is passed to Exporter.

QualityVerifier receives:

- RenderContext
- Rendered Image (the result produced by Renderer via Canvas.get_result)

QualityVerifier verifies:

- that a rendered result exists
- that rendered dimensions match the resolved Canvas/platform
  information in RenderContext
- that the image is structurally valid and decodable
- that the image format/mode is compatible with the resolved Canvas
  information

Successful behavior:

QualityVerifier returns the exact same rendered image object,
unchanged.

Failure behavior:

QualityVerifier raises QualityVerificationError. QualityVerificationError
inherits directly from VisualEngineError and is a sibling of
RenderingError and ExportError, not a subtype of either.

QualityVerifier never:

- renders
- draws
- accesses Canvas
- modifies the rendered image
- modifies Layers
- modifies RenderContext
- resolves assets
- resolves fonts
- executes templates
- exports
- validates payloads or requests
- evaluates sports or content correctness
- evaluates language quality
- evaluates branding compliance
- performs aesthetic or design judgment
- performs AI-based evaluation

Pipeline coordinates QualityVerifier as a lifecycle stage. Pipeline does
not implement quality verification logic itself.

---

# 13. Pipeline Specification

Pipeline coordinates the complete rendering lifecycle.

Pipeline invokes the following subsystems, in this order, and passes
each subsystem's output forward as the input to the next stage:

1. Validator — validation (raises ValidationError)
2. ConfigurationResolver — configuration resolution (raises
   ConfigurationError)
3. AssetResolver — asset resolution (raises AssetError)
4. FontResolver — font resolution (raises FontError)
5. Pipeline itself — RenderContext assembly from the four outputs above
   (no validation/resolution logic of its own)
6. Pipeline itself — Template Resolution/Selection (choosing which
   Template to invoke; not execution)
7. Template — Template Execution, whose direct output is Layer
   Generation
8. Renderer — rendering (raises RenderingError)
9. QualityVerifier — quality verification (raises
   QualityVerificationError; see Section 12)
10. Exporter — exporting (raises ExportError)

For every stage above except RenderContext assembly and Template
Resolution/Selection, Pipeline invokes the owning subsystem and does
not implement that subsystem's responsibility itself. RenderContext
assembly and Template Resolution/Selection are the only two acts
Pipeline performs directly, and neither contains validation,
resolution, execution, or rendering logic.

Pipeline propagates every exception raised by a subsystem it
coordinates (ValidationError, ConfigurationError, AssetError,
FontError, TemplateError, RenderingError, QualityVerificationError,
ExportError) unchanged. The pipeline propagates without
reinterpretation. Pipeline does not substitute fallback or degraded
output on failure (see Section 5, "Fail Fast").

Pipeline is the only component allowed to orchestrate multiple
subsystems.

Pipeline must execute these stages in the order defined by the
Rendering Lifecycle (Section 3).

Pipeline must not perform the responsibilities of the subsystems it
coordinates.

No other component may coordinate the rendering lifecycle.

End of Part 2.

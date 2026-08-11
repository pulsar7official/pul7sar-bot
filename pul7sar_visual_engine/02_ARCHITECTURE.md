# PUL7SAR Software Architecture

Version: 2.0

Status: Official Engineering Specification

---

# 1. Executive Summary

PUL7SAR is a modular, scalable, and maintainable sports media platform designed to deliver high-quality visual content across multiple digital platforms.

The architecture separates responsibilities into independent subsystems that communicate through well-defined interfaces.

Every subsystem is designed to be replaceable without affecting the rest of the platform.

The primary architectural goals are:

- Scalability
- Maintainability
- Reliability
- Performance
- Extensibility
- Testability

No subsystem should depend on implementation details of another subsystem.

All dependencies must flow toward abstractions.

---

# 2. Architectural Goals

The architecture must satisfy the following goals.

## 2.1 Separation of Responsibilities

Each module has one clearly defined responsibility.

Business logic, rendering logic, configuration, assets, templates, and exporting must remain independent.

---

## 2.2 Scalability

The platform must support future expansion without requiring architectural redesign.

New templates, renderers, export targets, and asset providers should be added without modifying existing core modules.

---

## 2.3 Reliability

Rendering failures must never compromise the entire rendering pipeline.

Every failure — recoverable or not — must propagate as the appropriate
VisualEngineError subtype (see Section 12, Exception Hierarchy) rather
than being silently absorbed or substituted with degraded output.

The Visual Engine does not perform fallback substitution. See Section 5
of the Rendering Specification ("Fail Fast") for the normative
principle.

---

## 2.4 Maintainability

Code should be understandable by engineers unfamiliar with the project.

Every public component must have a documented responsibility.

---

## 2.5 Extensibility

The architecture must allow future support for:

- Additional sports
- Additional languages
- Additional social platforms
- Additional rendering engines
- Animation
- Video generation

without modifying existing architecture.

---

# 3. Architectural Principles

PUL7SAR follows the following engineering principles.

- SOLID
- DRY
- KISS
- Clean Architecture
- Composition over Inheritance
- Dependency Injection
- Configuration over Hardcoding
- Immutable Data Structures

These principles are mandatory.

---

# 4. System Boundaries

The Visual Engine is responsible only for visual generation.

It is not responsible for:

- collecting news
- scraping websites
- AI text generation
- translation
- scheduling
- Telegram publishing
- social media publishing
- databases

The Visual Engine receives validated input and produces visual output.

Nothing more.

---

# 5. High-Level Architecture

The platform consists of independent subsystems.

```

                 News Pipeline
                       │
                       ▼
              Content Processing
                       │
                       ▼
              Visual Engine (this project)
                       │
                       ▼
         Delivery / Publishing System
                       │
                       ▼
              Publishing Services

```

Each subsystem communicates through defined interfaces.

No subsystem may directly manipulate another subsystem's internal implementation.

The Visual Engine's own internal export stage (Visual Export System,
Layer 5 — see Section 6) is distinct from, and upstream of, the
external Delivery / Publishing System shown above. The Visual Engine
produces finished, platform-adapted visual assets; it does not deliver
or publish them.

---

# 6. Core Architectural Layers

The Visual Engine consists of five architectural layers.

## Layer 1

Configuration

Responsible for accepting and resolving the incoming rendering request.

Owns two subsystems:

- **Validator** — validates the raw incoming request and produces a
  ValidatedPayload. Raises ValidationError.
- **ConfigurationResolver** — resolves engine/template/platform
  configuration for the request and produces ResolvedConfiguration.
  Raises ConfigurationError. Depends only on ValidatedPayload.

Neither subsystem renders, touches assets/fonts, or executes templates.
Full contracts are defined in Section 15, Step 1.

---

## Layer 2

Resources

Responsible for assets, fonts, overlays and branding resources.

Owns two subsystems:

- **AssetResolver** — resolves required visual assets and produces
  ResolvedAssets. Raises AssetError.
- **FontResolver** — resolves required fonts and produces
  ResolvedFonts. Raises FontError.

Both depend only on ValidatedPayload and ResolvedConfiguration produced
by Layer 1. Neither depends on the other. Full contracts are defined in
Section 15, Step 1.

---

## Layer 3

Template System

Responsible for describing visual composition.

Templates never render pixels.

Owns Template Execution and Layer Generation (a single act — see
Section 15, Step 3). Template Resolution/Selection is owned by
Pipeline, not by this layer (see Section 15, Step 1.5).

---

## Layer 4

Rendering System

Responsible for transforming declarative layers into rendered images, and
for verifying the structural/output integrity of the rendered result
before it is passed to the Visual Export System.

---

## Layer 5

Visual Export System

Responsible for platform-specific output generation.

Owns Exporter. Internal to the Visual Engine — not to be confused with
the external Delivery / Publishing System shown in Section 5, which is
outside the Visual Engine's boundary (see Section 4, System
Boundaries).

---

# 7. Dependency Rules

Dependencies always flow downward.

Configuration

↓

Resources

↓

Templates

↓

Rendering

↓

Export

Reverse dependencies are prohibited.

Circular dependencies are prohibited.

Direct access between unrelated layers is prohibited.

---

# 8. Architectural Constraints

The following constraints are mandatory.

Validator must never:

- resolve configuration
- resolve assets
- resolve fonts
- create RenderContext
- render pixels
- know templates

ConfigurationResolver must never:

- validate the raw request (it receives an already-validated payload)
- resolve assets
- resolve fonts
- create RenderContext
- render pixels
- know templates

AssetResolver must never:

- validate the raw request
- resolve configuration
- resolve fonts
- know templates
- know rendering logic

FontResolver must never:

- validate the raw request
- resolve configuration
- resolve assets
- know templates
- know rendering logic

Templates must never:

- render pixels
- load files
- resolve fonts
- resolve assets
- export images

Renderer must never:

- contain business logic
- understand sports
- know template types

Exporter must never:

- modify visual composition
- perform rendering

QualityVerifier must never:

- render pixels
- issue Canvas drawing operations
- modify the rendered image
- modify Layers
- modify RenderContext
- resolve assets
- resolve fonts
- execute templates
- export files
- validate payloads or requests
- evaluate sports, textual, or linguistic correctness
- evaluate branding compliance
- perform aesthetic or design judgment
- use AI-based quality evaluation
- contain business logic

Pipeline must never:

- implement validation logic
- implement configuration resolution logic
- implement asset resolution logic
- implement font resolution logic
- implement template execution logic
- implement rendering logic
- implement quality verification logic
- implement export logic
- substitute fallback or degraded output after a failure
- catch and reinterpret an exception raised by a subsystem it
  coordinates

Pipeline's sole responsibilities are RenderContext assembly, Template
Resolution/Selection, and invoking the subsystem that owns each other
stage, in lifecycle order, passing each stage's output forward as
input to the next.

---

# 9. Technology Independence

The architecture must remain independent of implementation technology.

Rendering backend implementations may change in the future.

Examples include:

- Pillow
- Skia
- Cairo
- SVG
- GPU rendering

Changing rendering technology must not require changes to templates.

---

# 10. Long-Term Scalability

The architecture is designed for long-term growth.

Future additions should include:

- video rendering
- motion graphics
- AI-assisted layouts
- remote asset repositories
- distributed rendering
- rendering queues
- cloud workers

These additions must integrate through existing architectural interfaces rather than replacing them.

---

# 11. Layer System Specification

The Layer system is the fundamental abstraction of the PUL7SAR Visual Engine.

Templates never draw pixels directly.

Instead, every template produces an ordered collection of Layer objects.

The Renderer is the only component allowed to interpret Layer objects and convert them into pixels.

A Layer must contain description only.

A Layer must never perform drawing, rendering, loading, or business logic.

---

### LayerKind

Every Layer MUST belong to exactly one LayerKind.

The PUL7SAR Visual Engine v1 defines exactly the following LayerKind values:

- BACKGROUND
- IMAGE
- TEXT
- ICON
- SHAPE
- GRADIENT
- TEXTURE
- OVERLAY

These eight values are the complete and authoritative LayerKind vocabulary for the current engine version.

No additional LayerKind may be introduced by implementation code, templates, or rendering backends without first updating the official Rendering Specification and Architecture Specification.

LayerKind values are semantic classifications only.

LayerKind must never contain business logic, branding rules, sports-specific meaning, or backend-specific behavior.

---

### LayerZone

Every layer belongs to exactly one visual zone.

Zones are rendered in fixed order.

The engine defines four standard zones:

1. BACKGROUND
2. CONTENT
3. BRAND
4. FOOTER

Templates may only create CONTENT layers.

BACKGROUND, BRAND and FOOTER layers are produced exclusively by BaseTemplate.

---

### Layer Ordering

Layers are rendered by:

Zone Order

↓

z_index

↓

Insertion Order

The renderer must never reorder layers automatically.

---

### Layer Structure

Every Layer contains:

- kind
- zone
- z_index
- properties

properties is a generic immutable mapping containing renderer-specific parameters.

Layer itself never interprets properties.

---

### Design Rules

Layer must be immutable.

Layer must contain no rendering logic.

Layer must contain no helper methods.

Layer must be backend independent.

Layer must be serializable.

Layer must be deterministic.

Two equal Layers must always describe identical rendering operations.
# 12. Exception Hierarchy

The Visual Engine MUST use a dedicated exception hierarchy.

All engine-specific exceptions MUST inherit from a single base exception.

Python built-in exceptions MUST NOT be exposed across subsystem boundaries.

---

## Base Exception

VisualEngineError

The root exception for every error produced by the Visual Engine.

---

## Configuration Errors

ConfigurationError

Raised when engine configuration cannot be loaded, validated, or resolved.

Examples:

- Missing configuration file.
- Invalid configuration value.
- Invalid YAML schema.

---

## Asset Errors

AssetError

Raised when an asset cannot be found or loaded.

Examples:

- Missing logo.
- Missing background.
- Unsupported image format.
- Corrupted asset.

---

## Font Errors

FontError

Raised when a required font cannot be loaded.

Examples:

- Font file missing.
- Invalid font.
- Unsupported font format.

---

## Template Errors

TemplateError

Raised when a template cannot be created or executed.

Examples:

- Unknown template.
- Invalid template implementation.
- Missing required layer.

---

## Rendering Errors

RenderingError

Raised whenever rendering cannot complete successfully.

Raised by Canvas implementations when a drawing operation cannot be
completed, and by Renderer when an unsupported LayerKind is dispatched
or a required Canvas operation is missing.

Examples:

- Canvas creation failed.
- Drawing operation failed.
- Renderer internal failure.
- Unsupported LayerKind dispatched (no entry in the normative dispatch
  table).
- Canvas implementation missing a required operation.

---

## Quality Verification Errors

QualityVerificationError

Raised when the rendered result fails structural/output integrity
verification.

QualityVerificationError inherits directly from VisualEngineError. It is
a sibling of RenderingError and ExportError, not a subtype of either.

Examples:

- No rendered result was produced.
- Rendered dimensions do not match the resolved Canvas/platform
  information in RenderContext.
- Rendered image is structurally invalid or not decodable.
- Rendered image format/mode is incompatible with the resolved Canvas
  information.

---

## Export Errors

ExportError

Raised when exporting the final image fails.

Examples:

- Cannot save image.
- Unsupported export format.
- File system write failure.

---

## Validation Errors

ValidationError

Raised by Validator when the raw incoming rendering request fails
validation.

Examples:

- Missing required payload field.
- Invalid render request.
- Unsupported platform profile.

---

## Rules

• Every engine exception MUST inherit from VisualEngineError.

• Exceptions MUST NOT contain rendering logic.

• Exceptions SHOULD contain only human-readable error messages.

• Exceptions MAY wrap lower-level exceptions using Python exception chaining.

• Engine subsystems MUST raise engine exceptions instead of raw built-in exceptions whenever possible.

• Each of ValidationError, ConfigurationError, AssetError, and FontError
  is raised exclusively by its named owning subsystem (Validator,
  ConfigurationResolver, AssetResolver, FontResolver respectively, per
  Section 15, Step 1). Pipeline never raises these directly; it
  propagates them unchanged.

• Canvas and Renderer never expose backend-specific (non-engine)
  exceptions across their boundaries; all such failures are raised as
  RenderingError. Pipeline propagates RenderingError, ValidationError,
  ConfigurationError, AssetError, FontError, TemplateError,
  QualityVerificationError, and ExportError unchanged — it never
  catches and reinterprets an exception raised by a subsystem it
  coordinates.
# 13. Canvas Abstraction

The Canvas is the backend-independent drawing surface of the Visual Engine.

Templates never draw on the Canvas directly.

The Renderer is the only subsystem allowed to issue drawing operations to the Canvas.

The Canvas itself is only an abstraction.

Concrete implementations (Pillow, Skia, Cairo, SVG, etc.) are provided by backend adapters.

---

## Responsibilities

The Canvas is responsible for exposing a minimal drawing interface.

It does not contain business logic.

It does not know templates.

It does not know football.

It does not know branding rules.

It only knows how to execute primitive drawing operations.

---

## Design Principles

The Canvas MUST remain backend independent.

No template may import a backend implementation.

The Renderer communicates only with the Canvas abstraction.

Concrete implementations are injected by the rendering pipeline.

---

## Supported Primitive Operations

The Canvas abstraction exposes exactly the following drawing operations:

- draw_image
- draw_text
- draw_shape
- draw_gradient
- draw_texture
- draw_overlay

These six operations constitute the complete normative drawing interface of Canvas for the current engine version.

No additional drawing operation may be introduced by Renderer, Layer, Template, or backend implementation unless the official Canvas Specification and Rendering Specification are updated first.

LayerKind values must map to these Canvas operations according to the normative LayerKind Dispatch table defined in Section 14.

Canvas implementations may maintain internal rendering state, but the abstract Canvas interface must not expose mutable state.

The Canvas abstraction also exposes one result-retrieval operation:

- get_result

get_result is not a drawing primitive. It is the finalization and result-access operation used by Renderer after all Layer drawing operations have completed.

Renderer MUST call get_result exactly once, after the complete ordered Layer collection has been dispatched.

get_result returns the completed rendered image owned by the Canvas until it is passed to the Exporter.

---

## State

Canvas implementations may maintain internal rendering state.

The abstract Canvas interface itself must not expose mutable state.

---

## Error Handling

Canvas implementations must raise RenderingError whenever a drawing operation cannot be completed.

Backend-specific exceptions must never escape outside the Canvas boundary.
# 14. Renderer Architecture

The Renderer is the execution engine of the Visual Engine.

Templates never draw.

Layers never draw.

Canvas never decides what to draw.

The Renderer is the only subsystem responsible for transforming a list of Layer objects into drawing operations executed on a Canvas.

---

## Responsibilities

The Renderer is responsible for:

- Receiving a RenderContext.
- Receiving an ordered collection of Layer objects.
- Rendering Layers in deterministic order.
- Selecting the correct Canvas operation for every LayerKind.
- Producing the final rendered result.

The Renderer never creates Layers.

The Renderer never modifies Layers.

The Renderer never modifies RenderContext.

---

## Rendering Pipeline

Rendering always follows the same sequence.

1. Receive RenderContext.
2. Receive ordered Layers.
3. Confirm required inputs (RenderContext, Layers, and Canvas) were received.
4. Iterate through Layers.
5. Dispatch every Layer to the corresponding Canvas operation.
6. Finish rendering.
7. Return the rendered output.

Step 3 is a defensive precondition check only. It is not payload or
request validation. Payload/request validation is owned exclusively by
Validator (see Section 15, Step 1.1), as established in the Rendering
Specification (Renderer Specification: "Renderer never: ... validates
payloads"). Pipeline itself does not implement validation logic either
— it only invokes Validator (see Section 8, "Pipeline must never").

The Renderer must never skip or reorder Layers.

---

## Layer Dispatch

Each LayerKind maps to exactly one Canvas operation.

| LayerKind | Canvas Method |
|-----------|---------------|
| BACKGROUND | draw_image |
| IMAGE | draw_image |
| TEXT | draw_text |
| ICON | draw_image |
| SHAPE | draw_shape |
| GRADIENT | draw_gradient |
| TEXTURE | draw_texture |
| OVERLAY | draw_overlay |

Dispatching must be deterministic and must follow the normative mapping above exactly.

The Renderer MUST use the LayerKind values defined in Section 11 and MUST use only the Canvas operations defined in Section 13.

The Renderer MUST NOT invent, infer, rename, or introduce Canvas operations for any LayerKind.

The Renderer MUST NOT introduce special handling for individual LayerKind values outside the normative dispatch table.

A LayerKind without a corresponding entry in the normative dispatch table MUST raise RenderingError.

A Canvas implementation missing a required operation MUST raise RenderingError when that operation is requested.

Dictionary-based dispatch is the preferred implementation strategy, but the implementation mechanism must not alter the normative mapping.
---

## Error Handling

Unknown LayerKind must raise RenderingError.

Canvas failures must be propagated as RenderingError.

The Renderer must never expose backend-specific exceptions.

---

## Design Principles

Renderer must be stateless.

Renderer must be deterministic.

Renderer must be backend independent.

Renderer must never contain branding rules.

Renderer must never know football concepts.

Renderer must never modify input data.

Renderer must depend only on abstractions.

---

## Performance

Renderer must execute in a single pass.

Complexity should remain O(n).

No recursive rendering.

No hidden sorting.

No duplicated traversal.

---

## Extensibility

The current engine defines a closed LayerKind vocabulary consisting of the eight values specified in Section 11.

Adding a new LayerKind is an architectural change and MUST NOT be performed implicitly by implementation code.

To introduce a new LayerKind, the following specifications MUST be updated first:

1. Section 11 — LayerKind Specification.
2. Section 13 — Canvas Abstraction, if a new Canvas operation is required.
3. Section 14 — Renderer Layer Dispatch.
4. 04_RENDERING_SPECIFICATION.md and any other normative specification affected by the change.

Only after the specifications have been updated may implementation code introduce the new LayerKind.

Existing LayerKind behavior and mappings must remain unchanged unless explicitly revised by the updated specifications.
# 15. Core Rendering Flow

This section defines the complete execution flow of the Visual Engine.

Every rendering request MUST follow this sequence without deviation.

---

## Step 1 — Pipeline

The Pipeline orchestrates the rendering process. It invokes the
subsystem responsible for each stage, in the order below, and passes
each stage's output forward as the input to the next stage.

The Pipeline never implements the logic of any stage it coordinates.
The Pipeline never validates, resolves, renders, verifies, or exports
anything itself — it only invokes the owning subsystem and forwards
results.

### Step 1.1 — Validator

Responsibility: Validate the raw incoming rendering request.

Input: Raw rendering request.

Output: ValidatedPayload (immutable).

Exception: ValidationError.

Relationship with Pipeline: Invoked first by Pipeline with the raw
request. Returns ValidatedPayload to Pipeline.

Stateless. Does not modify the raw request; produces a new
ValidatedPayload. Depends on no other subsystem.

---

### Step 1.2 — ConfigurationResolver

Responsibility: Resolve engine/template/platform configuration for the
request.

Input: ValidatedPayload.

Output: ResolvedConfiguration (immutable).

Exception: ConfigurationError.

Relationship with Pipeline: Invoked by Pipeline immediately after
Validator, with ValidatedPayload. Returns ResolvedConfiguration to
Pipeline.

Stateless. Does not modify ValidatedPayload. Depends only on
ValidatedPayload.

---

### Step 1.3 — AssetResolver

Responsibility: Resolve required visual assets referenced by the
request/configuration.

Input: ValidatedPayload, ResolvedConfiguration.

Output: ResolvedAssets (immutable).

Exception: AssetError.

Relationship with Pipeline: Invoked by Pipeline after
ConfigurationResolver, with ValidatedPayload and ResolvedConfiguration.
Returns ResolvedAssets to Pipeline.

Stateless from the Pipeline's perspective (may read from asset storage
internally; this is an implementation detail, not an architectural
one). Does not modify its inputs. Depends only on ValidatedPayload and
ResolvedConfiguration. Does not depend on FontResolver.

---

### Step 1.4 — FontResolver

Responsibility: Resolve required fonts referenced by the
request/configuration.

Input: ValidatedPayload, ResolvedConfiguration.

Output: ResolvedFonts (immutable).

Exception: FontError.

Relationship with Pipeline: Invoked by Pipeline after AssetResolver,
with ValidatedPayload and ResolvedConfiguration. Returns ResolvedFonts
to Pipeline.

Stateless from the Pipeline's perspective. Does not modify its inputs.
Depends only on ValidatedPayload and ResolvedConfiguration. Does not
depend on AssetResolver.

---

### Step 1.5 — Template Resolution / Selection

Pipeline resolves and selects the requested Template using
ValidatedPayload / ResolvedConfiguration.

Pipeline does not invoke (execute) the Template at this point —
invocation occurs in Step 3, after RenderContext exists.

This is the only Template-related responsibility Pipeline holds.
Template Execution and Layer Generation belong exclusively to the
Template component (Step 3).

The lookup mechanism Pipeline uses to map a request to a concrete
Template is an implementation detail and is intentionally
unspecified here — every Template conforms to the same interface
(Step 3), so Pipeline requires no knowledge of any Template's
internal implementation.

The Pipeline never performs rendering.

---

## Step 2 — RenderContext

RenderContext is created exactly once, by Pipeline, immediately after
Steps 1.1–1.4 (Validator, ConfigurationResolver, AssetResolver,
FontResolver) have all completed successfully.

RenderContext is assembled from ValidatedPayload, ResolvedConfiguration,
ResolvedAssets, and ResolvedFonts, plus render metadata.

After creation it becomes immutable.

RenderContext is shared read-only with exactly three subsystems:
Template, Renderer, and QualityVerifier.

Validator, ConfigurationResolver, AssetResolver, FontResolver, Canvas,
and Exporter never receive RenderContext.

No subsystem may modify it.

---

## Step 3 — Template

The Template receives:

- RenderContext

The Template executes and, as the direct output of that execution,
returns:

- Ordered list of Layer objects.

Template Execution and Layer Generation are a single act performed
entirely by Template — Layer Generation is not a separate stage owned
by a separate component.

Templates never render.

Templates never access Canvas.

Templates never perform drawing.

Templates only describe the visual composition.

---

## Step 4 — Renderer

The Renderer receives:

- RenderContext
- Ordered list of Layer objects
- Canvas implementation

The Renderer is responsible for interpreting each Layer.

The Renderer must never modify Layers.

The Renderer must never modify RenderContext.

The Renderer performs a single deterministic pass over the layer list.

---

## Step 5 — Canvas

Canvas receives only renderer-specific drawing properties.

Canvas never receives Template objects.

Canvas never receives RenderContext.

Canvas never interprets Layer semantics.

Canvas executes primitive drawing operations only.

Canvas implementations are backend specific.

---

## Step 6 — QualityVerifier

QualityVerifier is a dedicated subsystem, architecturally equivalent in
status to Renderer and Exporter. It is independent from Renderer,
Canvas, Exporter, and Pipeline.

QualityVerifier receives:

- RenderContext
- Rendered Image (the result produced by Renderer via Canvas.get_result)

QualityVerifier verifies only the structural/output integrity of the
rendered result:

- that a rendered result exists
- that rendered dimensions match the resolved Canvas/platform
  information in RenderContext
- that the image is structurally valid and decodable
- that the image format/mode is compatible with the resolved Canvas
  information

QualityVerifier never renders, never issues Canvas drawing operations,
never modifies the rendered image, Layers, or RenderContext, never
resolves assets or fonts, never executes templates, never exports, and
never evaluates sports, textual, linguistic, branding, or aesthetic
quality. It performs no AI-based evaluation and contains no business
logic. See Section 8 (Architectural Constraints) for the complete
restriction list.

On success, QualityVerifier returns the exact same rendered image
object, unchanged.

On failure, QualityVerifier raises QualityVerificationError (see
Section 12, Exception Hierarchy). Pipeline coordinates QualityVerifier
as a lifecycle stage but does not implement verification logic itself.

Relationship with Pipeline: invoked by Pipeline as one coordinated
stage, receiving RenderContext and the Rendered Image and returning
control to Pipeline.

Relationship with Renderer: QualityVerifier consumes Renderer's output.
It never calls Renderer and Renderer never calls it.

Relationship with Exporter: QualityVerifier's output (the unchanged
Rendered Image) becomes Exporter's input. QualityVerifier never
exports and Exporter never verifies.

---

## Step 7 — Exporter

Exporter receives the completed rendered image, unchanged from
QualityVerifier.

Exporter converts it into the required output format.

Examples:

- PNG
- JPEG
- WEBP

Exporter never performs rendering.

---

# Data Ownership

ValidatedPayload
    produced by Validator
    owned by Pipeline after production, shared read-only

ResolvedConfiguration
    produced by ConfigurationResolver
    owned by Pipeline after production, shared read-only

ResolvedAssets
    produced by AssetResolver
    owned by Pipeline after production, shared read-only

ResolvedFonts
    produced by FontResolver
    owned by Pipeline after production, shared read-only

RenderContext
    owned by Pipeline
    created exactly once, after the four pre-render stages (Validator,
    ConfigurationResolver, AssetResolver, FontResolver) complete
    shared read-only with exactly three subsystems: Template, Renderer,
    QualityVerifier — the only components that execute after its
    creation and require it
    never received by Validator, ConfigurationResolver, AssetResolver,
    FontResolver, Canvas, or Exporter

Layer
    owned by Template
    read-only after creation

Canvas
    owned by Rendering Backend

Rendered Image
    owned by Canvas until export
    QualityVerifier reads it but never takes ownership, mutates it, or
    replaces it — the same object passes through unchanged

---

# Rendering Rules

Layers must never be reordered.

Layers must never be modified.

Renderer must never create Layers.

Canvas must never interpret business rules.

Templates must never issue drawing commands.

Every subsystem has a single responsibility.

---

# Architectural Principle

Description flows downward.

Execution flows downward.

Knowledge never flows upward.

Templates describe.

Renderer interprets.

Canvas executes.

End of Architecture Specification.

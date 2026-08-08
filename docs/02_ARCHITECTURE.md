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

Every recoverable failure must have a documented fallback strategy.

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
                Export System
                       │
                       ▼
              Publishing Services

```

Each subsystem communicates through defined interfaces.

No subsystem may directly manipulate another subsystem's internal implementation.

---

# 6. Core Architectural Layers

The Visual Engine consists of five architectural layers.

## Layer 1

Configuration

Responsible for loading and validating configuration.

---

## Layer 2

Resources

Responsible for assets, fonts, overlays and branding resources.

---

## Layer 3

Template System

Responsible for describing visual composition.

Templates never render pixels.

---

## Layer 4

Rendering System

Responsible for transforming declarative layers into rendered images.

---

## Layer 5

Export System

Responsible for platform-specific output generation.

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

Asset managers must never:

- know templates
- know rendering logic

Exporter must never:

- modify visual composition
- perform rendering

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

## 8. Layer System Specification

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

BACKGROUND, BRAND and FOOTER layers are produced exclusively by BaseTemplate through OverlayManager.

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
# 9. Exception Hierarchy

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

Examples:

- Canvas creation failed.
- Drawing operation failed.
- Renderer internal failure.

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

Raised when validated input data becomes invalid before rendering.

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
# 10. Canvas Abstraction

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

LayerKind values must map to these Canvas operations according to the normative LayerKind Dispatch table defined in Section 11.

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
# 11. Renderer Architecture

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
3. Validate renderer inputs.
4. Iterate through Layers.
5. Dispatch every Layer to the corresponding Canvas operation.
6. Finish rendering.
7. Return the rendered output.

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

The Renderer MUST use the LayerKind values defined in Section 8 and MUST use only the Canvas operations defined in Section 10.

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

The current engine defines a closed LayerKind vocabulary consisting of the eight values specified in Section 8.

Adding a new LayerKind is an architectural change and MUST NOT be performed implicitly by implementation code.

To introduce a new LayerKind, the following specifications MUST be updated first:

1. Section 8 — LayerKind Specification.
2. Section 10 — Canvas Abstraction, if a new Canvas operation is required.
3. Section 11 — Renderer Layer Dispatch.
4. 04_RENDERING_SPECIFICATION.md and any other normative specification affected by the change.

Only after the specifications have been updated may implementation code introduce the new LayerKind.

Existing LayerKind behavior and mappings must remain unchanged unless explicitly revised by the updated specifications.
# 12. Core Rendering Flow

This section defines the complete execution flow of the Visual Engine.

Every rendering request MUST follow this sequence without deviation.

---

## Step 1 — Pipeline

The Pipeline is responsible for orchestrating the rendering process.

Responsibilities:

- Validate the incoming request.
- Resolve configuration.
- Resolve assets.
- Resolve fonts.
- Create the RenderContext.
- Select the requested Template.
- Invoke the Template.

The Pipeline never performs rendering.

---

## Step 2 — RenderContext

RenderContext is created exactly once.

After creation it becomes immutable.

Every subsystem receives the same RenderContext instance.

No subsystem may modify it.

---

## Step 3 — Template

The Template receives:

- RenderContext

The Template returns:

- Ordered list of Layer objects.

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

## Step 6 — Exporter

Exporter receives the completed rendered image.

Exporter converts it into the required output format.

Examples:

- PNG
- JPEG
- WEBP

Exporter never performs rendering.

---

# Data Ownership

ValidatedPayload
    owned by Pipeline

RenderContext
    owned by Pipeline
    shared read-only

Layer
    owned by Template
    read-only after creation

Canvas
    owned by Rendering Backend

Rendered Image
    owned by Canvas until export

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

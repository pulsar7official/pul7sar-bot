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

# 3. Rendering Lifecycle

Every render follows the exact same lifecycle.

```
Request

↓

Validation

↓

RenderContext Creation

↓

Configuration Resolution

↓

Asset Resolution

↓

Font Resolution

↓

Template Resolution

↓

Layer Generation

↓

Rendering

↓

Quality Verification

↓

Export

↓

Completed Result
```

No stage may be skipped.

No stage may modify previous stages.

---

# 4. Core Rendering Components

The rendering subsystem consists of the following components.

## RenderContext

Immutable render request state.

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

## Pipeline

Coordinates the rendering process.

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

### Fail Gracefully

Recoverable failures must use documented fallback strategies.

---

### Platform Independence

Rendering occurs once.

Exporting adapts the result for each platform.

---

# 6. RenderContext

RenderContext represents one immutable rendering request.

It is created once by the Pipeline.

Every subsystem receives the same instance.

No subsystem may modify it.

RenderContext contains:

- validated payload
- resolved configuration
- resolved assets
- resolved fonts
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
---

# 12. Pipeline Specification

Pipeline coordinates the complete rendering lifecycle.

Pipeline owns:

- validation
- context creation
- configuration loading
- asset resolution
- font resolution
- template execution
- rendering
- exporting

Pipeline is the only component allowed to orchestrate multiple subsystems.

No other component may coordinate the rendering lifecycle.

---

End of Part 2.

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

End of Part 1.

# PUL7SAR Visual Engine v2

## Software Architecture Specification (SAS)

**Project:** PUL7SAR Global Sports Platform

**Component:** Visual Engine v2

**Status:** Approved Architecture

**Version:** 2.0

---

# 1. Purpose

This document defines the official architecture of the PUL7SAR Visual Engine.

The Visual Engine is responsible for generating all branded visual assets used across the PUL7SAR ecosystem.

This document is the single source of truth for every AI model, developer, contributor, or future engineer working on the rendering system.

Implementation must always follow this specification.

If implementation conflicts with this document, this document takes precedence.

---

# 2. Scope

Visual Engine v2 is a standalone rendering module.

It is completely independent from the production Telegram bot.

The engine must never depend on:

- main.py
- Telegram APIs
- Social Media APIs
- Publishing logic
- Scheduling logic
- News collection logic

Its only responsibility is:

Input → Render → Export

The caller decides what to render.

The engine decides how to render.

---

# 3. Design Philosophy

The Visual Engine follows three immutable principles.

## Principle 1

Templates describe visuals.

Templates never draw pixels.

Every template produces a declarative collection of rendering layers.

The renderer is the only component responsible for transforming layers into pixels.

---

## Principle 2

Reusable functionality exists only once.

Backgrounds.

Lighting.

Brand elements.

Typography.

Watermarks.

Textures.

Gradients.

All common visual components are implemented once and reused everywhere.

No template may duplicate common rendering behavior.

---

## Principle 3

The rendering pipeline never crashes.

Every stage must define a fallback strategy.

Missing assets.

Missing fonts.

Unknown templates.

Rendering failures.

Configuration problems.
---

# 4. High-Level Architecture

The Visual Engine is designed as an isolated rendering subsystem.

It communicates with the production system only through validated rendering requests.

The production bot never performs rendering logic.

Likewise, the Visual Engine never performs publishing, scheduling, scraping, or business logic.

The architecture follows a strict separation of concerns.

```
                Production Bot
                        │
                        │
                Render Request
                        │
                        ▼
            ┌────────────────────┐
            │   Validation Layer  │
            └────────────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │   RenderContext     │
            └────────────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │ Template Registry   │
            └────────────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │   BaseTemplate      │
            └────────────────────┘
                        │
              Declarative Layers
                        │
                        ▼
            ┌────────────────────┐
            │ Renderer + Canvas   │
            └────────────────────┘
                        │
                        ▼
            ┌────────────────────┐
            │     Exporter        │
            └────────────────────┘
                        │
                        ▼
                 Final Image(s)
```

Every stage has one responsibility.

No component may bypass another stage.

---

# 5. Project Structure

The Visual Engine must follow the directory layout below.

```
pul7sar-visual-engine-v2/

engine/
│
├── core/
│   ├── context.py
│   ├── layer.py
│   ├── canvas.py
│   ├── renderer.py
│   └── pipeline.py
│
├── templates/
│
├── overlays/
│
├── assets/
│
├── fonts/
│
├── config/
│
├── data/
│
├── errors/
│
├── output/
│
└── utils/

tests/

examples/

docs/
```

The directory structure is considered part of the architecture.

Files may be added.

Existing responsibilities may not be changed without architectural approval.

---

# 6. Dependency Rules

Every dependency inside the Visual Engine follows one direction only.

```
Templates
      │
      ▼
Layer Abstractions
      │
      ▼
Renderer
      │
      ▼
Canvas Backend
```

Templates must never depend directly on:

- Pillow
- Canvas
- Renderer
- File System
- Export Logic

Templates only produce declarative Layers.

The renderer interprets those Layers.

This rule is mandatory.

Violation of this rule is considered an architectural defect.

---

# 7. Core Components

The engine is composed of five core components.

## RenderContext

Stores immutable rendering state.

Contains validated request information.

Contains resolved configuration.

Contains resolved assets.

Contains rendering metadata.

Contains no rendering logic.

---

## Layer

Represents one declarative drawing instruction.

A Layer never draws itself.

A Layer only describes:

- what
- where
- how

---

## Renderer

Receives ordered Layers.

Uses a Canvas implementation.

Produces pixels.

Contains no business logic.

---

## Canvas

Provides backend-independent drawing operations.

Canvas implementations may change.

Templates must remain unchanged.

---

## Pipeline

Coordinates the complete rendering process.

Validation.

Context creation.

Template execution.

Rendering.

Exporting.

Fallback handling.

Logging.

The Pipeline owns orchestration only.

It owns no rendering rules.
All failures must degrade gracefully instead of stopping image generation.

Generating a simplified image is always preferred over generating nothing.

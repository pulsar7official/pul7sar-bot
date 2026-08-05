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

Every layer belongs to exactly one kind.

The initial engine defines the following kinds:

- BACKGROUND
- GRADIENT
- IMAGE
- TEXT
- SHAPE
- ICON
- LOGO
- TEXTURE
- EFFECT

Future kinds may be added without modifying existing templates.

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

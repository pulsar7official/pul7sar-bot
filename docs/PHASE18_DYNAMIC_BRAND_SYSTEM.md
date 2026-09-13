# PUL7SAR Phase 18 — Dynamic Brand System

## Decision
PUL7SAR does not use a single context-blind accent and does not ask a diffusion model to redraw the platform mark.

The brand has two independent concerns:

1. **Structure** — stable and deterministic.
2. **Accent state** — contextual when safely supported by the story hero.

## Default state
The default accent for the distinctive **7 + pulse** is PUL7SAR red (`#E10600`).

It is used when:
- the story is general,
- there is no single visual hero,
- multiple entities have equal visual priority,
- hero confidence is below threshold,
- verified palette evidence is unavailable.

## Contextual state
A verified story hero may drive the 7/pulse accent when all are true:
- the hero is unambiguous,
- hero confidence >= 0.85,
- explicit palette evidence exists,
- palette confidence >= 0.80.

The resolver never guesses a club/team color from its name or from model memory.

## Locked rules
- Diffusion/generative models may never draw PUL7SAR branding.
- Context changes color state, not brand geometry.
- The default tint scope is `seven + pulse`.
- Ambiguous club-v-club stories fall back to PUL7SAR red unless Story Intelligence establishes a clear hero.
- Exact entity crests remain verified assets and are not recolored.
- Typography, scores and exact data remain deterministic layers.

## Implementation
- `engine/intelligence/dynamic_brand.py`
- `engine/intelligence/entity_theme.py`
- `engine/intelligence/brand_semantics.py`
- `tests/test_phase18_dynamic_brand.py`

## Next integration boundary
The Dynamic Brand decision must be consumed by the deterministic post-composer after Story-to-Visual planning and before final QA. The generative base-scene prompt receives only a negative/forbidden-brand contract.

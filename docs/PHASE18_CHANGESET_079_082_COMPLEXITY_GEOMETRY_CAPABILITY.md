# PUL7SAR Phase 18 — Canonical Change Sets 081–084

> Historical filename retained for continuity. The authoritative implementation sequence reserves 077–080 for fact schemas, Fact Lock integration, deterministic football geometry and layer-aware Hybrid Visual QA.

## Change Set 081 — Scene Complexity Minimization
Added `engine/intelligence/scene_complexity_policy.py`.

PUL7SAR no longer assumes that a football story needs a full generated football stadium or pitch. The policy selects the minimum physical dependency needed to communicate the story:
- transfers, injuries, records, statements, appointments, dismissals, awards, tables, draws and similar stories: no playing surface required,
- results/live moments/previews: only partial deterministic sport context,
- tactics: full deterministic surface,
- general stories: atmosphere only, no exact venue dependency.

This reduces hallucination risk before prompt construction begins.

## Change Set 082 — Expanded Cross-Sport Rules
Expanded `engine/intelligence/sport_visual_rules.py`.

Explicit profiles cover more than thirty sport families, including football, basketball, tennis, padel, badminton, volleyball, handball, baseball, American football, rugby, cricket, golf, boxing, MMA, wrestling, judo, taekwondo, athletics, Formula 1, motorsport, swimming, cycling, rowing, sailing, ice hockey, winter sports, table tennis, snooker, darts, gymnastics, weightlifting, equestrian and esports.

Arabic aliases are included for major sport names. Unknown sports receive a conservative fallback rather than an invented geometry contract.

Added `tests/test_phase18_sport_visual_rules.py`.

## Change Set 083 — Deterministic Football Geometry Renderer
Added/strengthened:
- `engine/intelligence/football_pitch_geometry.py`
- `engine/intelligence/football_pitch_projection.py`
- `engine/intelligence/football_pitch_renderer.py`

A projective homography maps regulation world-space geometry to an arbitrary four-corner image quadrilateral. The lazy-Pillow renderer creates a transparent deterministic pitch layer and can alpha-composite it over a base image. This is the direct replacement for asking FLUX to invent pitch proportions and markings.

## Change Set 084 — Geometry Capability Fail-Closed Policy
Added `engine/intelligence/geometry_capabilities.py` and integrated it into `EditorialPlanningService`.

A sport can require exact geometry without PUL7SAR yet having a renderer for it. The registry distinguishes policy requirement from implementation readiness.

Current declared deterministic renderer readiness:
- football: `football_pitch_projective_v1`

Other exact-geometry sports remain explicitly unavailable until their renderers are implemented.

Behavior:
- if a story only needs partial surface context and a renderer is unavailable, the surface is removed and the design falls back to verified assets + abstract atmosphere,
- if the story fundamentally requires full exact geometry (for example tactics), planning stops with `GEOMETRY_CAPABILITY_BLOCKED` rather than letting a diffusion model improvise.

Added `tests/test_phase18_geometry_capabilities.py`.

## Architecture principle
**Missing implementation must reduce visual ambition, never reduce factual or geometric standards.**

A visually simpler verified composition is preferred over a more impressive but structurally false generated scene.

## Production isolation
No production entrypoint was changed. `main`, `main.py`, Telegram production publishing, secrets and paid-provider policy remain untouched.

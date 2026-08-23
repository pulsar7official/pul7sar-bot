# PUL7SAR Phase 18 — Change Sets 075–078

## Change Set 075 — Event-specific Fact Schemas
Added `engine/intelligence/sports_fact_schema.py`.

Every `EditorialEvent` now has an explicit verified-fact schema with required slots, optional slots, exact-render slots, identity slots and forbidden implications.

Examples:
- Result requires subject, opponent and result status; exact score is deterministic if supplied.
- Transfer rumour requires subject, interested entity and rumour status; completed signing/presentation is forbidden.
- Injury requires subject and injury status; an exact absence duration is deterministic only if verified.
- Tactics treats formation and player roles as exact deterministic data.
- Draw/table/schedule values are exact and cannot be generated visually.

Added `tests/test_phase18_sports_fact_schema.py` and coverage that every event in the taxonomy owns a schema.

## Change Set 076 — Fact Lock -> Editorial Slot Integrity
Added `engine/intelligence/fact_locked_editorial_adapter.py`.

A copy/visual fact slot can now be used only when a `LockedClaim(kind=FACT)` backs the same metadata slot. `SAFE_INFERENCE` and `FORBIDDEN` claims cannot satisfy required editorial facts.

Fact confidence below 0.80 is rejected before visual planning. This makes the new Story-to-Visual path consume the existing Phase 18 Fact Lock rather than creating a parallel truth system.

Added `tests/test_phase18_fact_locked_editorial_adapter.py`.

## Change Set 077 — Deterministic Football Pitch Geometry
Added:
- `engine/intelligence/football_pitch_geometry.py`
- `engine/intelligence/football_pitch_projection.py`

The system now owns regulation world-space football geometry instead of asking diffusion to draw it.

The geometry model uses a 105m × 68m reference pitch and explicit primitives for:
- four boundary lines,
- exactly one halfway line,
- exactly one centre circle,
- symmetric penalty areas,
- symmetric goal areas,
- penalty marks,
- regulation reference dimensions.

The projective planner computes a four-corner homography and projects deterministic markings into an arbitrary image quadrilateral. This is the mathematical foundation for perspective-correct pitch overlays.

Added:
- `tests/test_phase18_football_pitch_geometry.py`
- `tests/test_phase18_football_pitch_projection.py`

## Change Set 078 — Layer-aware Hybrid Visual QA
Added `engine/intelligence/hybrid_visual_quality_gate.py`.

The final visual can no longer pass merely because a PNG exists. The gate hard-blocks:
- generated text leakage,
- generated PUL7SAR branding,
- fake generated logos/crests,
- severe generative defects,
- collage/split-scene output,
- missing required deterministic sport geometry,
- missing exact PUL7SAR brand asset,
- missing deterministic typography,
- missing verified hero identity when the layer plan requires one.

Added `tests/test_phase18_hybrid_visual_quality_gate.py`.

## Architecture state after Change Set 078

`Article extraction -> Fact Lock -> event fact schema -> fact-slot integrity -> multiple editorial-angle candidates -> visual-aware angle ranking -> concise headline/copy -> sport-aware production rules -> hybrid layer plan -> [generation only for safe atmosphere/context] + [deterministic geometry/data/text] + [verified identity/brand assets] -> layer-aware QA -> semantic/golden publication gates`

## Critical design consequence
FLUX or any future diffusion model is no longer asked to create an exact football pitch, PUL7SAR logo, exact score, table, formation, statistic or verified identity as part of one unconstrained image. Those responsibilities have explicit owners.

## Production isolation
`main`, `main.py`, Telegram production publishing and current production assets remain untouched. Phase 18 remains isolated on `phase18/story-intelligence`.

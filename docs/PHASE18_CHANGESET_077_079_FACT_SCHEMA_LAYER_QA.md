# PUL7SAR Phase 18 — Change Sets 077–079

## Change Set 077 — Event-specific sports fact schemas

Added `engine/intelligence/sports_fact_schema.py`.

The Story-to-Visual path now has explicit required, optional, exact-render and identity slots for the active editorial-event taxonomy. Results, live moments, previews, transfers, contracts, injuries, comebacks, suspensions, retirement, appointments, dismissals, statements, records, awards, trophies, draws, tables, tactics, officiating, controversies, financial news, organization news, schedules, qualification, elimination and general stories are validated before copy or visual planning.

Exact values such as scores, minutes, dates, standings, formations, fees and record values are marked for deterministic rendering instead of generative invention. Schemas also record forbidden implications, for example invented scores, invented signings, invented diagnoses or invented allegations.

## Change Set 078 — Fact-Lock-to-editorial slot binding

Added `engine/intelligence/fact_locked_editorial_adapter.py`.

A visual/editorial fact slot is no longer considered usable merely because it exists in an input mapping. Every supplied slot must be backed by a `LockedClaim(kind=FACT)` whose metadata names the same slot. `SAFE_INFERENCE` and `FORBIDDEN` claims cannot satisfy required editorial facts.

The adapter rejects missing required slots, unbacked supplied values and FACT claims below the locked 0.80 production-confidence floor. This provides a deterministic bridge between existing Fact Lock evidence and the Story-to-Visual planning contracts.

The new fact-schema and adapter contracts are exported from `engine/intelligence/__init__.py`.

## Change Set 079 — Hybrid layer leakage QA

Added:
- `engine/intelligence/visual_layer_qa.py`
- `tests/test_phase18_visual_layer_qa.py`

The new `HybridLayerQualityGate` enforces the ownership plan produced by `HybridVisualLayerPlanner`. Inspection evidence now has explicit blockers for generative leakage into layers reserved for deterministic code or verified assets:

- generated text into deterministic typography,
- generated PUL7SAR/platform branding into the verified brand layer,
- generated exact scores/statistics/numbers into deterministic data,
- generated club/team/competition marks into verified-asset marks,
- unverified generated identity into a verified hero-identity layer,
- generated playing-surface geometry when the sport requires deterministic geometry.

This gate consumes inspection evidence; it does not claim to perform computer vision itself and does not replace `SemanticPublicationGate` or Golden visual-quality review. A clean base scene can pass layer ownership while still failing semantic or aesthetic gates later.

`tools/phase18_colab_runner.py` now includes the new layer-QA regression module in its CPU preflight, so the GPU path refuses to spend generation time if the ownership contract is broken by a code regression.

## Production isolation and preserved gates

No changes were made to `main`, `main.py`, Telegram production publishing, production secrets or paid image APIs. No model, seed, BF16, `$0-local`, Fact Lock, identity, sentiment, neutrality, semantic-publication or Golden 8.5/9.0 threshold was weakened.

## Remaining gap

The new QA contract still needs real visual evidence extraction wired to it after a generated base scene. Until that detector/probe integration exists, layer leakage cannot be auto-cleared for publication. The active v4 Golden Candidate 1 also still requires a genuine CUDA/BF16 execution before any v4 visual-quality claim can be made.

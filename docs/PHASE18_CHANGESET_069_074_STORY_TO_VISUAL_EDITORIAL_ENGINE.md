# PUL7SAR Phase 18 — Change Sets 069–074

## Why this architecture changed
Real GPU proofs showed that prompt engineering alone is not a safe production strategy. A technically successful image could still contain malformed sport geometry, generated pseudo-branding, weak composition, or an editorial concept that is difficult to visualize reliably.

The new rule is: **PUL7SAR plans the wording and the visual production strategy together before any image model is called.** Generative AI is no longer responsible for every pixel or every exact fact.

## Change Set 069 — Story-to-Visual Editorial Engine
Added `engine/intelligence/story_visual_editorial.py`.

Introduces a stable sports-event taxonomy covering results, live moments, previews, confirmed transfers, rumours, contracts, injuries, comebacks, suspensions, retirement, appointments, dismissals, statements, records, awards, trophies, draws, tables, tactics, officiating, controversies, financial news, organization news, schedules, qualification, elimination and general stories.

Each event maps to a visual family and one of four production modes:
- `generative_scene`
- `hybrid`
- `deterministic_composition`
- `verified_asset_editorial`

Low-confidence stories automatically fall back to verified-asset editorial treatment instead of compensating with more imaginative generation.

## Change Set 070 — Sport-aware production rules
Added `engine/intelligence/sport_visual_rules.py`.

Separates event semantics from sport physics. A result is an event type; football, tennis, basketball or boxing determine different surface/equipment constraints.

Initial explicit sport profiles include football, basketball, tennis, golf, boxing, MMA, athletics, Formula 1, motorsport, swimming, cycling, volleyball, handball, ice hockey and winter sports, plus a conservative unknown-sport fallback.

The registry records:
- surface type,
- whether exact geometry should be deterministic,
- safe generative context,
- geometry requirements,
- high-risk generated elements.

## Change Set 071 — Visual-compatible editorial language
Added:
- `engine/intelligence/editorial_headline_grammar.py`
- `engine/intelligence/editorial_copy_builder.py`

The headline is no longer independent from the image. Every event has an editorial angle and visual anchor. Copy is built only from supplied verified fact slots. Optional context is used only when it stays inside the compact social-post budget.

The builder does not silently paraphrase or invent missing context to meet length limits.

## Change Set 072 — Visual-aware editorial angle selection
Added `engine/intelligence/editorial_angle_selector.py`.

When one story supports several verified angles, PUL7SAR now ranks them by:
- editorial importance,
- fact confidence,
- identity confidence,
- number of subjects,
- exact-text burden,
- exact-geometry burden,
- visual-copy verbosity,
- sensitive-story treatment.

Hard blockers include low fact confidence, unverified required identity, invented-scene dependency and identity confidence below the locked threshold.

This lets a slightly less important but far more reliable visual angle beat a complex angle that would be likely to hallucinate.

## Change Set 073 — Unified editorial planning service
Added:
- `engine/intelligence/story_to_visual_orchestrator.py`
- `engine/intelligence/editorial_planning_service.py`
- `engine/intelligence/story_event_resolver.py`

The planning flow is now:

`Fact-locked angle candidates -> visual-aware angle selection -> concise headline -> sport-aware production mode -> geometry contract -> layer ownership -> generation authorization`

The event resolver bridges existing explicit `story_type` values to the richer editorial-event taxonomy without inferring from prose.

A CPU-only inspection command was added:
`tools/phase18_story_to_visual_preview.py`

It can inspect a story plan without model loading or GPU use.

## Change Set 074 — Hybrid visual layer ownership
Added `engine/intelligence/hybrid_layer_planner.py`.

The final image is now decomposed by reliability:
- atmosphere/depth/lighting: generative when useful,
- sport-surface geometry: deterministic when exact geometry matters,
- verified subject identity: verified asset or identity-verified depiction,
- exact team/competition marks: verified assets,
- score/statistics/table/date: deterministic,
- editorial typography: deterministic,
- PUL7SAR brand and pulse: exact approved asset only.

This directly addresses the malformed football-pitch and pseudo-PUL7SAR failures seen in the real Colab proofs.

## Colab runner hardening
`tools/phase18_colab_runner.py` now rejects stale Golden contracts before GPU use. It requires the current v4 manifest, single-scene grammar, regulation-football geometry lock, `generated_branding_allowed=false`, and `brand_composition_policy=exact_assets_only_after_generation`.

The old summary-key mismatch that could display `geometry=None` or `branding=None` despite newer manifest fields was corrected.

## Regression coverage added
- `tests/test_phase18_story_visual_editorial.py`
- `tests/test_phase18_story_to_visual_orchestrator.py`
- `tests/test_phase18_story_visual_scenario_matrix.py`
- `tests/test_phase18_editorial_angle_selector.py`
- `tests/test_phase18_hybrid_layer_planner.py`
- `tests/test_phase18_editorial_planning_service.py`
- `tests/test_phase18_story_event_resolver.py`
- `tests/test_phase18_editorial_copy_builder.py`
- strengthened `tests/test_phase18_colab_runner.py`

The scenario matrix currently exercises 30 event/sport combinations without GPU use.

## Production isolation
No change was made to `main`, `main.py`, Telegram production publishing, production secrets or paid image APIs.

## Next engineering work
1. Connect verified article extraction/Fact Lock outputs to `EditorialAngleCandidate` creation.
2. Add event-specific fact schemas so results, transfers, injuries, records and schedules have required/optional fact slots.
3. Build deterministic geometry renderers beginning with football pitch/court/track primitives.
4. Build exact-asset identity composition for players, clubs, competitions and PUL7SAR branding.
5. Add visual QA that understands the layer plan and can reject model leakage into deterministic zones.
6. Only then return to GPU image generation and test several unrelated sports-news scenarios rather than optimizing one stadium image.

# PUL7SAR Phase 18 — Change Set 110
## Generator-Bypass Visual Execution Routing

### Goal
Move the provider/model decision one step later in the architecture. PUL7SAR must first decide whether a generator is needed at all.

### Why
A sports visual system should not invoke diffusion simply because the story belongs to football or because a historical workflow contains an image-generation stage. Tactical diagrams, tables, schedules, financial/data cards, low-confidence stories and verified-asset editorials can often be completed with deterministic composition and approved source assets only.

### Added
- `engine/intelligence/visual_execution_route.py`
- `PixelExecutionRoute`
- `VisualExecutionDecision`
- `VisualExecutionRouter`

### Execution routes
- `deterministic_only`: exact-data/geometry/editorial layers; no image provider is allowed.
- `verified_asset_only`: approved source imagery plus deterministic editorial layers; no image provider is allowed.
- `hybrid_generative`: generation is allowed only for elements explicitly assigned to the generator by `VisualGrammar`.
- `generative_scene`: provider execution is required only when generator-owned content is explicitly declared.

### Fail-closed behavior
- A deterministic plan cannot select a provider.
- A verified-asset plan cannot select a provider.
- A HYBRID plan with zero generator-owned elements bypasses provider execution instead of calling a model by habit.
- A GENERATIVE_SCENE plan with zero generator-owned elements is rejected as an invalid contract.

### Story orchestration integration
`StoryToVisualOrchestrator` now returns an `execution_route` after the approved `VisualGrammarDecision` is produced. Provider selection therefore becomes conditional on `execution_route.provider_selection_allowed`.

The intended architecture is now:

`Verified story -> editorial/visual plan -> VisualGrammar -> VisualExecutionRouter -> [provider only if required] -> deterministic exact layers -> QA/publication gates`

### Strategic effect
This is a direct step toward making PUL7SAR the visual system rather than a wrapper around FLUX, Colab or any future image generator. A model becomes an optional pixel source for specific non-exact layers, not the owner of the production pipeline.

### Invariants
- `main` remains untouched.
- `$0-local` remains the active cost policy.
- Exact branding, typography, scores, data, club marks and exact sport geometry remain deterministic.
- Identity/fact/neutrality gates remain unchanged.
- No paid API or provider dependency was added.
- No claim of a new Golden PNG is made by this change set.

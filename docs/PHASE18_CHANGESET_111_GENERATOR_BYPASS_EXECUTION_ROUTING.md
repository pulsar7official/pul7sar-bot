# PUL7SAR Phase 18 — Change Set 111
## Generator-Bypass Visual Execution Routing

### Goal
Move provider/model selection one step later in the architecture. PUL7SAR must first decide whether an image generator is needed at all.

### Added
- `engine/intelligence/visual_execution_route.py`
- `PixelExecutionRoute`
- `VisualExecutionDecision`
- `VisualExecutionRouter`
- `tests/test_phase18_visual_execution_route.py`

### Execution routes
- `deterministic_only`: exact data/geometry/editorial layers; no image provider is allowed.
- `verified_asset_only`: approved source imagery plus deterministic editorial layers; no image provider is allowed.
- `hybrid_generative`: generation is allowed only for elements explicitly assigned to the generator by `VisualGrammar`.
- `generative_scene`: provider execution is required only when generator-owned content is explicitly declared.

### Fail-closed rules
- Deterministic composition cannot select a provider.
- Verified-asset editorial cannot select a provider.
- HYBRID with zero generator-owned elements bypasses provider execution.
- GENERATIVE_SCENE with zero generator-owned elements is rejected.

### Story orchestration integration
`StoryToVisualOrchestrator` now returns an `execution_route` after the approved `VisualGrammarDecision` is produced.

Examples:
- result -> hybrid generation allowed only for approved atmospheric/non-exact elements;
- tactics/table -> deterministic only, provider selection blocked;
- injury/low-confidence -> verified asset only, provider selection blocked;
- confirmed transfer -> may use hybrid generation without inheriting pitch dependency.

### Golden/local handoff propagation repair
CI exposed that `GenerationPackageCompiler` correctly produced VisualGrammar metadata, but `LocalBackendRequestCompiler` dropped those fields while creating the local/portable request. The compiler now preserves the VisualGrammar contract, surface visibility, camera language, fantasy level, generator-owned elements, deterministic elements and forbidden generated elements.

### Architecture
`Verified story -> editorial/visual plan -> VisualGrammar -> VisualExecutionRouter -> [provider only if required] -> deterministic exact layers -> semantic/layer QA -> Golden review -> approved brand/typography -> publication gates`

The key rule is: **PUL7SAR owns the visual decision; a generator is only an optional pixel source.**

### Invariants
- `main` remains untouched.
- `$0-local` remains active.
- No paid provider/API was added.
- Exact branding, typography, scores/data, official marks and exact sport geometry remain deterministic.
- No genuine new GPU Golden PNG is claimed by this change set.

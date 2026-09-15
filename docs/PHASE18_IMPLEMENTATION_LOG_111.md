# PUL7SAR Phase 18 — Implementation Log Continuation 111

This is the authoritative continuation record for Generator-Bypass Visual Execution Routing on `phase18/story-intelligence`. No production branch is modified.

## Branch state
- Repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence` only.
- PR #1 remains open, Draft and unmerged against `main`.
- Change Set 110 already exists separately and aligns the Golden Hybrid v5 benchmark with `VisualGrammar`; it is not overwritten by this record.
- `main` / production entrypoint were not used as write targets.
- No genuine new Golden Hybrid v5 GPU PNG is claimed here.

## Change Set 111 — Generator-Bypass Visual Execution Routing

### Core addition
`VisualExecutionRouter` answers the question that must precede provider selection: **does the approved visual plan need an image generator at all?**

Routes:
- `DETERMINISTIC_ONLY`: exact data/geometry/editorial composition; generator/provider blocked.
- `VERIFIED_ASSET_ONLY`: approved source imagery plus deterministic editorial layers; generator/provider blocked.
- `HYBRID_GENERATIVE`: provider allowed only for explicitly declared generator-owned elements.
- `GENERATIVE_SCENE`: provider allowed only when generated content is explicitly declared.

Fail-closed behavior prevents a historical HYBRID label from invoking a provider when the grammar exposes no generator-owned elements.

### Story orchestration integration
`StoryToVisualDecision` now carries `execution_route`, derived only after the final/fallback `VisualGrammarDecision` is known.

Regression coverage proves:
- result -> hybrid generative route;
- tactics -> deterministic-only route;
- table -> deterministic-only route;
- injury -> verified-asset-only route;
- low-confidence story -> verified-asset-only provider bypass;
- confirmed transfer -> no pitch dependency while remaining eligible for restrained hybrid generation.

## CI-discovered propagation gap
The first validation after the new routing layer exposed an existing downstream gap in Golden v5 metadata propagation.

### Failed validation
- GitHub Actions Run `32714112806` / run `1522`.
- The new VisualExecutionRouter tests passed.
- The updated StoryToVisualOrchestrator tests passed.
- 23 downstream Golden v5 tests failed from the same root cause: `LocalBackendRequestCompiler` did not copy `visual_grammar_contract` / `visual_grammar_surface_visibility` and related fields from `GenerationPackage.metadata` into `LocalBackendGenerationRequest.metadata`.

### Repair
`engine/intelligence/local_backend_execution.py` now preserves:
- `visual_grammar_contract`
- `visual_grammar_provider_agnostic`
- `visual_grammar_surface_visibility`
- `visual_grammar_camera_language`
- `visual_grammar_fantasy_level`
- `visual_grammar_generated_elements`
- `visual_grammar_deterministic_elements`
- `visual_grammar_forbidden_generated_elements`

This keeps the story-level visual contract intact through the integrity-locked local/portable Golden handoff boundary.

### Verified success
- Repair commit: `d06807140a463943ea44cfc4581abe9e7dddda32`.
- GitHub Actions Run `32714229033` / run `1526`.
- Conclusion: `success`.
- Phase 18 CPU validation and downstream Golden Hybrid v5 contract checks completed successfully.

## Architecture after Change Set 111
`Verified Story`
-> `Editorial + Visual Plan`
-> `Provider-Agnostic VisualGrammar`
-> `VisualExecutionRouter`
-> if generation is unnecessary: verified assets / deterministic composition
-> if generation is necessary: provider-neutral request / eligible zero-cost backend
-> deterministic exact layers
-> semantic/layer QA
-> Golden quality review
-> exact approved PUL7SAR branding/typography
-> SemanticPublicationGate
-> publication readiness

**PUL7SAR owns the visual decision; a generator is an optional pixel source, not the architecture.**

## Invariants unchanged
- `main` untouched.
- PR #1 remains Draft and unmerged.
- `$0-local` remains active.
- No paid provider or API dependency added.
- FLUX.2 Klein remains a replaceable zero-cost backend candidate.
- Colab remains an execution environment, not an architectural dependency.
- Fact Lock, identity, state integrity and result-neutrality gates remain fail-closed.
- Generated PUL7SAR branding remains forbidden.
- Exact branding, typography, score/data, official marks and exact sport geometry remain deterministic.
- No fake PNG, fabricated GPU proof, fabricated score or publication-ready claim was added.

## Next engineering direction
1. Enforce `VisualExecutionDecision` at the provider-execution boundary so provider selection is structurally impossible when `provider_selection_allowed == False`.
2. Add provider-neutral execution interfaces above FLUX-specific/local adapters.
3. Add non-generator pipeline fixtures proving deterministic and verified-asset stories can complete without a generation job/GPU handoff.
4. Add non-pitch Golden benchmarks for transfer, injury/statement and data/tactics so visual quality is not optimized around one stadium benchmark.
5. Keep genuine rendered Candidate evaluation behind the existing 8.5/9.0 Golden quality and semantic integrity gates.

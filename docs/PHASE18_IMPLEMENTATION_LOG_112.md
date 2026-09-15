# PUL7SAR Phase 18 — Implementation Log Continuation 112

This is the authoritative continuation record for provider-boundary execution enforcement on `phase18/story-intelligence`. No production branch is modified.

## Change Set 112 — Provider Boundary Enforcement

### Goal
Make the generator-bypass decision enforceable at the provider execution boundary, not merely advisory metadata returned by story orchestration.

### Modified
- `engine/intelligence/provider_execution.py`
  - `ProviderExecutionPlanner.compile()` now requires a `VisualExecutionDecision`.
  - A deterministic-only or verified-asset-only route hard-blocks provider execution even when an eligible provider has already been selected.
  - Provider execution requires both `generator_required == True` and `provider_selection_allowed == True`.
  - Provider execution also requires a non-empty list of explicitly declared generator-owned elements.
  - The `GENERATE_BASE_SCENE` step records the visual-execution contract, execution route and exact generator-owned element list.
  - Exact logos, crests, text, score/data and exact sport geometry remain outside the image provider.
- `tests/test_phase18_provider_execution.py`
  - verifies deterministic and verified-asset routes cannot compile a provider plan;
  - verifies an ostensibly generative route with no generator-owned elements is rejected;
  - verifies the execution-route type is mandatory;
  - verifies generation instructions and metadata are bound to the declared generator-owned elements;
  - preserves previous exact-asset, identity-reference and provider-capability tests.

## Result
The architecture now has two independent protections:
1. `VisualExecutionRouter` decides whether a generator is required.
2. `ProviderExecutionPlanner` refuses to cross the provider boundary unless that decision explicitly authorizes generation.

This prevents accidental model invocation caused by legacy workflow shape, provider availability or a preselected backend.

## Verified CI
- Code/test head: `0ef2934864559b83998120076ad61731ec8d31c4`.
- GitHub Actions Run: `32714526219` / run `1541`.
- Conclusion: `success`.
- Discover-based Phase 18 validation: success.
- Phase 18 completion audit: success.
- Production isolation verification: success.
- Golden Hybrid v5 portable handoff build: success.
- Golden Hybrid v5 candidate batch build: success.
- Golden batch integrity verification: success.
- Current Golden Hybrid v5 contract assertion: success.
- No visual proof artifact was fabricated; the visual-proof upload step remained skipped when no genuine proof existed.

## Architecture after Change Set 112
`Verified Story`
-> `Editorial + Visual Plan`
-> `VisualGrammar`
-> `VisualExecutionRouter`
-> **generator bypass OR provider authorization**
-> `ProviderExecutionPlanner` enforcement
-> optional zero-cost provider/backend only when authorized
-> deterministic exact layers
-> semantic/layer QA
-> Golden review
-> exact approved PUL7SAR branding/typography
-> publication gates

## Invariants
- `main` untouched.
- PR remains Draft/unmerged.
- `$0-local` unchanged.
- No paid API/provider added.
- FLUX/Colab remain replaceable implementation/runtime options rather than architecture.
- Exact brand/text/data/official marks/sport geometry remain deterministic.
- No genuine Golden PNG is claimed by this change set.

## Next direction
Build provider-free execution plans for `DETERMINISTIC_ONLY` and `VERIFIED_ASSET_ONLY` stories so those routes can complete end-to-end without manufacturing a dummy generation package, provider selection or GPU job. Then add non-pitch Golden fixtures proving transfer, injury/statement and data/tactics families behave correctly across the full pipeline.

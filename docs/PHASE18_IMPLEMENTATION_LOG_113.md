# PUL7SAR Phase 18 — Implementation Log Continuation 113

This file is the authoritative continuation record for Change Set 113 on `phase18/story-intelligence`. No production branch is modified.

## Change Set 113 — Direct Non-Generative Visual Execution

### Goal
Remove the remaining architectural dependency that forced deterministic or verified-asset stories to pass through generation-oriented contracts even when `VisualExecutionRouter` had already proven that no image generator was required.

### Added
- `engine/intelligence/direct_visual_execution.py`
- `tests/test_phase18_direct_visual_execution.py`
- `DirectVisualExecutionPlanner`
- `DirectVisualExecutionPlan`
- explicit direct base ownership through `PROGRAMMATIC_CANVAS` or `VERIFIED_ASSET`
- deterministic execution stages for base preparation, exact assets, exact data/geometry, editorial text, QA and export

### Architectural result
For `DETERMINISTIC_ONLY` and `VERIFIED_ASSET_ONLY` routes, the pipeline can now proceed without creating or requiring:
- `GenerationPackage`
- image-provider selection
- image-model request compilation
- GPU generation job
- provider-generation provenance

The direct path still requires its own exact-layer integrity, fact/identity checks, typography/layout safety and publication gates. Generator bypass is not a QA bypass.

### Fail-closed behavior
- A generative or hybrid-generative route is rejected by `DirectVisualExecutionPlanner`.
- A verified-asset route is rejected if no `VERIFIED_IDENTITY_REFERENCE` asset is supplied.
- A supplied score is rejected when the planned layout has no score box.
- Exact data and deterministic-element ownership are carried explicitly into the direct execution plan.
- No missing score, formation, table value, geometry or identity is inferred from an image.

### Regression coverage
The new tests prove:
- table/data stories complete through a programmatic canvas with no GenerationPackage/provider/GPU requirement;
- injury/statement-style verified-asset routes use only approved verified source assets as the base;
- missing verified assets fail closed;
- hybrid result stories cannot enter the direct path;
- direct execution has a complete ordered stage list with no `generate_base_scene` stage;
- layout constraints remain enforced.

## CI evidence
Code/test head: `842d472e50ff50c562e03e4b332499197d8b4ade`.
GitHub Actions Run: `32716035780`.
Result: `success`.

The run completed successfully across:
- Phase 18 syntax checks;
- discover-based Phase 18 CPU validation;
- Phase 18 completion audit;
- production isolation verification;
- Golden Hybrid v5 portable handoff build;
- Golden Hybrid v5 batch build and integrity verification;
- current Golden Hybrid v5 contract assertions.

No GPU visual proof was fabricated by CPU CI, and no publication-ready claim is made from this run.

## Invariants unchanged
- `main` / production entrypoints remain untouched.
- PR #1 remains Draft and unmerged.
- `$0-local` remains the development cost policy.
- Generated PUL7SAR branding, exact text, scores, crests and exact sport geometry remain forbidden.
- Identity verification and result neutrality remain fail-closed.
- Golden visual thresholds and semantic publication gates remain unchanged.

## Current architecture
`Verified story -> Editorial/Visual plan -> VisualGrammar -> VisualExecutionRouter`

Then either:

`DETERMINISTIC_ONLY / VERIFIED_ASSET_ONLY -> DirectVisualExecutionPlanner -> exact layers -> direct QA -> export/publication gates`

or:

`HYBRID_GENERATIVE / GENERATIVE_SCENE -> GenerationPackage -> eligible zero-cost provider/backend -> generation provenance/semantic QA -> deterministic exact layers -> final QA/export gates`

## Remaining work
1. Build direct renderers/receipts for programmatic editorial backgrounds and verified-asset base placement so direct plans produce SHA-bound image bytes, not only execution contracts.
2. Add non-stadium Golden benchmarks for transfer, injury/statement and data/tactics visual families.
3. Bind direct outputs into the existing semantic/publication gate without inventing provider provenance for routes that correctly bypass providers.
4. Continue the genuine Golden visual proof path for generative/hybrid families on compatible CUDA/BF16 execution.

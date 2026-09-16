# Phase 18 Implementation Log 320 — Exact Composition Callable Provenance

## Baseline and branch isolation

- Required branch: `phase18/story-intelligence`
- Baseline HEAD reviewed before writing: `788daa1ae61c1044d9d4213d9c86e309889ba9b5`
- Baseline Change Set: CS319 — Deterministic Composition Preparation Checkpoint
- `main` observed before writing: `89b69e0972047af615162518dcc32dc1a16cd2dd`
- No write, merge, rebase, reset, force-update, or branch movement was performed on `main`.

CS319 was reviewed first. Its contract stops at CS270 deterministic composition execution preflight and deliberately does not render pixels.

## Gap identified

The next executable boundary, CS271 (`qwen_image_canonical_candidate_one_shot_composition_execution.py`), already provided strong controls:

- verified READY CS270 input;
- repository-byte binding of the candidate and declared runner source;
- attempt consumption before rendering;
- one-shot execution;
- exact composed-PNG byte binding;
- canvas-dimension enforcement;
- replay verification;
- no semantic, human, Golden, or publication authority.

However, the declared `runner_source_path` and the actual Python `compose_fn` callable were not cryptographically/procedurally linked.

The caller could theoretically supply:

- a benign repository-local file as `runner_source_path`, while
- passing a callable defined in a different file as `compose_fn`.

CS271 would bind the benign file in its receipt even though another callable actually produced the pixels.

This is a genuine composition-provenance gap immediately before the first composed candidate.

## Production change

Modified:

`engine/intelligence/qwen_image_canonical_candidate_one_shot_composition_execution.py`

Added fail-closed callable provenance checks using standard-library `inspect` and `ast` only.

### Pre-render checks

Before the attempt-consumption record is written, CS271 now requires:

1. `compose_fn` is callable and synchronous.
2. the callable source file can be resolved;
3. that source file is repository-local;
4. that source file is exactly the same file as `runner_source_path` after canonical path resolution;
5. the callable is a named top-level function;
6. its entrypoint name is present as a top-level function definition in the exact bound Python source.

A mismatch fails before output-directory creation and therefore before any composition attempt can be consumed or any pixel can be written.

### New receipt evidence

CS271 now records:

- `runner_entrypoint`

in both:

- `composition_attempt_consumption.json`, and
- `one_shot_composition_execution.json`.

The receipt policy also records that:

- callable source must equal the bound runner source;
- the runner entrypoint must be a top-level function.

### Replay verification

`verify_one_shot_composition_execution()` now:

- reopens the exact byte-bound runner source;
- parses those exact source bytes as Python;
- verifies the recorded entrypoint still exists as a top-level function;
- requires attempt-consumption evidence and the final CS271 receipt to agree on runner ID, runner source, and runner entrypoint.

The existing byte-drift checks remain intact.

## Tests changed

Modified:

`tests/test_phase18_qwen_image_canonical_candidate_one_shot_composition_execution.py`

The test harness now loads real temporary repository-local runner modules so the callable provenance contract is exercised rather than mocked away.

Coverage includes:

- a valid runner whose callable comes from the exact bound source;
- failed renderer still consuming the one-shot attempt;
- output dimension drift rejection;
- rejection when the callable comes from a different source file than the declared runner source;
- rejection of a lambda/non-top-level entrypoint;
- composed PNG byte-drift invalidation;
- runner-source byte-drift invalidation;
- existing-output-directory reuse rejection;
- preservation of downstream authority closures.

## Documentation added

Added:

- `docs/PHASE18_CHANGESET_320_EXACT_COMPOSITION_CALLABLE_PROVENANCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_320.md`

## Files added, modified, deleted

### Modified

- `engine/intelligence/qwen_image_canonical_candidate_one_shot_composition_execution.py`
- `tests/test_phase18_qwen_image_canonical_candidate_one_shot_composition_execution.py`

### Added

- `docs/PHASE18_CHANGESET_320_EXACT_COMPOSITION_CALLABLE_PROVENANCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_320.md`

### Deleted

- None.

## Commits

- `37d5b4365aab81976fee18e69a19e981271cf9b5` — bind composition callable to exact runner source.
- `6d29d7624c4d99ed13e3eeb50eb10735ac67b3a9` — regression coverage for callable provenance.
- `ea42c06ccc020858bd2b932218b58642fafb3d06` — CS320 contract documentation.
- current implementation-log commit is the commit containing this file.

## Preserved authority gates

CS320 does not change thresholds, verdict policy, or authority for:

- Fact/Freshness verification;
- Entity/Identity verification;
- manual source comparison when pixel identity is required;
- sentiment neutrality and loser-respect;
- `$0-local` generation policy;
- Semantic Base QA;
- Generated-Layer QA;
- deterministic layer ownership;
- composition/post-composition QA;
- Golden Visual Quality;
- Human Visual Review;
- exact brand/typography approval;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- publication readiness.

CS271 remains an execution authority only. A successful run may set `composition_executed=true`; it may not set visual approval, semantic approval, Golden status, or publication readiness.

## GPU/runtime status

The execution environment available during this change remained CPU-only:

- PyTorch: `2.10.0+cpu`
- CUDA available: `false`
- `torch.version.cuda`: `None`
- CUDA device count: `0`
- native BF16: `false`
- `nvidia-smi`: unavailable

Therefore no Qwen-Image GPU model load, CUDA/BF16 inference, genuine `canonical_candidate.png`, production composed PNG, or Genuine Golden Visual PNG was fabricated or claimed.

## Remaining gap

The first genuine Golden Visual still requires, in order:

1. a compatible zero-cost CUDA/BF16 host with the approved already-local Qwen snapshot and verifier assets;
2. genuine Qwen inference producing the exact candidate;
3. the already-built CS301/CS303/CS304/CS305/identity-aware/CS268 path;
4. exact CS269/CS270 deterministic composition inputs;
5. an actual project-native deterministic composition renderer whose callable is now required by CS320 to originate from the exact byte-bound repository source;
6. CS271 composition execution and CS272 composed-byte admission;
7. all post-composition semantic/layer/visual QA gates;
8. Golden quality and human review;
9. exact brand/typography and final composed approval;
10. final semantic approval and `SemanticPublicationGate`;
11. CS285 exact-byte Genuine Golden materialization;
12. CS286 publication readiness.

CS320 materially reduces step 5's provenance ambiguity without pretending that a renderer or GPU result already exists.

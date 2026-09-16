# Phase 18 Change Set 218 — Remote Renderer Safety Marker Regression Repair

## Scope

Branch: `phase18/story-intelligence` only.

This change set repairs the single failing regression introduced around the isolated remote-renderer engineering benchmark. It does **not** modify the canonical `$0-local` Golden path, generation runtime, semantic gates, publication gates, or `main`.

## Baseline diagnosis

The Phase 18 Story Intelligence Verification run `33110446398` executed 1,411 Phase 18 tests and failed exactly one test:

`test_missing_safety_marker_fails_closed`

The production validator was already correct: it requires the lowercase marker `no sponsor mark` as one of the mandatory renderer-safety phrases. The test attempted to remove `No sponsor mark` with an uppercase `N`, but the canonical benchmark prompt contains lowercase `no sponsor mark`. Python string replacement is case-sensitive, so the fixture was never changed and the validator correctly accepted it.

The failure was therefore a regression-test mutation defect, not a safety-gate failure.

## Change

`tests/test_phase18_remote_renderer_benchmark.py` now:

1. proves the canonical prompt actually contains `no sponsor mark`;
2. removes that exact lowercase marker once;
3. proves the mutated fixture differs from the original;
4. proves the required marker is genuinely absent; and
5. then requires `_validate_prompt()` to fail with `REMOTE_RENDERER_SAFETY_MARKER_MISSING`.

No production validator logic was weakened or changed.

## Safety / authority preservation

The remote benchmark remains strictly non-canonical:

- `cost_mode = $0-remote-zerogpu-study`
- `engineering_benchmark_only = true`
- `canonical_golden_eligible = false`
- `semantic_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

The canonical PUL7SAR policies remain unchanged: Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local` Golden execution, protected branding/text/exact-fact/entity-mark/exact-sport-geometry ownership, Semantic/Layer Ownership, Visual Critic hard failures, Human Review, Golden 8.5 minimum / 9.0+ elite target, Exact Brand/Typography Integrity, and SemanticPublicationGate.

## Files

Modified:
- `tests/test_phase18_remote_renderer_benchmark.py`

Added:
- `docs/PHASE18_CHANGESET_218_REMOTE_RENDERER_SAFETY_MARKER_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_218.md`

Deleted:
- none

`main` / `main.py`:
- untouched

## Golden Visual status

No new canonical Golden PNG is claimed by this change set. The remote ZeroGPU renderer path is an engineering benchmark only and cannot substitute for the accepted genuine Golden Visual path.

The remaining execution blocker is availability of a compatible approved `$0-local` host with the required CUDA/precision/VRAM/RAM/offload/model/runtime evidence. Until such a host is available, no canonical GPU result or visual score may be fabricated.

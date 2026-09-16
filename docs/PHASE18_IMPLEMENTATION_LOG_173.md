# Phase 18 Implementation Log — Change Set 173

## Branch isolation

Target branch: `phase18/story-intelligence` only.

`main` and `main.py` were not modified, merged, force-updated or used as write targets in this change set.

## State reviewed before the change

Phase 18 was actively migrating the Golden benchmark from Hybrid v5 to story-first Editorial v6. The reviewed v6 contracts established:

- generic football `PREVIEW` uses `context_only` sport-surface visibility;
- the story/editorial environment comes before the playing surface;
- no full-pitch master-shot requirement;
- no deterministic pitch replacement for this generic PREVIEW;
- generated exact sport geometry remains forbidden;
- branding and typography remain deterministic downstream layers;
- publication readiness remains fail-closed.

No GPU success was inferred from CPU CI.

## Gap identified

`LocalBackendRequestCompiler` still coupled geometry ownership to deterministic replacement. If a v6 PREVIEW had no reserved deterministic pitch region, it could infer `generated_sport_geometry_allowed=true` even though v6 explicitly forbids generated exact sport geometry.

This was a correctness and safety gap at the final provider-neutral → local FLUX handoff boundary.

## Changes made

### Modified

- `engine/intelligence/local_backend_execution.py`
  - separated exact sport-geometry ownership from deterministic replacement need;
  - all explicit VisualGrammar surface modes keep generated exact geometry forbidden;
  - `context_only` does not force surface replacement;
  - `partial_deterministic` / `full_deterministic` require replacement under the hybrid base-scene contract;
  - legacy packages without VisualGrammar metadata retain the previous fallback.

- `tests/test_phase18_local_backend_execution.py`
  - added `context_only` regression: generated exact geometry false, replacement false;
  - added `partial_deterministic` regression: generated exact geometry false, replacement true;
  - repaired both fixtures to use the already-supported `no humiliation` provider constraint so these ownership tests do not fail in unrelated prompt-translation code;
  - retained existing zero-cost, redaction, provenance, seed/canvas and visual metadata checks.

- `engine/intelligence/golden_prompt_budget.py`
  - repaired the concurrent Editorial v6 compact prompt so it remains below the locked 1,200-character budget;
  - preserved the exact v6 fail-closed markers for a single full-bleed scene, asymmetric hierarchy, no high-wide-central broadcast framing, no full-pitch master shot, fully unbranded base including platform names, and anti-collage composition;
  - kept turf contextual/subordinate and exact pitch markings/geometry forbidden.

### Added

- `docs/PHASE18_CHANGESET_173_STORY_FIRST_GEOMETRY_OWNERSHIP.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_173.md`

### Deleted

None.

## Commits created in this change set

- `975e788eff1e817af59f26fd684eb1f447ef277c` — separate contextual geometry ownership from replacement.
- `06faeac71e0491ec59e724a7240b7bab52c853e2` — add local-backend regression coverage.
- `7b7a3196e0a5d17035f8c88774a87e6e532b451e` — fit the current Golden editorial v6 scene prompt inside the locked budget.
- `d18a8a61e3e9afaadc59ea79c14f58de05b11368` — repair geometry-ownership regression fixtures without changing runtime policy.

Concurrent Phase 18 migration commits continued to align Golden v6 batch, Colab and semantic-continuation contracts. This log does not claim those separate changes as authored by Change Set 173.

## Gates preserved

No relaxation was made to:

- Fact Lock / factual accuracy;
- entity and identity verification;
- sentiment / neutrality / loser-respect policy;
- `$0-local` cost policy;
- FLUX/Qwen model/runtime integrity contracts;
- branding/text/exact-number/entity-mark generation prohibitions;
- generated exact sport-geometry prohibition;
- Qwen semantic visual gates;
- deterministic exact-layer ownership when story/grammar requires it;
- provenance/evidence replay;
- Golden visual-quality thresholds;
- Exact Brand / Typography integrity;
- SemanticPublicationGate or final publication readiness.

## Testing status

Story Intelligence Verification run `32977527649` executed 1,217 Phase 18 tests and exposed the active v5→v6 migration debt. Two errors belonged to the new geometry-ownership test fixtures because they used an unsupported ad-hoc negative-constraint phrase; those fixtures were repaired without changing runtime behavior. A large group of Golden failures was caused by the concurrent v6 compact scene prompt exceeding its locked 1,200-character budget; that prompt was compacted while retaining the v6 verifier markers.

Additional failures in that run were legacy-v5 Colab/smoke/continuation assertions still being migrated to the story-first v6 contract. This log does not mark Change Set 173 CI-green until a later Story Intelligence Verification run succeeds on a head containing the repairs. CPU CI success must never be interpreted as a genuine image-generation result.

## Genuine Golden Visual status / exact blocker

No genuine Golden Visual PNG was produced or claimed in this change set.

The remaining execution blocker is a compatible real local GPU environment able to satisfy the locked first-Golden path, including CUDA, native BF16, sufficient live GPU/system memory, approved local runtime/offload, pinned model/runtime evidence and `$0-local` execution. Until such a host runs Candidate 1, no PNG, visual score or benchmark will be fabricated.

## Next safe work

1. Continue removing legacy-v5 assertions that conflict with the now-active story-first Editorial v6 contract, without weakening v6 gates.
2. Keep v6 handoff, batch, smoke, Colab and provenance tooling consistent end-to-end.
3. Run Candidate 1 only when a compatible CUDA/BF16 host is available.
4. Do not authorize Seeds 2–4 until Candidate 1 is visually and semantically reviewed.

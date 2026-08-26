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

A CI failure during the migration also showed that multiple legacy v5 tests/contracts were still being aligned. No GPU success was inferred from CPU CI.

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
  - retained existing zero-cost, redaction, provenance, seed/canvas and visual metadata checks.

### Added

- `docs/PHASE18_CHANGESET_173_STORY_FIRST_GEOMETRY_OWNERSHIP.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_173.md`

### Deleted

None.

## Commits created in this change set

- `975e788eff1e817af59f26fd684eb1f447ef277c` — separate contextual geometry ownership from replacement.
- `06faeac71e0491ec59e724a7240b7bab52c853e2` — add local-backend regression coverage.
- documentation commits follow on the same Phase 18 branch.

A contemporaneous Phase 18 migration commit also added story-first specification metadata to `GenerationPackageCompiler`; this log does not claim that separate work as part of Change Set 173.

## Gates preserved

No relaxation was made to:

- Fact Lock / factual accuracy;
- entity and identity verification;
- sentiment / neutrality / loser-respect policy;
- `$0-local` cost policy;
- FLUX/Qwen model/runtime integrity contracts;
- branding/text/exact-number/entity-mark generation prohibitions;
- Qwen semantic visual gates;
- deterministic exact-layer ownership;
- provenance/evidence replay;
- Golden visual-quality thresholds;
- Exact Brand / Typography integrity;
- SemanticPublicationGate or final publication readiness.

## Testing status

Regression tests were added, but this log does not mark Change Set 173 CI-green until a GitHub Story Intelligence Verification run completes successfully on a head containing these changes. CPU CI success must not be interpreted as a genuine image-generation result.

## Genuine Golden Visual status / exact blocker

No genuine Golden Visual PNG was produced or claimed in this change set.

The remaining execution blocker is a compatible real local GPU environment able to satisfy the locked first-Golden path, including CUDA, native BF16, sufficient live GPU/system memory, approved local runtime/offload, pinned model/runtime evidence and `$0-local` execution. Until such a host runs Candidate 1, no PNG, visual score or benchmark will be fabricated.

## Next safe work

1. Let the current v6 CPU suite identify remaining legacy-v5 compatibility regressions.
2. Keep the v6 story-first Golden handoff consistent end-to-end through batch, smoke, Colab and provenance tooling.
3. Run Candidate 1 only when a compatible CUDA/BF16 host is available.
4. Do not authorize Seeds 2–4 until Candidate 1 is visually and semantically reviewed.

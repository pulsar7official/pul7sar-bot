# PUL7SAR Phase 18 — Change Set 186

## Pinned model-cache evidence before first genuine Golden Editorial v6 Candidate 1

### Problem

The canonical Golden Editorial v6 path already bound the immutable Qwen semantic snapshot into the Candidate 1 evidence packet, but FLUX cache preparation was still implicit at generation time. In addition, the combined first-Golden cache-budget preflight treated any locally cached model snapshot as sufficient evidence, even when it was not the approved pinned upstream revision.

That left two avoidable failure modes before the first genuine Golden PNG:

1. a stale Qwen or FLUX snapshot could make the shared cache budget look smaller than it really was;
2. Candidate 1 could begin with the exact FLUX revision not yet sealed as pre-generation evidence, forcing the executor to become the first place where model bytes were resolved.

### Implemented

- The shared cache-budget preflight now probes the exact approved immutable Qwen and FLUX revisions with `local_files_only=True` and validates their canonical snapshot revision before counting them as cached.
- The cache-budget receipt records both model IDs and both pinned revisions, plus whether each exact approved snapshot was present.
- The strict Golden v6 resource lock now runs the combined pinned cache-budget preflight before either model download.
- The exact pinned Qwen snapshot remains preflighted and bound.
- The exact pinned FLUX snapshot is now explicitly prefetched and validated before the runtime fingerprint and before Candidate 1.
- `cache_budget` and `flux_model_cache` are now part of the SHA-256/byte-size evidence map that accompanies Candidate 1.
- The final resource lock is upgraded to `pul7sar-first-genuine-golden-v6-resource-lock-v4` with status `FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED`.
- The canonical self-hosted Golden v6 workflow replays the combined cache budget, pinned Qwen cache, pinned FLUX cache, runtime fingerprints, strict staging, and final PNG before artifact upload.

### Safety preserved

This change does not authorize generation from the cache-budget step, does not change the model, does not introduce a paid provider, does not weaken BF16/resource gates, and does not alter semantic or publication policy. Human review, Golden quality, exact brand/typography and SemanticPublicationGate remain downstream and fail-closed.

### Files

Modified:

- `tools/phase18_preflight_first_golden_cache_budget.py`
- `tools/phase18_colab_first_genuine_resources_locked.py`
- `.github/workflows/phase18-first-genuine-golden-v6.yml`
- `tests/test_phase18_first_genuine_golden_v6_workflow.py`

Added:

- `docs/PHASE18_CHANGESET_186_PINNED_MODEL_CACHE_EVIDENCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_186.md`

Deleted: none.

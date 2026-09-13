# Phase 18 Change Set 139 — First Golden Shared Cache Budget

## Goal

Prevent the next strict Golden GPU session from partially downloading Qwen and then discovering that the same Hugging Face cache filesystem no longer has enough free space for FLUX.2 Klein 4B, or vice versa.

The existing Qwen and FLUX prefetch tools each had correct per-model free-space guards. Because both normally share the same cache filesystem, independent checks could still pass sequentially while the combined missing-model requirement was not available before the first download started.

## Added

### `engine/intelligence/first_golden_cache_budget.py`

Introduces a pure fail-closed combined cache-budget policy.

- If both approved snapshots are missing, the conservative requirement is the sum of the existing Qwen and FLUX headroom policies: 12 GiB + 30 GiB = 42 GiB.
- If Qwen is already cached, only the 30 GiB FLUX headroom remains required.
- If FLUX is already cached, only the 12 GiB Qwen headroom remains required.
- If both are cached, no additional free-space proof is required.
- Unknown free space fails closed whenever at least one approved model is missing.

This policy does not download models and does not authorize generation.

### `tools/phase18_preflight_first_golden_cache_budget.py`

A download-free preflight command that:

- requires `phase18/story-intelligence`;
- checks the exact approved Qwen and FLUX model IDs using `local_files_only=True`;
- inspects the shared Hugging Face cache filesystem;
- applies the combined conservative budget before any model download;
- writes `output/phase18_gpu_smoke/first-golden-cache-budget.json`;
- keeps `$0-local` and all generation/publication authorities false.

### `tests/test_phase18_first_golden_cache_budget.py`

Regression coverage for:

- both models missing with insufficient combined headroom;
- both models missing with sufficient combined headroom;
- Qwen-only cached;
- FLUX-only cached;
- both models cached;
- missing free-space proof;
- invalid negative disk values.

## Modified

### `tools/phase18_colab_first_golden_bootstrap.py`

The strict first-Golden bootstrap now runs the combined cache-budget preflight immediately after verified runtime repair makes `huggingface_hub` available, but before:

- the semantic runtime probe;
- Qwen model prefetch;
- FLUX model prefetch/readiness inside sealed staging;
- queue mutation;
- Candidate 1 generation.

It rejects cache-budget schema/branch/cost/authority drift and records the receipt path in its final bootstrap evidence.

### `tests/test_phase18_colab_first_golden_bootstrap.py`

The bootstrap regression contract now fixes the order:

`repository integrity -> runtime repair -> combined cache budget -> semantic runtime probe -> Qwen prefetch -> sealed Candidate 1 staging`

A failed combined budget must stop before semantic model prefetch and before any Golden staging.

## Deleted

Nothing.

## Gates unchanged

No change was made to:

- Fact Lock;
- entity/identity verification;
- sentiment or losing-side neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock;
- BF16 lock;
- Candidate/seed/canvas locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE or HYBRID_SURFACE requirements;
- deterministic football geometry ownership;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand/typography integrity;
- SemanticPublicationGate.

This change only prevents a known avoidable host-storage failure before expensive GPU work begins.

# Phase 18 Change Set 140 — GPU Smoke Shared Cache Budget Gate

## Goal

Carry the combined Qwen + FLUX cache-budget protection from the strict Colab first-Golden bootstrap into the self-hosted GPU smoke workflow, so a GPU session cannot begin downloading one approved model and only later discover that the shared Hugging Face cache filesystem cannot accommodate the other.

## Context

Change Set 139 introduced `FirstGoldenCacheBudgetPolicy` and the download-free command `tools/phase18_preflight_first_golden_cache_budget.py`.

The strict Colab bootstrap already used that policy before Qwen/FLUX model downloads. The self-hosted GPU smoke workflow still performed Qwen semantic preflight first and FLUX prefetch second without the combined shared-cache budget receipt.

That asymmetry could waste a scarce compatible GPU session even though the failure is predictable before any model download.

## Modified

### `.github/workflows/phase18-gpu-smoke.yml`

The workflow now:

1. proves repository/reference integrity;
2. proves CUDA-enabled PyTorch exists;
3. installs the already-approved Phase 18 GPU optional dependencies;
4. runs the download-free combined Qwen + FLUX cache-budget preflight;
5. verifies the receipt schema, protected branch, `$0-local`, exact Qwen/FLUX model IDs, no-download state, budget eligibility, and absence of generation/publication authority;
6. only then allows Qwen semantic/model preflight;
7. only then allows FLUX model prefetch/readiness and Candidate 1 generation.

The workflow branch-isolation step now also requires:

- `engine/intelligence/first_golden_cache_budget.py`;
- `tools/phase18_preflight_first_golden_cache_budget.py`.

The resulting `first-golden-cache-budget.json` is included in the tamper-evident GPU evidence manifest before replay verification and artifact upload.

### `tests/test_phase18_gpu_smoke_workflow.py`

The regression contract now proves:

- repository integrity remains before GPU/dependency/model work;
- the combined cache-budget command exists in the workflow;
- it runs after dependencies make `huggingface_hub` available but before Qwen or FLUX downloads;
- the exact approved Qwen and FLUX model IDs remain locked;
- the budget receipt must be eligible and download-free;
- generation, queue, PNG, and publication authorities remain false;
- the cache-budget receipt is sealed into the GPU evidence manifest.

## Added

This Change Set documentation and the corresponding implementation log.

## Deleted

Nothing.

## Gates unchanged

No change was made to:

- Fact Lock;
- entity/identity verification;
- sentiment or losing-side neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock;
- native BF16 lock;
- Candidate/seed/canvas locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE or HYBRID_SURFACE requirements;
- deterministic football geometry ownership;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand/typography integrity;
- SemanticPublicationGate.

## Why this reduces the remaining gap

The remaining blocker to the first genuine Golden Hybrid v5 PNG is still a compatible NVIDIA CUDA + BF16 execution host. This change does not fabricate that execution. It makes the next real GPU session more likely to reach Candidate 1 by eliminating a predictable shared-storage failure before either approved model begins downloading.

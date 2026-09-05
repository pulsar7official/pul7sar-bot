# PUL7SAR Phase 18 — Implementation Log 140

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed before and after the implementation work and was not modified, merged, force-updated, or used as a write target.

At the post-change comparison point, the Phase 18 branch remained diverged from `main`, ahead by 1231 commits and behind by 120 commits. The current `main` base commit observed during comparison was `fb585dde848ef5b6e2efe227090ad1d8f9b66644`.

## Change Set 140 — GPU Smoke Shared Cache Budget Gate

### Problem addressed

Change Set 139 introduced a combined, download-free Qwen + FLUX shared-cache budget preflight and integrated it into the strict Colab first-Golden bootstrap.

The self-hosted GPU smoke workflow still had an avoidable gap: it could start Qwen prefetch and only later discover that the same Hugging Face cache filesystem lacked enough remaining headroom for FLUX.2 Klein 4B, or the reverse depending on cached state.

Because a compatible self-hosted CUDA/BF16 window is scarce, that failure should be rejected before either approved model begins downloading.

### Added

- `docs/PHASE18_CHANGESET_140_GPU_SMOKE_SHARED_CACHE_BUDGET.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_140.md`

### Modified

#### `.github/workflows/phase18-gpu-smoke.yml`

Added the existing Change Set 139 shared-cache budget preflight to the real self-hosted GPU path.

The workflow order is now:

`repository integrity -> CUDA proof -> approved optional dependencies -> combined Qwen+FLUX cache budget -> Qwen semantic/model preflight -> FLUX prefetch/readiness -> Candidate 1 -> provenance -> Hybrid semantic path -> evidence sealing/replay`

The new workflow step validates:

- schema `pul7sar-first-golden-cache-budget-v1`;
- branch `phase18/story-intelligence`;
- `$0-local`;
- exact Qwen model `Qwen/Qwen2.5-VL-3B-Instruct`;
- exact FLUX model `black-forest-labs/FLUX.2-klein-4B`;
- `ready=true`;
- `downloads_performed=false`;
- combined budget eligibility;
- no generation, queue, PNG, or publication authority.

The branch-isolation step now requires both the cache-budget policy module and CLI.

The resulting `output/phase18_gpu_smoke/first-golden-cache-budget.json` is now included in the tamper-evident GPU evidence manifest.

#### `tests/test_phase18_gpu_smoke_workflow.py`

Expanded workflow regression coverage so that:

- repository integrity stays before the cache/model/generation path;
- the combined cache budget runs before Qwen and FLUX model downloads;
- model IDs and `$0-local` remain locked;
- the cache-budget stage cannot authorize generation or publication;
- the cache-budget receipt is sealed into evidence before replay/upload.

### Deleted

Nothing.

## Safety and publication gates preserved

The following were not weakened or bypassed:

- Fact Lock;
- entity/identity verification;
- sentiment/neutrality including respectful losing-side treatment;
- `$0-local` execution policy;
- FLUX.2 Klein 4B lock;
- native BF16 lock;
- Candidate/seed/canvas locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE semantic/layer ownership gate;
- deterministic football geometry ownership and artifact-integrity replay;
- Qwen HYBRID_SURFACE semantic/alignment gate;
- human-review SHA locks;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

No paid provider, hosted GPU fallback, API secret, fake PNG, fake benchmark, or publication bypass was added.

## Testing status

The code and regression-test changes were pushed to `phase18/story-intelligence` and should trigger the existing Phase 18 verification workflows.

At the time this log was written, final GitHub Actions results for the Change Set 140 head had not yet been confirmed. This log therefore does not claim CI-green status prematurely.

## Remaining blocker to first genuine Golden Visual PNG

A genuine Golden Hybrid v5 Candidate 1 still requires an actual compatible NVIDIA CUDA + BF16 host capable of running the locked FLUX.2 Klein 4B path and the required Qwen semantic stages.

That execution is not available in the current automation environment, so no PNG or benchmark was fabricated.

The next real GPU session is now better protected against avoidable shared-cache exhaustion before model downloads. Candidate 1 should still be the only seed executed until its Base/Hybrid semantic, geometric, human, and Golden quality review is complete.

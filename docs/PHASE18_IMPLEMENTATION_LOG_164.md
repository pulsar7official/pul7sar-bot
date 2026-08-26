# PUL7SAR Phase 18 — Implementation Log 164

## Branch isolation

- Target branch: `phase18/story-intelligence`.
- Reviewed Phase 18 HEAD before this change: `3ce8e8b04ac4dbc4601269d6196a1284fcec6cb4`.
- Reviewed `main` HEAD: `6b77770630c2f4ce84b67c477b291eca058ee182`.
- Branch state after the code/test changes: `diverged`; Phase 18 was 1,447 commits ahead of `main` and 159 behind.
- `main` / `main.py` were reviewed but not modified, merged, force-updated, or used as a write target.

## Pre-change CI state

Change Set 163 is now confirmed green:

- Phase 18 Story Intelligence Verification `32927820015 / 2826`: `success`.
- Adaptive Brand Pixel, Composition Matrix, Data Monument, Event Hybrid Context, Tactical Intelligence, Verified Match Result, Result Statement, Premium Hybrid Result, and Event Editorial companion workflows on the same source commit also completed successfully.

This closed the prior exact Golden venue-marker regression before Change Set 164 began.

## Gap identified

The concrete FLUX.2 Klein runtime already prefers Diffusers sequential CPU offload on constrained GPUs. Its own runtime documentation records why: a real T4-class host (~14.6 GiB VRAM) proved that model-level CPU offload can still OOM inside FLUX.2 attention at the locked Golden canvas.

However, if `enable_sequential_cpu_offload()` were unavailable, the factory could fall back to `enable_model_cpu_offload()`. That fallback was unsafe on a T4-class host and could waste the first genuine Candidate 1 attempt after all repository, model, semantic, runtime-fingerprint, and live-VRAM gates had already passed.

A second gap existed if callers set `prefer_sequential_cpu_offload=False`: low-VRAM model offload could be selected intentionally and bypass the default preference.

## Code change

### Modified — `engine/intelligence/flux2_klein_diffusers.py`

Added a fail-closed physical-VRAM safety gate around model-level CPU offload.

New behavior:

1. sequential CPU offload remains the preferred default;
2. if model-level offload would be used, CUDA physical VRAM must be measurable;
3. model-level offload is rejected at or below the default 16-GiB safety floor;
4. unknown CUDA VRAM is rejected instead of guessed;
5. disabling the sequential preference does not bypass the model-offload VRAM gate;
6. the model-offload safety floor is explicit in `Flux2KleinInferenceConfig` and must be positive.

No model, precision, seed, canvas, inference step, prompt, or publication policy was changed.

### Modified — `tests/test_phase18_flux2_klein_diffusers.py`

Added regression coverage for:

- high-memory model-offload acceptance;
- T4-class low-VRAM model-offload rejection;
- unknown-VRAM rejection;
- attempted low-VRAM bypass through `prefer_sequential_cpu_offload=False`;
- invalid safety-floor configuration;
- continued preference for sequential CPU offload.

## Added

- `docs/PHASE18_CHANGESET_164_LOW_VRAM_SEQUENTIAL_OFFLOAD_LOCK.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_164.md`

## Modified

- `engine/intelligence/flux2_klein_diffusers.py`
- `tests/test_phase18_flux2_klein_diffusers.py`

## Deleted

None.

## Commits in this change

- `e4508eefce2552d4aafca063abacd98f52e70174` — initial low-VRAM sequential-offload safety implementation.
- `43f8cc249f01447a836bebfc7cda60260066ee3c` — regression coverage.
- `bcfaced35db699bfb06318d9dab3e56d1bede902` — closed the explicit sequential-preference bypass and made all model-offload paths require measured high VRAM.
- `b9c525f88069f5d2fef5c3b09d7dcd5bccf32ac0` — aligned regression tests with the final fail-closed contract.

## Gates preserved

Unchanged and still fail-closed:

- factual integrity / Fact Lock;
- Entity/Identity Verification;
- Sentiment and result neutrality;
- `$0-local` execution policy;
- immutable approved FLUX.2 Klein 4B revision;
- immutable approved Qwen revision;
- native BF16;
- total/live-free-VRAM host qualification;
- lease-bound GPU requalification;
- runtime fingerprint stability;
- Candidate/request/seed/canvas/SHA locks;
- prohibition on generated platform branding, exact text/numbers, entity marks, and sport geometry;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` semantic gates;
- deterministic football geometry ownership;
- provenance/evidence replay;
- Golden Visual Quality: 8.5 minimum, 9.0+ elite;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate and final publication readiness.

## Tests

Pre-change evidence:

- Story Intelligence Verification `32927820015 / 2826`: `success` on Change Set 163.

Post-change status:

- The new code and tests were committed on `phase18/story-intelligence`.
- GitHub Actions should run automatically on the new HEAD; do not record Change Set 164 as CI-green until a completed successful Story Intelligence Verification run is observed.

## Golden PNG status

No genuine Golden Hybrid v5 Candidate 1 PNG was produced in this CPU/tooling environment. No placeholder, fake visual, synthetic benchmark score, or publication claim was created.

Exact external blocker remains a real host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live free VRAM;
- the pinned FLUX and Qwen revisions;
- stable runtime fingerprint through generation and semantic inspection.

This change narrows the remaining gap by ensuring that a T4-class or otherwise low-VRAM host cannot silently enter the known-risk model-level offload path when sequential CPU offload is unavailable. Candidate 1 remains the only authorized seed until a genuine image is produced and accepted through semantic, human, and Golden quality review.

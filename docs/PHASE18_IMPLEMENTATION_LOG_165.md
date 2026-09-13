# PUL7SAR Phase 18 — Implementation Log 165

## Branch isolation

- Target branch: `phase18/story-intelligence` only.
- Reviewed Phase 18 HEAD before this change: `9cf941a64c228704594bc29c8a9cc53aa333e684`.
- Reviewed `main` HEAD: `6b77770630c2f4ce84b67c477b291eca058ee182`.
- Current branch remained `diverged` from `main`; after the code/test changes it was 1,456 commits ahead and 159 behind.
- `main` / `main.py` were not modified, merged, force-updated, or used as a write target.

## Pre-change CI state

Change Set 164 is now confirmed green:

- Phase 18 Story Intelligence Verification `32931704204 / 2838`: `success`.
- Result Statement, Composition Matrix, Data Monument, Tactical Intelligence, Verified Match Result, Event Editorial, Premium Hybrid Result, Adaptive Brand Pixel and Event Hybrid Context companion workflows on the same source commit also completed successfully.

## Gap identified

Change Set 164 correctly prevented the concrete FLUX.2 factory from using model-level CPU offload on low-VRAM hosts when sequential CPU offload is unavailable. However, the factory discovers those offload methods only after calling `Flux2KleinPipeline.from_pretrained(...)`.

That left a remaining avoidable gap on the first genuine GPU session: a constrained host could pass repository, CUDA/BF16 and live-VRAM qualification, then begin cache/model preparation before the installed Diffusers build proved it exposes the sequential offload API required for safe T4-class execution.

This change moves that capability proof ahead of model-weight download/load work.

## Added

### `engine/intelligence/flux2_offload_capability.py`

Introduced a no-weight-load capability probe that inspects the installed `Flux2KleinPipeline` class only.

It proves:

- `Flux2KleinPipeline` exists;
- whether `enable_sequential_cpu_offload` exists;
- whether `enable_model_cpu_offload` exists;
- measured total VRAM is known;
- hosts at or below the existing 16-GiB model-offload safety floor select `sequential_cpu` only;
- high-VRAM hosts may use `model_cpu` only if sequential offload is unavailable;
- no model load, download, network use, queue mutation, image generation or publication authority occurs.

### `tools/phase18_preflight_flux2_offload.py`

Added a CPU/runtime-only CLI that consumes the already-generated GPU host qualification receipt and writes:

`output/phase18_gpu_smoke/flux2-offload-preflight.json`

It requires:

- branch `phase18/story-intelligence`;
- approved `black-forest-labs/FLUX.2-klein-4B` model identity;
- `local_cuda`;
- CUDA available;
- native BF16 proven;
- `$0-local`;
- measured physical VRAM;
- a safe offload mode from the installed Diffusers runtime.

The receipt keeps all generation, semantic, Golden and publication authority false.

### `tests/test_phase18_flux2_offload_capability.py`

Added regression coverage for:

- low-VRAM sequential success;
- low-VRAM model-only rejection;
- high-VRAM model-offload fallback;
- unknown VRAM fail-closed behavior;
- missing offload API rejection;
- zero-cost/no-authority preflight receipt;
- host model identity drift rejection.

### Documentation

- `docs/PHASE18_CHANGESET_165_PREMODEL_FLUX_OFFLOAD_CAPABILITY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_165.md`

## Modified

### `tools/phase18_colab_first_golden_bootstrap.py`

The strict Candidate 1 bootstrap now runs:

`repository integrity → runtime repair → GPU host qualification → FLUX offload capability preflight → shared cache budget → Qwen runtime/model → sealed Candidate 1 staging`

The offload preflight therefore happens before Qwen or FLUX model preparation. The bootstrap contract was upgraded to:

`pul7sar-first-golden-colab-bootstrap-v5`

It now records:

- `flux2_offload_preflight`;
- `flux2_safe_offload_mode`;
- `flux2_safe_offload_proven=true`;
- a SHA/size evidence record for the offload receipt.

### `tests/test_phase18_colab_first_golden_bootstrap.py`

Updated the canonical ordering and evidence expectations. Added fail-closed tests proving:

- low-VRAM offload-capability failure stops before cache/model download work;
- offload receipt authority drift is rejected;
- the v5 bootstrap evidence set includes the offload receipt.

### `.github/workflows/phase18-first-golden-review.yml`

The canonical self-hosted first-Golden workflow now replays the v5 bootstrap and the new offload evidence.

It verifies:

- offload receipt schema/readiness;
- approved FLUX identity and `$0-local`;
- pipeline capability is proven;
- selected safe mode matches the bootstrap;
- host total VRAM matches offload-preflight total VRAM;
- low-VRAM hosts are locked to `sequential_cpu`;
- the offload preflight did not load weights, download models, mutate the queue, generate pixels, approve semantics/Golden quality, or open publication.

### `tests/test_phase18_first_golden_review_workflow.py`

Updated regression assertions for bootstrap v5 and the offload evidence replay chain.

## Deleted

None.

## Commits in Change Set 165

- `2e2872c94bf6f2efffef8fe4506a6b2809a1e0a7` — offload capability engine.
- `8333849493a6a22d6dfd99b74c35190de422a5be` — offload preflight CLI.
- `cbc645dc689cad18c5e39b69f7e6282753baadea` — offload preflight regression tests.
- `16e65f2860a951dfe338a73513771047b2faf94f` — strict bootstrap integration.
- `32bb13ed440047d8c4cae07e9d0edca466a90a09` — bootstrap regression alignment.
- `221a8fb6161c1f3a0884341d08914b30bd515468` — canonical workflow evidence replay.
- `5f6cef54b22275b2594d1bd1c0c1206c40971abf` — workflow regression lock.
- `1333ccce231adf7362348804273587052d1bdee3` — Change Set documentation.

## Gates preserved

Still unchanged and fail-closed:

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
- generated platform branding/text/exact facts/entity marks/sport geometry prohibitions;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` semantic gates;
- deterministic football geometry ownership;
- provenance/evidence replay;
- Golden Visual Quality 8.5 minimum / 9.0+ elite;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate and final publication readiness.

## Tests

Confirmed pre-change evidence:

- Story Intelligence Verification `32931704204 / 2838`: `success` on Change Set 164.

Post-change:

- all Change Set 165 code/tests/documentation are committed to `phase18/story-intelligence`;
- GitHub Actions is expected to run automatically on the new HEAD;
- do not record Change Set 165 as CI-green until a completed successful Story Intelligence Verification run is observed.

## Golden PNG status

No genuine Golden Hybrid v5 Candidate 1 PNG was produced or claimed in this tooling-only environment.

Exact external blocker remains a physical host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live free VRAM;
- approved pinned FLUX/Qwen revisions;
- stable runtime fingerprint;
- safe installed Diffusers offload capability;
- successful real model execution and semantic inspection.

The remaining gap is smaller because a low-VRAM host with an incompatible Diffusers offload API will now fail **before** model weight loading/download work rather than during pipeline construction or inference. Candidate 1 remains the only authorized seed until a real image exists and passes semantic, human and Golden-quality review.

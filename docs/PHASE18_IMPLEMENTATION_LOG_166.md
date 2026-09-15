# PUL7SAR Phase 18 Implementation Log — Change Set 166

## Branch isolation reviewed first

Repository: `pulsar7official/pul7sar-bot`

Development branch: `phase18/story-intelligence`

Branch HEAD at start of this change set: `d602e1638d2766e051e46c53ac01d9f3e79faddb`

`main` observed independently at: `811576f5e23a4cbd1d195d7da5679d1cce356d42`

The branches remain diverged. A comparison after the code/test additions reported Phase 18 **1463 commits ahead / 160 behind** that observed `main` head. `main` and `main.py` were not write targets, were not merged, and were not force-updated.

## Previous verified baseline

Change Set 165 baseline is CI-green. For commit `d602e1638d2766e051e46c53ac01d9f3e79faddb`, GitHub Actions reports:

- Phase 18 Story Intelligence Verification run `32936028192` — `success`;
- Composition Matrix Verification — `success`;
- Verified Match Result, Premium Hybrid Result, Tactical Intelligence, Event Hybrid Context, Event Editorial, Result Statement, Adaptive Brand Pixel, and Data Monument companion workflows — `success`.

No GPU image is inferred from those CPU workflow successes.

## Change Set 166 — Host Memory Preflight Before First Golden Model Work

### Problem found

The first-Golden path now proves:

- immutable Phase 18 source;
- pinned FLUX/Qwen revisions;
- runtime fingerprint stability;
- CUDA/native BF16;
- total and live-free GPU VRAM;
- safe Diffusers CPU-offload API capability;
- cache budget;
- lease-bound GPU requalification.

However, sequential CPU offload also consumes system RAM. There was no independent fail-closed proof of *currently available host RAM* before Qwen/FLUX model preparation. A memory-starved zero-cost GPU host could therefore pass the GPU gates and fail later during model work.

### Added

1. `engine/intelligence/host_memory_qualification.py`
   - stdlib-only live memory measurement from `/proc/meminfo`;
   - total/available/used RAM plus swap telemetry;
   - 10 GiB default available-RAM admission floor;
   - no guessing when `MemAvailable` is missing;
   - no generation/publication authority.

2. `tools/phase18_preflight_host_memory.py`
   - Phase-18-only CPU preflight;
   - writes `output/phase18_gpu_smoke/host-memory-preflight.json`;
   - `$0-local`;
   - no download/model load/queue mutation/PNG.

3. `tools/phase18_colab_first_golden_host_memory_locked.py`
   - runs host-memory qualification before the existing runtime-locked Candidate 1 path;
   - SHA-binds the memory receipt and runtime-lock receipt;
   - keeps human/Golden/publication/Seeds 2-4 authority closed.

4. `tests/test_phase18_host_memory_qualification.py`

5. `tests/test_phase18_first_golden_host_memory_lock.py`

6. `docs/PHASE18_CHANGESET_166_HOST_MEMORY_PREFLIGHT.md`

7. this implementation log.

### Modified

No previously existing runtime or production file was modified. Change Set 166 is additive around the already CI-qualified Change Set 165 path.

### Deleted

None.

### Main branch

`main`: not modified.

`main.py`: not modified.

No merge or force-update was performed.

## Gate preservation

No relaxation was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen revision;
- native BF16;
- total/live-free VRAM qualification;
- safe offload qualification;
- lease-bound GPU requalification;
- runtime fingerprinting;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact facts/entity marks/sport geometry prohibitions;
- Qwen `BASE_SCENE` / `HYBRID_SURFACE` gates;
- deterministic football geometry;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate.

## Test status for Change Set 166

New regression tests have been committed and are discoverable under `tests/test_phase18_*.py`.

At the time this implementation log was written, the new branch HEAD had not yet produced a completed Story Intelligence Verification result, so Change Set 166 is **not** recorded as CI-green until an actual GitHub Actions success is observed.

## Exact remaining blocker

A genuine Golden Hybrid v5 PNG still requires an actual compatible execution host. The available tool environment for this run does not expose a machine meeting the complete runtime contract:

- NVIDIA CUDA;
- native BF16;
- sufficient total GPU VRAM;
- sufficient live-free GPU VRAM at execution time;
- safe Diffusers offload capability;
- sufficient currently available host RAM;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen revision;
- unchanged runtime fingerprint;
- `$0-local` execution.

No PNG, benchmark, score, or visual success is fabricated.

## Next safe work

After CI confirms Change Set 166, the next integration step should move the host-memory receipt into the canonical self-hosted first-Golden workflow/evidence replay so the GitHub-controlled GPU path enforces the same system-memory gate before model work. Until a compatible GPU host exists, Candidate 1 remains the only authorized Golden seed.

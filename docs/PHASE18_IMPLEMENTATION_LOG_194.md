# PUL7SAR Phase 18 Implementation Log — Change Set 194

## Branch isolation

All writes in this change set target `phase18/story-intelligence` only.

Starting Phase 18 HEAD reviewed for this run: `8f15e83e5d213d3e063edf999484ec71a626ca4b`.

Starting `main` HEAD observed during this run: `813ef31d2647e4353ca604e60e48975c79d7d95e`.

After the main code/test/workflow additions, Phase 18 HEAD reached `bde63cd474c3401f9dfac5fe8d37274e0674224d`. GitHub compare reported the branches still diverged, with Phase 18 ahead by 1679 commits and behind by 208 commits relative to the observed main HEAD. `main` and `main.py` were not modified, merged, rebased, force-updated, or used as write targets.

## Baseline verification state

Change Set 193 is confirmed CI-green.

Phase 18 Story Intelligence Verification run `33055976530` / run number `3236` completed with `success` on source HEAD `8f15e83e5d213d3e063edf999484ec71a626ca4b`.

Companion Phase 18 checks visible on the same source HEAD also completed successfully.

## Gap identified

Change Set 193 sealed two live just-in-time resource receipts immediately before Candidate 1:

- live GPU qualification, including native BF16 and live-free VRAM;
- live host-memory qualification.

The strict staging entrypoint replayed those files immediately after generation. However, the outer canonical offload evidence boundary later verified the staging receipt as a file without independently reopening and replaying the nested JIT resource receipts referenced by that staging receipt.

That meant a later workflow boundary could prove that the staging JSON itself was unchanged while not independently proving that its nested JIT GPU/RAM files still existed, still matched their recorded hashes/sizes, still met the required resource floors, and still carried no illegal authority.

For the first genuine Golden PNG, this nested evidence must replay end-to-end.

## Implemented

### 1. Reusable JIT resource replay verifier

Added `engine/intelligence/golden_jit_resource_replay.py`.

The verifier is CPU-safe and performs no CUDA probing, model loading, queue mutation, generation, or publication action. It:

- requires the current strict Golden staging v3 contract;
- requires Candidate 1, `$0-local`, and `bfloat16`;
- requires `pre_execution_resource_guard_bound=true`;
- re-hashes and size-checks both nested JIT evidence records;
- rejects repository path escape;
- revalidates GPU model identity, `local_cuda`, CUDA availability, native BF16, live-free VRAM floor, and no-download/no-paid/no-queue policy;
- revalidates current host-memory preflight schema, Phase 18 branch identity, live RAM floor, `$0-local`, and closed authority fields;
- compares the staging scalar resource values against the underlying receipt values;
- emits a deterministic `resource_fingerprint_sha256` over the two validated resource receipts and their key resource values;
- keeps generation, semantic, Golden, publication, and Seeds 2-4 authority closed.

### 2. JIT-replay-locked first genuine Golden v6 wrapper

Added `tools/phase18_colab_first_genuine_jit_replay_locked.py`.

The wrapper delegates to the already qualified pre-model + actual-execution offload path and then:

- validates the offload-lock v2 result;
- replays the nested inner resource-lock evidence record;
- replays the exact strict staging evidence record;
- runs `verify_golden_jit_resource_replay()` on that staging payload;
- writes a JIT replay receipt;
- requires the same PNG SHA across offload lock, inner resource lock, and strict staging;
- seals offload lock, inner resource lock, strict staging, JIT replay, and PNG identity in a final `pul7sar-first-genuine-golden-v6-jit-lock-v1` receipt;
- leaves human review required and all downstream authority closed.

### 3. Self-hosted JIT-replay-locked Golden v6 workflow

Added `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`.

The workflow is:

- manual only;
- self-hosted CUDA/BF16 only;
- `$0-local` only;
- pinned to immutable `github.sha` with `fetch-depth: 0`;
- reattached to local `phase18/story-intelligence` at the same SHA;
- read-only against `main` for merge-base / `main.py` isolation proof;
- forbidden from automatically replacing PyTorch;
- dependent on the JIT-replay-locked Candidate 1 wrapper;
- required to replay the outer evidence set before artifact upload;
- required to run the JIT replay verifier again from the current nested staging receipt before artifact upload;
- required to revalidate the current PNG signature/SHA/size;
- unable to grant human, Golden, publication, or Seeds 2-4 authority.

### 4. Regression coverage

Added:

- `tests/test_phase18_golden_jit_resource_replay.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_lock.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_workflow.py`

Coverage includes:

- valid nested GPU/RAM replay;
- GPU evidence byte tampering;
- low live-free VRAM even when the changed record is re-hashed;
- low available host RAM;
- staging publication-authority drift;
- evidence path escape;
- ordering from offload lock to nested JIT replay to final receipt;
- preservation of actual-offload binding;
- immutable/manual/self-hosted workflow source;
- JIT replay before artifact upload;
- exact outer evidence-set replay and PNG replay.

One ordering regression assertion was corrected after review: the first version searched for the imported function name `verify_golden_jit_resource_replay`, which appears before runtime execution. It was changed to target the actual runtime call site `jit = verify_golden_jit_resource_replay(...)`, preserving the intended ordering contract without weakening runtime behavior.

## Files changed

Added:

- `engine/intelligence/golden_jit_resource_replay.py`
- `tools/phase18_colab_first_genuine_jit_replay_locked.py`
- `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`
- `tests/test_phase18_golden_jit_resource_replay.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_lock.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_workflow.py`
- `docs/PHASE18_CHANGESET_194_JIT_RESOURCE_REPLAY_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_194.md`

Modified during the change set:

- `tests/test_phase18_first_genuine_golden_v6_jit_lock.py` (runtime-order assertion correction only).

Deleted: none.

## Safety and quality gates preserved

No gate was weakened. The following remain fail-closed:

- factual integrity / Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful result treatment;
- `$0-local` execution;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen revision/snapshot;
- native BF16;
- total/live-free VRAM and live host-RAM qualification;
- safe Diffusers offload qualification and actual-executor offload binding;
- model-cache revision locks and post-cache disk headroom;
- stable runtime fingerprint;
- Candidate/request/seed/canvas/SHA identity locks;
- generation/execution provenance replay;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Qwen BASE_SCENE/layer ownership;
- story-first Golden Editorial v6 composition-map lock;
- Golden minimum `8.5` / elite target `9.0+`;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate and final publication readiness;
- Seeds 2-4 remain unauthorized before genuine Candidate 1 succeeds and is visually accepted.

## Test status for Change Set 194

The code, tests, workflow, documentation, and runtime-order regression correction were committed to `phase18/story-intelligence`.

Story Intelligence Verification run `33060887668` was created for the code/test HEAD `52666471564bb5d82419556f84110284637dfd38` and was still `queued` at the last check. No CI-green claim is made for Change Set 194 until an actual Story Intelligence Verification run completes successfully on a HEAD containing these changes.

## First genuine Golden PNG status

No new Golden Editorial v6 PNG was generated or claimed in this change set.

The exact external execution blocker remains the absence, in the currently available execution environment, of a compatible self-hosted host simultaneously proving:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM through the final pre-execution boundary;
- verified safe local Diffusers offload;
- exact pinned FLUX and Qwen snapshots;
- stable runtime fingerprint;
- sufficient post-cache disk headroom;
- `$0-local` execution.

Until such a host is available, Candidate 1 cannot honestly be reported as generated. No placeholder, fake PNG, synthetic benchmark, or fabricated visual score is permitted.

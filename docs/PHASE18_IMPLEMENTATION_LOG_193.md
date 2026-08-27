# PUL7SAR Phase 18 Implementation Log — Change Set 193

## Branch isolation

All writes in this change set target `phase18/story-intelligence` only.

Starting Phase 18 HEAD reviewed for this run: `0ff5cdf65fd7be65cddaefb3d7f3e9e889d58676`.

Starting `main` HEAD observed during this run: `97c2f28c14de7088183eb988eb941df79161f97d`.

The branches remain diverged. After the code/test changes, the compare reported Phase 18 ahead by 1671 commits and behind by 203 commits. `main` and `main.py` were not modified, merged, rebased, force-updated, or used as a write target.

## Baseline verification state

Change Set 192 is now confirmed CI-green.

Story Intelligence Verification run `33051874723` / run number `3228` completed with `success` on source HEAD `0ff5cdf65fd7be65cddaefb3d7f3e9e889d58676`.

This closes the two known offload-regression failures documented in Change Set 192 and gives this run a clean baseline before adding the next execution guard.

## Gap identified

The current Golden Editorial v6 resource/runtime wrappers perform strong early qualification before model/cache/runtime work. However, the strict first-genuine staging entrypoint still delegated Candidate 1 without a final live resource measurement at the last direct boundary before generation.

This differs from the durable worker path, which already has cycle-level and lease-bound resource requalification. In the direct strict-Golden path, live-free VRAM or host RAM could theoretically fall after early qualification because of another process or a long preparation window.

That would make the early receipt stale even though all factual, semantic and provenance contracts remained intact.

## Implemented

### 1. Just-in-time GPU requalification immediately before Candidate 1

Modified `tools/phase18_colab_first_genuine_golden.py` to run `phase18_qualify_gpu_host.py` immediately before the delegated strict Candidate-1 command.

The JIT GPU receipt must prove:

- host eligibility;
- FLUX.2 Klein 4B model identity;
- `local_cuda` runtime;
- CUDA available;
- native BF16 supported;
- `$0-local` cost mode;
- positive live-free and required VRAM values;
- live-free VRAM >= the required Golden floor;
- policy still forbids queue mutation, model downloads, dependency installation and paid APIs.

### 2. Just-in-time host-RAM requalification

The same strict staging entrypoint now executes `phase18_preflight_host_memory.py` immediately before Candidate 1 and requires:

- current host-memory receipt schema;
- Phase 18 branch identity;
- `ready=true`;
- `$0-local`;
- currently available RAM >= the configured first-Golden RAM floor;
- no model load/download, queue, generation, semantic, Golden, or publication authority.

### 3. Resource evidence sealed across generation

Both JIT receipts are SHA-256/byte-size recorded before Candidate 1 begins.

After generation and semantic staging return, the same files are replayed and must remain byte-identical before the generated PNG can be described as ready for human Golden review.

The final staging receipt records:

- `pre_execution_resource_guard_bound=true`;
- sealed JIT GPU evidence;
- sealed JIT host-memory evidence;
- live-free VRAM and its required floor;
- available host RAM and its required floor.

### 4. Regression coverage

Added `tests/test_phase18_first_genuine_golden_jit_resources.py` covering:

- valid JIT GPU qualification;
- low live-free VRAM rejection;
- illegal/paid resource-authority rejection;
- valid JIT host memory;
- low host-RAM rejection;
- evidence tampering after sealing;
- execution ordering proving JIT resource guard occurs before Candidate 1 and evidence replay occurs before genuine-candidate verification.

## Files changed

Modified:

- `tools/phase18_colab_first_genuine_golden.py`

Added:

- `tests/test_phase18_first_genuine_golden_jit_resources.py`
- `docs/PHASE18_CHANGESET_193_JIT_PREEXECUTION_RESOURCE_GUARD.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_193.md`

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
- total/live-free VRAM and host-RAM qualification;
- safe Diffusers offload qualification and actual-executor offload binding;
- model-cache revision locks and post-cache disk headroom;
- stable runtime fingerprint;
- Candidate/request/seed/canvas/SHA identity locks;
- generation and execution provenance replay;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Qwen BASE_SCENE/layer ownership;
- story-first Golden Editorial v6 composition-map lock;
- Golden quality minimum `8.5` / elite target `9.0+`;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate and final publication readiness;
- Seeds 2–4 remain unauthorized before genuine Candidate 1 succeeds and is visually accepted.

## Test status for Change Set 193

Code/test changes were committed on Phase 18. A new GitHub Actions run is expected from the branch update.

No CI success is claimed for Change Set 193 until an actual Story Intelligence Verification run completes successfully on a HEAD containing these changes.

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

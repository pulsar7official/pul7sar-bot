# PUL7SAR Phase 18 Implementation Log — Change Set 192

## Branch isolation

All writes in this change set target `phase18/story-intelligence` only. `main` and `main.py` were not modified, merged, rebased, force-updated, or used as a write target.

Starting Phase 18 HEAD reviewed for this run: `ff60609e4e4c9d3d05419b3d997ef1a046085ccd`.

Starting `main` HEAD reviewed for this run: `f93db9e90a338892e08d38c8dcf8083935890360`.

The branches remain diverged. The starting compare showed Phase 18 ahead by 1657 commits and behind by 193 commits.

## Baseline verification state

Story Intelligence Verification run `33047722293` / run number `3216` completed with `failure` in `Syntax and discover validation` after successfully installing dependencies. The downloaded job log shows **1,284 Phase 18 tests** were executed and exactly two tests failed. Multiple companion Phase 18 visual workflows on the same source state succeeded.

### Exact failure 1 — source-position false negative

`test_phase18_first_genuine_golden_v6_offload_workflow.FirstGenuineGoldenV6OffloadWorkflowTests.test_pre_model_offload_guard_runs_before_inner_candidate_path`

The test compared the source position of `phase18_colab_first_genuine_resources_locked.py` with the first occurrence of `GoldenOffloadProvenanceLock().verify`. The latter occurs inside the helper definition `_bind_actual_offload()` before `main()`, so the source-position assertion reported `inner=11836` and `actual=10001` even though the runtime call site `actual_offload = _bind_actual_offload(inner, offload)` is correctly after the inner Candidate-1 resource lock.

### Exact failure 2 — stale pre-model-only schema expectation

`test_phase18_first_genuine_golden_v6_offload_lock.FirstGenuineGoldenV6OffloadLockTests.test_wrapper_orders_offload_before_resource_model_work`

This older regression still required:

- `pul7sar-first-genuine-golden-v6-offload-lock-v1`
- `FIRST_GENUINE_GOLDEN_V6_PREMODEL_OFFLOAD_RESOURCE_LOCK_VERIFIED`

Change Set 191 deliberately upgraded the wrapper to bind the actual executor offload result, so the current stronger contract is:

- `pul7sar-first-genuine-golden-v6-offload-lock-v2`
- `FIRST_GENUINE_GOLDEN_V6_ACTUAL_OFFLOAD_RESOURCE_LOCK_VERIFIED`

The runtime was correct; the stale regression had not migrated to the v2 evidence contract.

## Implemented

### 1. Runtime-call-site order regression repair

Updated `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py` so ordering is measured using the concrete runtime call site:

`actual_offload = _bind_actual_offload(inner, offload)`

instead of the helper implementation text.

The test continues to require:

- GPU qualification before offload preflight.
- Offload preflight before the inner Golden v6 Candidate-1 path.
- Inner Candidate-1 resource/runtime/semantic lock before actual-offload postflight.
- Actual offload mode binding and publication/seeds closure.

A separate helper-integrity regression now asserts that `_bind_actual_offload()` still calls `GoldenOffloadProvenanceLock().verify`, rejects selected/actual mode drift, and rejects missing `actual_offload_mode_bound` evidence.

### 2. Legacy v1 offload regression aligned to stronger v2 contract

Updated `tests/test_phase18_first_genuine_golden_v6_offload_lock.py` to require the current Change Set 191 v2 schema/status and both evidence bindings:

- `safe_offload_preflight_bound = true`
- `actual_offload_mode_bound = true`

The existing tests for low-VRAM sequential offload, verified high-VRAM model-CPU fallback, total-VRAM identity and authority drift remain unchanged in intent.

## Files changed

Modified:

- `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py`
- `tests/test_phase18_first_genuine_golden_v6_offload_lock.py`

Added:

- `docs/PHASE18_CHANGESET_192_OFFLOAD_WORKFLOW_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_192.md`

Deleted: none.

Production/runtime modules modified: none.

## Safety and quality gates preserved

No gate was weakened. The following remain fail-closed:

- factual integrity / Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful loss/result treatment;
- `$0-local` execution;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen revision/snapshot;
- native BF16;
- total/live-free VRAM and live host-RAM qualification;
- safe Diffusers offload qualification and actual-executor offload binding;
- post-cache disk headroom;
- stable runtime fingerprint;
- lease-bound resource evidence;
- Candidate/request/seed/canvas/SHA identity locks;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Qwen BASE_SCENE/layer ownership;
- Golden quality minimum `8.5` / elite target `9.0+`;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate and final publication readiness;
- Seeds 2–4 remain unauthorized before genuine Candidate 1 succeeds and is visually accepted.

## Test status for Change Set 192

Regression repair commits:

- `a2c9cdb5c5a4efb928275eb71fd7104f8d4f4e0c` — runtime-call-site order regression repair.
- `3008a61651ee5d82583bba1e9e50ab96d233c454` — stale v1 offload-lock regression aligned to v2 actual provenance.

A new GitHub verification result must complete before Change Set 192 is described as CI-green. No success is claimed in this log until an actual run completes successfully.

## First genuine Golden PNG status

No new Golden Editorial v6 PNG was generated or claimed in this change set.

The exact external execution blocker remains the absence, in the currently available execution environment, of a self-hosted host simultaneously proving:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM through execution;
- a verified safe local Diffusers offload path;
- exact pinned FLUX and Qwen snapshots;
- stable runtime fingerprint;
- sufficient post-cache disk headroom;
- `$0-local` execution.

Until such a host is available, Candidate 1 cannot honestly be reported as generated. No placeholder, fake PNG, synthetic benchmark, or fabricated visual score is permitted.

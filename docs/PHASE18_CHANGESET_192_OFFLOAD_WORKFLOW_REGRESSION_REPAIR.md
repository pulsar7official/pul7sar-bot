# Phase 18 Change Set 192 — Offload Workflow Regression Repair

## Scope

Branch: `phase18/story-intelligence` only. `main` and `main.py` are not modified.

## Why this change was required

Change Set 191 correctly introduced end-to-end binding between the safe FLUX.2 CPU-offload mode selected before model work and the actual offload mode reported by the executor that produced Candidate 1. Story Intelligence Verification run `33047722293` / run `3216` executed **1,284 Phase 18 tests** and failed with exactly two regression failures; the runtime/offload implementation itself was not reported as failing.

The downloaded job log identified both failures precisely:

1. `test_phase18_first_genuine_golden_v6_offload_workflow.FirstGenuineGoldenV6OffloadWorkflowTests.test_pre_model_offload_guard_runs_before_inner_candidate_path` compared the location of `phase18_colab_first_genuine_resources_locked.py` with the first textual occurrence of `GoldenOffloadProvenanceLock().verify`. That verifier text occurs inside the helper definition `_bind_actual_offload()` before `main()`, so the source-position assertion produced a false negative even though runtime execution correctly calls `_bind_actual_offload(inner, offload)` after the inner Candidate-1 resource lock completes.
2. `test_phase18_first_genuine_golden_v6_offload_lock.FirstGenuineGoldenV6OffloadLockTests.test_wrapper_orders_offload_before_resource_model_work` still expected the Change Set 189 pre-model-only wrapper contract `pul7sar-first-genuine-golden-v6-offload-lock-v1` / `FIRST_GENUINE_GOLDEN_V6_PREMODEL_OFFLOAD_RESOURCE_LOCK_VERIFIED`. Change Set 191 intentionally upgraded the wrapper to v2 with actual-executor provenance: `pul7sar-first-genuine-golden-v6-offload-lock-v2` / `FIRST_GENUINE_GOLDEN_V6_ACTUAL_OFFLOAD_RESOURCE_LOCK_VERIFIED`.

## Changes

### Runtime-call-site ordering regression repair

`tests/test_phase18_first_genuine_golden_v6_offload_workflow.py` now orders concrete runtime call sites:

1. GPU host qualification.
2. FLUX.2 pre-model offload capability preflight.
3. Golden v6 resource/runtime/semantic Candidate-1 path.
4. `actual_offload = _bind_actual_offload(inner, offload)`.

A separate regression assertion verifies that `_bind_actual_offload()` itself still calls `GoldenOffloadProvenanceLock().verify` and rejects selected/actual mode drift or missing actual-mode binding.

### Legacy v1 regression alignment to actual-offload v2

`tests/test_phase18_first_genuine_golden_v6_offload_lock.py` now expects the stronger current v2 contract and status, and explicitly requires both:

- `safe_offload_preflight_bound = true`;
- `actual_offload_mode_bound = true`.

The earlier low-VRAM sequential requirement, high-VRAM verified model-CPU fallback, total-VRAM identity binding and authority-drift tests remain intact.

No production/runtime implementation was weakened or changed.

## Preserved gates

This change does not modify or relax:

- Fact Lock and factual integrity.
- Entity/Identity Verification.
- Sentiment/Neutrality and respectful result framing.
- `$0-local` execution policy.
- Pinned FLUX.2 Klein 4B and Qwen revisions.
- Native BF16 requirement.
- Total/live-free VRAM, live host RAM, safe-offload, cache/headroom and runtime-fingerprint gates.
- Candidate/request/seed/canvas/SHA locks.
- Generated text/branding/exact-fact/entity-mark/exact-sport-geometry prohibitions.
- Qwen BASE_SCENE/layer-ownership checks.
- Golden quality floor `8.5`, elite target `9.0+`.
- Exact Brand/Typography integrity.
- SemanticPublicationGate and publication readiness.
- Seeds 2–4 remain unauthorized before Candidate 1 is genuinely produced and accepted.

## Files

Modified:

- `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py`
- `tests/test_phase18_first_genuine_golden_v6_offload_lock.py`

Added:

- `docs/PHASE18_CHANGESET_192_OFFLOAD_WORKFLOW_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_192.md`

Deleted: none.

## Golden PNG status

No Golden Editorial v6 PNG is claimed by this change set. A genuine Candidate 1 still requires a compatible self-hosted environment proving NVIDIA CUDA, native BF16, sufficient live VRAM and host RAM, safe local Diffusers offload, exact pinned FLUX/Qwen snapshots, stable runtime fingerprint, sufficient post-cache disk headroom, and `$0-local` execution.

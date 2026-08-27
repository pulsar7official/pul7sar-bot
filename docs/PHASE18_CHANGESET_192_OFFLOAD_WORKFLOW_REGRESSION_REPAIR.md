# Phase 18 Change Set 192 — Offload Workflow Regression Repair

## Scope

Branch: `phase18/story-intelligence` only. `main` and `main.py` are not modified.

## Why this change was required

Change Set 191 correctly introduced end-to-end binding between the safe FLUX.2 CPU-offload mode selected before model work and the actual offload mode reported by the executor that produced Candidate 1. The corresponding Story Intelligence verification run (`33047722293`) failed in `Syntax and discover validation`.

Source review identified a regression-test ordering bug in `tests/test_phase18_first_genuine_golden_v6_offload_workflow.py`: the test used `wrapper.index("GoldenOffloadProvenanceLock().verify")` as the position of the runtime postflight. That text occurs inside the helper function definition `_bind_actual_offload()` near the top of the file, before `main()` and before the actual Candidate-1 resource-lock call sites. Therefore the test could report that actual-offload provenance ran too early even though runtime execution correctly calls `_bind_actual_offload(inner, offload)` only after the inner Golden v6 resource lock returns.

## Change

The regression test now orders concrete runtime call sites:

1. GPU host qualification.
2. FLUX.2 pre-model offload capability preflight.
3. Golden v6 resource/runtime/semantic Candidate-1 path.
4. `actual_offload = _bind_actual_offload(inner, offload)`.

A separate regression assertion still verifies that `_bind_actual_offload()` itself calls `GoldenOffloadProvenanceLock().verify`, and that it rejects selected/actual mode drift and missing actual-mode binding.

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

Added:

- `docs/PHASE18_CHANGESET_192_OFFLOAD_WORKFLOW_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_192.md`

Deleted: none.

## Golden PNG status

No Golden Editorial v6 PNG is claimed by this change set. A genuine Candidate 1 still requires a compatible self-hosted environment proving NVIDIA CUDA, native BF16, sufficient live VRAM and host RAM, safe local Diffusers offload, exact pinned FLUX/Qwen snapshots, stable runtime fingerprint, sufficient post-cache disk headroom, and `$0-local` execution.

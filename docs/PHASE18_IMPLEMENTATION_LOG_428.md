# Phase 18 Implementation Log — CS428

## Title
JIT First-Golden Execution Blocker Probe Binding

## Scope
Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

`main` was not modified.

## Starting state
CS427 HEAD: `29216a5e37a6a219eba375ecb2e5df7f9c4713d6`.

The exact-head Phase 18 Story Intelligence Verification run `34712291389` (run number 5635) completed successfully before CS428 began.

CS427 had introduced `tools/phase18_probe_first_golden_execution_blocker.py`, a non-authoritative zero-cost probe that reports whether the current host has the minimum execution prerequisites for the first genuine Golden v6 attempt: offline-only flags, `$0-local`, CUDA runtime/device availability, native BF16, and the exact approved Qwen2.5-VL and FLUX.2 immutable snapshots already present in the local Hugging Face cache.

The remaining integration gap was that the JIT execution path did not invoke that probe automatically before entering the heavier CUDA/offload/resource/generation chain.

## Changes

### Modified
`tools/phase18_colab_first_genuine_jit_replay_locked.py`

Added:

- `EXECUTION_PROBE` receipt path at `output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json`.
- Import of the existing CS427 blocker probe as `inspect_execution_blockers`.
- `_probe_execution_prerequisites()` helper that records the probe result inside the repository output tree.
- CLI fail-closed ordering: `main()` runs and records the blocker probe before calling `run()`.
- Exit code `2` when `ready_for_authoritative_golden_preflight` is not exactly `true`.

The lower-level `run()` function was intentionally left independent of this host probe so existing deterministic/unit replay tests can continue exercising the JIT evidence logic without requiring a CUDA host. The authoritative workflow CLI path receives the same guard again as defense in depth.

### Modified
`.github/workflows/phase18-first-genuine-golden-v6-jit.yml`

Added a dedicated `Record first-Golden execution blocker probe before CUDA preflight` step immediately after immutable checkout/branch-isolation verification and before the existing native CUDA/BF16 preflight.

The workflow now executes:

`tools/phase18_probe_first_golden_execution_blocker.py --output output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json`

before entering the existing CUDA/BF16 preflight or JIT generation chain. A non-ready probe exits non-zero and the job fails closed. Because the existing evidence upload step uses `if: always()` and includes `output/phase18_gpu_smoke/**`, the blocker receipt remains available even when the probe itself terminates the execution before Candidate 1 generation.

The original independent CUDA-enabled PyTorch/native-BF16 preflight was intentionally preserved after the probe as a defense-in-depth runtime gate.

No generation prompt, seed, model selection, immutable model revision, image parameter, publication rule, identity rule, factual rule, sentiment rule, semantic-publication rule, or visual-quality threshold was changed.

### Added / subsequently strengthened
`tests/test_phase18_first_genuine_golden_v6_jit_blocker_probe_integration.py`

Regression coverage verifies that:

- the blocker probe is integrated into the JIT CLI;
- the CLI probe executes before the heavier JIT `run()` path;
- a non-ready result exits fail-closed before Candidate 1 execution;
- the probe remains explicitly non-authoritative, zero-cost, offline-only, and unable to grant generation/publication/Seeds 2-4 authority;
- exact Qwen/FLUX local snapshots and native BF16 remain prerequisites;
- the workflow executes the blocker probe before its native CUDA/BF16 preflight;
- the blocker receipt path is under `output/phase18_gpu_smoke/**`, which the JIT workflow uploads with `if: always()`;
- `run()` remains separate from the CLI host probe for existing CPU-side replay testing.

### Deleted
Nothing.

## Security and quality invariants preserved

- Branch remains `phase18/story-intelligence` only.
- No write to `main`.
- `$0-local` remains mandatory.
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` remain mandatory.
- Network model downloads remain unauthorized.
- CUDA-enabled PyTorch remains required.
- Native BF16 remains required; no FP16/FP32 substitution was introduced.
- Qwen2.5-VL and FLUX.2 identities/revisions remain the approved immutable revisions.
- Factual, identity/entity, sentiment, semantic-publication, and visual-quality gates are unchanged.
- `human_visual_review_approved=false` remains downstream until genuine human review.
- `golden_quality_approved=false` remains downstream.
- `publication_ready=false` remains downstream.
- `seeds_2_to_4_authorized=false` remains downstream.

## Why this materially reduces the remaining gap

Before CS428, an apparently compatible self-hosted runner could enter workflow preflight/offload work and only later reveal that a required CUDA/BF16/local-model-cache prerequisite was absent. After CS428, the JIT workflow records one deterministic blocker receipt immediately after immutable branch isolation and before the independent CUDA/BF16 preflight or Candidate 1 chain.

Because the receipt is written under `output/phase18_gpu_smoke/` and the workflow uploads that tree with `if: always()`, a failed first-Golden attempt can preserve the exact blocker evidence instead of leaving only an opaque failed step. The JIT CLI repeats the same probe before `run()` as defense in depth if it is invoked directly outside the workflow.

## First Genuine Golden Visual PNG status

No genuine Golden Visual PNG was created or claimed in CS428.

The remaining non-substitutable execution requirement is a compatible self-hosted NVIDIA host with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient VRAM/RAM/storage, and both approved immutable Qwen2.5-VL and FLUX.2 snapshots already present in the local Hugging Face cache while all offline/zero-cost constraints remain active.

CS428 does not weaken or bypass that blocker; it makes the blocker observable earlier and persistently records it before expensive execution begins.

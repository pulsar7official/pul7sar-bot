# Phase 18 Implementation Log — CS437

## Scope

CS437 advances the first genuine Golden Visual path without generating or fabricating a PNG. It introduces one fail-closed, non-authoritative pre-GPU decision point that proves immutable Phase 18 source identity before evaluating the existing local execution blocker probe.

Branch scope remains `phase18/story-intelligence` only. `main` is not modified.

## Added

### `tools/phase18_probe_first_golden_pre_gpu.py`

Introduces a unified pre-GPU receipt with schema:

`pul7sar-phase18-first-golden-pre-gpu-probe-v1`

The probe:

1. Requires an immutable 40-character expected commit SHA.
2. Reuses `phase18_probe_first_golden_source_identity.inspect()` first.
3. Refuses to evaluate the execution environment when source identity is not ready or the expected SHA is invalid.
4. Only after source proof succeeds, reuses `phase18_probe_first_golden_execution_blocker.inspect()` unchanged.
5. Preserves nested source/execution receipts instead of flattening or weakening their evidence.
6. Rejects network, generation, publication, or Seeds 2–4 authority drift in either nested report.
7. Performs no downloads, model loading, generation, queue mutation, publication, or PNG creation.

The unified receipt keeps:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

### `tests/test_phase18_first_golden_pre_gpu_probe.py`

Adds deterministic regression coverage for:

- source proof executing before environment proof;
- successful readiness only when both source and environment are ready;
- source failure preventing the execution probe entirely;
- execution-environment failure remaining fail-closed;
- invalid expected commit preventing environment evaluation;
- nested generation-authority drift rejection;
- nested network-authority drift rejection;
- final Golden/publication/Seeds authority remaining closed.

### `docs/PHASE18_IMPLEMENTATION_LOG_437.md`

Records this change set and remaining blocker.

## Modified

None.

## Deleted

None.

## Unchanged contracts

CS437 does not change:

- prompts;
- Candidate 1 seed;
- generation dimensions or parameters;
- Qwen2.5-VL model ID or immutable revision;
- FLUX.2 model ID or immutable revision;
- factual gates;
- entity/identity gates;
- sentiment neutrality rules;
- semantic-publication gates;
- visual-quality or human-review gates;
- zero-cost `$0-local` policy;
- offline-only model resolution policy;
- native-BF16 requirement;
- CUDA/GPU/VRAM/RAM/filesystem thresholds;
- dependencies.

## Why this materially reduces the remaining gap

Before CS437, source identity and execution readiness existed as separate receipts. A workflow could invoke the environment blocker independently after branch isolation, but there was no single receipt proving that the exact immutable dispatch source was accepted before environment readiness was considered.

CS437 makes that ordering explicit and reusable: wrong branch, wrong SHA, dirty tracked source, unproven main merge-base, or a forbidden `main.py` Phase 18 diff prevents any execution-environment readiness decision. Only a clean, exact Phase 18 source may proceed to CUDA/BF16/VRAM/RAM/headroom/runtime/cache checks.

This reduces the chance that the first compatible GPU opportunity is spent on an execution rooted in the wrong or mutable source state.

## Testing state

The new regression suite is committed and is intended to run under the existing `Phase 18 Story Intelligence Verification` discovery path. The exact CS437 terminal CI result must be checked on the final CS437 HEAD; do not describe CS437 as terminal-green until that run completes successfully.

## Remaining blocker to the first genuine Golden Visual PNG

No genuine Golden PNG is produced by CS437.

Actual Candidate 1 generation still requires a compatible self-hosted NVIDIA execution host satisfying all existing gates together, including:

- CUDA-enabled PyTorch;
- at least one real CUDA device;
- native BF16;
- approved GPU identity / compute capability;
- sufficient total and live-free VRAM;
- sufficient currently available system RAM;
- sufficient local filesystem working headroom;
- approved generation runtime;
- coherent Qwen2.5-VL semantic runtime;
- exact approved Qwen2.5-VL snapshot resolvable locally;
- exact approved FLUX.2 snapshot resolvable locally;
- `HF_HUB_OFFLINE=1`;
- `TRANSFORMERS_OFFLINE=1`;
- `PUL7SAR_PHASE18_COST_MODE=$0-local`;
- no network model download;
- no FP16/FP32 substitution.

Human visual review, Golden-quality approval, publication readiness, and Seeds 2–4 authorization remain false until a real generated Candidate 1 artifact passes their existing gates.

## Next safe integration step

Bind `tools/phase18_probe_first_golden_pre_gpu.py --expected-commit <dispatch SHA>` into the canonical, JIT, and offload Golden workflows immediately after immutable checkout/branch reattachment and before any standalone execution blocker/CUDA preflight. Keep the existing branch-isolation checks as defense in depth. This integration should replace duplicate standalone probe invocation only after regression coverage proves equivalent or stronger fail-closed behavior.

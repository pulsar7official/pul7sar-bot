# Phase 18 Implementation Log — CS442

## Scope

CS442 advances the first genuine Golden Visual path without touching `main`. It integrates the already-approved attested pre-GPU readiness chain into the JIT Candidate 1 workflow before the existing CUDA/resource/generation path.

## Branch isolation

- Writable branch: `phase18/story-intelligence` only.
- `main` remains read-only and is not modified.
- The workflow still reattaches the immutable dispatch SHA to `phase18/story-intelligence` and rejects `main.py` appearing in the Phase 18 diff.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`

Added an attested pre-GPU step after immutable branch reattachment and before the existing execution-blocker/CUDA checks. The step:

- invokes `tools/phase18_run_first_golden_pre_gpu_attested.py`;
- binds the proof to exact `${{ github.sha }}` / `DISPATCH_SHA`;
- writes receipt, attestation, and summary under `output/phase18_gpu_smoke/`;
- requires `ready_for_authoritative_golden_preflight=true`;
- requires `receipt_attested=true` and an empty blocker list;
- rejects any drift in `authoritative_gate`, network-download, generation, publication, or Seeds 2–4 authority.

The pre-existing `phase18_probe_first_golden_execution_blocker.py`, explicit CUDA/native-BF16 proof, and JIT resource replay remain after this new attested proof as defense in depth. No generation parameter, prompt, seed, approved model ID/revision, or quality gate was relaxed.

## Added

### `tests/test_phase18_first_golden_jit_attested_pre_gpu_integration.py`

Standard-library `unittest` regression coverage proving:

1. the attested runner is bound to exact dispatch SHA;
2. attested pre-GPU proof runs before the legacy execution blocker;
3. the legacy blocker remains before explicit CUDA/BF16 proof;
4. CUDA/BF16 proof remains before Candidate 1 JIT generation;
5. `$0-local`, Hugging Face offline mode, Transformers offline mode, closed authorities, main isolation, and FP16/FP32 refusal remain explicit.

## Deleted

None.

## Preserved gates

- factual verification: unchanged;
- entity/identity verification: unchanged;
- sentiment/loser-respect neutrality: unchanged;
- `$0-local` zero-cost execution: unchanged;
- offline/local-only model resolution: unchanged;
- immutable approved Qwen/FLUX identities and revisions: unchanged;
- semantic-publication gates: unchanged;
- visual-quality/human-review gates: unchanged;
- `publication_ready=false` until existing downstream authority rules are satisfied;
- `seeds_2_to_4_authorized=false` until existing downstream authority rules are satisfied.

## Testing/status

CS441 (`20a49e81275451611b7a39af6c0f762bf6b0e078`) was confirmed terminal-green across the retrieved Phase 18 PR workflows, including `Phase 18 Story Intelligence Verification` run `34748507685` with conclusion `success`.

CS442 relies on repository CI to validate YAML/discovery and the new unittest integration contract on the exact new branch HEAD. No genuine PNG is claimed by this change.

## Remaining blocker toward the first genuine Golden PNG

Actual generation still requires a compatible self-hosted NVIDIA execution host satisfying all existing runtime gates simultaneously: CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient live VRAM/RAM/filesystem headroom, compatible generation/semantic runtime, and exact approved Qwen2.5-VL and FLUX.2 snapshots already resolvable locally with network downloads disabled.

The canonical and offload generation workflows still need the same attested pre-GPU integration pattern in subsequent safe changes. CS442 deliberately changes JIT only so CI can validate the integration pattern before propagating it to the other two generation paths.

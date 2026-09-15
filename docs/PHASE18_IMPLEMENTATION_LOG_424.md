# Phase 18 Implementation Log 424 — JIT Native BF16 Runtime Gate

## Scope

Branch: `phase18/story-intelligence` only. `main` remains read-only and is not modified by this change set.

CS424 advances the first genuine Golden Editorial v6 Candidate 1 path by making the JIT workflow prove native CUDA BF16 support at runtime before any model loading or generation work is attempted.

## Baseline reviewed

CS423 HEAD: `b0da65e4195cc40b1166eeeb09613d2865213b6f`.

The Phase 18 Story Intelligence Verification workflow for CS423 completed successfully on run `34700521744`, confirming the prior JIT offline-only contract was terminal-green before CS424 began.

## Gap found

The JIT workflow already required the self-hosted runner labels `gpu`, `cuda`, and `bf16`, and it proved `torch.cuda.is_available()`. However, runner labels are scheduling metadata, not runtime proof. The workflow did not independently prove that:

- PyTorch exposes a CUDA runtime version;
- at least one CUDA device is visible to the process; or
- `torch.cuda.is_bf16_supported()` is available and returns true.

That gap could waste the first compatible-looking GPU execution by allowing Candidate 1 to reach deeper model/resource stages on a host that cannot execute the approved native-BF16 path.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`

The preflight now fails closed before Candidate 1 execution unless all of the following are true:

- `HF_HUB_OFFLINE=1`;
- `TRANSFORMERS_OFFLINE=1`;
- `torch.cuda.is_available()` is true;
- `torch.version.cuda` is not null;
- at least one CUDA device is visible;
- `torch.cuda.is_bf16_supported()` exists and returns true.

No FP16 or FP32 substitution is allowed. The runtime diagnostic records the active CUDA device name, compute capability, CUDA runtime, device count, and `native_bf16=true` while preserving `model_cache_mode=offline-local-only`.

## Added

### `tests/test_phase18_first_genuine_golden_v6_jit_native_bf16_contract.py`

Regression coverage asserts that:

- CUDA runtime, device visibility, and native BF16 are all checked;
- offline/local-only model resolution remains mandatory;
- the self-hosted runner contract is unchanged;
- branch isolation from `main` remains in place;
- downstream human-review, Golden-quality, publication, and Seeds 2–4 authorities remain fail-closed; and
- the native-BF16 gate occurs before Candidate 1 execution.

### `docs/PHASE18_IMPLEMENTATION_LOG_424.md`

This implementation log documents CS424.

## Deleted

None.

## Preserved gates

CS424 does not change model IDs, immutable model revisions, prompts, seeds, generation parameters, factual verification, identity/entity verification, sentiment neutrality, semantic-publication gating, visual-quality gating, human visual review, or the `$0-local` no-network policy.

The following authorities remain false until their separate downstream gates are satisfied:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Test/CI status

CS423 baseline verification: terminal-green (`Phase 18 Story Intelligence Verification`, run `34700521744`).

CS424 CI is expected to run on the final CS424 HEAD after this log commit. It must not be described as terminal-green until GitHub reports a successful terminal result on that exact SHA.

## Genuine Golden PNG status

No genuine Golden PNG was created or claimed in CS424. The remaining non-substitutable blocker is an actually available self-hosted NVIDIA execution host with CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved immutable Qwen2.5-VL and FLUX.2 snapshots already present in the canonical local Hugging Face cache. Network model download remains unauthorized.

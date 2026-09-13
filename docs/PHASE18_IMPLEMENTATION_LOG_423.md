# Phase 18 Implementation Log — CS423

## Scope

CS423 hardens the First Genuine Golden v6 JIT fallback path so that it preserves the same zero-cost/offline model-resolution contract as the primary Golden v6 workflow. No change was made to `main`.

Starting Phase 18 branch SHA: `1db1102b37963193f0ba3e4817674e5b9de2566e`.

The prior Story Intelligence Verification run `34697835725` completed successfully on that exact SHA, establishing CS422 as terminal-green before CS423 began.

## Problem found

`.github/workflows/phase18-first-genuine-golden-v6-jit.yml` already required the dedicated self-hosted CUDA/BF16 Phase 18 runner and `$0-local`, but unlike the primary Golden v6 workflow it did not explicitly export Hugging Face/Transformers offline mode. That left the JIT fallback path less strict than the primary path even though no network model download is permitted for the First Genuine Golden execution.

## Changes

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`
  - Added `HF_HUB_OFFLINE: "1"` at job scope.
  - Added `TRANSFORMERS_OFFLINE: "1"` at job scope.
  - Strengthened the CUDA preflight so it fails closed unless both offline flags are present.
  - Added explicit `model_cache_mode: offline-local-only` diagnostic output.
  - Preserved the existing exact runner labels, branch isolation, `$0-local` cost mode, JIT resource replay, artifact replay, and downstream authority locks.

### Added

- `tests/test_phase18_first_genuine_golden_v6_jit_offline_contract.py`
  - Verifies both offline environment flags are permanently required by the JIT workflow.
  - Verifies the preflight checks those environment flags rather than merely setting them.
  - Verifies the dedicated `self-hosted/linux/x64/gpu/cuda/bf16/pul7sar-phase18` runner contract remains intact.
  - Verifies the branch remains `phase18/story-intelligence` and the existing `main.py` isolation check remains present.
  - Guards against accidental granting of publication or Golden-quality authority.

### Deleted

- Nothing.

## Safety and gate preservation

CS423 does not modify model IDs, pinned revisions, prompts, seeds, generation parameters, factual verification, identity verification, sentiment handling, semantic-publication gates, visual-quality gates, Human Visual Review authority, Golden approval authority, publication authority, or Seeds 2–4 authorization.

The JIT workflow remains unable to replace or install PyTorch automatically and still requires actual CUDA execution. The change only makes the alternative execution path stricter by forcing local-cache-only model resolution.

## Genuine Golden status

No genuine Golden Visual PNG was created in CS423. This change does not simulate GPU execution and does not fabricate an image result.

The non-substitutable execution requirement remains a compatible self-hosted NVIDIA host with CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the canonical local Hugging Face cache.

## Commits

- `278ff3a7ab1a9e77ae6ca03f0b1723d39cc7eca7` — enforce offline-only JIT Golden v6 execution.
- `9fda9411c6360cb9620e18a61921b28320939003` — add regression coverage for the JIT offline contract.

The documentation commit containing this log follows those functional commits.

# Phase 18 Implementation Log 430

## Scope

CS430 strengthens the canonical First Genuine Golden v6 workflow on `phase18/story-intelligence` only. `main` remains read-only and is not modified.

## Reviewed state

- CS429 head: `1cdbdafbcd2d728e72a44e2c0e9c89d185c48a3f`.
- CS429 Story Intelligence Verification run `34718384431` completed successfully.
- `main` was observed read-only at `84eb035559f48754d49eac7a348e431a9b511871` during this change set.
- No genuine Golden PNG was present or fabricated.
- The JIT workflow already recorded the non-authoritative first-Golden blocker probe before CUDA preflight, while the canonical Golden v6 workflow did not.

## Problem closed in CS430

The canonical `.github/workflows/phase18-first-genuine-golden-v6.yml` previously entered CUDA validation directly after immutable checkout and branch isolation. A host missing CUDA, native BF16, or locally resolvable approved model snapshots could therefore fail before the strengthened CS429 blocker receipt was written.

This created an avoidable diagnostic asymmetry between the JIT path and the canonical path and could waste the first compatible self-hosted execution opportunity.

## Changes

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6.yml`
  - Requires `tools/phase18_probe_first_golden_execution_blocker.py` to exist after immutable checkout.
  - Records `output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json` before CUDA preflight.
  - Keeps the probe under `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`.
  - Strengthens the canonical CUDA preflight to require an actual CUDA runtime, at least one CUDA device, and `torch.cuda.is_bf16_supported() == true`.
  - Explicitly refuses FP16/FP32 substitution.
  - Preserves the existing `if: always()` evidence upload covering `output/phase18_gpu_smoke/**`, so the blocker receipt is retained even when later Golden execution fails.
  - Does not alter approved model IDs/revisions, prompts, seeds, generation parameters, evidence replay, source binding, upload transport attestation, or downstream authority gates.

### Added

- `tests/test_phase18_first_genuine_golden_v6_canonical_blocker_probe_integration.py`
  - Verifies blocker-probe execution precedes canonical CUDA preflight.
  - Verifies `$0-local`, both offline flags, CUDA runtime/device, native BF16, and no FP16/FP32 substitution remain mandatory.
  - Verifies the blocker receipt remains covered by always-uploaded evidence.
  - Verifies main-isolation checks and downstream authority gates remain present.

- `docs/PHASE18_IMPLEMENTATION_LOG_430.md`

### Deleted

- None.

## Gates preserved

CS430 does not alter factual gates, entity/identity verification, sentiment neutrality, semantic-publication controls, visual-quality thresholds, prompts, seeds, generation parameters, dependencies, approved Qwen2.5-VL identity/revision, or approved FLUX.2 identity/revision.

No paid inference, network model download, FP16/FP32 quality downgrade, automatic publication, Human Visual Review approval, Golden quality approval, or Seeds 2-4 authorization is introduced.

The final authority state remains fail-closed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Test intent

Repository CI must prove:

1. Python/unittest discovery remains valid.
2. Canonical Golden v6 records the strengthened blocker receipt before CUDA validation.
3. CUDA runtime, device count, native BF16, `$0-local`, and offline-only model resolution cannot be silently weakened.
4. The diagnostic receipt survives failure through the existing always-upload evidence tree.
5. Main isolation and downstream authority controls remain present.

## Remaining gap to first genuine Golden PNG

A genuine Candidate 1 still requires a compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, at least one real CUDA device, native BF16, sufficient VRAM/RAM/storage, and both exact approved Qwen2.5-VL and FLUX.2 immutable snapshots already locally resolvable with network access disabled.

CS430 does not fabricate that environment or a PNG. It reduces the remaining execution gap by ensuring the canonical path now produces the same precise fail-closed blocker evidence as the JIT path before any heavy Golden execution begins.

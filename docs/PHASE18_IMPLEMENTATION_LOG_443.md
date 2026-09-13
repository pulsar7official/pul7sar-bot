# Phase 18 Implementation Log — CS443

## Scope

Integrate the already-approved attested first-Golden pre-GPU contract into the **offload** Candidate 1 execution workflow on `phase18/story-intelligence`, without changing `main`, prompts, seeds, model identities/revisions, generation parameters, dependencies, editorial gates, semantic-publication gates, or visual-quality authority.

## Starting state reviewed

- Starting Phase 18 HEAD: `459b7a19ed448f470112bcc872a777a59b6e1ba7` (CS442).
- `Phase 18 Story Intelligence Verification` push and pull-request runs for CS442 completed successfully.
- `main` was treated as read-only and remained outside all writes.
- The JIT workflow already contained the attested pre-GPU runner from CS442.
- The offload workflow still moved from immutable branch isolation directly to the legacy execution blocker and CUDA/BF16 proof.

## Changes

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6-offload.yml`
  - Added explicit existence checks for:
    - `tools/phase18_run_first_golden_pre_gpu_attested.py`
    - `tools/phase18_probe_first_golden_pre_gpu.py`
    - `tools/phase18_attest_first_golden_pre_gpu_receipt.py`
  - Added `Attest immutable source and zero-cost host before offload Golden execution` immediately after immutable branch/main isolation and before the existing execution blocker.
  - Bound the attested runner to the immutable dispatch SHA with `--expected-commit "$DISPATCH_SHA"`.
  - Added offload-scoped receipt, attestation, and summary paths.
  - Added fail-closed replay of the summary schema, exact expected commit, readiness result, empty blocker set, and closed authority fields.
  - Kept the existing execution blocker, explicit CUDA/native-BF16 proof, offload preflight, actual offload provenance, resource lock, PNG replay, and artifact upload steps intact.

### Added

- `tests/test_phase18_first_golden_offload_attested_pre_gpu_integration.py`
  - Standard-library `unittest` regression coverage for exact-SHA binding, execution ordering, offload-scoped evidence names, `$0-local`, offline-only model resolution, closed authorities, `main.py` isolation, BF16 no-substitution policy, and preservation of actual-offload provenance checks.
- `docs/PHASE18_IMPLEMENTATION_LOG_443.md`

### Deleted

- None.

## Preserved gates and invariants

- Branch remains `phase18/story-intelligence`; `main` is not modified.
- Factual and entity/identity verification gates are unchanged.
- Sentiment neutrality and loser-respect rules are unchanged.
- Semantic-publication gates are unchanged.
- Human visual review and Golden quality authority remain closed until the existing downstream review contract is satisfied.
- `$0-local` remains mandatory.
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` remain mandatory.
- No network model download is authorized.
- Native BF16 remains mandatory; FP16/FP32 quality substitution remains refused.
- Approved Qwen and FLUX model IDs/revisions are unchanged.
- Candidate 1 prompts, seed, canvas, and generation parameters are unchanged.
- Seeds 2–4 remain unauthorized.

## Execution order after CS443

1. Validate explicit dispatch and immutable SHA.
2. Checkout and reattach exact `phase18/story-intelligence` commit.
3. Prove `main.py` isolation against `origin/main`.
4. Run the attested source + zero-cost host pre-GPU contract against the exact dispatch SHA.
5. Replay the attested summary and reject any blocker or authority drift.
6. Run the pre-existing execution blocker probe.
7. Prove CUDA-enabled PyTorch, a real CUDA device, native BF16, and offline-only mode.
8. Run the pre-existing offload-locked Candidate 1 path and all downstream provenance/PNG replay gates.

## Testing

- Added deterministic `unittest` coverage discoverable by the existing Phase 18 CPU validation harness.
- Repository CI is expected to execute the new regression through normal push verification on the exact CS443 HEAD.
- No GPU generation result is claimed by this change set.

## Remaining gap to the first genuine Golden Visual PNG

A genuine PNG still requires an eligible self-hosted NVIDIA runner satisfying all existing runtime/resource constraints simultaneously, including CUDA-enabled PyTorch, at least one real CUDA device, native BF16, approved GPU/compute capability, sufficient live-free VRAM, sufficient available system RAM, sufficient filesystem/cache headroom, compatible generation/semantic runtime, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already resolvable locally under offline `$0-local` execution.

The canonical Golden workflow still needs the same attested pre-GPU integration. No compatible GPU execution is fabricated or inferred in CS443.

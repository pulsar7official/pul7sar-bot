# Phase 18 Implementation Log 429

## Scope

CS429 strengthens the non-authoritative first-Golden execution blocker probe on `phase18/story-intelligence` only. `main` remains read-only and is not modified.

## Reviewed state

- CS428 head: `a42d26ff7296718bcc1f50c80e9caed6e9e82160`.
- CS428 Story Intelligence Verification run `34715346654` completed successfully.
- `main` was observed read-only at `3fea83752c426545c3c8e352ac36bd9d28ffa399` during this change set.
- No genuine Golden PNG was present or fabricated.
- The canonical Golden v6 workflow still enters its CUDA preflight without recording the CS427/CS428 blocker probe first; that workflow integration remains a downstream preparatory gap.

## Problem closed in CS429

The CS427 blocker probe previously treated the presence of an exact revision directory under the Hugging Face cache as sufficient proof that the approved Qwen2.5-VL and FLUX.2 snapshots were cached. A stale, empty, partial, or otherwise locally unresolvable directory could therefore create a false-positive readiness signal before the authoritative cache preflights.

Directory presence is no longer sufficient.

## Changes

### Modified

- `tools/phase18_probe_first_golden_execution_blocker.py`
  - Bumped the diagnostic receipt schema from `pul7sar-phase18-first-golden-execution-blocker-probe-v1` to `...-v2`.
  - Added a local-only snapshot resolver backed by `huggingface_hub.snapshot_download(..., local_files_only=True)`.
  - Re-validates the resolved immutable revision with `assert_snapshot_revision`.
  - Keeps all model network download authority disabled.
  - Distinguishes expected revision-directory presence from an actually locally resolvable snapshot in the receipt.
  - `qwen_cached` / `flux_cached` are now true only when the exact approved snapshot resolves locally, not merely when a directory with the revision name exists.
  - Preserves fail-closed blocker codes and all non-authoritative authority fields.

- `tests/test_phase18_first_golden_execution_blocker_probe.py`
  - Updated ready-path fixtures to inject a deterministic local resolver without requiring model downloads.
  - Added assertions for schema v2 and local-only resolution mode.
  - Added a regression proving that exact revision-directory presence alone cannot make the probe ready when local snapshot resolution fails.
  - Preserved coverage for offline policy, `$0-local`, CUDA, CUDA runtime, device count, native BF16, immutable revisions, and both approved model snapshots.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_429.md`

### Deleted

- None.

## Gates preserved

CS429 does not alter prompts, seeds, generation parameters, model IDs, approved immutable revisions, dependencies, factual gates, identity/entity verification, sentiment neutrality, semantic-publication gates, or visual-quality gates.

The probe remains explicitly non-authoritative and keeps:

- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

No FP16/FP32 substitution or paid/network inference fallback is introduced.

## Test intent

The repository CI must prove:

1. Python syntax and unittest discovery remain valid.
2. A fully qualified host can pass only when both approved immutable snapshots resolve through local-only Hugging Face cache semantics.
3. Mere directory presence cannot satisfy Qwen/FLUX readiness.
4. Missing offline flags, `$0-local`, CUDA runtime/device, native BF16, or either approved local snapshot remains fail-closed.
5. The probe cannot grant generation/publication/Seeds 2-4 authority.

## Remaining gap to first genuine Golden PNG

A genuine Candidate 1 still requires a compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient VRAM/RAM/storage, and both exact approved Qwen2.5-VL and FLUX.2 snapshots already locally resolvable with network access disabled.

Preparatory work still worth completing before that host is used: bind this strengthened blocker receipt into the canonical `phase18-first-genuine-golden-v6.yml` workflow before its CUDA preflight, matching the JIT workflow's CS428 behavior, while preserving artifact upload on failure.

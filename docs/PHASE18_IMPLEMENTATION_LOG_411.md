# PUL7SAR Phase 18 — Implementation Log 411

## Scope

Branch: `phase18/story-intelligence` only.

`main` remains read-only and is not modified, merged, rebased, reset, or force-updated by this change set.

## Starting state

CS410 ended at branch HEAD:

`a2759cd597b16bd8784dbb4934aa2cde073e33ba`

The Phase 18 Story Intelligence Verification workflow run `34630248888` failed in the early `Syntax and discover validation` job. The full run executed 2,320 tests and reported exactly one failure:

`tests/test_phase18_flux_model_revision_lock.py::FluxModelRevisionLockTests::test_prefetch_command_pins_same_revision_for_cache_and_download`

The stale assertion required the literal source fragment:

`revision=FLUX2_KLEIN_4B_REVISION`

That source shape ceased to exist when CS410 intentionally converted `tools/phase18_prefetch_flux2.py` from a downloader-capable prefetch path into a strict local-cache proof. The approved revision is now supplied to `_require_cached_snapshot(...)`, and the helper invokes `snapshot_download(..., revision=revision, local_files_only=True)`.

The dedicated CS410 local-cache regression tests were already green in the same failing CI run, confirming that the failure was a stale source-shape assertion rather than a regression in the production hard-lock.

## CS411 change

### Modified

- `tests/test_phase18_flux_model_revision_lock.py`
  - Renamed the stale test intent from cache-and-download to local-cache proof.
  - Removed the obsolete literal requirement `revision=FLUX2_KLEIN_4B_REVISION`.
  - Now verifies the actual fail-closed contract:
    - `_require_cached_snapshot(...)` is used.
    - `FLUX2_KLEIN_4B_LOCAL.model_id` is bound into the cache proof.
    - `FLUX2_KLEIN_4B_REVISION` remains explicitly supplied.
    - the helper passes `revision=revision`.
    - `local_files_only=True` remains explicit.
    - the v2 cache receipt remains revision-pinned.
    - `assert_snapshot_revision(...)` remains part of the path verification.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_411.md`

### Deleted

- Nothing.

### Production behavior

No production code was changed in CS411.

In particular, CS410's FLUX.2 `$0-local` hard-lock remains intact:

- no network-capable fallback was restored;
- the approved immutable revision was not changed;
- `local_files_only=True` remains mandatory;
- absence of the approved local snapshot remains fail-closed;
- FLUX generation/model/prompt behavior was not modified.

## Safety and authority gates

CS411 does not weaken or open any downstream authority. Existing factual, entity/identity, sentiment, semantic-publication, visual-quality, source-binding, zero-cost, evidence, and provenance gates remain unchanged.

Human visual review approval, Golden-quality approval, publication readiness, and Seeds 2–4 authorization remain separate fail-closed states and are not granted by this change.

## Testing

Baseline CI evidence from run `34630248888`:

- 2,320 tests executed in the failing discovery/validation step.
- Exactly one failure: the obsolete FLUX source-shape assertion described above.
- CS410's dedicated `test_phase18_flux2_local_cache_only.py` coverage passed in that same run.
- Other Phase 18 workflows on the same CS410 branch state were green; the blocking regression was isolated to the early Story Intelligence validation suite.

CS411 changes only that stale regression test and leaves production hard-lock logic untouched. A fresh Story Intelligence Verification run on the resulting branch HEAD is required before CS411 may be called terminal-green.

## First Genuine Golden Visual status

No First Genuine Golden Visual PNG is claimed or fabricated by CS411.

The remaining non-substitutable execution blocker is a compatible self-hosted NVIDIA generation host satisfying the Golden v6 runtime contract, including:

- `self-hosted`, `linux`, `x64`, `gpu`, `cuda`, `bf16`, `pul7sar-phase18` runner labels;
- CUDA-enabled PyTorch with CUDA actually available;
- native BF16 support;
- sufficient live VRAM, system RAM, and storage/headroom;
- the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the local Hugging Face cache, because network fallback is intentionally disabled;
- successful execution of the existing factual, identity, sentiment, semantic, zero-cost, visual-quality, evidence, source-binding, readiness, and transport-attestation gates.

Until that real CUDA/BF16 path executes successfully, no generated file is to be represented as the genuine Golden Visual.

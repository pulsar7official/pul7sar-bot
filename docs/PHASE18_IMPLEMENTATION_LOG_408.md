# Phase 18 Implementation Log — CS408

Date: 2026-09-11
Branch: `phase18/story-intelligence` only
Starting HEAD: `a7e682eb0c5e6991ec7bbd369be5f9785961b321`

## Goal

Reduce the remaining execution-time gap before the first Genuine Golden Visual PNG by making the Qwen2.5-VL cache proof itself strictly local-cache-only. Preserve all factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, Human Review, Golden Quality, publication, and Seeds 2–4 authority gates.

## Review before changes

- CS407 (`a7e682eb0c5e6991ec7bbd369be5f9785961b321`) was reviewed first.
- Phase 18 Story Intelligence Verification run `34601180154` for CS407 completed successfully.
- `main` was inspected read-only and was not modified.
- Golden v6 already exports `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` and later rejects Qwen evidence when `downloaded_now` is true.
- `tools/phase18_prefetch_qwen.py`, however, still contained a second `snapshot_download(...)` call without `local_files_only=True` when the approved snapshot was absent. In the Golden workflow the offline environment would normally make that path fail, but the tool itself did not independently guarantee `$0-local` behavior and could attempt network resolution if invoked in a drifted environment.

## Modified

### `tools/phase18_prefetch_qwen.py`

The Qwen helper is now a local-cache proof rather than a downloader.

Changes:

1. Replaced the nullable `_cached_snapshot(...)` probe with `_require_cached_snapshot(...)`.
2. The only Hugging Face snapshot resolution now passes the approved exact model ID, immutable revision, and `local_files_only=True`.
3. Missing local model bytes fail immediately with `QWEN_APPROVED_LOCAL_SNAPSHOT_REQUIRED`; there is no second call or network fallback.
4. Removed the download branch entirely.
5. The emitted cache receipt now states explicitly:
   - `downloaded_now = false`
   - `network_download_authorized = false`
   - `local_files_only = true`
6. Existing snapshot-completeness and immutable-revision checks remain required.
7. No model IDs or approved revisions were changed.

## Added

### `tests/test_phase18_qwen_local_cache_only.py`

CPU-only regression coverage proving that:

1. The cache lookup is pinned to the approved Qwen2.5-VL model ID and immutable revision.
2. `local_files_only=True` is always supplied.
3. A missing snapshot fails closed after exactly one local-only lookup with no network fallback.
4. `main()` has no direct `snapshot_download(...)` call that bypasses `_require_cached_snapshot(...)`.
5. The zero-cost receipt contract explicitly keeps downloads/network authorization false and local-only resolution true.

## Deleted

No files were deleted. The former runtime download fallback inside `tools/phase18_prefetch_qwen.py` was removed.

## Dependency changes

None.

## Gate impact

No authority gate was relaxed or opened.

- Factual/news verification: unchanged.
- Entity/identity verification: unchanged.
- Sentiment and loser-respect policy: unchanged.
- `$0-local`: strengthened at the Qwen cache-resolution boundary.
- Approved immutable Qwen revision: unchanged and still mandatory.
- Approved immutable FLUX revision and CS407 local-only loader: unchanged.
- CUDA/native-BF16 requirement: unchanged.
- Semantic inspection and SemanticPublicationGate: unchanged and fail-closed.
- Human visual review: still required and not approved by this change.
- Golden Quality: still false until human review.
- `publication_ready`: remains false.
- Seeds 2–4: remain unauthorized.

## Commits

- `be15bba9a578f5fd90f77aadbf1d27ad99837ead` — make the Qwen cache proof strictly local-cache-only and remove the download fallback.
- `2ff43b60ed422fd2d9c41a046ae36a052d11a8b6` — add regression coverage for the local-cache-only Qwen boundary.

## Testing

The new regression tests require no CUDA, model weights, network access, or image generation. Repository CI is triggered by the commits. CS408 must not be called terminal-green until Phase 18 Story Intelligence Verification for the final CS408 HEAD completes successfully.

No Genuine Golden PNG is created or claimed by this change.

## Remaining blocker

A real self-hosted NVIDIA runner is still required with all of the following:

- workflow labels `self-hosted`, `linux`, `x64`, `gpu`, `cuda`, `bf16`, `pul7sar-phase18`,
- CUDA-enabled PyTorch,
- native BF16 support,
- sufficient live VRAM, host RAM, and storage,
- the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in local cache before execution,
- compatible Diffusers/Transformers runtime.

With CS407 and CS408 together, both the FLUX construction boundary and the Qwen cache-proof boundary now refuse network fallback independently of the surrounding workflow offline environment.

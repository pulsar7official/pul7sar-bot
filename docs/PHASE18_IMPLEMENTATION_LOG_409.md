# Phase 18 Implementation Log 409 — Qwen Local-Only CI Regression Repair

## Scope

Branch: `phase18/story-intelligence` only. `main` was inspected read-only and was not modified.

This change set repairs the CPU verification regression introduced after CS408 without weakening the Qwen local-cache-only contract, factual/identity/sentiment gates, semantic-publication isolation, visual-quality gates, or any downstream publication authority.

## Starting state

- Phase branch starting HEAD: `e4b6e50a6d1994f483b1490471c0b1ede7281b39`.
- `Phase 18 Story Intelligence Verification` run `34607039045` on that SHA completed with `failure`.
- The failure occurred in `Syntax and discover validation`, before any GPU execution.
- GitHub Actions job logs showed the exact stale assertion: `tests/test_phase18_qwen_model_prefetch.py` still required the literal source text `revision=MODEL_REVISION`.
- CS408 had intentionally moved the Hugging Face cache lookup behind `_require_cached_snapshot(snapshot_download, MODEL_ID, MODEL_REVISION)`, where the helper passes `revision=revision` and `local_files_only=True`.
- Therefore the failing assertion tested obsolete source shape rather than the actual zero-cost/local-only safety contract.

## Modified

### `tests/test_phase18_qwen_model_prefetch.py`

Replaced the obsolete literal assertion with checks for the current fail-closed contract:

- `snapshot_path = _require_cached_snapshot(snapshot_download, MODEL_ID, MODEL_REVISION)` must remain present.
- the helper must pass `revision=revision`.
- `local_files_only=True` must remain present.
- the receipt must continue to assert `$0-local`.
- `downloaded_now` must remain `False`.
- `network_download_authorized` must remain `False`.
- receipt-level `local_files_only` must remain `True`.
- immutable revision validation through `assert_snapshot_revision(snapshot, MODEL_REVISION)` remains required.
- no inference `pipeline(` call is allowed in the cache-proof tool.

No production Qwen code was weakened or changed in CS409.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_409.md` (this log).

## Deleted

- No files deleted.
- No safety, provenance, publication, identity, sentiment, or visual-quality gates removed.

## Test evidence

Fix commit: `38bc6d6f6e28c6447626b7f3b075b382ce33fcf5`.

`Phase 18 Story Intelligence Verification` run `34612603643` completed successfully on that exact SHA.

Notably:

- `Syntax and discover validation`: success.
- `Completion and production isolation`: success.
- visual-study handoff build/verification: success.
- result-family publication isolation verification: success.
- project-native/adaptive/self-contained brand studies: success.
- Golden editorial v6 CPU build/verification: success.
- legacy-logo non-canonical assertion: success.
- all expected CPU-side artifacts uploaded successfully.

This demonstrates that CS408's Qwen local-only behavior is compatible with the complete Phase 18 CPU verification suite once the stale source-shape assertion is corrected.

## Zero-cost and gate posture

Unchanged and fail-closed:

- Qwen exact approved revision remains required.
- Qwen cache resolution remains `local_files_only=True` with no network fallback.
- FLUX.2 exact approved revision remains local-cache-only.
- cost mode remains `$0-local`.
- factual, identity, sentiment, semantic-publication and visual-quality gates remain intact.
- `human_visual_review_approved = false`.
- `golden_quality_approved = false`.
- `publication_ready = false`.
- `seeds_2_to_4_authorized = false`.

## Genuine Golden PNG status

No Genuine Golden Visual PNG was generated or claimed in CS409.

The available execution environment remains CPU-only (`torch=2.10.0+cpu`, CUDA unavailable, no CUDA device, BF16 unavailable, and `nvidia-smi` unavailable). The remaining non-substitutable blocker is execution on a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally.

CS409 materially reduces the remaining gap by restoring the full CPU verification baseline required before any legitimate GPU Golden run.

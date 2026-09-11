# Phase 18 Implementation Log 412 — Canonical Hugging Face Snapshot Cache Proof

## Scope

Branch: `phase18/story-intelligence` only. `main` was reviewed read-only and was not modified, merged, rebased, reset, or force-updated.

CS412 advances the first genuine Golden Visual PNG path without generating or claiming a PNG. It strengthens the common immutable-model revision proof used by the Qwen semantic path and FLUX generation path.

## Starting state

The branch started CS412 at `c7a29d6ca9ed83b1d42948d58d71ae3c87c1460f`. CS411 Story Intelligence Verification run `34635528012` had completed successfully.

The approved-model helper previously accepted any resolved path whose immediate parent was named `snapshots` and whose final directory name was the approved 40-character commit SHA. A locally fabricated path such as `/tmp/fabricated/snapshots/<approved-sha>` could therefore satisfy the path-shape revision check even though it was not in the standard Hugging Face Hub cache hierarchy used by the `$0-local` model-cache gates.

## Changes

### Modified

- `engine/intelligence/approved_model_revisions.py`
  - added `_assert_canonical_hf_snapshot_path(...)`;
  - now requires the standard `models--<owner>--<repo>/snapshots/<commit-sha>` cache hierarchy before accepting a resolved revision;
  - preserves the existing full 40-character SHA validation and exact expected-revision comparison;
  - affects the shared revision proof already used by both Qwen and FLUX cache/runtime paths, without changing approved model IDs or revisions.

### Added

- `tests/test_phase18_approved_model_revision_cache_path.py`
  - accepts a canonical Hugging Face snapshot-cache path;
  - rejects a fabricated `snapshots/<approved-sha>` path outside `models--...`;
  - rejects an empty repository component in the cache directory;
  - confirms revision drift is still rejected inside an otherwise canonical cache hierarchy.

### Deleted

Nothing.

## Gate preservation

No factual, entity-identity, sentiment, semantic-publication, visual-quality, Human Visual Review, Golden Quality, or publication authority gate was weakened. No model ID, immutable model revision, prompt, generation parameter, dependency, or publication behavior changed.

The downstream authority remains fail-closed: Human Visual Review approval, Golden Quality approval, publication readiness, and Seeds 2–4 authorization are not granted by this change.

## Zero-cost / local-only effect

CS407–CS410 already made the concrete loaders/cache proofs local-only. CS412 tightens the meaning of the cached snapshot evidence itself: an approved SHA in an arbitrary local directory is no longer sufficient. The revision proof must come from a standard Hugging Face Hub cache snapshot hierarchy.

## Testing

The new regression suite is intentionally CPU-safe and filesystem-only; it does not load model weights, perform inference, use the network, or create a PNG. Repository CI should run the normal Phase 18 Story Intelligence verification after these commits. A terminal-green claim must wait for that run to finish successfully.

## Remaining blocker to the first genuine Golden PNG

No genuine Golden Visual PNG was produced or claimed in CS412. The remaining non-substitutable execution blocker is a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present in the local Hugging Face cache. The Golden workflow remains `$0-local` and must fail closed if those requirements are absent.

# Phase 18 Implementation Log — CS468

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Baseline reviewed before this change: CS467 at `04aad6dbff57fb611277d23f7c158026956f9c64`.

`main` is not a write target for this change set.

## Objective

Close a provenance gap before the first genuine Golden Visual PNG: source-commit binding alone does not prove that the checked-out tracked working tree and index remained unchanged while the authoritative Candidate 1 attempt executed on a self-hosted runner.

CS468 adds an immutable tracked-source baseline/replay gate around the entire attempt. It permits generated runtime artifacts only beneath `output/` while rejecting tracked-source mutation, staged mutation, HEAD/tree/index drift, unexpected untracked source-shadow files, branch drift, source SHA drift, cost-mode drift, or offline-policy drift.

## Added

- `tools/phase18_verify_first_golden_tracked_source_integrity.py`
  - `capture` records the exact Phase 18 branch, HEAD, HEAD tree, index tree, deterministic staged-index fingerprint, tracked-file count, tracked worktree/index cleanliness, and the initial untracked-file set.
  - baseline capture requires no unexpected untracked files before preflight.
  - `verify` requires the same branch, source SHA, tree, index tree, index fingerprint, and tracked-file count after the attempt.
  - tracked worktree and index must remain clean.
  - post-attempt untracked files are accepted only beneath `output/`.
  - `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` remain mandatory.
  - all Human Review, Golden, generation, publication, network-download and Seeds 2–4 authority fields remain closed.

- `tests/test_phase18_first_golden_tracked_source_integrity.py`
  - verifies a clean immutable replay with runtime files beneath `output/`.
  - rejects tracked worktree mutation.
  - rejects an untracked source-shadow file outside `output/`.
  - rejects HEAD drift.
  - rejects offline-policy drift.

## Modified

- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - requires the new integrity tool in the immutable checkout.
  - captures tracked-source baseline immediately after checkout/main-isolation and before any execution/model preflight.
  - replays tracked-source integrity after exact review-bundle replay and immediately before success artifact upload.
  - upload therefore remains fail-closed if any tracked source or unexpected untracked source file changed during the attempt.

- `tests/test_phase18_first_golden_fresh_workflow.py`
  - asserts the tracked-source baseline wraps the entire execution path.
  - asserts final tracked-source replay occurs after bundle replay and before success upload.

## Deleted

None.

## Preserved gates

No factual, identity, sentiment/loser-respect, semantic-publication, Human Visual Review, Golden-quality, Candidate 1 prompt/seed/steps/dimensions/guidance, Qwen2.5-VL, FLUX.2, native-BF16, zero-cost, offline-only, publication, or Seeds 2–4 authority was relaxed.

The following remain false by construction in the new evidence:

- `authoritative_gate`
- `network_download_authorized`
- `generation_authorized`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`
- `seeds_2_to_4_authorized`

## Execution status

This change does not fabricate or claim a Golden PNG. Actual Candidate 1 generation still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots present locally under the existing `$0-local` / offline-only contract.

## Remaining gap

Once CI validates CS468, the remaining decisive step is still a genuine execution of the existing freshness-bound GPU workflow on a runner satisfying every CUDA/BF16/model-cache/resource gate. If that environment is unavailable, no PNG is to be fabricated or substituted.

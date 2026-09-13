# Phase 18 Implementation Log 400

## Scope
CS400 — integrate the CS399 source-bound artifact replay directly into the First Genuine Golden v6 workflow before evidence upload.

## Branch isolation
- Target branch: `phase18/story-intelligence` only.
- Starting branch HEAD: `52d790fccf2e35be5a0518bffb9370bbe57f2708`.
- `main` was read only; observed at `b40f5446fa8ce71accb53f46f364aedeba5c8d35` during this change set.
- No merge, rebase, reset, force update, or write to `main` was performed.

## Problem closed
CS399 added an independent source-bound artifact verifier, but the First Genuine Golden v6 workflow did not execute that composite verifier before uploading evidence. The workflow separately replayed model/resource/runtime/staging evidence and source-commit binding, leaving the final composed CS399 contract as a post-download-only operation.

CS400 makes the composed source-bound replay a required pre-upload gate. This reduces the gap between a successful CUDA/BF16 generation and a trustworthy artifact without granting Human Review, Golden Quality, publication, or Seeds 2–4 authority.

## Changes
### Modified
`.github/workflows/phase18-first-genuine-golden-v6.yml`

- Requires `tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py` during immutable branch/tool isolation.
- Adds `Replay complete source-bound artifact contract before upload` after source binding and before artifact upload.
- Runs the composite verifier against the Candidate 1 resource lock with `--artifact-root .` and immutable `${{ github.sha }}` supplied as the external expected source SHA.
- Writes `output/phase18_gpu_smoke/first-genuine-golden-v6-source-bound-replay.json` only after successful replay.
- Re-parses the replay receipt and fails unless status is `FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED`, `source_commit_verified=true`, and all downstream authority flags remain false.

Workflow change commit: `603b1959c04a593deeefcd9073b3edde9e0f3f04`.

### Added
`tests/test_phase18_first_genuine_golden_v6_source_bound_replay_workflow.py`

Regression coverage protects:
- presence of the composite verifier tool guard;
- replay ordering before artifact upload;
- binding to immutable `${{ github.sha }}`;
- repository-root artifact replay;
- persisted replay receipt inside the uploaded `output/phase18_gpu_smoke/**` tree;
- verified replay status/source commit;
- fail-closed Human Review, Golden Quality, publication, and Seeds 2–4 authority.

Test commit: `8ad288d9b41becfa70b81ebb14b0f0c8a177223f`.

### Deleted
None.

### Dependencies
None changed.

### Generation/model/prompt behavior
No generation model, prompt, factual, identity, sentiment, zero-cost, semantic-publication, layer-ownership, or visual-quality logic was weakened or changed.

## Testing
The repository CI triggered from the branch commits. CS400 must not be called terminal-green until the relevant Phase 18 verification run finishes successfully on the exact code-and-test-bearing SHA/current documented HEAD.

The new workflow path remains intrinsically GPU-blocked for real PNG production unless a self-hosted runner with the required labels and capabilities is available. No PNG is fabricated by this change.

## Remaining blocker to the first genuine Golden PNG
A real execution still requires the First Genuine Golden v6 workflow to run on a compatible self-hosted NVIDIA host with:
- CUDA-enabled PyTorch;
- native BF16 support;
- sufficient VRAM/RAM/storage;
- exact approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally;
- `$0-local` / offline model resolution intact.

Until that execution occurs successfully, Candidate 1 remains ungenerated in this environment and all downstream authority remains fail-closed.

# Phase 18 Implementation Log 398 — Golden v6 Source-Commit Workflow Integration

## Scope

Branch: `phase18/story-intelligence` only.

`main` was read only and was not modified, merged, rebased, reset, or force-updated.

## Starting state

Starting Phase 18 HEAD: `2ab5252b0628677d6314582c37887354cd3d7c21`.

The `verify-story-intelligence` check on that exact SHA completed successfully, so CS397 source-commit provenance binding was terminal-green before this change set began.

Observed `main` HEAD during this change set: `482c2be7dd48f595035724a4ddb94d0d7a82a899` (read only).

## Gap closed

CS397 introduced `tools/phase18_bind_first_genuine_golden_source_commit.py`, but the First Genuine Golden v6 workflow did not yet invoke it. A real GPU run could therefore produce a valid resource-lock/PNG artifact without including the new exact-source-commit provenance envelope.

CS398 integrates that binder into the actual Candidate 1 workflow while preserving all existing factual, identity, sentiment/loser-respect, `$0-local`, semantic-publication, generated-layer, visual-quality, Human Review, Golden Quality, and publication fail-closed gates.

## Code changes

### Modified

`.github/workflows/phase18-first-genuine-golden-v6.yml`

Changes:

1. The branch-isolation/preflight step now requires `tools/phase18_bind_first_genuine_golden_source_commit.py` to exist at the immutable dispatched commit.
2. After the existing model/resource/runtime/semantic/staging/PNG evidence replay and before artifact upload, the workflow now runs the binder in `bind` mode against `output/phase18_gpu_smoke/first-genuine-golden-v6-resource-lock.json`.
3. The resulting envelope is written to `output/phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json`.
4. The workflow immediately replays that envelope in `verify` mode against the immutable `${{ github.sha }}` exposed as `DISPATCH_SHA`.
5. Because the envelope is inside `output/phase18_gpu_smoke/**`, it is included automatically in the existing Candidate 1 evidence artifact.

Workflow integration commit: `ca6b81703cdedee47352ec2eaba3d22708dddf2e`.

### Added

`tests/test_phase18_first_genuine_golden_v6_source_binding_workflow.py`

Regression coverage verifies that:

- the binder tool is explicitly required by workflow preflight;
- source binding runs before artifact upload;
- bind and verify both operate on the canonical v6 resource-lock and source-binding envelope paths;
- verification uses immutable `${{ github.sha }}` through `DISPATCH_SHA`;
- the source-binding envelope remains under the uploaded `output/phase18_gpu_smoke/**` evidence tree;
- Human Review, Golden Quality, publication, and Seeds 2–4 authority remain fail-closed in the binder.

Regression-test commit: `84d575118c8b1e1fbe0006c8531342efd7bcb8ba`.

### Deleted

Nothing.

### Dependencies

No dependency changes.

### Generation semantics

No generation model, prompt, factual/identity/sentiment policy, semantic-publication gate, model revision, CUDA/BF16 requirement, cache policy, image-quality gate, or publication authority was weakened or bypassed.

## Validation

Repository-level GitHub CI is the authoritative validation path for this branch. The new workflow and regression test were committed so the existing `verify-story-intelligence` workflow can perform syntax/discovery/regression validation on the exact branch SHA.

This log does not claim terminal-green status until the relevant check on the exact code-and-test-bearing SHA has completed successfully.

## Genuine Golden PNG status

No Genuine Golden Visual PNG was fabricated or claimed in CS398.

The non-substitutable execution blocker remains the absence, in the currently available execution environment, of a compatible self-hosted NVIDIA CUDA/native-BF16 runner satisfying the v6 labels and runtime contract, with CUDA-enabled PyTorch, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local` policy.

When such a runner executes the v6 workflow, Candidate 1 must now prove not only PNG/evidence integrity but also exact source-commit provenance before the evidence artifact is uploaded. Downstream Human Review, Golden Quality approval, publication readiness, and Seeds 2–4 authorization remain false.

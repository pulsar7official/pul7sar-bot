# Phase 18 Implementation Log — CS397

## Scope

CS397 adds an independent source-commit provenance binding for the First Genuine Golden Editorial v6 artifact path. The goal is to ensure that a resource-lock receipt that is otherwise valid cannot be replayed as if it came from a different commit on the same `phase18/story-intelligence` branch.

## Starting state

- Working branch: `phase18/story-intelligence`
- Starting HEAD reviewed: `ad31d243648c9149b4d55a7f1d82df1fd7d61926`
- `main` reviewed read-only at: `064fd78cefdf033722e1ca81353a617a3753c43d`
- No merge, rebase, reset, force-update, or direct modification was performed on `main`.
- Phase 18 Story Intelligence Verification run `34552296762` for CS396 completed successfully.

## Gap found

The existing v6 resource-lock and artifact replay chain strongly binds branch, Candidate 1, `$0-local`, CUDA/BF16 evidence, pinned Qwen/FLUX revisions, runtime stability, staging evidence, PNG SHA-256, byte count, and downstream fail-closed authority.

However, the final artifact provenance did not independently bind the bundle to the exact 40-character Git commit SHA that executed generation. A valid artifact from another commit on the same branch could therefore satisfy the existing branch-level identity checks unless the workflow-run metadata was inspected separately.

## Added

### `tools/phase18_bind_first_genuine_golden_source_commit.py`

CPU-safe provenance utility with two operations:

- `bind`: records the exact `git rev-parse HEAD` SHA and requires the current branch to be exactly `phase18/story-intelligence`.
- `verify`: replays the binding against an externally supplied expected source SHA, intended to come from immutable workflow-run metadata.

The source envelope also binds the v6 resource-lock file by SHA-256 and byte count and keeps all downstream authority fail-closed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

The utility performs no model loading, no image generation, no network access, and grants no publication or Golden-quality authority.

### `tests/test_phase18_bind_first_genuine_golden_source_commit.py`

Regression coverage verifies:

1. exact source-commit binding and replay,
2. rejection when the expected workflow SHA differs,
3. rejection if the bound resource-lock bytes are altered,
4. rejection if binding is attempted from `main` or any non-Phase-18 branch,
5. rejection of downstream authority drift in the source-binding envelope.

## Commits

- `67078b3f42e7bdc5330ac88f91aca40f0569a93c` — add exact source-commit binding utility.
- `7057d4c065ba43f1bfe5f4150b4e3b82aad6c2e7` — add source-binding regression tests.

## Tests performed before repository write

The new focused suite was executed in an isolated local test layout:

```text
Ran 5 tests in 0.010s
OK
```

No CUDA/GPU result was fabricated. This test only validates CPU-safe provenance logic.

## Modified

None in existing production generation logic during CS397.

## Deleted

None.

## Gate preservation

CS397 does not loosen or bypass factual/freshness, Entity/Identity, sentiment neutrality / loser-respect, `$0-local`, semantic-publication, generated-layer, visual-quality, Human Review, Golden Quality, or publication gates.

## Remaining integration gap

The new source-binding utility is intentionally additive and is not yet wired into `.github/workflows/phase18-first-genuine-golden-v6.yml`. Until that integration is performed and regression-guarded, the official v6 workflow continues to rely on GitHub workflow metadata plus its existing immutable checkout checks for source-SHA provenance.

The next safe change is to invoke source binding immediately after the v6 resource-lock is produced, verify it against `${{ github.sha }}`, and upload the binding envelope with the genuine artifact. That integration should be completed without altering generation semantics or downstream authority.

## Genuine Golden execution blocker

No Genuine Golden PNG was created in CS397. Actual model inference still requires a compatible self-hosted NVIDIA CUDA/native-BF16 runner with CUDA-enabled PyTorch, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already available locally under the `$0-local` contract.

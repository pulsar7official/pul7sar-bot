# Phase 18 Implementation Log — CS469

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Baseline reviewed before this change: CS468 at `3db8392b64e86a51d041a7314f93ea332592e910`.

`main` is not a write target for this change set.

## Objective

Close a workflow supply-chain provenance gap before the first genuine Golden Visual PNG. The First Genuine Golden workflow already bound source commit, tracked worktree/index integrity, runner/CUDA identity, approved model snapshots, freshness evidence, source provenance, PNG bytes, and the exact Human Review bundle; however, it still referenced GitHub Actions by mutable major-version tags (`actions/checkout@v4` and `actions/upload-artifact@v4`).

CS469 pins every external action used by the first-Golden workflow to an exact, verified 40-character commit SHA. This prevents a mutable upstream tag from changing the code executed by the authoritative attempt without a repository code review.

## Verified upstream action pins

The action tag objects were read from GitHub before changing the workflow:

- `actions/checkout` tag `v4.2.2` resolves to `11bd71901bbe5b1630ceea73d27597364c9af683`.
- `actions/upload-artifact` tag `v4.6.2` resolves to `ea165f8d65b6e75b540449e92b4886f43607fa02`.

The workflow now uses those exact commit SHAs while retaining the release versions as comments for maintainability.

## Added

- `tests/test_phase18_first_golden_workflow_action_pins.py`
  - requires `actions/checkout` to use the exact verified `v4.2.2` commit SHA.
  - requires both success and failure `actions/upload-artifact` paths to use the exact verified `v4.6.2` commit SHA.
  - rejects floating `@v4` and `@main` refs.
  - rejects any external action reference in this workflow that is not a full lowercase 40-character commit SHA.

## Modified

- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - changed `actions/checkout@v4` to `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`.
  - changed both `actions/upload-artifact@v4` references to `actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2`.
  - no generation logic, factual gate, identity gate, sentiment gate, semantic-publication gate, visual-quality gate, zero-cost/offline gate, model revision, Candidate 1 parameter, or authority state was changed.

## Deleted

None.

## Preserved gates

No factual, identity, sentiment/loser-respect, semantic-publication, Human Visual Review, Golden-quality, Candidate 1 prompt/seed/steps/dimensions/guidance, Qwen2.5-VL, FLUX.2, native-BF16, zero-cost, offline-only, publication, or Seeds 2–4 authority was relaxed.

The following remain closed by construction:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Testing

CS469 adds a regression test that parses every `uses:` entry in the First Genuine Golden workflow and fails if any external action is not pinned to a full commit SHA. GitHub Actions is the authoritative repository test environment for this change set.

## Execution status

This change does not fabricate or claim a Golden PNG. Actual Candidate 1 generation still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots present locally under the existing `$0-local` / offline-only contract.

## Remaining gap

After CI validates CS469, the decisive remaining step is still a genuine execution of the freshness-bound GPU workflow on a runner satisfying every CUDA/BF16/model-cache/resource gate. If that environment is unavailable, no PNG is to be fabricated or substituted.

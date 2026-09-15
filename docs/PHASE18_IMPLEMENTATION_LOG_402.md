# Phase 18 Implementation Log — CS402

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed read-only and was not modified, merged, rebased, reset, force-updated, or used as a write target.

Starting Phase 18 HEAD: `a36e4efe60c57a0a6a799c740ea43b234aead79d`.

## Prior-state verification

CS401 introduced a fail-closed artifact-readiness manifest written only after the composite source-bound artifact replay succeeds. The current Golden v6 workflow still uploads diagnostic evidence with `if: always()`, which is intentional for failure diagnosis.

A residual self-hosted-runner risk remained: an early failure before the composite verifier executes can leave output from an earlier workflow run in the persistent workspace. A fixed-name readiness marker could therefore be present in a diagnostic artifact even though the current run never reached readiness verification.

The marker itself grants no Human Review, Golden Quality, publication, or Seeds 2–4 authority, but its fixed filename made stale-run provenance unnecessarily ambiguous.

## CS402 change

### Modified

`tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`

The readiness contract is now bound to the GitHub Actions workflow execution identity as well as source commit, resource-lock, PNG bytes, evidence replay, and zero-cost semantics.

Changes:

- readiness schema advanced from `pul7sar-first-genuine-golden-v6-artifact-ready-v1` to `...-v2`;
- readiness payload now requires positive integer `workflow_run_id` and `workflow_run_attempt`;
- the CLI obtains these values from `GITHUB_RUN_ID` and `GITHUB_RUN_ATTEMPT` by default, both of which are supplied by GitHub Actions without a workflow YAML change;
- explicit CLI overrides remain available for safe local replay/testing;
- readiness filenames are now run-specific:
  `first-genuine-golden-v6-artifact-ready-run-<run_id>-attempt-<attempt>.json`;
- invalid, missing, zero, non-canonical, or boolean run identities fail closed;
- the same-run marker is removed before replay begins;
- the obsolete fixed-name v1 marker is removed whenever the composite verifier is reached;
- `verify_artifact_ready_manifest(...)` reconstructs the expected readiness payload and rejects any workflow-run, source, PNG, evidence, cost-mode, or authority drift;
- the freshly written manifest is replay-verified immediately before the CLI exits successfully.

This closes the stale-marker ambiguity for a repeated source SHA: a prior run may remain in a persistent self-hosted workspace, but its readiness filename and payload identify a different GitHub workflow run and therefore cannot represent readiness for the current run.

### Modified tests

`tests/test_phase18_first_genuine_golden_v6_artifact_ready_manifest.py`

Coverage now verifies:

- v2 readiness schema;
- exact workflow run-id/run-attempt binding;
- deterministic run-specific readiness filename;
- source/resource-lock/PNG binding remains intact;
- incomplete evidence still fails closed;
- invalid or missing run identity fails closed;
- Human Review, Golden Quality, publication, and Seeds 2–4 remain false;
- stale run id or stale run attempt is rejected during readiness replay;
- the run-specific manifest is still written atomically without a `.tmp` residue.

## Commits

- `6cd3ef6fd3b2f6dc0b84e1240d9ed7558a0729f7` — run-bind the artifact readiness contract.
- `98ebb936d83e60fec1f27267ac6f5c8676335c69` — regression coverage for run-bound readiness markers.

## Deleted

No repository files were deleted.

## Unchanged safety and publication boundaries

No generation model, model revision, prompt, factual gate, identity gate, sentiment/loser-respect rule, semantic-publication gate, visual-quality gate, cost mode, or publication authority was changed.

The readiness marker continues to mean only `eligible_for_human_visual_review=true`. It explicitly keeps:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

The `$0-local` contract and offline pinned-model requirements remain unchanged.

## Testing state

GitHub Actions started automatically for code-and-test-bearing SHA `98ebb936d83e60fec1f27267ac6f5c8676335c69`.

At the time this log was written, `Phase 18 Story Intelligence Verification` run `34576499149` and the other Phase 18 checks were queued, so CS402 is not described as terminal-green yet.

## Genuine Golden PNG status

No Genuine Golden PNG was fabricated or claimed.

The remaining execution blocker is unchanged: the real Golden v6 workflow requires the qualified self-hosted runner labels `self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`, CUDA-enabled PyTorch with native BF16 support, sufficient RAM/VRAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the local cache so execution remains `$0-local` and offline.

CS402 materially reduces the gap by ensuring that a readiness marker can be attributed to the exact workflow execution that produced and replay-verified Candidate 1 rather than merely to a persistent runner workspace or repeated source commit.

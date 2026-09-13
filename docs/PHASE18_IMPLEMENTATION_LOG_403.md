# Phase 18 Implementation Log — CS403

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed read-only and was not modified, merged, rebased, reset, force-updated, or used as a write target.

Starting Phase 18 HEAD: `5c0d9df6f2a688e4b38dc3965f0f6f5073778689`.

## Prior-state verification

CS402 is terminal-green: `Phase 18 Story Intelligence Verification` run `34576534910` completed successfully on the starting SHA.

CS402 bound the readiness manifest to the exact GitHub workflow run id and attempt. A remaining post-download provenance gap was identified: the composite verifier CLI was producer-oriented. Invoking it after downloading an artifact would replay the source-bound evidence and then delete/rewrite the same-run readiness marker before verifying it. That proved a newly reconstructed marker, but did not independently prove that the readiness marker contained in the uploaded artifact was unchanged.

This did not open Human Review, Golden Quality, publication, or Seeds 2–4 authority, but it left the uploaded readiness marker without a dedicated read-only replay path.

## CS403 change

### Modified

`tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`

Added a read-only consumer/replay mode for an existing run-bound readiness manifest:

- new CLI flag `--verify-existing-ready`;
- the flag replays the complete source-bound artifact contract first;
- it resolves the exact expected readiness filename from `workflow_run_id` and `workflow_run_attempt`;
- it requires the readiness marker to already exist beside the resource-lock receipt;
- it parses the uploaded JSON without rewriting, normalizing, deleting, or replacing it;
- it reconstructs the exact expected v2 readiness payload using the freshly replayed source/PNG/evidence result;
- it rejects missing markers, invalid JSON, non-object JSON, stale run ids/attempts, source/resource-lock/PNG drift, evidence drift, cost-mode drift, and any downstream authority drift;
- successful read-only replay reports `artifact_ready_manifest_verified=true` and `artifact_ready_manifest_rewritten=false`;
- producer mode remains the default and retains atomic same-run marker creation.

This creates a clean producer/consumer separation: the GPU workflow can create readiness, while a later CPU-only verifier can prove the exact readiness marker that was actually uploaded.

### Modified tests

`tests/test_phase18_first_genuine_golden_v6_artifact_ready_manifest.py`

Added regression coverage for:

- successful replay of an existing uploaded readiness marker without changing its bytes;
- rejection when the exact run-bound marker is missing;
- rejection when only a different run id marker exists;
- rejection of a tampered marker that attempts to set `publication_ready=true`;
- rejection of invalid JSON while proving the invalid file remains unchanged.

Existing coverage still protects `$0-local`, exact source/resource-lock/PNG binding, nine evidence files plus semantic replay, run-id/run-attempt binding, atomic producer writes, and fail-closed Human Review/Golden/publication/Seeds 2–4 authority.

## Commits

- `316704070958dfdff5cb3c888b14cce65b308365` — add read-only Golden v6 readiness replay.
- `5f22895c6e3fd0c1365872c27a203f2a27be9b60` — add regression coverage for existing-marker replay.

## Deleted

No repository files were deleted.

## Unchanged safety and publication boundaries

No generation model, pinned model revision, prompt, factual gate, entity/identity gate, sentiment/loser-respect rule, zero-cost rule, semantic-publication gate, generated-layer gate, visual-quality gate, or publication authority was weakened or changed.

The readiness contract continues to mean only `eligible_for_human_visual_review=true`. It still requires:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

The `$0-local`, offline-cache-only, pinned Qwen2.5-VL and FLUX.2 requirements remain unchanged.

## Testing state

The code-and-test-bearing SHA is `5f22895c6e3fd0c1365872c27a203f2a27be9b60`. GitHub Actions is expected to run the Phase 18 verification suite for this SHA and for the documentation HEAD. CS403 must not be described as terminal-green until the required verification run completes successfully.

## Genuine Golden PNG status

No Genuine Golden PNG was fabricated or claimed.

The execution blocker remains the qualified self-hosted GPU environment required by the genuine Golden v6 workflow: runner labels `self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`, CUDA-enabled PyTorch with native BF16 support, sufficient RAM/VRAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally so execution remains `$0-local` and offline.

CS403 reduces the remaining gap by making the final readiness decision independently replayable after artifact download without mutating the evidence being verified.

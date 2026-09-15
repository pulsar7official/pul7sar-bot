# Phase 18 Implementation Log — CS406

## Scope

Branch: `phase18/story-intelligence` only. `main` remains read-only and was not modified.

CS406 integrates the CS405 upload-transport attestation into the real First Genuine Golden Editorial v6 workflow. The goal is to make transport provenance part of the same fail-closed execution path that will eventually produce Candidate 1 on a compatible self-hosted CUDA/BF16 runner.

## Starting state

- Starting Phase 18 HEAD: `c78ddde51aee3b9a2cab1aff858dbb61c958b020`.
- CS405 verification run `34591423951` completed successfully on that SHA.
- `main` was inspected read-only and was not changed.
- No Genuine Golden PNG was generated in this CPU-only automation environment.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6.yml`

1. Added `actions: read` while retaining `contents: read`. No write permission was added.
2. Added a branch-isolation guard requiring `tools/phase18_attest_first_genuine_golden_v6_uploaded_artifact.py` to exist on the dispatched immutable Phase 18 commit.
3. Added step id `golden_evidence_upload` to the primary Candidate 1 evidence upload so its immutable `artifact-id` and SHA-256 `artifact-digest` outputs can be consumed.
4. Added a post-upload transport-attestation step that:
   - consumes `${{ github.sha }}`, `${{ github.run_id }}`, `${{ github.run_attempt }}`, upload `artifact-id`, and upload `artifact-digest`;
   - requires the run-bound readiness manifest created by the source-bound verifier;
   - fetches the exact uploaded artifact metadata through the GitHub REST `GET /repos/{owner}/{repo}/actions/artifacts/{artifact_id}` endpoint using the workflow token with read-only Actions permission;
   - performs bounded retry for transient metadata visibility/network errors;
   - writes REST metadata atomically;
   - invokes the CS405 attester, which reuses the CS404 metadata verifier;
   - refuses to proceed unless source commit and uploaded artifact metadata are both verified and the artifact is only *eligible* for Human Visual Review.
5. Added a second, separate audit artifact containing only the fetched REST metadata and transport attestation. The original Golden evidence archive is not rewritten after upload, avoiding circular provenance.
6. Human Visual Review approval, Golden Quality approval, publication readiness, and Seeds 2–4 authorization remain explicitly false.

## Added

### `tests/test_phase18_first_genuine_golden_v6_transport_attestation_workflow.py`

Regression coverage asserts:

- Actions permission remains read-only.
- The CS405 attester is required by branch isolation.
- Primary upload occurs before transport attestation.
- `artifact-id` and `artifact-digest` come from the exact primary `actions/upload-artifact` step.
- REST transport lookup is GET-only.
- Source SHA, run ID, run attempt, upload artifact ID, and upload digest are all passed into attestation.
- The transport attestation is uploaded separately from the original evidence archive.
- Human Review, Golden Quality, publication, and Seeds 2–4 authority remain fail-closed.

## Deleted

Nothing.

## Dependency changes

None.

## Generation/model/prompt changes

None. Candidate selection, factual gates, identity gates, sentiment/loser-respect gates, semantic-publication gates, pinned model revisions, `$0-local` policy, CUDA/BF16 requirements, and visual-quality gates are unchanged.

## Commits

- `d2820bab1ffe7665d1a2e48f42f983c6052593a5` — integrate post-upload transport attestation into the First Genuine Golden v6 workflow.
- `6b4182fc6ec43d52319feeb473d479875847965d` — add regression coverage for the workflow integration.

## Testing

The dedicated regression test was added to the repository and will be exercised by the existing Phase 18 verification workflows on the resulting branch HEAD. CS406 must not be described as terminal-green until the main Phase 18 Story Intelligence Verification run for the final CS406 HEAD completes successfully.

## Remaining blocker

A real Candidate 1 Genuine Golden PNG still requires execution of `.github/workflows/phase18-first-genuine-golden-v6.yml` on the designated self-hosted runner labels:

`self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`

The host must provide CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally so the run remains offline and `$0-local`.

No PNG is fabricated when those conditions are unavailable.

## Trust chain after CS406

`factual/identity/sentiment gates -> pinned $0-local model cache -> CUDA/BF16 generation -> semantic/layer/visual gates -> Genuine PNG -> evidence replay -> exact source binding -> run-bound readiness -> primary artifact upload -> GitHub REST transport verification -> upload-action/REST transport attestation -> separate immutable audit artifact -> Human Visual Review eligibility`

Human Visual Review itself remains unapproved, Golden Quality remains unapproved, publication remains blocked, and Seeds 2–4 remain unauthorized.

# Phase 18 Implementation Log — CS507

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

## Starting state
Reviewed CS506 at `880c22ba7631422fba114599716ef7fc010bae7b` and its GitHub Actions results before changing code. The live fresh-workflow regression added in CS506 caused both Story Intelligence Verification and CPU Verification Diagnostics to fail during unittest discovery/validation. The production fresh workflow itself remained unchanged.

## Root cause
`tests/test_phase18_live_fresh_workflow_activation.py` incorrectly required the live Candidate 1 workflow text to contain the downstream authority field names `human_visual_review_approved`, `golden_quality_approved`, `publication_ready`, and `seeds_2_to_4_authorized`.

The live workflow is intentionally scoped to generating, proving, packaging, replaying, and uploading the exact Candidate 1 review bundle. Human visual approval, Golden-quality approval, semantic publication readiness, and Seeds 2–4 authorization are downstream authorities and must not be granted by this generation workflow. Requiring those field names to be present in this YAML conflated preservation of downstream gates with self-approval inside Candidate 1 execution.

## Changes
### Modified
- `tests/test_phase18_live_fresh_workflow_activation.py`
  - Preserved locks for exact branch, self-hosted GPU/CUDA/native-BF16 runner labels, `$0-local`, offline-only execution, four pre-generation evidence files, freshness-bound launcher ordering, source binding, PNG structure, PNG chunk semantics, canonical RGB8 encoding, review-bundle packaging, and review-bundle replay.
  - Replaced the invalid requirement that downstream approval/publication authority tokens merely appear in the workflow.
  - Added a fail-closed assertion that the Candidate 1 workflow does **not** self-grant Human Visual Review, Golden-quality approval, publication readiness, or Seeds 2–4 authorization as `true`.
  - Added assertions that successful execution ends by uploading the exact review bundle for downstream review.

### Added
- `docs/PHASE18_IMPLEMENTATION_LOG_507.md`

### Deleted
- None.

## Production impact
No production generator, model/runtime code, evidence binder, freshness guard, PNG verifier, publication logic, or workflow YAML was changed. This is a regression-test correction only.

## Gate preservation
The change does not weaken factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline-only, semantic-publication, exact model/runtime provenance, CUDA/native-BF16, PNG integrity/canonical encoding, Human Visual Review, Golden-quality, publication, or Seeds 2–4 gates. It makes the test accurately enforce the authority boundary: Candidate 1 may produce a review bundle, but it may not approve or publish itself.

## Testing/status
CS506 GitHub Actions evidence was reviewed before this change: Story Intelligence Verification #6128 and CPU Verification Diagnostics #312 failed, with Story Intelligence failing at `Syntax and discover validation` and CPU Diagnostics preserving validator failure semantics. The CS507 correction is committed for fresh CI validation; it must not be described as CI-green until exact-head runs complete successfully.

## Golden PNG status
No Golden Visual PNG was fabricated or claimed. The live fresh workflow still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device with native BF16 support, sufficient resources, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already available locally under the `$0-local` / offline-only contract.

## Remaining path
1. Obtain green CPU/Story Intelligence CI on exact CS507 HEAD.
2. Keep the live freshness-bound Candidate 1 workflow unchanged unless a concrete defect is found.
3. Execute it only on the compatible approved self-hosted NVIDIA environment.
4. If Candidate 1 is genuinely produced and all machine/evidence gates pass, upload the exact review bundle for downstream Human Visual Review and Golden-quality decision; publication and Seeds 2–4 remain blocked until their independent gates authorize them.

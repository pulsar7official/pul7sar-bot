# Phase 18 Implementation Log — CS419

## Scope

Branch: `phase18/story-intelligence` only. `main` remained read-only.

CS419 removes a CPU-side blocker in the First Genuine Golden v6 post-generation readiness chain. CS417/CS418 established a ten-record evidence contract by adding `local_only_model_receipts`, but the source-bound artifact readiness builder still required and emitted the legacy value `9`. A genuine GPU run could therefore have generated and verified Candidate 1 successfully, then failed before readiness/upload transport attestation.

## Baseline reviewed

- Starting branch HEAD: `d8a8f32481effee04ca7dbe807223e114e086db3`.
- Story Intelligence Verification run `34684348197` for CS418 completed successfully.
- `main` was read only; observed HEAD: `63eb7a1ca9c3aa9f61ae88181ab1a569f39529b5`.
- The canonical artifact verifier already reports ten verified evidence files and includes `local_only_model_receipts`.
- The source-bound readiness builder still checked `evidence_files_verified != 9` and wrote `evidence_files_verified: 9`.

## Changes

### Modified — `tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`

- Added `EXPECTED_EVIDENCE_FILES = 10` as the single readiness count contract.
- Replaced the legacy hard-coded readiness check for nine evidence files with the ten-record constant.
- Replaced the legacy readiness manifest value `evidence_files_verified: 9` with the ten-record constant.
- No Human Review, Golden Quality, publication, or Seeds 2–4 authority was opened.
- No model loading, generation, network access, or prompt logic was changed.

Functional commit: `711779732aea3ab6b0d96d8dab6ac55b2b8263f4`.

### Modified — `tests/test_phase18_verify_first_genuine_golden_v6_source_bound_artifact.py`

- Updated the artifact replay fixture to the canonical ten-record evidence count.
- Added an assertion that successful source-bound replay preserves the count of ten.
- Added a readiness-manifest regression proving that ten evidence files are emitted.
- Added a negative regression proving that the legacy nine-record contract is rejected with `ARTIFACT_READY_EVIDENCE_NOT_VERIFIED`.
- Existing source-commit binding, tamper rejection, flattened artifact topology, missing-binding, ambiguous-binding, and authority-closure coverage remains intact.

Test commit: `361f8f3efe6a7047c2e1027817989bf1e892bb54`.

## Deleted

Nothing.

## Gate preservation

CS419 does not weaken or bypass any factual, entity/identity, sentiment, `$0-local`, semantic-publication, visual-quality, Human Review, source-commit, or artifact-integrity gate. The following remain closed by contract:

- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`
- `seeds_2_to_4_authorized = false`

The approved Qwen2.5-VL and FLUX.2 model IDs/revisions, local-cache-only policy, `network_download_authorized = false`, CUDA/BF16 requirements, prompts, and generation parameters were not changed.

## Why this materially reduces the Golden gap

Before CS419, the execution chain contained an internal contract mismatch: the canonical artifact replay could prove all ten evidence records while the next source-bound readiness stage still required exactly nine. On a compatible GPU this would have blocked the workflow after expensive generation work and before a reviewable artifact could become transport-attested. CS419 aligns that downstream readiness boundary with the current ten-record evidence chain.

## Testing status

The repository CI triggered by the CS419 commits is the authoritative full-suite verification. This log intentionally does not claim terminal-green status until the new branch HEAD finishes its Story Intelligence Verification run.

## Remaining blocker

A First Genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA execution host with CUDA-enabled PyTorch, native BF16 support, sufficient live VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in canonical local Hugging Face cache. Network model download is not an allowed workaround. No PNG is fabricated by this change set.

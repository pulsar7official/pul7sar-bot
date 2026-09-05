# Phase 18 Implementation Log 224 — Qwen Image 2512 Measurement Admission

## Branch isolation

- Target branch only: `phase18/story-intelligence`.
- Baseline HEAD reviewed before writing: `57bebf2a5f55b03ba3201f5e0dc48d5f9414af03`.
- `main` reviewed separately at `2a6dee5bb64895a1658be84d7ce018cd71a08dff`.
- No merge, force-update, commit, file write or `main.py` modification was performed against `main`.

## Baseline verification

The baseline Phase 18 HEAD was already green. GitHub returned Story Intelligence Verification Run `33131239169 / run 3590` with `conclusion=success`, alongside successful companion Phase 18 workflows for the same commit.

## Problem found

Change Sets 222–223 correctly created an explicit local Qwen Image 2512 candidate and pinned the immutable upstream revision, while intentionally leaving:

- `minimum_vram_gb=None`;
- `runtime_floor_proven=false`;
- `local_runtime_qualified=false`;
- `local_generation_authorized=false`.

The generic local runtime gate therefore correctly blocks execution. What was missing was a separate, non-authoritative admission layer that can tell a future self-hosted GPU whether it is worth spending a real measurement attempt on the exact pinned snapshot, without inventing a VRAM floor.

## Added

1. `engine/intelligence/qwen_image_measurement_admission.py`
   - verifies the SHA-bound explicit local-candidate declaration;
   - locks model ID and revision to `Qwen/Qwen-Image-2512@2ce1c28560fbc62c9f5531e076b237d3575330a9`;
   - requires `$0-local` and rejects declaration authority drift;
   - requires CUDA, Torch, native BF16, total VRAM and live-free VRAM observability;
   - requires the existing live host-memory gate;
   - requires Diffusers plus `QwenImagePipeline` API availability;
   - checks exact snapshot revision and completeness (`model_index.json` plus safetensors);
   - requires 57.7 GiB repository capacity plus 8 GiB working headroom when uncached, or 8 GiB headroom when the exact complete snapshot is already cached;
   - emits a SHA-sealed measurement receipt with all generation/semantic/Golden/publication authority explicitly false.

2. `tools/phase18_preflight_qwen_image_measurement.py`
   - reads a pinned candidate declaration from the repository;
   - probes current local CUDA/BF16/live resources, host RAM, Diffusers capability and cache state;
   - performs no network download, model load, inference or queue mutation;
   - writes the sealed measurement receipt and exits non-zero when blocked.

3. `tests/test_phase18_qwen_image_measurement_admission.py`
   - declaration SHA binding and authority rejection;
   - no inference of a runtime floor from observed VRAM;
   - BF16/live VRAM/host RAM checks;
   - host-memory authority drift rejection;
   - uncached disk requirement;
   - exact pinned complete snapshot handling;
   - incomplete or wrong-revision snapshot rejection;
   - `QwenImagePipeline` API requirement.

4. `docs/PHASE18_CHANGESET_224_QWEN_IMAGE_MEASUREMENT_ADMISSION.md`.

5. `docs/PHASE18_IMPLEMENTATION_LOG_224.md`.

## Modified during hardening

- `tools/phase18_preflight_qwen_image_measurement.py`
  - removed unsealed path metadata that had initially been appended after receipt hashing; the persisted receipt is now fully covered by its canonical SHA.

- `engine/intelligence/qwen_image_measurement_admission.py`
  - strengthened exact-cache detection so a directory named `snapshots/<approved SHA>` is not accepted unless it is a real complete snapshot;
  - added rejection for authority drift in the reused host-memory receipt.

- `tests/test_phase18_qwen_image_measurement_admission.py`
  - aligned fixtures with complete-snapshot requirements and added regression coverage for incomplete snapshots and host-memory authority drift.

## Deleted

Nothing.

## Canonical gates preserved

No factual, identity, sentiment, semantic, quality or publication gate was weakened. In particular, the following remain fail-closed:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and loser-respect rules;
- canonical `$0-local` execution requirement;
- pinned model/runtime evidence;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Semantic/Layer Ownership;
- byte-bound Visual Critic hard failures;
- Human Review;
- Golden `8.5 minimum / 9.0+ elite`;
- Exact Brand Integrity;
- Typography Integrity;
- `SemanticPublicationGate`.

The new receipt itself keeps `runtime_floor_proven=false`, `local_runtime_qualified=false`, `generation_authorized=false`, `semantic_approved=false`, `golden_quality_approved=false` and `publication_ready=false`.

## Testing status for this change set

An intermediate Story Intelligence Verification Run `33134230170 / run 3600` executed against code HEAD `28c5aba451dc336d5433ed3cd4e47c0164de5b4d` and failed in `Syntax and discover validation`. That run occurred after the snapshot-completeness hardening but before the regression fixtures were updated in commit `5cef152c86dc44d151302363e84d9071a379ec07`. The GitHub API exposes the failed step but not a usable textual assertion log in this run context, so no unsupported cause is claimed beyond that ordering fact.

After that intermediate run was launched, the regression suite was updated to create a complete pinned snapshot fixture and to cover incomplete-snapshot and host-memory-authority failures explicitly. Companion Phase 18 workflows observed on the corrected test head include successful runs. A successful Story Intelligence result for the final Change Set 224 HEAD is still required before this change set is called fully CI-green.

## Golden Visual status

No new canonical Golden PNG was fabricated or claimed in this run.

The exact remaining blocker is measured execution: the available environment for this run does not expose a self-hosted `$0-local` GPU host on which the pinned Qwen Image 2512 snapshot can be loaded and measured with CUDA/native BF16, sufficient live VRAM, sufficient system RAM and safe runtime/offload evidence. The new measurement admission reduces that gap by screening such a host without falsely converting resource observations into a runtime floor.

## Next safe step after CI

On the first suitable self-hosted GPU, run the explicit local-candidate declaration through `tools/phase18_preflight_qwen_image_measurement.py`. Only if that measurement admission is green should Phase 18 spend a real model-load/runtime-floor experiment on the exact pinned Qwen Image snapshot. Even a successful model-load measurement must remain separate from canonical generation authorization until a measured runtime floor and the normal semantic/critic/human/Golden gates are satisfied.

# Phase 18 Implementation Log — Change Set 174

## Branch isolation

Target branch: `phase18/story-intelligence` only.

`main` and `main.py` were not modified, merged, force-updated or used as write targets in this change set.

## State reviewed before the change

The reviewed branch had moved the Golden benchmark to story-first Editorial v6 and had active concurrent repairs aligning the Golden v6 builder/specification with the current `VisualGrammar`, `SportsEditorialSceneDirector`, `VisualConceptDirector` and `OriginalSceneSpecification` APIs.

The most recent completed Story Intelligence run inspected during this change set (`32982506961`, run 3010, on earlier head `18c98f1b...`) had failed `Syntax and discover validation` with 34 errors from the stale Golden builder API. The branch subsequently received focused fixes for that API/schema migration.

A separate deterministic gap remained in the direct first-PNG orchestration path:

- `tools/phase18_preflight_semantic_gpu.py` emits `pul7sar-phase18-semantic-gpu-preflight-v2`;
- v2 proves the immutable approved Qwen model revision and resolved snapshot revision;
- `tools/phase18_first_png.py` still accepted only the legacy semantic-preflight v1 schema.

On a compatible host this would have rejected a valid current Qwen preflight before FLUX execution, wasting the GPU opportunity even though the semantic runtime/model had been correctly qualified.

## Changes made

### Modified

- `tools/phase18_first_png.py`
  - now requires semantic-preflight v2;
  - binds the preflight to `QWEN25_VL_3B_REVISION` from the central approved-model-revision contract;
  - requires `model_revision`, `resolved_snapshot_revision` and `revision_pinned=true` to match the approved immutable Qwen snapshot;
  - retains existing CUDA, runtime-ready, model-ready, `$0-local` and non-authority requirements;
  - adds Qwen revision/snapshot evidence to the first-PNG evidence payload.

- `tests/test_phase18_first_png_preflight.py`
  - updates semantic-preflight fixtures to the immutable v2 receipt;
  - adds positive assertions for revision pinning;
  - adds a fail-closed revision/snapshot drift regression;
  - preserves ordering, queue, provenance, precision and publication-authority regression coverage.

### Added

- `docs/PHASE18_CHANGESET_174_FIRST_PNG_QWEN_V2_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_174.md`

### Deleted

None.

## Commits created

- `0c678188eb7caea7b0f840f78477bd11f58cf592` — bind first-PNG semantic preflight to immutable Qwen v2 contract.
- `32b602fedec90d76a9c48233e02e18ba18b42463` — update first-PNG semantic preflight regression coverage.
- documentation commits follow on the same Phase 18 branch.

## Gates preserved

No factual, identity, sentiment, zero-cost, generation, semantic, visual-quality or publication threshold was relaxed.

Still fail-closed:

- Fact Lock / factual integrity;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful treatment of losing sides;
- `$0-local` only;
- pinned FLUX and Qwen revisions;
- native BF16 plus GPU/VRAM/RAM/offload qualification;
- Candidate/request/seed/canvas/SHA locks;
- generated text, branding, exact facts, entity marks and exact sport geometry prohibitions;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` inspection;
- provenance and evidence replay;
- Golden `8.5` minimum and `9.0+` elite thresholds;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate / final publication readiness.

## Testing status

The code and regression changes were pushed to the Phase 18 branch. At the time this log entry was created, a completed Story Intelligence verification result for the new Change Set 174 head had not yet been observed, so this log does not claim CI-green status prematurely.

The prior inspected failing run was fully analyzed; its 34 errors were caused by the stale Golden v6 builder API and were already being corrected on the same branch before this change set. Change Set 174 addresses an independent first-PNG/Qwen preflight version mismatch that would have blocked actual GPU execution later.

## Genuine Golden PNG status

No genuine Golden Visual PNG is claimed.

The exact remaining external execution blocker is a compatible host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM through lease/execution;
- safe local Diffusers offload/runtime;
- pinned FLUX/Qwen revisions;
- stable runtime fingerprint;
- `$0-local` execution.

Until such a host is available, Candidate 1 cannot be truthfully generated in this environment. No placeholder, fake PNG, fabricated benchmark or invented visual score was created.

## Next step

Wait for CPU CI on the current v6/API/revision-aligned branch, repair any remaining deterministic migration errors without relaxing gates, then execute Candidate 1 only on a compatible resource-qualified GPU host. Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and passes the required semantic and visual review chain.
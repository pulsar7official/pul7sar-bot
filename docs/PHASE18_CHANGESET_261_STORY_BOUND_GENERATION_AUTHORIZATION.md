# Phase 18 Change Set 261 — Story-Bound Canonical Generation Authorization

## Purpose

Change Set 261 closes the authority gap between a successful Change Set 260 live
pipeline-load/offload recheck and the future canonical Qwen Image inference call.
It is deliberately an authorization-only boundary: it does not call the pipeline,
create pixels, score pixels, approve a Golden, or grant publication authority.

## Required upstream proof

The input must be one exact, repository-contained CS260 receipt proving all of the
following for the same story/model/runtime tuple:

- production semantic replay executed;
- all fresh story gates passed;
- live observable host identity matched;
- exact pinned Qwen Image 2512 model revision;
- zero-cost local execution mode;
- model weights loaded;
- sequential CPU offload enabled;
- live same-host recheck passed;
- controlled-trial preflight valid;
- no inference or downstream approval already claimed.

The CS260 receipt digest is independently recomputed before authorization.

## Authorization scope

A passing CS261 receipt is scoped to exactly:

`single_story_single_model_revision_single_runtime_fingerprint`

It byte-binds the source CS260 receipt and carries its Story SHA, locked model ID,
model revision, cost mode, and expected runtime fingerprint.

Only `canonical_generation_authorized` is newly permitted to become `true`.
The following remain explicitly `false`:

- `inference_executed`
- `genuine_canonical_inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Fail-closed rules

CS261 rejects:

- a CS260 receipt outside the repository or behind a symlink;
- schema/status/model/revision/cost-mode drift;
- missing fresh semantic or runtime preflight proof;
- any premature inference, Golden, semantic, human-review, or publication authority;
- a bad CS260 digest;
- source-byte changes after authorization;
- cross-story, cross-model, or cross-runtime verification drift;
- overwriting an existing output directory.

## Files

- `engine/intelligence/qwen_image_story_bound_generation_authorization.py`
- `tests/test_phase18_qwen_image_story_bound_generation_authorization.py`
- `tools/phase18_build_story_bound_generation_authorization.py`
- `docs/PHASE18_CHANGESET_261_STORY_BOUND_GENERATION_AUTHORIZATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_261.md`

## Golden path after this change

`source-backed story → semantic replay → story-bound trial → live host → live pipeline load/offload → CS261 authorization → genuine inference → byte-bound pixel QA → Visual Critic → Human Review → Golden threshold → Brand/Typography → SemanticPublicationGate`

A CS261 receipt alone is not a Golden and is not publication-ready.

# Phase 18 Change Set 222 — Explicit Remote-to-Local Model Candidate Declaration

## Purpose

Change Set 221 deliberately stops at a non-authoritative local-qualification docket. A remote ZeroGPU research leader may justify scarce local measurement time, but the docket leaves `local_model_candidate_id = null` and grants no runtime or Golden authority.

Change Set 222 closes the next gap without turning research evidence into canonical evidence. It requires an **explicit caller-selected PUL7SAR `LocalModelCandidate`** and only accepts an exact curated model match for the remote renderer.

## New contract

`pul7sar-phase18-remote-renderer-explicit-local-candidate-v1`

A successful declaration proves only that:

- the qualification docket is valid and SHA-bound;
- the caller explicitly named a model profile already curated in `ZERO_COST_LOCAL_CANDIDATES`;
- the curated local model is an exact upstream-model match for the research renderer;
- the candidate remains `$0-local` by policy;
- the research pixels are not reusable as canonical evidence.

It does **not** prove:

- an immutable upstream model revision;
- a measured local runtime floor;
- CUDA/precision/VRAM/RAM readiness;
- local generation authorization;
- Semantic approval;
- Golden approval;
- Publication readiness.

## Exact-match policy

The first exact mapping is deliberately narrow:

- `qwen-image-2512` → `Qwen/Qwen-Image-2512` / `local-qwen-image-2512`

`flux2-dev` is **not** silently mapped to `FLUX.2-klein-4B`. Those are different model profiles. Until an exact curated local FLUX.2-dev profile exists, a FLUX.2-dev research leader fails closed with `REMOTE_LOCAL_CANDIDATE_NO_EXACT_CURATED_LOCAL_MATCH`.

This prevents a visually promising research result from being converted into a different canonical renderer merely because the names are related.

## Current Qwen status

The curated `Qwen/Qwen-Image-2512` profile is Elite, but its PUL7SAR runtime floor is intentionally unproven (`runtime_floor_proven = false`) and no immutable local-execution revision is yet approved in `approved_model_revisions.py`.

Therefore a successful Change Set 222 declaration still records:

- `pinned_model_revision_required = true`
- `pinned_model_revision = null`
- `measured_runtime_readiness_required = true`
- `local_runtime_qualified = false`
- `local_generation_authorized = false`

The next canonical step is measurement and revision pinning on suitable `$0-local` hardware, not generation by assumption.

## Files

### Added

- `engine/intelligence/remote_renderer_local_candidate.py`
- `tools/phase18_build_remote_renderer_local_candidate.py`
- `tests/test_phase18_remote_renderer_local_candidate.py`
- `docs/PHASE18_CHANGESET_222_EXPLICIT_REMOTE_TO_LOCAL_MODEL_CANDIDATE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_222.md`

### Modified

- None of the existing generation/runtime/publication modules.

### Deleted

- None.

## Preserved gates

No Fact, Entity/Identity, Sentiment/Neutrality, canonical `$0-local`, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry, Semantic/Layer Ownership, Visual Critic, Human Review, Golden 8.5/9.0+, Brand/Typography, or SemanticPublication gate is weakened.

Remote pixels remain research-only and cannot become Golden evidence.

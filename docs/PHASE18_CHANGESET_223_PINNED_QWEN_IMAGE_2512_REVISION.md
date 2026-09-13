# Phase 18 Change Set 223 — Pinned Qwen Image 2512 Revision

## Purpose

Change Set 222 requires an explicit curated local model candidate before remote renderer research can advance toward canonical local measurement. The first exact candidate is `Qwen/Qwen-Image-2512`.

The next blocker was that the curated model profile still identified a mutable Hugging Face repository name without an approved immutable upstream revision for local execution.

Change Set 223 pins the exact Qwen Image 2512 snapshot intended for future PUL7SAR local measurement while preserving the independent runtime-readiness gate.

## Approved immutable revision

Model:

`Qwen/Qwen-Image-2512`

Approved revision:

`2ce1c28560fbc62c9f5531e076b237d3575330a9`

The revision corresponds to the verified Qwen model upload commit and is intentionally immutable. PUL7SAR does not rely on mutable `main` for canonical evidence.

The official model distribution remains Apache-2.0, approximately 57.7 GB, BF16, and uses the Qwen Image Diffusers pipeline. Pinning the bytes does **not** prove that current hardware can execute the model.

## Contract change

The explicit local candidate declaration is upgraded to:

`pul7sar-phase18-remote-renderer-explicit-local-candidate-v2-pinned-revision`

A successful Qwen declaration now records:

- `local_model_revision = 2ce1c28560fbc62c9f5531e076b237d3575330a9`
- `pinned_model_revision_required = true`
- `pinned_model_revision_proven = true`
- `pinned_model_revision = 2ce1c28560fbc62c9f5531e076b237d3575330a9`

It still records:

- `runtime_floor_proven = false`
- `measured_runtime_readiness_required = true`
- `local_runtime_qualified = false`
- `local_generation_authorized = false`
- `canonical_golden_eligible = false`
- `publication_ready = false`

## Why this matters

A future local Qwen Image test can now fail closed on snapshot drift before scarce GPU time is spent. The remaining blocker is measured `$0-local` runtime compatibility, not ambiguity about which model bytes should be tested.

`FLUX.2-dev` remains intentionally unmatched: Change Set 223 does not create or infer a local FLUX.2-dev profile and does not substitute FLUX.2 Klein.

## Files

### Modified

- `engine/intelligence/approved_model_revisions.py`
- `engine/intelligence/remote_renderer_local_candidate.py`
- `tests/test_phase18_remote_renderer_local_candidate.py`

### Added

- `docs/PHASE18_CHANGESET_223_PINNED_QWEN_IMAGE_2512_REVISION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_223.md`

### Deleted

- None.

## Gate preservation

Pinning a model revision is evidence of model identity only. It does not bypass Fact Lock, Identity Verification, Sentiment/Neutrality, canonical `$0-local`, resource/runtime readiness, Semantic/Layer Ownership, Visual Critic, Human Review, Golden 8.5/9.0+, Exact Brand/Typography, or SemanticPublicationGate.

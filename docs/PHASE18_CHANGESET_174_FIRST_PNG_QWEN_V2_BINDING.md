# Phase 18 Change Set 174 — First-PNG Immutable Qwen v2 Binding

## Purpose

Close a pre-GPU contract mismatch in the direct first-PNG path without weakening any generation, semantic, factual, identity, sentiment, zero-cost, visual-quality or publication gate.

The semantic preflight had already advanced to `pul7sar-phase18-semantic-gpu-preflight-v2`, with the approved immutable Qwen model revision and canonical snapshot revision recorded in its receipt. `tools/phase18_first_png.py` still expected the legacy v1 schema, so a compatible CUDA host could pass the real semantic preflight and then be rejected by the orchestration wrapper before FLUX execution.

## Changes

### Modified `tools/phase18_first_png.py`

- upgraded the accepted semantic preflight contract from v1 to v2;
- imported the approved immutable Qwen revision from `approved_model_revisions` rather than duplicating the SHA;
- required all of the following before queue mutation:
  - exact Qwen model ID;
  - exact approved Qwen model revision;
  - resolved snapshot revision equal to the approved revision;
  - `revision_pinned=true`;
  - semantic runtime ready;
  - semantic model ready;
  - CUDA available;
  - `$0-local` cost mode;
  - no generation, queue, PNG or publication authority drift;
- preserved the semantic model revision/snapshot evidence in the first-PNG evidence payload.

### Modified `tests/test_phase18_first_png_preflight.py`

- aligned semantic-preflight fixtures to the v2 immutable-revision contract;
- added assertions for the pinned Qwen revision;
- added a fail-closed regression test for Qwen revision/snapshot drift;
- retained existing ordering, zero-cost, authority, provenance and queue-mutation tests.

## Security and quality properties preserved

No model, prompt, seed, canvas, visual threshold or publication decision was relaxed.

The following remain fail-closed:

- Fact Lock and factual integrity;
- entity/identity verification;
- sentiment/neutrality and respectful result framing;
- `$0-local` execution;
- pinned FLUX and Qwen revisions;
- native BF16 and GPU/resource qualification;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- Qwen `BASE_SCENE` / `HYBRID_SURFACE` semantic review;
- provenance/evidence replay;
- Golden `8.5` minimum / `9.0+` elite visual-quality thresholds;
- Exact Brand / Typography integrity;
- SemanticPublicationGate and final publication readiness.

## Deleted

None.

## GPU status

No genuine Golden PNG is claimed by this change set. The available execution environment does not provide the compatible NVIDIA CUDA/native-BF16/resource-qualified host required to execute the pinned FLUX.2 Klein and Qwen path. This change only removes a deterministic contract mismatch that would otherwise waste the next compatible GPU session.
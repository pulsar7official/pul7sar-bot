# Phase 18 Implementation Log 309 — Lineage-Bound Semantic Publication Evidence

## Starting state

Branch: `phase18/story-intelligence` only.

Starting HEAD reviewed before changes: `14d13066cfdac0ae3d95138476bb4649226a165b`.

`main` was read only. No write, merge, rebase, reset, or force-update was performed against `main`.

## Finding

The audit continued from CS282 through CS283/CS284 immediately before CS285 Genuine Golden materialization.

CS283 correctly byte-binds the exact CS282 receipt, exact composed PNG, and repository SemanticPublicationGate policy sources, and explicitly says that a real GenerationPackage/BaseSceneEvidence/zero-cost verifier profile must be reconstructed downstream.

CS284 v1, however, accepted an external semantic-publication evidence JSON and, before executing `SemanticPublicationGate`, checked only:

1. `story_snapshot_sha256` equals CS283; and
2. `composed_candidate_png_sha256` equals CS283.

The external `GenerationPackage`, `BaseSceneEvidence`, and `VisionVerifierProfile` were otherwise reconstructed directly from that JSON.  The CS284 replay verifier reopened the byte-bound evidence file and re-ran the gate, but did not repeat the raw Story/PNG checks.  This was a concrete cross-run / evidence-envelope substitution surface directly before Genuine Golden authorization.

## Implementation

### Added

- `engine/intelligence/qwen_image_semantic_publication_evidence_lineage.py`
  - defines evidence-envelope schema v2;
  - requires exact CS283 receipt binding (path/file SHA/byte size/receipt SHA);
  - requires exact CS282 binding inherited from CS283;
  - requires exact composed-PNG metadata and generation context;
  - requires Story/PNG/CS282 lineage inside GenerationPackage metadata and BaseSceneEvidence provenance;
  - requires BaseSceneEvidence output_ref to point at the exact composed PNG path;
  - fail-closes unless verifier is local zero-cost and no-network;
  - binds verifier lineage to `$0-local`, `network_allowed=false`, `local_files_only=true`.

- `tests/test_phase18_qwen_image_semantic_publication_evidence_lineage.py`
  - exact lineage accepted;
  - different CS283 run rejected despite compatible Story/PNG;
  - CS282 parent substitution rejected;
  - PNG path substitution rejected even with same PNG SHA;
  - paid/nonlocal/network verifier rejected before SemanticPublicationGate;
  - package/base provenance drift rejected.

- `docs/PHASE18_CHANGESET_309_LINEAGE_BOUND_SEMANTIC_PUBLICATION_EVIDENCE.md`.

### Modified

- `engine/intelligence/qwen_image_composed_candidate_semantic_publication_execution.py`
  - schema upgraded from CS284 v1 to v2;
  - execution now validates the lineage-bound evidence envelope before reconstructing gate inputs;
  - replay verification performs the same validation before re-running SemanticPublicationGate;
  - copied final composed PNG/generation context/quality state is replay-checked;
  - no new publication or Golden authority added.

### Deleted

None.

## Gate preservation

Unchanged / still required transitively:

- factual/freshness locks;
- entity and identity verification;
- sentiment neutrality and loser-respect;
- generated-layer and post-composition semantic QA;
- Golden visual-quality adjudication;
- Human Visual Review;
- exact brand and typography review;
- final composed approval;
- final semantic approval;
- repository `SemanticPublicationGate` execution;
- Genuine Golden materialization;
- separate publication readiness.

CS284 v2 still sets `genuine_golden_png_created=false` and `publication_ready=false`.  A gate pass alone cannot create or publish a Golden PNG.

## Testing status

Regression tests were added in-repository. GitHub Actions status for the code-bearing CS309 HEAD must be treated as authoritative; this log must not claim terminal-green until the workflow completes successfully.

## Genuine Golden blocker

No PNG generation was fabricated during CS309. Genuine generation still requires a compatible zero-cost host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the approved compatible QwenImagePipeline/Diffusers runtime, the exact approved already-local Qwen model snapshot, sequential CPU offload support, and sufficient RAM/VRAM proven by a real model load and inference.

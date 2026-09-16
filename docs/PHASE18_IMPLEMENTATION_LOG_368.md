# Phase 18 Implementation Log 368 — CS338 Visual-Quality Request Snapshot Lineage

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Starting branch HEAD reviewed before writes: `1f9ca3c8f5f35914a3d44bd12f69271fb853689b`.

`main` was reviewed read-only and was not merged, rebased, reset, force-updated, or otherwise modified.

## Proven downstream target

The branch tree proves that the first existing continuation after CS337/CS273 toward visual-quality review is:

`engine/intelligence/qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`

This existing CS338 contract consumes an exact, independently reverified CS337 semantic checkpoint, replays its exact CS273 receipt, builds the existing CS274 visual-quality review request, reverifies CS274, and stops before CS275.

Before this change, CS338 dropped the exact Qwen-Image generator snapshot byte lineage that CS367 had already sealed into CS337.

## Modified

### Production

`engine/intelligence/qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`

- advanced CS338 schema from `v1` to `v2`;
- added five-field generator snapshot lineage preservation;
- requires an upstream verified byte inventory;
- validates snapshot digest, file-count, total-byte, and model-revision shapes;
- performs field-by-field comparison against freshly verified CS337 during construction and verification;
- keeps generator identity independent from semantic/visual verifier identity;
- keeps CS275 and every later authority closed.

Production commit: `05b39f617b832789a59c933be3584ff51043a797`.

### Tests

`tests/test_phase18_qwen_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`

- upgraded the CS337 fixture with exact generator snapshot lineage;
- verifies propagation of all five fields;
- verifies rejection of an unverified snapshot before CS274 construction;
- verifies inventory-SHA tampering is rejected after recomputing the outer receipt digest;
- verifies model-revision tampering is rejected after recomputing the outer receipt digest;
- retains semantic rejection, cross-story rejection, exact CS273-to-CS274 binding, premature-authority, and no generation/scoring/network/publication shortcut coverage.

Code-and-test-bearing commit: `c5e72773f08effac2f50225d95e964b700879fe3`.

## Added

`docs/PHASE18_CHANGESET_368_CS338_VISUAL_QUALITY_REQUEST_SNAPSHOT_LINEAGE.md`

`docs/PHASE18_IMPLEMENTATION_LOG_368.md`

Changeset documentation commit: `18d3665f40a052cd77351af80c306a60f7f68d7e`.

## Deleted

None.

## Dependencies

None added or changed.

## Test / CI status

The relevant exact code-and-test SHA is `c5e72773f08effac2f50225d95e964b700879fe3`.

GitHub Actions `Phase 18 Story Intelligence Verification` run `34213091450` / run number `5172` completed successfully on that exact SHA. CS368 is terminal-green.

Terminal-green status grants no runtime, semantic, visual, Human Review, Golden, semantic-publication, publication, or authoritative permission beyond the contract already encoded in the receipts.

## Authority preservation

This change does not execute visual-quality evidence and does not grant Human Review, Golden, semantic-publication, publication, or authoritative status.

The continuation still requires:

- `visual_quality_review_requested = true` only after exact CS337/CS273 semantic passage;
- `visual_quality_review_executed = false`;
- `visual_quality_review_approved = false`;
- `composed_visual_approved = false`;
- `semantic_approved = false`;
- `human_visual_review_approved = false`;
- `golden_quality_approved = false`;
- `genuine_golden_png_created = false`;
- `publication_ready = false`;
- `authoritative = false`.

Factual/freshness, Entity/Identity, sentiment neutrality and loser-respect, zero-cost, semantic-publication, visual-quality, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, and external publication gates remain intact.

## Genuine Golden blocker

No genuine Qwen-Image inference or Genuine Golden PNG is claimed by CS368. The first genuine image still requires a compatible zero-cost execution host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16 support, sufficient proven RAM/VRAM under real Qwen-Image load/inference, the approved runtime, and the exact already-local pinned generator/verifier assets. Paid and network-model fallbacks remain prohibited.

## Remaining gap

CS368 is terminal-green. The next proven branch-local continuation is `qwen_image_visual_quality_review_request_to_evidence_admission.py` (CS339), which consumes CS338 and advances through existing CS275 evidence admission while stopping before CS276. Any further change must preserve exact generator lineage without granting downstream authority prematurely.

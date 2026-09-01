# Phase 18 Implementation Log 306 — Exact Generated-Layer Lineage Coherence

## Scope

Branch: `phase18/story-intelligence` only.

`main` is read-only for this change set and must not be modified, merged, rebased, or force-updated by this work.

Starting Phase 18 HEAD: `606617ec95497d7edd37f7c8b496ec37bf6fec2b` (CS305).

## Review finding

The audit continued downstream from CS266 and confirmed that CS267 already provides the byte-bound human Pixel Identity Review Evidence contract, so a new review-result mechanism was not needed.

The next real production edge is CS268 Generated-Layer QA. CS268 already verified CS264, CS265, and (when required) CS267 and compared story SHA/candidate PNG. However, those independent validations did not require exact chained receipt identity.

This left a narrow cross-run substitution surface:

- a different valid CS264 receipt for the same story/candidate could be supplied alongside a CS265 receipt that had been created from another CS264 receipt;
- a valid CS267 identity result for the same story/candidate could be supplied even if its exact CS266 request was bound to another CS265 receipt.

No factual or identity verdict was automatically fabricated by this gap, but provenance could become internally inconsistent. CS306 closes that surface fail-closed.

## Added

- `tests/test_phase18_qwen_image_generated_layer_lineage_coherence.py`
- `docs/PHASE18_CHANGESET_306_EXACT_GENERATED_LAYER_LINEAGE_COHERENCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_306.md`

## Modified

- `engine/intelligence/qwen_image_canonical_candidate_generated_layer_qa.py`

Changes:

1. Added exact receipt-binding comparison for CS264 → CS265.
2. Added CS266 replay from CS267's byte-bound `source_cs266_request`.
3. Added exact receipt-binding comparison for CS265 → CS266 → CS267.
4. Applied both lineage checks during CS268 construction and CS268 verification.
5. Preserved the existing CS268 schema and receipt payload so downstream consumers are not granted new authority and no unrelated schema migration is forced.

## Deleted

None.

## Testing added

Dedicated CS306 regressions cover:

- accepting the exact repository path/hash/size/receipt-digest binding;
- rejecting same-story cross-run receipt-path substitution;
- rejecting receipt-digest substitution;
- rejecting CS267 whose exact CS266 request points at a different CS265 receipt;
- accepting the exact CS265 → CS266 → CS267 chain.

The existing Phase 18 GitHub Actions suite is used as the repository-wide compatibility test after the branch updates. Its final status is not pre-declared here; the run must complete on the final CS306 HEAD before terminal-green can be claimed.

## Safety / authority preservation

No gate was weakened or bypassed. In particular:

- Fact/Freshness and story binding remain upstream requirements.
- Entity/Identity evidence remains launch-lineage-bound via CS305.
- Human pixel identity approval remains CS266/CS267-bound when required.
- Sentiment neutrality and loser-respect rules are unchanged.
- `$0-local`, offline/local-only generation contracts are unchanged.
- Generated-layer QA still grants no semantic-publication authority.
- Human Visual Review, Exact Brand/Typography, Golden quality, Genuine Golden materialization, and publication readiness remain downstream and closed.

The following remain false at CS268:

- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

## Genuine PNG execution status

CS306 is deterministic control-plane/provenance work. It is not evidence of Qwen model loading or image inference.

A first genuine Golden Visual still requires a compatible zero-cost execution host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized QwenImagePipeline/Diffusers runtime, sequential CPU offload support, the exact approved already-local Qwen snapshot, and sufficient RAM/VRAM demonstrated by an actual model load and inference.

No `canonical_candidate.png`, composed production PNG, or Genuine Golden PNG is claimed by this change set unless such inference actually occurs and passes all downstream gates.

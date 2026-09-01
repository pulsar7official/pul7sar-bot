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
- `tests/test_phase18_qwen_image_canonical_candidate_generated_layer_qa.py` (CI regression repair; no production gate weakening)

Production changes:

1. Added exact receipt-binding comparison for CS264 → CS265.
2. Added CS266 replay from CS267's byte-bound `source_cs266_request`.
3. Added exact receipt-binding comparison for CS265 → CS266 → CS267.
4. Applied both lineage checks during CS268 construction and CS268 verification.
5. Preserved the existing CS268 schema and receipt payload so downstream consumers are not granted new authority and no unrelated schema migration is forced.

CI regression repair:

6. Updated the pre-CS306 CS268 test fixtures so their mocked CS265 receipt now carries the exact byte/hash/size/receipt binding to the mocked CS264 receipt.
7. Added a mocked CS266 request file and exact CS265 binding for human-identity test paths.
8. Updated mocked CS267 evidence so it carries the exact byte-bound `source_cs266_request`, matching the production CS265 → CS266 → CS267 lineage that CS306 now requires.
9. Kept the CS306 lineage enforcement itself unchanged; the repair changes stale tests rather than relaxing `_assert_exact_receipt_binding` or `_verify_required_identity_lineage`.

## Deleted

None.

## Testing added

Dedicated CS306 regressions cover:

- accepting the exact repository path/hash/size/receipt-digest binding;
- rejecting same-story cross-run receipt-path substitution;
- rejecting receipt-digest substitution;
- rejecting CS267 whose exact CS266 request points at a different CS265 receipt;
- accepting the exact CS265 → CS266 → CS267 chain.

The first repository-wide GitHub Actions run on CS306 HEAD `f590f05be833294a50f387f2ee0423d13e8080f6` exposed a compatibility regression in the older CS268 unit-test fixtures during `Syntax and discover validation`:

- 1,940 tests were executed;
- 1 test failed and 5 tests errored;
- all six affected tests were in `tests/test_phase18_qwen_image_canonical_candidate_generated_layer_qa.py`;
- the dedicated CS306 lineage-coherence tests passed;
- the six legacy tests reached `QWEN_GENERATED_LAYER_QA_CS264_CS265_LINEAGE_DRIFT` because their mocked CS265/CS267 receipts predated the newly mandatory exact lineage fields.

This was a test-fixture drift, not evidence that the production lineage check should be weakened. Commit `09ea908a4dd731c817dde61ae3d9f001a16e9000` repairs those fixtures by modeling the exact CS264 → CS265 and CS265 → CS266 → CS267 bindings. The repository-wide suite must complete on the final CS306 repair HEAD before terminal-green is claimed.

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

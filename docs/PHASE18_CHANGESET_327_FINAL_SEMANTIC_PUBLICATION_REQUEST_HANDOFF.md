# Phase 18 Change Set 327 — Final Semantic → Semantic Publication Request Handoff

## Purpose

CS327 removes the remaining manual receipt-selection step between the exact CS326 Final Composed Visual Approval checkpoint and the repository's existing CS282/CS283 contracts.

It does **not** execute `SemanticPublicationGate`, does **not** manufacture CS284 execution evidence, does **not** create a Genuine Golden PNG, and does **not** set `publication_ready=true`.

## Exact continuation

`CS326 exact checkpoint`
→ replay the exact `cs281_receipt` selected by CS326
→ CS282 Final Semantic Approval
→ independent CS282 verification
→ CS283 Semantic Publication Execution Request
→ independent CS283 verification
→ `SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_REQUIRED`

The exact Story SHA and exact composed-PNG repository path/SHA-256/byte-size must remain identical across CS326, CS281, CS282, and CS283.

## Fail-closed authority boundary

CS327 may carry forward only authority actually established by the existing contracts:

- `composed_visual_approved=true` from CS281;
- `semantic_approved=true` from CS282;
- `semantic_publication_execution_requested=true` from CS283.

It requires all of the following to remain closed:

- `semantic_publication_gate_executed=false`;
- `semantic_publication_allowed=false`;
- `genuine_golden_png_created=false`;
- `publication_ready=false`.

If any upstream receipt or exact composed PNG drifts, the continuation fails closed. If a CS283 verifier result attempts to report publication allowance before CS284, CS327 rejects it.

## Zero-cost / network posture

The continuation sets Hugging Face / Transformers / Datasets offline environment flags defensively before downstream deterministic receipt construction. CS282 and CS283 do not require model downloads, and CS327 adds no model-generation or network fallback path.

## Why CS327 stops before CS284

CS284 is intentionally separate because it executes the real repository `SemanticPublicationGate` and requires real external execution evidence containing a serialized `GenerationPackage`, `BaseSceneEvidence`, and zero-cost `VisionVerifierProfile` for the exact story/image lineage. CS327 must not infer or fabricate those inputs.

## Preserved gates

The existing factual/freshness, entity/identity, sentiment and loser-respect, zero-cost, generated-layer, composition, post-composition semantic, Golden-quality, Human Visual Review, exact brand, typography, Final Composed Visual, Final Semantic, and SemanticPublicationGate contracts are not weakened or bypassed.

## Files

- `tools/phase18_continue_composed_approval_to_semantic_publication_request.py`
- `tests/test_phase18_composed_approval_semantic_publication_request_checkpoint.py`
- this document
- `docs/PHASE18_IMPLEMENTATION_LOG_327.md`

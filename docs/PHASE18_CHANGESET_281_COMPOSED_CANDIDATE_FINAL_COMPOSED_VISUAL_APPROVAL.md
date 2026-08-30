# Phase 18 Change Set 281 — Final Composed Visual Approval

## Purpose

CS281 adds a deterministic, fail-closed aggregation gate for final composed-visual authority. It does not perform a new model inspection or manual review. Instead, it requires the exact post-composition semantic QA path (CS273) and the exact final Human/Brand/Typography presentation path (CS280) to agree on the same Story and the same composed PNG bytes.

## Preconditions

CS281 requires CS273 to verify successfully with:

- `composition_executed = true`
- `composed_candidate_bytes_admitted_for_post_composition_qa = true`
- `semantic_inspection_executed = true`
- `hybrid_surface_semantic_qa_approved = true`

CS281 independently requires CS280 to verify successfully with:

- `human_visual_review_approved = true`
- `final_presentation_review_requested = true`
- `final_presentation_review_executed = true`
- `final_presentation_review_evidence_admitted = true`
- `final_presentation_review_approved = true`
- `exact_brand_integrity_approved = true`
- `typography_integrity_approved = true`

Both source receipts must still have final composed, global semantic, Genuine Golden, and publication authorities closed at their respective stages.

## Exact-byte lineage

CS281 re-opens both source receipts and the composed PNG from repository-relative bindings. The Story SHA-256 must match across CS273 and CS280. The composed PNG must match across both paths by repository-relative path, SHA-256, and byte size. Any receipt drift or PNG drift fails closed.

This prevents a semantically inspected image from being combined with Human/Brand/Typography approval for a different image, even when both belong to the same story.

## Authority opened

A valid CS281 receipt establishes only:

- `final_composed_visual_approval_executed = true`
- `composed_visual_approved = true`

It carries forward the already-proven upstream approvals needed to explain why composed authority is valid.

## Authority deliberately not opened

CS281 keeps all of the following false:

- `semantic_approved`
- `genuine_golden_png_created`
- `publication_ready`

Therefore composed-visual approval is not a substitute for final semantic authority or `SemanticPublicationGate`.

## CLI safety

`tools/phase18_approve_composed_candidate_final_visual.py` accepts only source receipt paths, output directory, and repository root. It exposes no manual approval, semantic, Golden, or publication override flag.

## Genuine execution boundary

CS281 does not claim that a production Qwen-Image candidate exists. A Genuine Golden Visual still requires the genuine inference chain on a compatible zero-cost CUDA/BF16 execution host followed by all existing byte-bound gates.

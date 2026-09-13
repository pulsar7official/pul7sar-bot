# Phase 18 Change Set 325 — Human Review → Final Presentation Request

## Purpose

CS325 closes two adjacent control-plane gaps after the CS324 Human Visual Review request without synthesizing any human or presentation verdict.

First, review of the real CS278/CS279 contracts exposed a latent lineage defect: CS279 read `generation_context`, `weighted_score`, and `quality_tier` directly from CS278 even though the CS278 v1 receipt does not copy those fields. A genuine approved CS278 could therefore fail at CS279 with a missing-key error even though its exact CS277 source contains the required values.

CS279 now recovers those values from the exact CS277 receipt already byte-bound inside CS278, replays CS277, and rejects story, PNG, or receipt-digest drift.

Second, a new fail-closed continuation accepts an already-existing CS278 receipt produced from genuinely external Human Visual Review evidence, proves that it belongs to the exact CS277 request selected by CS324, then creates and independently verifies CS279 only.

## New route

`CS324 HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED`
→ external independent Human Visual Review
→ existing CS278 evidence admission
→ **CS325 exact CS277/CS278 replay**
→ CS279 Final Presentation / Brand / Typography review request
→ `FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED`

CS325 does **not** create CS278 evidence, does not infer or alter the human verdict, does not create CS280 presentation evidence, and does not grant final presentation, exact brand, typography, composed, semantic, Genuine Golden, or publication authority.

## Production changes

- Modified `engine/intelligence/qwen_image_composed_candidate_final_presentation_review_request.py` so CS279 recovers generation context and Golden score/tier from the exact CS277 lineage when processing a real CS278 receipt.
- Added `tools/phase18_continue_human_review_to_final_presentation_request.py` to bind one approved pre-existing CS278 receipt to the exact CS277 selected by CS324 and create/replay CS279.

## Regression coverage

- Real CS278 receipt shape without copied context successfully recovers context from exact CS277.
- CS277 story drift is rejected.
- CS277 composed-PNG drift is rejected.
- Rejected Human Visual Review cannot open CS279.
- CS278 must reference the exact CS277 selected by CS324.
- Premature publication/final authority is rejected.
- Successful continuation stops at request authority only.

## Authority boundary

At the successful CS325 checkpoint:

- `golden_quality_approved = true`
- `human_visual_review_approved = true` only because a pre-existing independently admitted CS278 says so
- `final_presentation_review_requested = true`
- `final_presentation_review_executed = false`
- `final_presentation_review_approved = false`
- `exact_brand_integrity_approved = false`
- `typography_integrity_approved = false`
- `composed_visual_approved = false`
- `semantic_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

The next authority-producing step remains genuine external CS280 Final Presentation Review evidence. The GPU/Qwen generation blocker remains independent of this control-plane improvement.

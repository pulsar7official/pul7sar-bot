# Phase 18 Change Set 267 — Canonical Candidate Pixel Identity Review Evidence

## Purpose

CS267 closes the control-plane gap between the byte-bound CS266 pixel-identity review request and any later identity-sensitive visual-quality work. It does **not** perform face recognition, does **not** create a review, and does **not** infer identity automatically.

The only admissible production review method in this Change Set is `manual_source_comparison`. The independently produced review document must be bound to the exact story SHA, exact candidate PNG SHA-256, exact canonical human targets, and the complete set of source identity references already required by CS266.

## Required checks

Every admitted review document must explicitly contain boolean results for all four checks:

- `candidate_subject_matches_canonical_entity`
- `no_identity_substitution`
- `no_ambiguous_or_conflicting_identity`
- `source_backed_reference_evidence_used`

Identity approval is true only when all four are true. A single false result produces a rejected identity review and cannot advance downstream authority.

## Provenance and fail-closed behavior

CS267 replays the CS266 verifier, binds the CS266 request bytes, binds the external review-document bytes, reopens the exact candidate binding through CS266, requires the exact review targets, and requires the exact source-reference set. Any byte drift in the request or review evidence invalidates the CS267 receipt.

The implementation records that general semantic scene inspection is not identity evidence and that the external review is structurally admitted rather than automatically generated.

## Authority boundary

An approved CS267 receipt may set only:

- `pixel_identity_review_executed = true`
- `identity_approved = true`

It cannot set any of the following:

- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

Those gates remain separate and mandatory.

## Zero-cost and generation boundary

CS267 is CPU/control-plane only. It does not load Qwen-Image, execute CUDA, perform inference, or create image pixels. It does not modify the `$0-local` generation contract.

## Files

- `engine/intelligence/qwen_image_canonical_candidate_pixel_identity_review_evidence.py`
- `tests/test_phase18_qwen_image_canonical_candidate_pixel_identity_review_evidence.py`
- `tools/phase18_admit_canonical_candidate_pixel_identity_review_evidence.py`
- `docs/PHASE18_CHANGESET_267_CANONICAL_CANDIDATE_PIXEL_IDENTITY_REVIEW_EVIDENCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_267.md`

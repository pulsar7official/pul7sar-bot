# Phase 18 Change Set 280 — Composed Candidate Final Presentation Review Evidence

## Purpose

CS280 admits an independent manual final-presentation verdict for the exact composed PNG requested by CS279. It exists to preserve a separate, byte-bound approval boundary for exact PUL7SAR brand geometry and typography before final composed/semantic/publication authority can open.

## Preconditions

CS280 re-verifies CS279 and requires:

- `human_visual_review_approved = true`
- `final_presentation_review_requested = true`
- all final-presentation execution/approval fields still false at request time
- the exact CS279 receipt bytes
- the exact `composed_candidate.png` bytes
- the exact repository Brand/Typography policy-source bytes bound by CS279

## External evidence contract

The external JSON must use schema `pul7sar-phase18-composed-candidate-final-presentation-review-v1` and provide:

- exact Story Snapshot SHA-256
- exact composed-candidate PNG SHA-256
- exact CS279 review-request receipt SHA-256
- `review_method = independent_manual_final_presentation_review`
- non-empty `reviewer_id`
- non-empty `review_notes`
- one explicit Boolean result for every CS279 presentation check
- `decision = approve | reject`

Approval is fail-closed: `approve` is accepted only when every required check is true. `reject` must contain at least one failed check.

## Authority

CS280 may open only the presentation-review authorities supported by the admitted evidence:

- `final_presentation_review_executed = true`
- `final_presentation_review_evidence_admitted = true`
- `final_presentation_review_approved = true|false`
- `exact_brand_integrity_approved = true|false`
- `typography_integrity_approved = true|false`

It always keeps these false:

- `composed_visual_approved`
- `semantic_approved`
- `genuine_golden_png_created`
- `publication_ready`

Therefore exact Brand/Typography approval cannot self-promote a candidate into a Genuine Golden PNG or bypass SemanticPublicationGate.

## Provenance guarantees

Verification re-opens the CS279 request, composed PNG, external evidence JSON, and all policy-source bindings. Any byte drift invalidates the receipt. No CLI option exists to override approval, Golden, semantic, or publication state.

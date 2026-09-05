# Phase 18 Change Set 307 — Exact Golden Adjudication Lineage

## Purpose

CS307 repairs the Golden-quality adjudication edge after the CS303 sealed-candidate admission migration and closes the remaining cross-run substitution surface at the first downstream stage that consumes multiple independently supplied receipts.

The production branch is `phase18/story-intelligence` only. `main` remains read-only.

## Review finding

CS269, CS270, CS271, CS272, CS273, CS274 and CS275 were audited downstream from CS306. Each single-source transition reopens and re-verifies its exact upstream receipt and exact candidate/composed PNG bytes.

CS276 is different: it consumes CS263, CS272 and CS275 independently. Two concrete issues were found.

1. Its CS263 contract still expected the pre-CS303 shape: `inference_executed`, top-level `seed`, and `source_cs262_receipt`. A genuine current CS303 admission instead provides `genuine_canonical_inference_executed`, `handoff_sealed`, `candidate_bytes_admitted_for_post_generation_qa`, `source_canonical_inference_receipt`, and `inference_settings`. Therefore a genuine candidate following the current production lineage would fail at Golden adjudication even when all earlier gates passed.
2. CS276 compared story/candidate bytes across the three inputs, but did not prove that the supplied CS263 was the exact admission embedded in the CS272 composition lineage or that the supplied CS272 was the exact admission embedded in the CS275 visual-quality lineage.

## Contract changes

The CS276 receipt schema becomes `pul7sar-phase18-qwen-image-composed-candidate-golden-quality-adjudication-v2`.

CS276 now requires the current sealed admission authority:

- `genuine_canonical_inference_executed=true`
- `handoff_sealed=true`
- `candidate_bytes_admitted_for_post_generation_qa=true`
- `cost_mode=$0-local`
- `network_allowed=false`
- `local_files_only=true`

Generation context is derived from the current admission:

- request identity is anchored to `source_canonical_inference_receipt.receipt_sha256`;
- seed is read only from sealed `inference_settings.seed`;
- legacy `source_cs262_receipt`, top-level `seed`, and `inference_executed` are no longer accepted as authority.

## Exact-lineage replay

Before the existing `GoldenVisualQualitySelector` is executed, CS307 replays:

`CS272 -> CS271 -> CS270 -> CS269 -> CS268 -> CS264 -> exact CS303 candidate admission`

and separately:

`CS275 -> CS274 -> CS273 -> exact CS272 admission`.

The supplied receipts must match those derived bindings by repository-relative path, SHA-256, byte size, and receipt digest. Same-story/same-PNG cross-run substitution therefore fails closed.

The same lineage replay is performed both during receipt construction and during later verification.

## Authority preservation

CS307 does not change any Golden score threshold, blocker definition, selector behavior, identity rule, sentiment rule, factual gate, or publication rule. It only repairs compatibility and provenance.

Even when `golden_quality_approved=true`, CS276 still keeps the following false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `publication_ready`

Human Review, final semantic approval, exact brand/typography review, `SemanticPublicationGate`, Genuine Golden materialization and final publication readiness remain downstream.

## No fabricated visual

This change set is control-plane/provenance work only. It does not claim a Qwen model load, CUDA inference, a genuine canonical candidate, a composed production PNG, or a Genuine Golden PNG.

# Phase 18 Change Set 306 — Exact Generated-Layer Lineage Coherence

## Purpose

Change Set 306 closes a post-generation lineage-substitution surface at the CS268 Generated-Layer QA edge.

Before CS306, CS268 independently verified a supplied CS264 Semantic Base QA receipt and a supplied CS265 Identity Requirement receipt, then required matching story SHA and candidate PNG. For a required human identity it also independently verified CS267 Pixel Identity Review Evidence and required the same story/candidate plus an approved identity verdict.

Those checks were strong but did not prove that the separately supplied receipts belonged to the exact same chained run. A second valid CS264 receipt for the same story/candidate could be paired with a CS265 that had actually been created from a different CS264 receipt. Likewise, a valid CS267 result could come through a CS266 request bound to a different CS265 receipt for the same story/candidate.

CS306 makes exact receipt lineage coherence mandatory inside the production CS268 engine.

## Contract added

CS268 now requires:

1. The supplied CS265 receipt's `source_cs264_receipt` must equal the exact repository-relative path, SHA-256, byte size, and receipt SHA-256 of the supplied CS264 receipt.
2. When pixel-identity review is required, CS267's byte-bound `source_cs266_request` is reopened and replayed through the existing CS266 verifier.
3. That exact CS266 request's `source_cs265_receipt` must equal the exact repository-relative path, SHA-256, byte size, and receipt SHA-256 of the supplied CS265 receipt.
4. Any path drift, byte drift, receipt-digest drift, symlink/path escape, or cross-run substitution fails closed.

This is enforced both when CS268 is created and when a CS268 receipt is later verified.

## Authority boundary

CS306 changes lineage admissibility only. It does not grant or weaken factual, identity, sentiment, semantic-publication, visual-quality, Human Review, branding, Golden Visual, or publication authority.

A generated-layer QA receipt continues to keep these downstream authorities closed:

- `semantic_approved=false`
- `human_visual_review_approved=false`
- `genuine_golden_png_created=false`
- `golden_quality_approved=false`
- `publication_ready=false`

Identity approval remains possible only through the already-established CS266/CS267 human pixel-identity evidence path when CS265 requires it.

## Zero-cost / execution boundary

CS306 performs deterministic repository-local verification only. It introduces no network call, paid service, model download, GPU inference, or alternative generation path. The existing `$0-local` generation lineage remains upstream and unchanged.

## Regression coverage

A dedicated CS306 regression module checks:

- exact receipt binding is accepted;
- same-story cross-run path substitution is rejected;
- receipt-digest substitution is rejected;
- CS267 evidence whose CS266 request is bound to another CS265 receipt is rejected;
- the exact CS265 → CS266 → CS267 chain is accepted.

The full Phase 18 CI remains the final compatibility check for the complete repository.

## Remaining path to the first Genuine Golden Visual

After a genuine CUDA/BF16 Qwen candidate exists, the protected path is now:

`sealed candidate → CS303 exact-byte admission → CS304 semantic QA → CS305 launch-lineage identity requirement → CS266/267 pixel identity review when required → CS268 exact-lineage generated-layer QA → composition/generated-layer/visual-quality gates → Human Review → Exact Brand/Typography → SemanticPublicationGate → Genuine Golden materialization → publication readiness`.

CS306 does not fabricate or substitute the missing genuine GPU inference.

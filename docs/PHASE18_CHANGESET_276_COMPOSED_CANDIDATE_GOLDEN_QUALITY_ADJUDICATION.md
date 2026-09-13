# Phase 18 Change Set 276 — Composed Candidate Golden Quality Adjudication

## Purpose

CS276 closes the provenance gap between CS275 visual-quality evidence and the existing `GoldenVisualQualitySelector` without inventing generation context.

`GoldenVisualEvaluation` requires `request_id`, `seed`, `scores`, and `blockers`. CS275 already owns byte-bound scores/blockers, but neither a free CLI request id nor an arbitrary seed is acceptable. CS276 therefore derives both only from already verified generation provenance.

## Authentic generation context

CS262 records the exact seed in its successful one-shot inference receipt. CS263 re-verifies CS262 and carries that seed plus the exact CS262 receipt digest and canonical-candidate PNG binding.

CS272 carries both the source canonical-candidate PNG binding and the composed-candidate PNG binding. CS275 carries the exact composed PNG whose admitted manual visual-quality evidence supplies the score/blocker set.

CS276 requires and re-verifies all three receipts:

- CS263 — proves successful genuine canonical inference context and seed;
- CS272 — proves the exact CS263 base candidate is the source of composition;
- CS275 — proves the reviewed composed PNG and its complete score/blocker evidence.

The base PNG bindings from CS263/CS272 must match in repository path, SHA-256, byte size and dimensions. The composed PNG bindings from CS272/CS275 must match the same way. Story SHA must match across all three.

## Selector request id

The existing quality contract needs a unique non-empty `request_id`, but CS262 predates that field. CS276 does not accept a request id from the caller. It deterministically constructs:

`qwen-cs262-<exact CS262 receipt_sha256>`

This is an identifier for the exact successful inference receipt, not a fabricated generation claim. Changing the CS262 inference receipt changes the selector request id and invalidates the lineage.

## Golden authority

CS276 invokes the existing `GoldenVisualQualitySelector` and `GoldenVisualEvaluation`; it does not duplicate or alter the 8.5 Golden floor, 8.0 core floor, 9.0 Elite target, score weights, or blocker semantics.

The selector may establish:

- `golden_quality_selector_executed=true`;
- `golden_quality_approved=true|false` according to the existing contract;
- `quality_tier=below_golden|golden|elite`.

Even a passing Golden-quality result must retain:

- `composed_visual_approved=false`;
- `semantic_approved=false`;
- `human_visual_review_approved=false`;
- `genuine_golden_png_created=false`;
- `publication_ready=false`.

Therefore Golden scoring cannot bypass Human Review, final semantic approval, exact PUL7SAR brand/typography verification, or `SemanticPublicationGate`.

## Fail-closed cases

CS276 rejects cross-story inputs, base-candidate lineage drift, composed-candidate lineage drift, missing/invalid CS262 digest context, invalid seed, altered source receipt bytes, altered source receipt digests, incomplete upstream authority, premature downstream authority, altered adjudication verdicts, and reuse of an existing output directory.

The production CLI accepts only receipt paths and an output path. It has no `--request-id`, `--seed`, `--score`, or `--blocker` inputs.

## Genuine Golden PNG status

CS276 is control-plane/post-review adjudication. It does not execute Qwen Image inference, create a production candidate, conduct Human Review, or create a Genuine Golden Visual PNG. A real Golden visual remains impossible until a compatible zero-cost CUDA/BF16 runtime executes the genuine upstream CS262 path and the resulting pixels pass all later gates.

# Phase 18 — Change Set 349

## Semantic Publication Gate → Genuine Golden Materialization

CS349 connects the current Phase 18 continuation chain to the existing CS285 Genuine Golden materialization contract without creating any new publication authority and without generating or mutating image pixels.

## Exact lineage

`CS348 checkpoint -> independent CS348 replay -> exact CS348-selected CS284 replay -> require repository SemanticPublicationGate allowed result -> existing CS285 exact-byte materialization -> independent CS285 replay -> STOP before publication readiness`.

## Admission requirements

CS349 is fail-closed unless all of the following remain true on the exact replayed lineage:

- Final Composed Visual approval is present.
- Final Semantic approval is present.
- Semantic publication execution was requested.
- The repository SemanticPublicationGate actually executed.
- `semantic_publication_allowed=true` was produced by CS284 itself.
- CS284 has no semantic-publication failures.
- The same story snapshot and exact same composed-PNG binding survive the CS348/CS284 lineage.
- CS348 and CS284 both still report `genuine_golden_png_created=false` and `publication_ready=false` before CS285.

A CS348 or CS284 rejection cannot reach CS285.

## Existing CS285 reuse

CS349 calls `qwen_image_genuine_golden_materialization.py` rather than replacing it. CS285:

- re-verifies the exact CS284 receipt;
- requires CS284 publication allowance;
- reopens the exact composed PNG;
- validates PNG signature, chunk framing, CRCs, IHDR dimensions, and terminal IEND;
- copies the exact source bytes to `genuine_golden_visual.png`;
- verifies byte identity and immutable lineage;
- sets Genuine Golden creation only for that exact-byte artifact;
- leaves publication readiness false.

CS349 independently re-verifies the resulting CS285 receipt and requires the Golden PNG SHA-256 and byte size to match the source composed PNG.

## Authority boundary

A successful CS349 may record:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true`
- `byte_identity_preserved=true`
- `genuine_golden_png_created=true`

It must still record:

- `publication_ready=false`
- `authoritative=false`

Therefore CS349 cannot publish, upload, or grant downstream publication readiness.

## Preserved gates

CS349 does not weaken or bypass factual/freshness verification, entity/identity verification, sentiment neutrality and loser-respect, zero-cost/offline constraints, semantic QA, visual-quality review, Golden-quality adjudication, Human Visual Review, exact Brand/Typography Presentation Review, Final Composed approval, Final Semantic approval, or SemanticPublicationGate execution.

## Genuine-image caveat

CS349 is a continuation/materialization contract, not an image generator. A production Genuine Golden PNG can only exist after a genuine Qwen candidate has been generated in the approved zero-cost compatible runtime and has passed the complete upstream chain. Test fixtures that exercise the contract are not production Golden Visuals.

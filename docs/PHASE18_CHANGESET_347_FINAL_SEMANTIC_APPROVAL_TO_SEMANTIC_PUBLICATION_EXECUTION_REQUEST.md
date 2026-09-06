# Phase 18 Change Set 347 — Final Semantic Approval → Semantic Publication Execution Request

## Purpose
CS347 connects the current exact CS346 checkpoint to the repository's existing CS283 SemanticPublicationGate execution-request contract without executing or bypassing the gate.

## Exact continuation
`CS346 -> exact CS282 -> existing CS283 request -> STOP`

CS347 independently replays CS346, reopens and independently replays the exact CS282 receipt selected by CS346, invokes `build_semantic_publication_execution_request`, and independently verifies the resulting CS283 receipt.

## Fail-closed requirements
- CS346 must retain all upstream Golden-quality, Human Review, Presentation/Brand/Typography, Final Composed, and Final Semantic approvals.
- CS346 and CS282 must retain `genuine_golden_png_created=false` and `publication_ready=false`.
- The exact CS282 receipt hash, Story SHA-256, and composed PNG binding must match.
- CS283 must bind the same Story and composed PNG and must remain request-only.

## Authority boundary
A successful CS347 receipt means only that independent SemanticPublicationGate execution has been requested. It explicitly requires:

- `semantic_publication_execution_requested=true`
- `semantic_publication_gate_executed=false`
- `semantic_publication_allowed=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

CS347 does not execute `SemanticPublicationGate`, does not fabricate the evidence envelope required by CS284, does not mutate pixels, does not perform model inference, and does not create or publish a Golden PNG.

## Existing downstream contract
The next existing contract is CS284 v2, `qwen_image_composed_candidate_semantic_publication_execution.py`. It validates lineage-bound external execution evidence and runs the repository `SemanticPublicationGate`. Even gate success leaves Genuine-Golden creation and publication readiness closed for downstream authority.

After a genuine allowed CS284 result, the separate existing `qwen_image_genuine_golden_materialization.py` contract remains downstream.

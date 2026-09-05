# Phase 18 Change Set 348 — Semantic Publication Request → Gate Execution

## Purpose
CS348 connects the exact CS347 Semantic Publication Execution Request to the repository's existing CS284 v2 `SemanticPublicationGate` execution contract without manufacturing a publication decision or granting Golden/publication authority.

## Exact continuation
`CS347 -> exact CS283 -> lineage-bound execution evidence -> existing CS284 v2 -> STOP`

CS348 independently replays CS347, reopens and independently verifies the exact CS283 request selected by CS347, binds the supplied execution-evidence file inside the repository, invokes the existing CS284 v2 execution contract exactly once, independently verifies the resulting CS284 receipt, and preserves the repository gate decision exactly.

## Fail-closed requirements
- CS347 must still be request-only: Final Composed and Final Semantic approvals true, request true, gate execution false, allowed false, Genuine Golden false, publication readiness false, authoritative false.
- The exact CS283 receipt selected by CS347 must reopen byte-for-byte and its receipt hash must match.
- Story SHA-256 and composed-PNG binding must remain identical across CS347, CS283, and CS284.
- Execution evidence must be a non-empty repository-bound regular file and must remain byte-identical.
- CS284 itself reasserts exact CS283/CS282/PNG/generation-context lineage and zero-cost/offline verifier requirements before evaluating `SemanticPublicationGate`.
- CS348 does not accept any external `allowed` override. The `semantic_publication_allowed` value is copied only from the independently verified CS284 decision.
- A CS284 rejection remains a rejection. CS348 does not retry, upgrade, or reinterpret it.

## Authority boundary
A successful CS348 receipt means that the repository SemanticPublicationGate was genuinely executed from admitted evidence. It may record either `semantic_publication_allowed=true` or `false` according to CS284, while always requiring:

- `semantic_publication_gate_executed=true`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

CS348 does not generate pixels, load Qwen, materialize a Golden PNG, upload media, or publish anything.

## Downstream
Only a genuinely allowed CS284 result may continue toward the repository's separate `qwen_image_genuine_golden_materialization.py` contract. That downstream stage must still verify its own exact lineage and authority requirements. A rejected CS284 result is terminal for that candidate.

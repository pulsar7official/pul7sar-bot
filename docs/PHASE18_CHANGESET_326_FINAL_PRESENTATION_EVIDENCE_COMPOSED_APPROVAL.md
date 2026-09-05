# Phase 18 — Change Set 326

## Final Presentation Evidence → Final Composed Visual Approval

CS326 removes one remaining manual receipt-selection gap between the CS325 final-presentation request checkpoint, genuinely external CS280 presentation evidence, and deterministic CS281 final-composed aggregation.

## Goal

Advance one exact composed candidate only when all of the following remain true:

1. CS325 is the expected non-authoritative checkpoint and is still waiting for final presentation evidence.
2. The exact CS279 request named by CS325 re-verifies against the same Story and composed PNG bytes.
3. Final presentation evidence is supplied externally and is admitted only by the existing CS280 contract.
4. A rejected CS280 verdict stops the candidate. CS281 is never built after rejection.
5. An approved CS280 verdict must also approve exact brand integrity and typography integrity.
6. Before CS281 is allowed to execute, the exact review lineage is replayed back through CS279 → CS278 → CS277 → CS276 → CS275 → CS274 → CS273.
7. CS281 must independently re-verify and approve the exact same composed PNG.

## New orchestration

`tools/phase18_continue_final_presentation_evidence_to_composed_approval.py`

Inputs:

- one exact CS325 checkpoint;
- one pre-existing repository-local external final-presentation review file;
- a new repository-local output directory.

The orchestrator does **not** author, infer, repair, or reinterpret the review. It passes the external file to CS280 unchanged.

### Approved route

`CS325 → exact CS279 → external manual review → CS280 → exact lineage replay to CS273 → CS281`

Resulting checkpoint status:

`FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL`

At this point only `composed_visual_approved=true` is newly legitimate. Global semantic approval, Genuine Golden materialization, and publication remain false.

### Rejected route

`CS325 → exact CS279 → external manual review → CS280 rejection → stop`

Resulting checkpoint status:

`COMPOSED_CANDIDATE_REJECTED_BY_FINAL_PRESENTATION_REVIEW`

No CS281 receipt is created.

## Preserved authority boundaries

CS326 does not change Fact/Freshness, Entity/Identity, sentiment neutrality, loser-respect, zero-cost/local-only, semantic QA, visual-quality thresholds, Human Visual Review, presentation-review rules, Final Semantic Approval, SemanticPublicationGate, Genuine Golden materialization, or publication readiness.

Even after an approved CS281:

- `semantic_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`
- checkpoint `authoritative = false`

CS280 remains an independent manual review contract. CS326 cannot synthesize its reviewer identity, notes, per-check results, or decision.

## Regression coverage

`tests/test_phase18_final_presentation_evidence_composed_approval_checkpoint.py` covers:

- approved external CS280 evidence continuing to exact CS281;
- rejected CS280 evidence preventing CS281 execution;
- composed-PNG byte drift failing closed;
- final semantic/publication authority remaining closed;
- no Qwen-Image generation path in the orchestrator;
- no manual presentation verdict string authored by the orchestrator.

## Remaining path

After CS326 approval, the next legitimate stage is Final Semantic Approval. That stage must remain distinct from final composed approval and must continue to preserve lineage-bound SemanticPublicationGate semantics before CS285 Genuine Golden materialization.

This change set does not claim that a real composed candidate or Genuine Golden PNG has been produced.

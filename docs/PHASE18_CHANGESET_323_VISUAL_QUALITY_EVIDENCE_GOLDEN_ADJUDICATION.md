# Phase 18 Change Set 323 — Visual-Quality Evidence to Golden Adjudication

## Purpose

CS323 closes the operator-wiring gap after CS322 without fabricating visual judgment. CS322 ends at an exact byte-bound CS274 visual-quality review request. CS323 accepts only a repository-local external review document that already satisfies the CS275 `manual_visual_quality_review` contract, admits it through the existing CS275 verifier, and then executes the existing CS276 v2 Golden-quality adjudication against the exact canonical/composed lineage.

## Production entry point

`tools/phase18_continue_visual_quality_evidence_to_golden_adjudication.py`

Required inputs:

- one exact CS322 checkpoint in `VISUAL_QUALITY_REVIEW_EVIDENCE_REQUIRED` state;
- one explicit repository-local external manual visual-quality review document;
- one explicit current CS303 canonical candidate admission receipt;
- one new repository-local output directory.

The candidate-admission path remains explicit, but CS276 v2 independently proves that it is the exact admission derived from the CS272 composition lineage. A wrong admission therefore cannot be accepted.

## Exact continuation

The tool performs this fail-closed sequence:

1. validate the non-authoritative CS322 checkpoint and require its semantic pass / CS274 request state;
2. resolve and independently replay the exact CS272 and CS274 receipts referenced by CS322;
3. independently replay the supplied CS303 canonical candidate admission and preserve `$0-local`, `network_allowed=false`, and `local_files_only=true`;
4. require exact Story SHA, canonical candidate and composed-candidate byte bindings across CS322 / CS272 / CS274 / CS303;
5. pass the external review file to CS275 without modifying or synthesizing its scores, blockers, reviewer identity, method, or notes;
6. independently replay the CS275 evidence receipt;
7. invoke CS276 v2 with the exact CS303, CS272 and newly admitted CS275 receipts;
8. independently replay CS276 and re-check Story/canonical/composed lineage;
9. emit a non-authoritative orchestration checkpoint preserving the CS276 Golden-quality result exactly.

## Human evidence boundary

CS323 does not perform visual review. It does not create a reviewer ID, notes, score fields, blocker fields, or the `manual_visual_quality_review` method value. Those values must already exist in the external review document, and CS275 remains the authority that validates them against the exact CS274 request and exact composed PNG bytes.

Semantic QA is not accepted as substitute evidence for visual-quality scoring.

## Golden-quality boundary

CS276 is the only component allowed to apply `GoldenVisualQualitySelector` in this continuation. CS323 never forces a pass and never converts a rejected evaluation into approval.

When CS276 returns `golden_quality_approved=true`, CS323 reports:

`GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW`

When CS276 returns false, CS323 reports:

`COMPOSED_CANDIDATE_REJECTED_BY_GOLDEN_QUALITY`

The orchestration checkpoint itself remains `authoritative=false`.

## Authorities that remain closed

Regardless of Golden-quality outcome, CS323 requires these authorities to remain false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `publication_ready`

A Golden-quality pass therefore is not Human Visual Review, final composed approval, final semantic approval, Genuine Golden materialization, or publication readiness.

## Zero-cost / network policy

CS323 performs no generation or model inference. It reasserts local-only Hugging Face/Transformers/Datasets environment flags and requires the canonical admission to preserve the `$0-local`, network-forbidden contract.

## Regression contract

`tests/test_phase18_visual_quality_evidence_golden_adjudication_checkpoint.py` covers:

- exact CS322 → CS272/CS274 continuation;
- exact external evidence → CS275 → CS276 continuation;
- preservation of a Golden pass without final authority escalation;
- preservation of a Golden rejection without override;
- cross-story, canonical-candidate and composed-byte drift guards;
- `$0-local`/local-only admission requirements;
- independent CS275 and CS276 replay;
- absence of Qwen-Image generation, publication shortcuts, or human-review synthesis.

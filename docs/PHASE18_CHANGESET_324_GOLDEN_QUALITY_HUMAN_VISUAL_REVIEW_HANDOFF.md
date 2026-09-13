# Phase 18 Change Set 324 — Golden Quality → Human Visual Review Request

## Objective

Remove the remaining operator-wiring gap between an exact CS323 Golden-quality pass and the existing CS277 Human Visual Review request, without automating or fabricating the Human Visual Review itself.

## Baseline

- Branch: `phase18/story-intelligence`
- Baseline HEAD: `86ee08809eed818979890ea83b71b5db5a7399cf`
- Baseline CS323 Story Intelligence verification: terminal `success` (`Phase 18 Story Intelligence Verification #4675`).
- `main` is out of scope and must never be modified by this change set.

## Problem

CS323 already binds genuine external manual visual-quality evidence into CS275 and executes/replays CS276 Golden-quality adjudication. On a Golden-quality pass it stops with:

`GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW`

The repository already has CS277, which re-verifies CS276 and creates a byte-bound request for independent Human Visual Review. However, the transition from CS323 to the exact CS277 request still required the operator to manually select the CS276 receipt.

That selection is unnecessary provenance risk. The system should use the exact CS276 receipt already recorded by CS323, while still stopping before any Human Visual Review verdict.

## Implementation

Added `tools/phase18_continue_golden_quality_to_human_visual_review_request.py`.

The continuation:

1. Requires an exact repository-local CS323 checkpoint.
2. Requires the CS323 state to be `GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW`.
3. Requires visual-quality evidence and Golden-quality adjudication to have actually passed.
4. Resolves only the `cs276_receipt` recorded by that CS323 checkpoint.
5. Independently replays CS276.
6. Checks exact Story SHA, source-candidate binding, and composed-candidate byte binding against CS323.
7. Builds CS277 from that exact CS276 receipt.
8. Independently replays CS277.
9. Re-checks Story and exact composed PNG continuity.
10. Emits a non-authoritative checkpoint with status `HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED`.

## Deliberate stop boundary

CS324 does **not**:

- execute Human Visual Review;
- create CS278 Human Visual Review evidence;
- invent a reviewer ID, notes, checklist result, approval, or rejection;
- modify or render image pixels;
- grant composed-visual approval;
- grant final semantic approval;
- create a Genuine Golden PNG;
- authorize publication.

The resulting state remains:

- `golden_quality_approved = true`
- `human_visual_review_requested = true`
- `human_visual_review_executed = false`
- `human_visual_review_approved = false`
- `composed_visual_approved = false`
- `semantic_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

## Gate preservation

CS324 does not weaken or replace:

- factual/freshness gates;
- entity/identity gates and manual identity comparison where required;
- sentiment neutrality and loser-respect requirements;
- `$0-local` / no-network generation policy;
- Semantic Base and Hybrid-Surface QA;
- Generated-Layer QA;
- deterministic composition ownership and byte admission;
- Golden Visual Quality thresholds;
- independent Human Visual Review;
- exact brand/logo/typography verification;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- Genuine Golden materialization or publication readiness.

## Tests

Added `tests/test_phase18_golden_quality_human_visual_review_request_checkpoint.py` covering:

- exact Golden pass → exact CS277 request;
- no final authority after CS277 request creation;
- Golden rejection cannot open Human Visual Review;
- cross-story drift fails closed;
- composed-byte drift fails closed;
- source-level guardrails against CS278/verdict fabrication, model generation, or publication shortcuts.

## Remaining path

After a genuine candidate reaches this checkpoint:

`CS276 Golden pass → CS324/CS277 request → genuine independent human review → CS278 evidence → exact brand/typography and final composed/semantic gates → SemanticPublicationGate → CS285 Genuine Golden PNG → CS286 readiness`

The project is still blocked from producing the first genuine generated candidate in the currently available execution environment if compatible CUDA/BF16 Qwen-Image execution is unavailable. CS324 does not fabricate any PNG to hide that blocker.

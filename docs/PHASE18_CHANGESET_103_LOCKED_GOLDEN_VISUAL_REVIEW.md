# PUL7SAR Phase 18 — Change Set 103: Locked Golden Visual Review

## Purpose
Wire the exact SHA-locked pitch artifact that passed HYBRID_SURFACE semantic/alignment review into the Golden 8.5/9.0 quality gate.

Before this change, the generic Golden batch review tooling was tied to PNG paths from the original generation batch. The newer football flow had already moved downstream to a manually selected, SHA-locked, semantically approved pitch variant. Without a dedicated bridge, the Golden quality step could accidentally score the wrong artifact.

## Added

### `engine/intelligence/locked_golden_visual_review.py`
- Requires a `FOOTBALL_PITCH_SEMANTIC_REVIEW_COMPLETE` receipt.
- Requires `semantic_approved=true`.
- Requires `publication_ready=false` and `golden_quality_approved=false` upstream.
- Requires all protected downstream gates to remain unwaived.
- Re-hashes the exact locked PNG and rejects byte drift.
- Builds a human-review template with null scores and the complete `GoldenVisualBlockers` schema.
- Revalidates candidate, request ID, seed, PNG path and SHA before accepting human scores.
- Requires exact score and blocker schemas; deleting a blocker fails closed.
- Applies the existing `GoldenVisualEvaluation` thresholds and hard-blocker precedence.
- Even an approved Golden result remains `publication_ready=false`.

### `tools/phase18_build_locked_golden_review.py`
Builds the human review template from an approved locked-pitch semantic receipt. No scores are fabricated.

### `tools/phase18_review_locked_golden.py`
Evaluates the completed human review against the same semantic receipt and exact locked PNG bytes. Returns non-zero when the candidate does not meet Golden quality.

### `tests/test_phase18_locked_golden_visual_review.py`
Regression coverage proves:
- semantic failure blocks template creation;
- template is bound to the exact locked PNG SHA;
- a clean 8.7 review may reach Golden quality but never publication readiness;
- generated platform branding rejects a 9.9-scored image;
- missing hard-blocker fields fail closed;
- PNG tampering after semantic review is rejected;
- request identity drift is rejected.

## Architecture after Change Set 103
`Genuine FLUX Candidate 1 -> Base semantic/layer gate -> CPU pitch diagnostics -> explicit human preset review -> SHA-locked pitch selection -> locked-pitch Qwen HYBRID_SURFACE review -> SHA-bound Locked Golden Visual review -> exact approved brand/typography composition -> SemanticPublicationGate -> final publication readiness`

## Safety invariants unchanged
- `main` / `main.py` untouched.
- Fact Lock and identity verification remain fail-closed.
- Sentiment/neutrality unchanged.
- `$0-local`, FLUX.2 Klein 4B, BF16, seeds/canvases unchanged.
- SemanticPublicationGate remains mandatory.
- Golden thresholds remain 8.5 minimum / 9.0+ elite; hard blockers override scores.
- Generated PUL7SAR branding remains forbidden.
- Exact approved brand and typography asset integrity remains required before final publication composition.
- No GPU PNG, paid provider, secret, model weights, font files, fake benchmark or fabricated score is introduced.

## Remaining external blocker
A genuine Golden Hybrid v5 Candidate 1 still needs a compatible CUDA/BF16 host. This change does not fabricate that image; it makes the post-GPU path executable against the exact bytes that survive pitch selection and semantic review.

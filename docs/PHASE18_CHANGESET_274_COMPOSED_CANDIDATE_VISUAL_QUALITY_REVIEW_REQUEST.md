# Phase 18 — Change Set 274
## Composed Candidate Visual Quality Review Request

### Purpose
CS274 creates the immutable handoff between the approved CS273 post-composition semantic surface and later visual-quality evidence. It does **not** generate Visual Critic scores and does **not** grant Golden, Human Review, semantic-publication, or publication authority.

### Why this boundary exists
The repository already contains `engine/intelligence/golden_visual_quality.py`, including `GoldenVisualScores`, `GoldenVisualBlockers`, `GoldenVisualEvaluation`, `GoldenVisualQualitySelector`, and the Golden/elite floors. That contract evaluates supplied scores; it is not itself an image critic. Treating CS273 semantic evidence as those scores would fabricate visual-quality evidence.

CS274 therefore binds the exact image and the exact quality contract before any later score evidence may be admitted.

### Required upstream state
The source CS273 receipt must verify successfully and must assert all of the following:

- `composition_executed = true`
- `composed_candidate_bytes_admitted_for_post_composition_qa = true`
- `semantic_inspection_executed = true`
- `hybrid_surface_semantic_qa_approved = true`

The following downstream authorities must still be false upstream:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

### Byte-bound inputs
The request reopens and binds:

1. the exact CS273 receipt;
2. the exact `composed_candidate.png` referenced by CS273;
3. the exact repository bytes of `engine/intelligence/golden_visual_quality.py`.

Repository-relative path, SHA-256, and byte size are recorded for bound files. Symlinks and repository escape are rejected.

### Quality-contract binding
Rather than duplicating the Golden contract, CS274 obtains score-field and blocker-field names from the existing dataclasses and records the existing thresholds:

- `GOLDEN_WEIGHTED_FLOOR`
- `GOLDEN_CORE_FLOOR`
- `ELITE_TARGET`

The source file containing the evaluation formula is itself byte-bound. Contract drift therefore invalidates the request.

### Authority model
CS274 may set only:

- `visual_quality_review_requested = true`

It must keep all of these false:

- `visual_quality_review_executed`
- `visual_quality_review_approved`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

### Fail-closed rules
Verification rejects at least:

- a failed or altered CS273 receipt;
- candidate-byte drift;
- story binding drift;
- Golden-quality-contract source drift;
- a rehashed receipt attempting to grant downstream authority;
- incomplete review requirements;
- an existing output directory.

### What CS274 explicitly does not do
It does not:

- infer scores from Qwen2.5-VL semantic QA;
- define an unverified automatic Visual Critic;
- execute Human Review;
- mark a PNG Golden;
- grant global semantic publication approval;
- grant publication readiness;
- weaken factual, identity, sentiment, zero-cost, layer-ownership, or existing visual-quality gates.

### Next safe step
Admit **actual** visual-quality review evidence that is bound to this request and exact composed PNG, validate every score/blocker field, and evaluate it through the existing `GoldenVisualQualitySelector`. Human Review and publication authority must remain separate after that evaluation.

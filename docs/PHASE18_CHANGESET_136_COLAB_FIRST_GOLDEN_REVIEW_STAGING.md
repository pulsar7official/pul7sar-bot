# Phase 18 Change Set 136 — Colab First Golden Review Staging

## Goal

Reduce the remaining manual gap between the first genuine CUDA/BF16 Candidate 1 generation and the exact human visual review that must precede Golden scoring.

The repository already had the required trusted pieces separately:

- `phase18_first_png.py` for the genuine Candidate 1 path;
- first-PNG provenance postflight;
- Hybrid v5 handoff;
- strict BASE_SCENE and HYBRID_SURFACE semantic continuation;
- a SHA-bound Hybrid human-review bundle;
- a SHA-bound human-review decision template.

The remaining operational risk was that a Colab/GPU session still required several manual commands after the first PNG. A wrong file, stale receipt or accidental seed change could therefore increase review friction even though all underlying gates already existed.

## Added

### `tools/phase18_colab_first_golden_review.py`

A strict orchestration wrapper that runs only Candidate 1 through the current approved chain:

`Candidate 1 -> provenance -> Hybrid handoff -> BASE_SCENE/HYBRID_SURFACE QA -> human-review bundle -> human-review template`

It does not implement a new generator and does not bypass any existing contract. `phase18_first_png.py` remains the owner of repository integrity, CUDA/BF16 qualification, Qwen preflight, exact FLUX snapshot handling, queue execution and first-PNG provenance postflight.

The new wrapper then:

1. binds the successful Candidate 1 output into the canonical Golden Hybrid v5 handoff;
2. requires BASE_SCENE semantic/layer ownership approval;
3. requires deterministic football Hybrid composition and HYBRID_SURFACE semantic/alignment approval;
4. prepares the exact SHA-bound base/Hybrid PNG review bundle;
5. builds but never fills or evaluates the human decision template;
6. emits `first-golden-human-review-packet.json` with SHA-256 for both review images;
7. keeps `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`;
8. explicitly keeps Seeds 2-4 unauthorized.

### `tests/test_phase18_colab_first_golden_review.py`

Regression coverage locks:

- the branch to `phase18/story-intelligence`;
- Candidate 1 only;
- trusted-step ordering;
- semantic approval before human-review staging;
- no automatic human decision;
- no automatic Golden evaluation;
- SHA-bound review artifacts inside the repository;
- `$0-local` and publication fail-closed behavior.

## Modified

No existing runtime file was modified in this change set.

## Deleted

Nothing.

## Gates preserved

No weakening was introduced for:

- Fact Lock;
- entity/identity verification;
- sentiment and losing-side neutrality;
- `$0-local` zero paid-provider policy;
- FLUX.2 Klein 4B lock;
- native BF16 lock;
- seed/canvas locks;
- generated text/branding/score/crest/geometry exclusions;
- Qwen BASE_SCENE and HYBRID_SURFACE semantic inspection;
- deterministic football geometry ownership;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

The wrapper stops before any human acceptance, Golden scoring, exact-brand publication composition or publication authorization.

## Result

A compatible Colab or self-hosted GPU host can now use one Phase 18 command to reach the exact human-review-ready Candidate 1 packet without spending Seeds 2-4 or manually chaining the post-generation tools.

No genuine GPU PNG is claimed by this change set because the repository-development environment used for this work does not provide a compatible NVIDIA CUDA/BF16 execution host.

# Phase 18 Change Set 133 — SHA-bound Hybrid Human Review Bundle

## Purpose

Change Set 132 can produce the first genuine deterministic Hybrid PNG that has passed both BASE_SCENE layer ownership inspection and HYBRID_SURFACE semantic/alignment inspection. The remaining visual decision is intentionally human: verify that the deterministic pitch actually looks photographic, integrated and premium before any Golden-quality score or preset lock is allowed.

The gap was that the reviewer still had to locate the correct base and Hybrid artifacts manually. That creates unnecessary risk of reviewing a stale or different PNG.

## Added

### `engine/intelligence/hybrid_human_review_bundle.py`

Builds a tamper-evident review package from a successful strict Hybrid semantic continuation. It:

- requires Candidate 1;
- requires `FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY`;
- requires BASE_SCENE and HYBRID_SURFACE approval;
- requires deterministic artifact integrity;
- replays SHA-256 for both the original FLUX base and the semantic-approved Hybrid PNG;
- cross-checks those hashes against the artifact-integrity receipt;
- copies both PNGs byte-for-byte into one stable review directory;
- replays SHA-256 after copying;
- records a review manifest;
- requires explicit human review;
- performs no automatic preset selection;
- cannot grant Golden quality or publication authority.

### `tools/phase18_prepare_hybrid_human_review.py`

CPU-only command that consumes the strict continuation receipt and writes the review package plus a receipt.

Default review directory:

`output/phase18_visual_proof/hybrid-human-review/candidate-01/`

Default receipt:

`output/phase18_gpu_smoke/hybrid-human-review-bundle.json`

### `tests/test_phase18_hybrid_human_review_bundle.py`

Regression coverage for:

- byte-identical copies of base and Hybrid PNGs;
- mandatory human review and no automatic selection;
- Hybrid-byte tampering rejection;
- missing semantic approval rejection;
- publication-authority drift rejection;
- repository path-escape rejection.

## Safety properties

This change does not alter generation, Qwen inference, deterministic football geometry, Golden scoring, brand composition or publication logic. It only prepares the exact already-approved semantic artifacts for human visual inspection.

The following remain unchanged and fail-closed:

- Fact Lock;
- identity verification;
- sentiment and losing-side neutrality;
- `$0-local` execution policy;
- FLUX.2 Klein 4B and BF16 locks;
- generated text/branding/exact-number/entity-mark/geometry exclusions;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football ownership;
- Golden minimum 8.5 / elite 9.0+ thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

## Result

A future successful Candidate 1 run can now end with a stable two-image human-review package containing exactly:

1. the provenance-bound FLUX base;
2. the deterministic Hybrid PNG that passed semantic/alignment QA.

No additional FLUX generation is required to perform that comparison, and the reviewer cannot accidentally inspect different bytes from those that passed the automated gates.

# PUL7SAR Phase 18 — Change Set 138

## Strict First-Golden Colab Bootstrap

### Goal

Reduce the remaining gap between a fresh Colab CUDA session and the first genuine Golden Hybrid v5 Candidate 1 review packet without weakening any factual, identity, sentiment, zero-cost, semantic or visual-quality gate.

### Problem

The repository already contained two useful but separate Colab paths:

- `phase18_colab_bootstrap.py`, which repairs/probes the verified Pillow/Transformers/Qwen runtime but can deliberately degrade to engineering-proof mode when semantic preparation fails;
- `phase18_colab_first_golden_review_sealed.py`, which is the strict modern Candidate 1 path through provenance, semantic QA, deterministic football composition and SHA-sealed human-review staging.

For the first genuine Golden Visual, semantic degradation is not an acceptable success mode. A fresh Colab session therefore still required the operator to understand which bootstrap was safe to combine with the strict sealed review path.

### Added

#### `tools/phase18_colab_first_golden_bootstrap.py`

A fresh-runtime entrypoint that:

1. requires `phase18/story-intelligence`;
2. runs the CPU-only repository/reference integrity preflight before dependency repair or model work;
3. reuses the exact verified Colab runtime repair from `phase18_colab_bootstrap.py`;
4. requires the fresh-process CUDA/Pillow/Transformers/Qwen runtime probe to succeed;
5. requires the exact local Qwen snapshot prefetch to succeed;
6. delegates Candidate 1 generation and downstream review staging to `phase18_colab_first_golden_review_sealed.py`;
7. returns only after the exact Base and Hybrid review PNGs are SHA-sealed and replay-verified.

Unlike the general engineering bootstrap, this command has **no semantic engineering-proof fallback**. If Qwen runtime or model preparation fails, it stops before the strict Golden staging path is launched.

The output explicitly preserves:

- Candidate `1` only;
- `$0-local`;
- `human_visual_review_approved=false`;
- `golden_quality_approved=false`;
- `publication_ready=false`;
- `seeds_2_to_4_authorized=false`.

#### `tests/test_phase18_colab_first_golden_bootstrap.py`

Regression coverage now proves:

- repository integrity runs before runtime repair and semantic/model preparation;
- semantic runtime failure is fatal for this Golden bootstrap rather than becoming an engineering fallback;
- Qwen prefetch failure blocks before sealed Candidate 1 staging;
- repository authority drift blocks before runtime repair;
- `main` or any wrong branch is rejected before preflight;
- output paths cannot escape the repository;
- the successful path preserves all downstream human/Golden/publication/Seeds 2-4 locks.

### Modified

No existing generation, semantic, quality, publication or production runtime was modified. The new entrypoint reuses existing qualified components.

### Deleted

Nothing.

### Safety / gate preservation

No change was made to:

- Fact Lock;
- entity/identity verification;
- sentiment and losing-side neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B model lock;
- native BF16 lock;
- Candidate/seed/canvas locks;
- generated text, PUL7SAR branding, score/number, crest/entity-mark and exact sport-geometry exclusions;
- Qwen BASE_SCENE or HYBRID_SURFACE semantic gates;
- deterministic football geometry ownership;
- Golden minimum 8.5 / elite 9.0+ thresholds;
- exact brand/typography integrity;
- SemanticPublicationGate.

### Preferred next compatible Colab command

From the Phase 18 repository root on a compatible CUDA/BF16 runtime:

`PYTHONPATH=. python tools/phase18_colab_first_golden_bootstrap.py`

This is now the preferred fresh-runtime route. It stops before human acceptance and Golden scoring and cannot authorize Seeds 2-4.

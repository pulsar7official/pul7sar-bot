# PUL7SAR Phase 18 — Change Set 128

## First-PNG Provenance Postflight

This change set closes a stale-result gap in the first genuine Golden Candidate 1 GPU path without weakening any factual, identity, neutrality, zero-cost, semantic-publication or Golden visual-quality gate.

A durable generation job reaching `succeeded` and pointing at a `.png` file is no longer treated as sufficient evidence by itself. The result can now be replayed against the locked Candidate 1 identity, the exact executor-result JSON, proof metadata and current PNG bytes before it is accepted as a reusable genuine Golden base image.

### Added

- `engine/intelligence/first_png_provenance_postflight.py`
  - requires Candidate 1;
  - requires a terminal `succeeded` durable job;
  - rechecks request ID, payload SHA-256, provider, model, seed, candidate number and `$0-local` metadata;
  - rejects proof/executor paths that escape the repository;
  - delegates byte-level executor/metadata/PNG replay to the existing `GenerationProvenanceLock`;
  - returns PNG, executor-result and proof-metadata SHA-256 values;
  - explicitly keeps semantic approval, Golden-quality approval and publication readiness false.

- `tools/phase18_verify_first_png_provenance.py`
  - CPU-only CLI for replaying the postflight from the durable queue after Candidate 1 succeeds;
  - resolves the canonical worker executor-result path from job ID and attempt unless an explicit path is supplied;
  - writes `output/phase18_gpu_smoke/first-png-provenance-postflight.json` by default;
  - does not generate an image, mutate the queue, run semantic inspection, score visual quality or authorize publication.

- `tests/test_phase18_first_png_provenance_postflight.py`
  - proves a valid succeeded result passes full replay;
  - rejects non-succeeded jobs;
  - rejects locked job identity drift;
  - rejects executor/proof-metadata tampering;
  - rejects paths outside the repository.

### Deleted

Nothing.

### Production isolation

`main` and `main.py` were not modified. No production publishing path was changed.

### Security and quality invariants

Unchanged:

- Fact Lock and source/story integrity;
- identity verification;
- sentiment and winner/loser neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B and native BF16;
- seed/canvas locks;
- generated brand/text/score/crest/exact-sport-geometry exclusions;
- Qwen semantic inspection;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact brand and typography integrity.

The postflight is deliberately evidence-only and cannot promote a result to publication-ready state.

### Remaining blocker

No new Golden Hybrid v5 Candidate 1 PNG is claimed by this change set. A compatible NVIDIA CUDA/BF16 host is still required for genuine FLUX.2 Klein execution. The new postflight materially reduces the remaining risk by ensuring that an old, tampered or mismatched `succeeded` queue result cannot be reused as genuine evidence when that GPU becomes available.

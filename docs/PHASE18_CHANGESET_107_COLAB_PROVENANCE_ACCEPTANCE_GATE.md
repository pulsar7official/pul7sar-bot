# PUL7SAR Phase 18 — Change Set 107

## Colab generation-provenance acceptance gate

Change Set 107 integrates the Generation Provenance SHA Lock directly into the Colab Golden Hybrid v5 base-acceptance path. A PNG is no longer accepted into `output/phase18_colab/latest.json` merely because its executor result matches request/seed/model/payload/cost fields.

### Added behavior

`tools/phase18_colab_runner.py` now replays `GenerationProvenanceLock` before either a newly generated base or a previously generated reusable base is accepted.

The acceptance replay requires the durable evidence chain to remain consistent:

- Candidate and request identity remain locked.
- FLUX.2 Klein 4B remains the model.
- Handoff payload SHA-256 remains identical.
- Cost mode remains `$0-local`.
- Executor precision remains `bfloat16` through the provenance verifier.
- Executor PNG path resolves to the exact base PNG being accepted.
- Registered proof metadata resolves to the same PNG and identity.
- Executor-result JSON, proof metadata JSON and base PNG are independently SHA-256 hashed.
- `publication_ready` remains `false`.

The accepted Colab summary now records the provenance status and hashes, including:

- `generation_provenance_status`
- `base_png_sha256`
- `executor_result_sha256`
- `proof_metadata`
- `proof_metadata_sha256`
- `provenance_resolved_dtype`
- `provenance_cost_mode`

### Existing-result reuse is now fail-closed

If a cached candidate appears to match the Golden request but its durable provenance cannot be replayed, the runner refuses to reuse it and emits `COLAB_EXISTING_BASE_PROVENANCE_FAILED`. The operator must inspect the evidence or explicitly regenerate with `--force`; stale evidence is not silently trusted.

### Tests

`tests/test_phase18_colab_runner.py` now verifies:

- verified provenance is attached to accepted Colab summaries;
- unverified provenance is rejected;
- publication-ready input is never accepted by this pre-publication path.

The existing Golden contract, result identity, SHA, zero-cost and PNG checks remain intact.

### Gates unchanged

This change does not alter Fact Lock, identity verification, sentiment/neutrality, FLUX.2 Klein 4B, BF16 generation requirements, seeds/canvases, `$0-local`, Base Semantic Layer Ownership, Qwen semantic inspection, SemanticPublicationGate, Golden 8.5/9.0 thresholds, generated-brand exclusion, Exact Brand Integrity or Typography Integrity.

No production branch, paid provider, secret, model weights, font files, fake PNG, fabricated benchmark or fabricated visual score is introduced.

### Why this reduces the remaining gap

The first genuine Candidate 1 will now leave the GPU stage with a Colab summary that has already replayed the durable generation evidence. Downstream Candidate Review no longer discovers provenance problems only after the generation step; corrupted or stale executor/metadata evidence is blocked at base acceptance itself.

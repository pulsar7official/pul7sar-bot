# PUL7SAR Phase 18 — Change Set 129

## GPU Smoke First-PNG Provenance Postflight Integration

This change set affects `phase18/story-intelligence` only. `main` is not modified.

### Purpose

Close the remaining evidence gap in the self-hosted Golden GPU smoke workflow. The first real Candidate 1 PNG must not be sealed into the GPU evidence manifest merely because the generation command returned a PNG. The exact succeeded durable job, executor result, proof metadata and current PNG bytes must replay successfully through the existing First-PNG Provenance Postflight first.

### Changes

- `.github/workflows/phase18-gpu-smoke.yml`
  - now verifies that `engine/intelligence/first_png_provenance_postflight.py` and `tools/phase18_verify_first_png_provenance.py` exist on the protected branch;
  - runs `phase18_verify_first_png_provenance.py` immediately after the real-PNG signature check and before evidence sealing;
  - requires status `FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED`;
  - requires Candidate 1, `$0-local`, and BF16 replay;
  - explicitly requires semantic, Golden-quality and publication approval to remain false;
  - adds the provenance-postflight receipt to the tamper-evident GPU evidence manifest.

- `tests/test_phase18_gpu_smoke_workflow.py`
  - locks the postflight into the workflow contract;
  - proves ordering `generation → provenance postflight → evidence manifest → replay verification → artifact upload`;
  - proves the postflight receipt is included in the evidence manifest;
  - proves the postflight cannot self-authorize semantic, Golden-quality or publication gates.

### Deleted

Nothing.

### Security and editorial invariants preserved

No changes were made to Fact Lock, identity verification, sentiment/neutrality, `$0-local`, FLUX.2 Klein 4B, native BF16, seed/canvas locks, generated branding/text/score/crest/exact-geometry exclusions, Qwen semantic inspection, SemanticPublicationGate, Golden 8.5/9.0 thresholds, or exact brand/typography integrity.

No fake PNG, hosted paid GPU fallback, provider secret, precision downgrade, semantic bypass or publication shortcut was introduced.

### Why this reduces the remaining gap

When the first compatible CUDA/BF16 host becomes available, the self-hosted workflow can now produce Candidate 1 and immediately prove that the evidence being sealed is still the exact executor/metadata/PNG chain that generated it. Stale or tampered bytes fail before artifact evidence is accepted.

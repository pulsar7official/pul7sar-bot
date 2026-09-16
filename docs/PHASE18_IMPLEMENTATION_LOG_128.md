# PUL7SAR Phase 18 — Implementation Log 128

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed first

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Pull request: #1, open, Draft, not merged.
- Branch state before this pass: `diverged` from `main`, 1058 commits ahead and 101 commits behind.
- Reviewed head before this pass: `3c929ce06a546b47a0fca76939c265b5c393b998`.
- Existing verification on that head was green:
  - Phase 18 Story Intelligence Verification run `32753386715` / run 1988: `success`.
  - Phase 18 Composition Matrix Verification run `32753386728` / run 10: `success`.
- No merge, update, force-write or direct modification to `main` was performed.

## Progress made — Change Set 128

Implemented a **First-PNG Provenance Postflight** so a durable Candidate 1 job cannot be reused merely because it says `succeeded` and references a PNG path.

### Added

- `engine/intelligence/first_png_provenance_postflight.py`
  - requires Candidate 1 and a genuinely succeeded durable job;
  - binds the job back to the locked Golden candidate request ID, payload SHA-256, provider, model, seed and `$0-local` metadata;
  - repository-scopes proof and executor paths;
  - replays the existing `GenerationProvenanceLock` against the exact executor result, proof metadata and current PNG bytes;
  - emits tamper-evident SHA-256 values for PNG, executor result and proof metadata;
  - cannot grant semantic, Golden-quality or publication approval.

- `tools/phase18_verify_first_png_provenance.py`
  - CPU-only postflight command for the first succeeded GPU job;
  - loads the locked Candidate 1 from the Golden batch and the durable queue job;
  - defaults to the canonical worker executor result `output/phase18_worker_results/<job-id>-attempt-<attempt>.json`;
  - writes a non-publishing receipt under `output/phase18_gpu_smoke/`;
  - does not generate an image or mutate the queue.

- `tests/test_phase18_first_png_provenance_postflight.py`
  - validates successful full provenance replay;
  - rejects non-succeeded jobs;
  - rejects durable-job identity drift;
  - rejects executor/proof-metadata tampering;
  - rejects repository path escape.

- `docs/PHASE18_CHANGESET_128_FIRST_PNG_PROVENANCE_POSTFLIGHT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_128.md`

### Modified

No existing production or runtime file was modified in this pass. Change Set 128 is additive and reuses the existing trusted provenance contracts.

### Deleted

Nothing.

### `main`

Untouched.

## Why this materially reduces the remaining gap

Before Change Set 128, `phase18_first_png.py` correctly required a durable job to reach `succeeded` and to point to a PNG, but a later reuse of that succeeded queue entry still needed an explicit byte-level replay before it should be trusted as genuine Golden evidence. Change Set 128 provides that replay as a dedicated fail-closed postflight using the existing provenance authority rather than inventing a parallel checksum scheme.

When Candidate 1 is finally produced on a compatible GPU, the safe evidence sequence can now include:

`durable job succeeded → first-PNG provenance postflight → exact executor/metadata/PNG SHA replay → Base semantic/layer ownership → deterministic football geometry → receipt-backed Hybrid QA → Qwen HYBRID_SURFACE → SHA-bound Golden review`

The postflight does not authorize any downstream gate.

## Test status for this pass

- The new tests are discoverable as `tests/test_phase18_*.py` and therefore enter the existing Phase 18 CI suite automatically.
- A fresh CI result for the final Change Set 128 head is not claimed in this log until GitHub Actions completes it.
- CPU CI must not fabricate a Golden GPU PNG.

## Invariants preserved

No changes were made to:

- Fact Lock, source consensus or story-state integrity;
- identity verification and verified-subject rules;
- sentiment and winner/loser neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B;
- native BF16 requirement;
- seed/canvas locks;
- generated PUL7SAR branding/text/score/crest/exact sport-geometry exclusions;
- Qwen Base/HYBRID_SURFACE semantic inspection;
- deterministic football geometry or receipt-backed Hybrid QA;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite target);
- exact final brand and typography integrity requirements.

No Fake PNG, paid provider, hosted-GPU fallback, secret, precision downgrade, semantic bypass, brand-integrity bypass or publication shortcut was introduced.

## Exact remaining blocker to the first genuine Golden Hybrid v5 PNG

The available execution environment still does not expose a compatible NVIDIA CUDA/BF16 host for FLUX.2 Klein 4B. Therefore no new Candidate 1 PNG is fabricated or claimed.

A compatible host is still required for the genuine generation step. Once available, Candidate 1 should remain the only seed spent until its image is reviewed. Change Set 128 reduces the risk after that run by making stale/tampered succeeded-job reuse fail closed before semantic or visual-quality review.

Final publication remains independently blocked until the exact user-approved PUL7SAR logo/geometry/font assets are SHA-locked and pass the existing brand/typography/publication gates.

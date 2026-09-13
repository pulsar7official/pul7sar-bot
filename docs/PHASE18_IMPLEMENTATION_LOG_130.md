# PUL7SAR Phase 18 — Implementation Log 130

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed first

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch state during this pass: `diverged` from `main`, 1163 commits ahead and 108 commits behind after the code/test commits in this pass.
- Base commit reported by compare: `4c0adf6e9d74216e0e9e79c9fea6c981c1de97cd`.
- Merge base reported by compare: `386529f2352c9c6d9a099ac817b9b73077545240`.
- No merge, update, force-write or direct modification to `main` was performed.

## Progress made — Change Set 130

Closed the trust gap between the self-hosted GPU smoke workflow and the direct `phase18_first_png.py` entrypoint. The direct command now requires the same First-PNG provenance replay before it can report either newly generated success or reuse of an already-succeeded Candidate 1 job.

### Added

- `docs/PHASE18_CHANGESET_130_FIRST_PNG_POSTFLIGHT_INTEGRATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_130.md`

### Modified

- `tools/phase18_first_png.py`
  - added `EXPECTED_POSTFLIGHT_STATUS` and locked BF16 postflight contract;
  - added `_run_provenance_postflight(...)` using the existing CPU-only verifier;
  - requires Candidate 1, exact job ID, `$0-local`, `bfloat16`, and no semantic/Golden/publication self-authorization;
  - adds a dedicated provenance-postflight receipt path to the command contract;
  - runs provenance replay before returning `FIRST_REAL_GOLDEN_PNG_ALREADY_EXISTS`;
  - runs provenance replay after a newly successful GPU worker cycle and before returning `FIRST_REAL_GOLDEN_PNG_GENERATED`;
  - verifies the replayed PNG path is the same PNG being reported;
  - exposes the postflight receipt in the one-command evidence/result payload.

- `tests/test_phase18_first_png_preflight.py`
  - proves the new-generation path runs postflight before reporting success;
  - proves the existing-succeeded-job path replays provenance before reuse;
  - verifies the postflight command and identity lock;
  - rejects precision drift and publication-authority drift;
  - rejects PNG-path disagreement between one-command output and replay evidence.

### Deleted

Nothing.

### `main`

Untouched.

## Why this materially reduces the remaining gap

Before this pass, the GPU workflow path was stricter than the direct one-command path. An already-succeeded durable job could be reported by `phase18_first_png.py` after only checking that its PNG still existed. A newly generated PNG was also reported before the separate provenance-postflight CLI was replayed.

Now both supported GPU entry paths require the same post-generation trust boundary:

`real Candidate 1 PNG → succeeded durable job → provenance postflight → exact PNG/executor/proof-metadata SHA replay → report reusable generation success`

A durable `succeeded` state by itself is no longer enough.

## Test status for this pass

- Regression tests were added to the normal `tests/test_phase18_*.py` suite.
- A fresh GitHub Actions result for the final Change Set 130 head is not claimed until the workflow completes.
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

No fake PNG, paid provider, hosted-GPU fallback, secret, precision downgrade, semantic bypass, brand-integrity bypass or publication shortcut was introduced.

## Exact remaining blocker to the first genuine Golden Hybrid v5 PNG

The available execution environment still does not expose a compatible NVIDIA CUDA/BF16 host for FLUX.2 Klein 4B. No new Candidate 1 PNG is fabricated or claimed.

A compatible host is still required for the genuine generation step. Candidate 1 should remain the only seed spent until its visual result is reviewed through the existing semantic/layer, deterministic geometry, Hybrid QA and SHA-bound Golden-quality stages.

Final publication remains independently blocked until the exact user-approved PUL7SAR logo/geometry/font assets are SHA-locked and pass the existing brand/typography/publication gates.

# PUL7SAR Phase 18 — Implementation Log 129

This log records work on `phase18/story-intelligence` only. `main` was not modified.

## Branch state reviewed first

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Branch state before this pass: `diverged` from `main`, 1090 commits ahead and 103 commits behind.
- Base commit reported by compare: `7dece5cb4f1978d88a9b41735e84c7e7e38a9149`.
- Merge base reported by compare: `386529f2352c9c6d9a099ac817b9b73077545240`.
- No merge, update, force-write or direct modification to `main` was performed.

## Progress made — Change Set 129

Integrated the existing **First-PNG Provenance Postflight** directly into the self-hosted Golden GPU smoke workflow so the real Candidate 1 PNG cannot be sealed into GPU evidence before executor/result/proof-metadata/PNG bytes replay successfully.

### Added

- `docs/PHASE18_CHANGESET_129_GPU_SMOKE_PROVENANCE_POSTFLIGHT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_129.md`

### Modified

- `.github/workflows/phase18-gpu-smoke.yml`
  - proves the provenance-postflight engine and CLI exist on the protected branch;
  - runs `tools/phase18_verify_first_png_provenance.py` after the real-PNG signature check;
  - requires `FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED`;
  - requires Candidate 1, `$0-local`, and replayed BF16 execution;
  - explicitly requires semantic, Golden-quality and publication approvals to remain false;
  - includes `first-png-provenance-postflight.json` in the tamper-evident evidence manifest before replay verification and artifact upload.

- `tests/test_phase18_gpu_smoke_workflow.py`
  - locks provenance postflight into the GPU workflow contract;
  - proves ordering `generation → postflight → evidence build → evidence replay → upload`;
  - proves postflight evidence is sealed into the manifest;
  - proves no downstream semantic/Golden/publication gate can be self-authorized by the postflight.

### Deleted

Nothing.

### `main`

Untouched.

## Why this materially reduces the remaining gap

Change Set 128 created a CPU-only provenance replay command, but the self-hosted GPU workflow did not yet require it before evidence sealing. Change Set 129 closes that operational gap. A real PNG now has to survive both immediate PNG validation and full provenance replay before it is accepted into the GPU evidence manifest.

The intended GPU sequence is now:

`repository integrity → CUDA/BF16 → Qwen preflight → FLUX readiness → Candidate 1 → real PNG validation → first-PNG provenance postflight → tamper-evident evidence manifest → evidence replay verification → artifact upload`

No semantic or visual-quality approval is inferred from provenance success.

## Test status for this pass

- The updated tests are discoverable as `tests/test_phase18_*.py` and therefore enter the existing Phase 18 CPU CI suite.
- A fresh CI result for the final Change Set 129 head is not claimed until GitHub Actions completes it.
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

A compatible host is still required for the genuine generation step. Once available, Candidate 1 should remain the only seed spent until its image is reviewed. Change Set 129 ensures the resulting evidence chain fails closed if the succeeded durable job, executor result, proof metadata or PNG bytes no longer match.

Final publication remains independently blocked until the exact user-approved PUL7SAR logo/geometry/font assets are SHA-locked and pass the existing brand/typography/publication gates.
